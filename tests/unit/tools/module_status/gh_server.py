"""A tiny local stand-in for the GitHub issues API, so the tracker's network paths are tested without a network."""
import http.server, json, socket, threading
from urllib.parse import parse_qs, urlparse


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        page = int(parse_qs(urlparse(self.path).query).get("page", ["1"])[0])
        if self.server.mode == "403":
            code, body = 403, {"message": "API rate limit exceeded"}
        elif self.server.mode == "not-json":
            code, body = 200, None
        else:
            code, body = 200, (self.server.issues if page == 1 else [])
        data = b"this is not json" if body is None else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class FakeGitHub:
    """with FakeGitHub(issues, mode) as url: ...   mode: ok | 403 | not-json | down (nothing listens)."""

    def __init__(self, issues=(), mode="ok"):
        self.issues, self.mode = list(issues), mode

    def __enter__(self):
        if self.mode == "down":
            s = socket.socket()
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
            s.close()
            return f"http://127.0.0.1:{port}"
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.issues, self.server.mode = self.issues, self.mode
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def __exit__(self, *exc):
        if self.mode != "down":
            self.server.shutdown()
            self.server.server_close()
