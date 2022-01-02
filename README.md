# showmark
A simple markdown viewer and html converter

![example](examples/example.png)


## Features
 - basic markdown like titles, bold, italic, monospace ✔️
 - syntax highlighting ✔️
 - clickable links ✔️
 - code blocks between three backticks ✔️
 - nested lists ✔️
 - updates on file change ✔️
 - light and dark theme ✔️
 - export to html ✔️
 - easily stylable ✔️

## Usage

```
$ python showmark.py --help
usage: showmark.py [-h] [--export output] input

positional arguments:
  input            Markdown file

optional arguments:
  -h, --help       show this help message and exit
  --export output  export to html

$ python showmark.py path/to/file.md
$ python showmark.py path/to/file.md --export output.html
```

## Installation

requires python3.6 or newer
```
pip install pywebview[qt] markdown watchdog mdx_linkify mdx_truly_sane_lists yaml
```
