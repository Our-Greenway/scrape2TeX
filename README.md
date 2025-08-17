# Scrape2TeX

Scrape2TeX is a Python-to-LaTeX tool that automates the conversion of legacy research papers hosted on OurGreenway.ca into printable PDF reports using structured LaTeX output.

[Documentation also found here](https://brand-component-kit.vercel.app/scrape2tex)

## Prerequisites

To run Scrape2TeX, you’ll need:

- LaTeX (which includes XeLaTeX)
- Python
- Visual Studio Code (or another IDE, but VS Code is recommended)
- LaTeX Workshop extension for VS Code

## Installation

Install the required Python packages:

```bash
pip install beautifulsoup4 requests
```

## Usage

Use the following command template to run the scraper:

```bash
python3 scrape2TeX.py "https://www.ourgreenway.ca/<!-PAGE!->" \
--out "<!- [OPTIONAL] output file, default: output.tex ->" \
--images "<!- [OPTIONAL] image directory, default: ./images ->" \
--header "<!- TYPE OF ARTICLE ->" \
--date "<!- [OPTIONAL] date of writing, default: today's date ->"
```

Refer to the video for a full walkthrough:

[Watch on YouTube](https://www.youtube.com/watch?v=zX78W-SeGRs)

## Web scraping algorithm

Each page's main content is extracted from within the `<main>` tag. The scraper converts elements as follows:

- `<h1>` → `\titletext{...}` (Main title of the article)
- `<h3>` with "WRITTEN BY:" → `\authortext{...}` (Author name)
- `<h3>` with "EDITED BY:" → `\editedtext{...}` (Editor name)
- `<h2>` → `\section{...}` (Section subheadings)
- `<p>` (normal paragraph) → plain LaTeX paragraph with inline links as `\footnote{\url{...}}`
- `<p>` starting with source indicators → excluded from main body
- `<p>` after a source indicator → rendered as reference entry under `\section{Sources}`
- `<img>` → `\includegraphics{...}` inside `\begin{figure}...\end{figure}`
- `<a>` inside `<p>` → converted to `\footnote{\url{...}}` if safe, otherwise treated as a normal paragraph

