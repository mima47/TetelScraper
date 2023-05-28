from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from pypandoc.pandoc_download import download_pandoc

import langEN as lang
import html2text as h2t
import requests
import pypandoc
import re
import os

def isPandocInstalled():
    try:
        pypandoc.get_pandoc_version()
        return True
    except:
        return False

def installPandoc():
    download_pandoc()

def checkInternetConnection(host='http://google.com'):
    try:
        requests.get(host)
        return True
    except:
        return False

def removeJunk(element):
    #Remove unnecessary tags, such as ads
    for tag in element.find_all("script"):
        tag.decompose()

    for tag in element.find_all("ins"):
        tag.decompose()

    for tag in element.find_all("div", class_="code-block-label"):
        tag.decompose()
    
    for tag in element.find_all("div", class_="page-link"):
        tag.decompose()

    for tag in element.find_all("a"):
        tag.decompose()

    #Remove every div with "code-block" in it. These are ads.
    regex = re.compile('.*code-block-.*')
    for tag in element.find_all("div", {"class" : regex}):
        tag.decompose()
    
    return element

def writeToHtml(data, title, path):
    html = "<html>\n<body>\n" + str(data.prettify()) + "\n</body>\n</html>"

    path = os.path.join(path, title)
    file = os.path.join(path, title + ".html")

    if os.path.isdir(path):
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        os.mkdir(path)
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)


def writeToText(data, title, path):
    html = "<html>\n<body>\n" + str(data.prettify()) + "\n</body>\n</html>"
    
    path = os.path.join(path, title)
    file = os.path.join(path, title + ".txt")

    if os.path.isdir(path):
        with open(file, "w", encoding="utf-8") as f:
            f.write(h2t.html2text(html))
    else:
        os.mkdir(path)
        with open(file, "w", encoding="utf-8") as f:
            f.write(h2t.html2text(html))

def writeToWord(data, title, path):
    path = os.path.join(path, title)
    file = os.path.join(path, title + ".docx")

    if os.path.isdir(path):
        pypandoc.convert_text(source=data, format="html", to="docx", outputfile=file, extra_args=['-RTS'])
    else:
        os.mkdir(path)
        pypandoc.convert_text(source=data, format="html", to="docx", outputfile=file, extra_args=['-RTS'])

def getPage(url):
    return requests.get(url)

def parsePage(page, host):
    #Parse the raw web page
    soup = bs(page, "html.parser")

    #pf-content is the only div we need for erettsegi.com
    if host == "erettsegi.com":
        return soup.find("div", class_="pf-content")
    #This is for blog.verselemzes.hu
    return soup.find("div", class_="entry-content")

#Find the title of the page
def getTitle(page):
    try:
        return page.find("h1", class_="title").get_text().replace(":","")
    except:
        return "tetel"

def checkUrl(url):
    result = {"value": False, "reason": "", "host":""}
    parsedUrl = urlparse(url)

    if parsedUrl.netloc != "erettsegi.com" and parsedUrl.netloc != "blog.verselemzes.hu":
        result["reason"] = lang.webpageNotSupported
        return result

    try:
        page = requests.get(url)
        if page.status_code != 200:
            result["reason"] = lang.invalidUrl + str(page.status_code)
            return result
    except:
        result["reason"] = lang.hostNotFound
        return result

    result["value"] = True
    result["reason"] = lang.urlPass
    result["host"] = parsedUrl.netloc
    return result
