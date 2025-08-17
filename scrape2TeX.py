import argparse
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime

#  python3 scrape2TeX.py "https://www.ourgreenway.ca/dispatches-cwa1" --header "Research Brief"
#Latex Helper functions

sourceIndicators = ["source:", "sources:", "sources (", "reference:", "references:", "bibliography:"]

latexBadDictonary = [r"[{}]",r"\\",r"\n", r"\r",]

latexEscapeDictonary = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "%": r"\%",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

def replaceURL(match):
    url = match.group(1)
    if isSafeURL(url):
        return f"\\url{{{url}}}"
    else:
        return latexEscape(url)
    
def isSafeURL(url: str):
    return url.startswith("http") and not any(re.search(p, url) for p in latexBadDictonary)

def latexEscape(s: str):
    if s is None:
        return ""
    s = s.replace("\\", latexEscapeDictonary["\\"])
    return "".join(latexEscapeDictonary.get(ch, ch) for ch in s)

def insertWordbreak(s: str):
    return re.sub(r"([/:\-?&=])", r"\1\\allowbreak{}", s)

def cleanFilename(name: str):
    name = re.sub(r"[^\w\-.]+", "_", name)
    return name[:200] if len(name) > 200 else name

def toTitleCase(text: str):
    return text.title().strip() if text else ""


# Scrape text & download imgs
def linkToFootnote(tag):
    output = ""
    for content in tag.contents:
        if isinstance(content, NavigableString):
            output += latexEscape(content)
        elif content.name == "a":
            text = latexEscape(content.get_text(strip=True))
            href = content.get("href", "").strip()
            if text and href:
                if isSafeURL(href) and all(c not in href for c in "{}\\%$&_#^~") and len(href) < 100:
                    output += f"{text}\\footnote{{\\url{{{href}}}}}"
                else:
                    output += f"{text} ({latexEscape(href)})"
            elif text:
                output += text
        else:
            output += latexEscape(content.get_text(" ", strip=True))

    return output.strip()


def processReferenceText(tag):
    output = ""
    
    for content in tag.contents:
        if isinstance(content, NavigableString):
            output += latexEscape(content)
        elif content.name == "a":
            text = content.get_text(strip=True)
            href = content.get("href", "").strip()
            if text and href:
                output += f"{latexEscape(text)} {href}"
            elif text:
                output += latexEscape(text)
        else:
            output += latexEscape(content.get_text(" ", strip=True))
    return output.strip()

def isSourceParagraph(tag):
    if tag.name != "p":
        return False
    
    text = tag.get_text(strip=True)
    textLower = text.lower()
    
    return any(textLower.startswith(indicator) for indicator in sourceIndicators)

def scrapeResearchPage(url: str):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    main = soup.find("main")
    if not main:
        raise ValueError("No <main> tag found in the page.")
    soup = main

    data = {}

    h1 = soup.find("h1")
    data["title"] = toTitleCase(h1.get_text(strip=True)) if h1 else ""

    author = soup.find("h3", string=lambda s: s and "WRITTEN BY:" in s.upper())
    data["author"] = (
        toTitleCase(author.get_text(strip=True).split(":", 1)[-1].strip()) if author else ""
    )

    edited = soup.find("h3", string=lambda s: s and "EDITED BY:" in s.upper())
    data["edited_by"] = (
        toTitleCase(edited.get_text(strip=True).split(":", 1)[-1].strip()) if edited else ""
    )

    content = []
    references = []
    inSourceSection = False
    
    for tag in soup.find_all(["h2", "p", "img"]):
        if tag.name == "h2":
            inSourceSection = False 
            content.append({"type": "subheading", "text": latexEscape(tag.get_text(strip=True).capitalize())})
        elif tag.name == "p":
            if isSourceParagraph(tag):
                inSourceSection = True
                continue
            elif inSourceSection:
                #Special case for sources txt
                txt = processReferenceText(tag)
                if txt:
                    references.append({"type": "reference", "text": txt})
            else:
                #Regular content paragraph
                txt = linkToFootnote(tag)
                if txt:
                    content.append({"type": "paragraph", "text": txt})
        elif tag.name == "img":
            if inSourceSection:
                inSourceSection = False  
            src = tag.get("src")
            if src:
                content.append({"type": "image", "src": urljoin(url, src)})
    
    data["content"] = content
    data["references"] = references

    return data

