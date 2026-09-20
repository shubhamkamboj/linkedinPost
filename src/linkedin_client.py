from __future__ import annotations

import json
import urllib.error
import urllib.request


API_BASE = "https://api.linkedin.com"

# Current LinkedIn Marketing API version: September 2026
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
    Get the authenticated LinkedIn member ID using
    LinkedIn OpenID Connect userinfo endpoint.

    Required OAuth scopes:
        openid
        profile
        w_member_social
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
):
    """
    Create and publish a text post on the authenticated
    LinkedIn member's profile.
    """

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
        data=json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8"),
    )

    post_id = (
        response_headers.get("x-restli-id")
        or response_headers.get("X-RestLi-Id")
    )

    if not post_id and body:
        try:
            data = json.loads(body)
            post_id = data.get("id")
        except json.JSONDecodeError:
            pass

    return {
        "status": status,
        "post_id": post_id,
        "response": body,
    }