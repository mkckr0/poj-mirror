import base64
import mimetypes
import os
from pathlib import Path, PurePath
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

# res = requests.get("http://poj.org/problem?id=23")
# print("text/html" in res.headers["Content-Type"])
# print("Can not find problem" in res.text)

# src = "raw\\poj.org\\problem\\1002.jpg"
RAW_DIR = "raw/poj.org"

# x = PurePath("../" * len(PurePath(src).relative_to(RAW_DIR).parts)).joinpath("problem\\id_1001.html")

# image to base64 data url
# path = "D:\source\poj-mirror\out\poj.org\images\\table_back.jpg"
# with open(path, "rb") as file:
#     data = base64.b64encode(file.read()).decode()
#     mime = mimetypes.guess_type(path)[0]
#     url = f"data:{mime};base64,{data}"
# print(url)


# css_url_regex = re.compile(r"""url\(['"]?([^\)'"]*)['"]?\)""")
# with open("raw/poj.org/poj.css", "r", encoding="utf8") as file:
#     css = file.read()

# def sub_data_url(match: re.Match) -> str:
#     path = os.path.join(RAW_DIR, match.group(1))
#     with open(path, "rb") as file:
#         data = base64.b64encode(file.read()).decode()
#     mime = mimetypes.guess_type(path)[0]
#     url = f"url(data:{mime};base64,{data})"
#     return url

# print(css_url_regex.sub(sub_data_url, css))
# x = css_url_regex.findall(css)

# js_url_regex = re.compile(r"""src\s*=\s*['"]([^'"]*)['"]""")
# with open("raw/poj.org/poj.js", "r", encoding="utf8") as file:
#     js = file.read()

# js = js[:js.find("\nvar _hmt")]
# print(js)
# x = js_url_regex.findall(js)
# print(x)

# def file_to_base64_url(path: str) -> str:
#     with open(path, "rb") as file:
#         data = base64.b64encode(file.read()).decode()
#     mime = mimetypes.guess_type(path)[0]
#     return f"data:{mime};base64,{data}"

# def sub_data_url(match: re.Match) -> str:
#     path = os.path.join(RAW_DIR, match.group(1))
#     return f'src="{file_to_base64_url(path)}"'

# js = js_url_regex.sub(sub_data_url, js)
# print(js)

# with open("out\poj.org\problem\id_3129.html", "r", encoding="utf8") as file:
#     html = BeautifulSoup(file, "lxml")
# print(html.select("img[src],image[src]"))

print(urlparse("3233/12312312").scheme)