def downloadImage(content, imageDirectory):
    os.makedirs(imageDirectory, exist_ok=True)
    for item in content:
        if item.get("type") == "image":
            imgURL = item["src"]
            try:
                r = requests.get(imgURL, timeout=20)
                r.raise_for_status()
                parsed = urlparse(imgURL)
                basename = os.path.basename(parsed.path) or "image"
                fname = cleanFilename(basename)
                localPath = os.path.join(imageDirectory, fname)
                with open(localPath, "wb") as f:
                    f.write(r.content)
                item["local_src"] = os.path.join(imageDirectory, fname).replace("\\", "/")
            except Exception as e:
                    print(f"Failed to download {imgURL}")
                    item["type"] = "skip"
#LaTeX

def dataToTex(data, headerLabel="Research Brief", dateText="", sourceURL=""):
    lines = []
    lines.append(r"\documentclass[letter]{ourGreenwayBrand}")
    lines.append("")
    lines.append(fr"\headerlabel{{{latexEscape(headerLabel)}}}")
    lines.append("")
    lines.append(fr"\titletext{{{latexEscape(data.get('title',''))}}}")
    lines.append(r"\subtitletext{}")
    lines.append(fr"\authortext{{{latexEscape(data.get('author',''))}}}")
    lines.append(fr"\editedtext{{{latexEscape(data.get('edited_by',''))}}}")
    lines.append(fr"\datetext{{{latexEscape(dateText)}}}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append(r"\MakeBrandTitle")
    lines.append("")

    #Main content
    for item in data.get("content", []):
        typ = item.get("type")
        if typ == "subheading":
            lines.append(fr"\section{{{item['text']}}}")
        elif typ == "paragraph":
            lines.append(item["text"])
            lines.append("")
        elif typ == "image":
            src = item.get("local_src") or item.get("src", "")
            lines.append(r"\begin{figure}[htbp]")
            lines.append(r"  \centering")
            lines.append(fr"  \includegraphics[width=0.7\textwidth]{{{src}}}")
            lines.append(r"\end{figure}")
            lines.append("")
        elif typ == "skip":
            continue 

    #Reference handling
    references = data.get("references", [])
    if references:
        lines.append(r"\newpage")  
        lines.append(r"\section{Sources}")  
        lines.append("")
            
        urlPattern = re.compile(r'(https?://\S+)')

        for ref in references:
            if ref.get("type") == "reference":
                refText = ref["text"]
                refText = urlPattern.sub(replaceURL, refText)

                refText = re.sub(r'(\S+)\s+\\url\{\1\}', r'\\url{\1}', refText)

                lines.append(f"\\hspace{{1em}}{refText}")
                lines.append("")

    lines.append(r"\vspace{2em}")
    lines.append(r"\fbox{\parbox{\dimexpr\textwidth-2\fboxsep-2\fboxrule\relax}{")
    lines.append(r"\raggedright")
    lines.append(r"  \small This PDF was automatically generated using the Python-to-LaTeX tool available at~\url{https://github.com/Our-Greenway/scrape2TeX}.\\[0.5em]")
    lines.append(fr"  If there are any differences, the online version at~\url{{{latexEscape(data.get('source_url', sourceURL))}}} shall prevail.")
    lines.append(r"}}")

    lines.append(r"\end{document}")
    
    return "\n".join(lines)

#Operating
def main():
    todayDate = datetime.today().strftime("%B %d, %Y")
    parser = argparse.ArgumentParser(description="Scrape OurGreenway research text and generate LaTeX report")
    parser.add_argument("url", help="Web page URL to scrape")
    parser.add_argument("--out", default="output.tex", help="Path to write the .tex file (default: output.tex)")
    parser.add_argument("--images", default="images", help="Directory to save downloaded images (default: images/)")
    parser.add_argument("--header", default="Research Brief", help="Header label text")
    parser.add_argument("--date", default=todayDate, help="Date string")
    args = parser.parse_args()

    data = scrapeResearchPage(args.url)
    downloadImage(data.get("content", []), args.images)
    tex = dataToTex(data, headerLabel=args.header, dateText=args.date, sourceURL=args.url)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(tex)

if __name__ == "__main__":
    main()