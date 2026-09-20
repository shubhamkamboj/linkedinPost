from __future__ import annotations

import http.server
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
CALLBACK = "http://localhost:8765/callback"
SCOPE = "openid profile w_member_social"

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    code = None
    state = None
    error = None
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        CallbackHandler.code = qs.get("code", [None])[0]
        CallbackHandler.state = qs.get("state", [None])[0]
        CallbackHandler.error = qs.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h2>LinkedIn authorization received.</h2><p>You can close this browser tab.</p>")
    def log_message(self, *args):
        pass


def main():
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise SystemExit("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET first.")

    state = secrets.token_urlsafe(24)
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": CALLBACK,
        "state": state,
        "scope": SCOPE,
    })
    url = AUTH_URL + "?" + params
    print("\n1) Add this redirect URL to your LinkedIn app if required:")
    print(CALLBACK)
    print("\n2) Opening LinkedIn authorization in your browser...\n")

    server = http.server.HTTPServer(("localhost", 8765), CallbackHandler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    webbrowser.open(url)
    while CallbackHandler.code is None and CallbackHandler.error is None:
        pass
    server.server_close()

    if CallbackHandler.error:
        raise SystemExit(f"LinkedIn authorization failed: {CallbackHandler.error}")
    if CallbackHandler.state != state:
        raise SystemExit("OAuth state mismatch. Aborting.")

    form = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": CallbackHandler.code,
        "redirect_uri": CALLBACK,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=form, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as response:
        token = json.loads(response.read().decode())

    print("\n===== COPY THESE VALUES TO GITHUB SECRETS =====")
    print("LINKEDIN_ACCESS_TOKEN=")
    print(token.get("access_token", ""))
    print("\nToken details:")
    print(json.dumps({k:v for k,v in token.items() if k != "access_token"}, indent=2))
    print("\nIf your app has OIDC profile access, the project can resolve the member URN automatically.")
    print("================================================\n")

if __name__ == "__main__":
    main()
