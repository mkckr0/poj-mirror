from http import HTTPStatus
import os
import re
import time
import traceback
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests


URL = "http://poj.org"
RAW_DIR = "raw/poj.org"

html_list = [
    "",
    "page?id=1000",
    "faq.htm",
]

extra_list = [
    "images/bar.jpg",
    "images/table_back.jpg",
]

os.makedirs(RAW_DIR, exist_ok=True)

session = requests.session()


def mangle_url_path(path: str):
    o = path.replace("?", "/")
    if len(path) == 0:
        o = "index.html"
    return o


def is_error_page(path: str) -> bool:
    with open(path, "rb") as file:
        html = BeautifulSoup(file.read(), "lxml")
    return html.find("title").text.strip() == "Error"


def download_url(url: str, indent: int = 2, disable_cache: bool = False) -> str:
    print(f"{' '*indent}downloading {url}...", end="")

    filename = mangle_url_path(url)
    filepath = os.path.join(RAW_DIR, filename)
    if not disable_cache and os.path.exists(filepath):
        print("skip")
        return filepath

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        res = session.get(urljoin(URL, url))
    except Exception as e:
        print()
        traceback.print_exc()
        return None
    if res.status_code != HTTPStatus.OK:
        print(res.reason)
        return None
    if "text/html" in res.headers["Content-Type"]:
        if "Can not find problem" in res.text:
            return None
    with open(filepath, "wb") as file:
        file.write(res.content)

    print("done")
    time.sleep(1)

    return filepath


def download_html(path: str, indent: int = 2):
    disable_cache = False
    retry_time = 0
    while retry_time < 3:
        filepath = download_url(path, indent, disable_cache)
        if not filepath:
            return
        if is_error_page(filepath):
            if not disable_cache:
                disable_cache = True
            else:
                time.sleep(5)
        else:
            break
        retry_time += 1

    with open(filepath, "r", encoding="utf8") as file:
        html = file.read()
    res_regex = re.compile(
        r"""(?:src|href)\s*=\s*['"]?([\w\d_/]*\.(?:css|js|ico|wmf|png|apng|avif|gif|jpg|jpeg|jfif|pjpeg|pjp|svg|webp|bmp|cur|tif|tiff))"""
    )
    css_url_regex = re.compile(r"""url\(['"]?([^\)'"]*)['"]?\)""")
    for url in res_regex.findall(html):
        # print(url)
        raw_path = download_url(url, indent + 2)

        if not raw_path:
            continue

        if url.endswith(".css"):
            with open(raw_path, "r", encoding="utf8") as file:
                for css_url in css_url_regex.findall(file.read()):
                    download_url(css_url, indent + 4)
        if url.endswith(".js"):
            js_url_regex = re.compile(r"""src\s*=\s*['"]([^'"]*)['"]""")
            with open(raw_path, "r", encoding="utf8") as file:
                for js_url in js_url_regex.findall(file.read()):
                    if js_url.startswith("https://hm.baidu.com"):
                        continue
                    download_url(js_url, indent + 4)


def download_volumes():
    # get volume count
    res = session.get(urljoin(URL, "problemlist"))
    html = BeautifulSoup(res.content, "lxml")
    count = int(html.select_one("center>a:last-child").text)
    for volume in range(1, count + 1):
        download_html(f"problemlist?volume={volume}")
    return count


def download_problems():
    res = session.get(urljoin(URL, "problemlist"))
    html = BeautifulSoup(res.content, "lxml")
    count = int(html.select_one("center>a:last-child").text)
    print(f"volume count: {count}")

    res = session.get(urljoin(URL, f"problemlist?volume={count}"))
    html = BeautifulSoup(res.content, "lxml")
    max_id = int(html.select_one("table.a tr:last-child td").text)
    print(f"max problem id: {max_id}")

    for id in range(1000, max_id + 1):
        download_html(f"problem?id={id}")


for url in html_list:
    download_html(url)

for url in extra_list:
    download_url(url)

download_volumes()
download_problems()

download_url("images/3129_1.gif")