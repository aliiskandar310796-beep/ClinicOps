"""Local static server that mirrors GitHub Pages' clean-URL fallback.

GitHub Pages transparently serves a file's content when a visitor requests
its path without the .html extension, and it does so even when a same-named
directory also exists alongside the file (docs/research.html vs. the
docs/research/ subpage hub, which has no index.html of its own). Confirmed
directly against production:

    GET /research       -> 200, research.html's content, no redirect
    GET /research/      -> 404 (no docs/research/index.html)
    GET /research.html  -> 200, identical content

Python's stdlib `http.server` has no such fallback: a bare extensionless
path either 404s, or — worse, if a same-named directory exists — gets
redirected to that directory (the opposite of GitHub Pages' precedence).
The CI/E2E jobs spin up a local server to exercise real in-page navigation
(clicking nav links, which are now extensionless), so the handler here
reproduces the one behavior those jobs actually depend on: prefer the
sibling .html file whenever the request has no extension and no trailing
slash, before falling back to default directory/file serving.
"""

from __future__ import annotations

import functools
import http.server
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


class CleanUrlRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        raw = unquote(urlsplit(path).path)
        last_segment = raw.rsplit("/", 1)[-1]
        if raw and not raw.endswith("/") and "." not in last_segment:
            html_candidate = Path(super().translate_path(raw + ".html"))
            if html_candidate.is_file():
                return str(html_candidate)
        return super().translate_path(path)


def main() -> None:
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8103
    handler = functools.partial(CleanUrlRequestHandler, directory=directory)
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"serving {directory} at http://localhost:{port} (GitHub Pages clean-URL fallback)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
