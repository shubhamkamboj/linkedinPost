from __future__ import annotations

import json
import urllib.error
import urllib.request


API_BASE = "https://api.linkedin.com"
DEFAULT_VERSION = "202609"


def _request(url, method="GET", headers=None, data=None):
    req = urllib.request.Request(
        url,
        method=method,
        headers=headers or {},
        data=data,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, dict(response.headers), body

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"LinkedIn API HTTP {e.code}: {body}"
        ) from e

    except urllib.error.URLError as e:
        raise RuntimeError(
            f"LinkedIn API connection error: {e}"
        ) from e


def get_member_urn(access_token: str) -> str:
    """
    Resolve the authenticated LinkedIn member using the OpenID Connect
    userinfo endpoint.

    Required OAuth scopes:
      - openid
      - profile
      - w_member_social
    """

    status, _, body = _request(
        f"{API_BASE}/v2/userinfo",
        method="GET",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Linkedin-Version": DEFAULT_VERSION,
        },
    )

    if status != 200:
        raise RuntimeError(
            f"LinkedIn userinfo request failed: HTTP {status}: {body}"
        )

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Invalid JSON returned by LinkedIn userinfo endpoint: {body}"
        ) from e

    sub = data.get("sub")

    if not sub:
        raise RuntimeError(
            "LinkedIn userinfo response did not contain 'sub'."
        )

    return f"urn:li:person:{sub}"


def create_text_post(
    access_token: str,
    person_urn: str,
    commentary: str,
    version: str = DEFAULT_VERSION,
    link_url: str | None = None,
):
    """
    Create and publish a text post on the authenticated LinkedIn member's
    personal profile.

    The complete commentary is sent as-is. No truncation or character slicing
    is performed in this function.
    """

    if not commentary or not commentary.strip():
        raise ValueError("Cannot publish an empty LinkedIn post.")

    commentary = commentary.strip()

    # Safety check. The generator is configured below this limit, but this
    # protects the API call if another script creates output/latest.txt.
    if len(commentary) > 3000:
        raise ValueError(
            f"LinkedIn commentary is {len(commentary)} characters; "
            "refusing to publish above the 3000-character safety limit."
        )

    payload = {
        "author": person_urn,
        "commentary": commentary,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    # Give LinkedIn a native Article content target for the guide. The raw URL
    # remains in commentary, while the Article target provides a clear native
    # click target for the external guide.
    if link_url:
        payload["content"] = {
            "article": {
                "source": link_url,
                "title": "Java Backend Master Guide",
                "description": (
                    "Java, Spring Boot, Microservices, System Design and "
                    "Production Engineering interview preparation."
                ),
            }
        }

    serialized_payload = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    print(
        f"LinkedIn API payload prepared: "
        f"commentary_chars={len(commentary)}, "
        f"commentary_utf8_bytes={len(commentary.encode('utf-8'))}, "
        f"guide_link_card={'ENABLED' if link_url else 'DISABLED'}, "
        f"payload_bytes={len(serialized_payload)}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Linkedin-Version": version,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    status, response_headers, body = _request(
        f"{API_BASE}/rest/posts",
        method="POST",
        headers=headers,
        data=serialized_payload,
    )

    post_id = (
        response_headers.get("x-restli-id")
        or response_headers.get("X-RestLi-Id")
        or response_headers.get("X-Restli-Id")
    )

    if not post_id and body:
        try:
            data = json.loads(body)
            post_id = data.get("id")
        except json.JSONDecodeError:
            pass

    if status not in (200, 201):
        raise RuntimeError(
            f"LinkedIn post creation failed: HTTP {status}: {body}"
        )

    print(
        f"LinkedIn API accepted post: "
        f"status={status}, post_id={post_id or 'NOT_RETURNED'}"
    )

    return {
        "status": status,
        "post_id": post_id,
        "response": body,
        "commentary_char_count": len(commentary),
        "commentary_utf8_byte_count": len(commentary.encode("utf-8")),
    }
