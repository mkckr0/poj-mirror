import base64
import mimetypes
import os
from pathlib import Path, PurePath
import re
import shutil
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

RAW_DIR = "raw/poj.org"
OUT_DIR = "out/poj.org"


def transform_path(src: str) -> str:
    path = PurePath(src)
    if not path.name:
        return src
    if not path.suffix or path.suffix == ".htm":
        path = path.with_suffix(".html")

    path = path.as_posix().replace("=", "_")
    path = path.replace("?", "/")

    return path


def transform_url(cur: str, src: str) -> str:
    return (
        PurePath("../" * len(PurePath(cur).parent.relative_to(RAW_DIR).parts))
        .joinpath(src)
        .as_posix()
    )


def transform_html(src: str, dst: str):
    with open(src, "rb") as file:
        html = BeautifulSoup(file, "lxml")

    if "3129" in str(src):
        img = html.find("image", src="images/3462_1.gif")
        img["src"] = "images/3129_1.gif"

    for a in html.select("a[href]"):
        if (
            a["href"].startswith("problem?")
            or a["href"].startswith("problemlist?")
            or a["href"] == "problemlist"
            or a.text.strip() == "Home Page"
            or a.text.strip() == "F.A.Qs"
            or a.text.strip() == "Frequently Asked Questions"
        ):
            a["href"] = transform_path(a["href"])
            a["href"] = transform_url(src, a["href"])
            if a.text.strip() == "Home Page":
                a["href"] = a["href"] + "/index.html"
        elif not urlparse(a["href"]).scheme:
            a["href"] = urljoin("http://poj.org", a["href"])
    for link in html.select("link[href]"):
        link["href"] = transform_url(src, link["href"])
    for tag in html.select("script[src],img[src],image[src]"):
        tag["src"] = transform_url(src, tag["src"])
    for tag in html.select("[background]"):
        tag["background"] = transform_url(src, tag["background"])

    go_form = html.find("form", action="gotoproblem")
    if go_form:
        del go_form["action"]
        del go_form["method"]
        go_url = "problem/id_${pid}.html"
        go_url = transform_url(src, go_url)
        go_form["onsubmit"] = (
            f"event.preventDefault(); let pid = (new FormData(event.target)).get('pid'); window.location=`{go_url}`"
        )

    # go_button = html.find("input", value="Go")
    # if go_button:
    #     go_button["type"] = "button"
    #     go_url = "problem/id_${pid}.html"
    #     go_url = transform_url(src, go_url)
    #     go_url = go_url.replace(
    #         "xxx", r"""${document.querySelector("input[name='pid']").value}"""
    #     )
    #     go_button["onclick"] = f"window.location=`{go_url}`"

    with open(dst, "wb") as file:
        file.write(html.encode())


def file_to_base64_url(path: str) -> str:
    with open(path, "rb") as file:
        data = base64.b64encode(file.read()).decode()
    mime = mimetypes.guess_type(path)[0]
    return f"data:{mime};base64,{data}"


css_url_regex = re.compile(r"""url\(['"]?([^\)'"]*)['"]?\)""")
js_url_regex = re.compile(r"""src\s*=\s*['"]([^'"]*)['"]""")

for dirpath, dirnames, filenames in os.walk(RAW_DIR):
    for filename in filenames:
        raw_path = PurePath(dirpath, filename)
        out_path = raw_path.as_posix().replace(RAW_DIR, OUT_DIR)

        if raw_path.suffix and raw_path.suffix == ".css":
            with open(raw_path, "r", encoding="utf8") as file:
                css = file.read()

            def sub_data_url(match: re.Match) -> str:
                path = os.path.join(RAW_DIR, match.group(1))
                return f"url({file_to_base64_url(path)})"

            css = css_url_regex.sub(sub_data_url, css)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf8") as file:
                file.write(css)
        elif raw_path.suffix and raw_path.suffix == ".js":
            with open(raw_path, "r", encoding="utf8") as file:
                js = file.read()
            js = js[: js.find("\nvar _hmt")]

            def sub_data_url(match: re.Match) -> str:
                path = os.path.join(RAW_DIR, match.group(1))
                return f'src="{file_to_base64_url(path)}"'

            js = js_url_regex.sub(sub_data_url, js)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf8") as file:
                file.write(js)
        elif raw_path.suffix and raw_path.suffix not in [".htm", ".html"]:
            # directly copy
            # print(out_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            shutil.copyfile(raw_path, out_path)
            continue
        else:
            # handle html
            # print(path)
            out_path = transform_path(out_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            transform_html(raw_path, out_path)
            # break

with open(PurePath(OUT_DIR, "problemlist.html"), "w", encoding="utf8") as file:
    file.write(
        """<head>
  <meta http-equiv="Refresh" content="0; URL=problemlist/volume_1.html" />
</head>"""
    )
