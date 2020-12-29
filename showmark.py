import webview
import fire
import markdown
from mdx_linkify.mdx_linkify import LinkifyExtension
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


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
            "fenced_code",
            LinkifyExtension(linker_options={"callbacks": [open_in_default_browser]}),
            "mdx_truly_sane_lists"
        ]
        self.csspath = "style.css"
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

        html = f"<div class='doc'>\n{html}\n</div>"
        return html

    def display(self, path):
        self.path = path
        html = self.get_html(path)
        self.window = webview.create_window(os.path.basename(path), html=html)
        # watch the file for changes
        event_handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=path)
        observer.start()
        webview.start(self.set_css)

    def update_html(self):
        html = self.get_html(self.path)
        self.window.load_html(html)


if __name__ == "__main__":
    display = MarkdownDisplay()
    fire.Fire(display.display)
