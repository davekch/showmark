import webview
import fire
import markdown
from mdx_linkify.mdx_linkify import LinkifyExtension
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
        markdown_extensions=["fenced_code", "mdx_truly_sane_lists"],
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
        self.extensions = [LinkifyExtension(
            linker_options={"callbacks": [open_in_default_browser]}
        )]
        self.extensions += SETTINGS["markdown_extensions"]
        if os.path.isabs(SETTINGS["style"]):
            self.csspath = SETTINGS["style"]
        else:
            self.csspath = os.path.join(DIR, SETTINGS["style"])
        self.window = None
        self.path = None

    def set_css(self):
        with open(self.csspath) as f:
            css = f.read()
            self.window.load_css(css)

    def get_html(self, path):
        try:
            with open(path) as f:
                html = markdown.markdown(f.read(), extensions=self.extensions)
        except FileNotFoundError:
            html = f"<p>The file {path} does not exist.</p>"

        return html

    def display(self, path):
        self.path = path
        html = self.get_html(path)
        print(html)
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
    display = MarkdownDisplay()
    fire.Fire(display.display)
