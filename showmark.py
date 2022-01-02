import webview
import argparse
import markdown
from mdx_linkify.mdx_linkify import LinkifyExtension
from pygments.formatters import HtmlFormatter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import yaml

DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(DIR, "showmark.yml")
try:
    with open(CONFIG_PATH) as f:
        SETTINGS = yaml.safe_load(f)
except FileNotFoundError:
    SETTINGS = dict(
        style="style.css",
        markdown_extensions=["fenced_code", "mdx_truly_sane_lists", "codehilite"],
        window=dict(
            text_select=True,
        ),
    )
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(SETTINGS, f)


def open_in_default_browser(attrs, new=False):
    attrs[(None, "target")] = "_blank"
    return attrs


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, display):
        super().__init__()
        self.display = display

    def on_modified(self, event):
        display.update_html()


class MarkdownDisplay:
    def __init__(self):
        self.extensions = [
            "mdx_linkify"
        ]
        self.extensions += SETTINGS["markdown_extensions"]
        if os.path.isabs(SETTINGS["style"]):
            self.csspath = SETTINGS["style"]
        else:
            self.csspath = os.path.join(DIR, SETTINGS["style"])
        self.window = None
        self.path = None

    def get_css(self):
        css = HtmlFormatter(style=SETTINGS["pygmentize_style"]).get_style_defs()
        with open(self.csspath) as f:
            css += f.read()
        return css

    def set_css(self):
        css = self.get_css()
        self.window.load_css(css)

    def get_html(self, path):
        try:
            with open(path) as f:
                html = markdown.markdown(f.read(), extensions=self.extensions)
        except FileNotFoundError:
            html = f"<p>The file {path} does not exist.</p>"

        return html

    def export(self, inpath, outpath):
        html = f"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="utf-8">
</head>

<style>
{self.get_css()}
</style>

<body>
{self.get_html(inpath)}
</body>
</html>
"""
        with open(outpath, "w") as f:
            f.write(html)

    def display(self, path):
        self.path = path
        html = self.get_html(path)
        self.window = webview.create_window(
            os.path.basename(path),
            html=html,
            **SETTINGS["window"]
        )
        # watch the file for changes
        event_handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=path)
        observer.start()
        webview.start(self.set_css, debug=SETTINGS.get("debug", False))

    def update_html(self):
        html = self.get_html(self.path)
        self.window.load_html(html)
        self.set_css()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Markdown file")
    parser.add_argument("--export", metavar="output", help="export to html")
    args = parser.parse_args()

    display = MarkdownDisplay()
    if args.export:
        display.export(args.input, args.export)
    else:
        display.display(args.input)
