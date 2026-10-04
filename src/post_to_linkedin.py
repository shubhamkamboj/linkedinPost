from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from linkedin_client import create_text_post, get_member_urn


ROOT = Path(__file__).resolve().parents[1]
BOOK_LINKS_FILE = ROOT / "config" / "book_links.txt"


def load_guide_links() -> list[str]:
    """
    Load guide URLs exclusively from config/book_links.txt.

    No guide URL is hardcoded anywhere in Python code.
    """
    if not BOOK_LINKS_FILE.exists():
        raise RuntimeError(
            f"Guide link file does not exist: {BOOK_LINKS_FILE}"
        )

    links: list[str] = []

    for raw_line in BOOK_LINKS_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        link = raw_line.strip()

        if not link:
            continue

        if link.startswith("#"):
            continue

        if not re.fullmatch(r"https://\S+", link):
            raise RuntimeError(
                f"Invalid guide URL in {BOOK_LINKS_FILE}: {link}"
            )

        links.append(link)

    if not links:
        raise RuntimeError(
            f"No guide URLs found in {BOOK_LINKS_FILE}"
        )

    if len(set(links)) != len(links):
        raise RuntimeError(
            "Duplicate guide URLs found in config/book_links.txt."
        )

    return links


def validate_guide_cta(
    post: str,
    metadata: dict,
    guide_links: list[str],
) -> str:
    """
    Validate that the generated post contains:
      1. Guide CTA marker
      2. The exact guide URL selected by the generator
      3. A URL from the configured guide-link file

    Returns the selected guide URL.
    """

    if "📘" not in post:
        raise RuntimeError(
            "Guide CTA marker is missing from the generated post."
        )

    metadata_guide_link = str(
        metadata.get("guide_link", "")
    ).strip()

    if not metadata_guide_link:
        raise RuntimeError(
            "guide_link is missing from output/metadata.json."
        )

    if metadata_guide_link not in guide_links:
        raise RuntimeError(
            "The guide link stored in metadata.json is not present "
            "in config/book_links.txt."
        )

    if metadata_guide_link not in post:
        raise RuntimeError(
            "The selected guide link is missing from the generated post."
        )

    configured_links_in_post = [
        link
        for link in guide_links
        if link in post
    ]

    if len(configured_links_in_post) != 1:
        raise RuntimeError(
            "Generated post must contain exactly one configured "
            "guide link. Found: "
            + str(configured_links_in_post)
        )

    actual_link = configured_links_in_post[0]

    if actual_link != metadata_guide_link:
        raise RuntimeError(
            "Guide link mismatch between generated post and metadata."
        )

    return actual_link


def main():
    enabled = (
        os.getenv(
            "AUTO_POST_ENABLED",
            "false",
        ).lower()
        == "true"
    )

    force_run = (
        os.getenv(
            "FORCE_RUN",
            "false",
        ).lower()
        == "true"
    )

    if not enabled and not force_run:
        print(
            "AUTO_POST_ENABLED is not true and "
            "FORCE_RUN is not true. Skipping LinkedIn publish."
        )
        return

    token = os.getenv(
        "LINKEDIN_ACCESS_TOKEN",
        "",
    ).strip()

    person_urn = os.getenv(
        "LINKEDIN_PERSON_URN",
        "",
    ).strip()

    version = (
        os.getenv(
            "LINKEDIN_VERSION",
            "202609",
        ).strip()
        or "202609"
    )

    if not token:
        raise RuntimeError(
            "Missing LINKEDIN_ACCESS_TOKEN GitHub Secret."
        )

    post_file = ROOT / "output" / "latest.txt"

    if not post_file.exists():
        raise RuntimeError(
            "output/latest.txt does not exist. "
            "Run generate_post.py first."
        )

    post = post_file.read_text(
        encoding="utf-8"
    ).strip()

    if not post:
        raise RuntimeError(
            "Generated post is empty."
        )

    meta_file = ROOT / "output" / "metadata.json"

    metadata = {}

    if meta_file.exists():
        metadata = json.loads(
            meta_file.read_text(
                encoding="utf-8"
            )
        )

    # ---------------------------------------------------------
    # Load guide links ONLY from config/book_links.txt
    # ---------------------------------------------------------

    guide_links = load_guide_links()

    selected_guide_link = validate_guide_cta(
        post,
        metadata,
        guide_links,
    )

    # ---------------------------------------------------------
    # LinkedIn safety validation
    # ---------------------------------------------------------

    print("=" * 70)
    print("LINKEDIN PUBLISH VALIDATION")
    print("=" * 70)

    print(
        f"Character count : {len(post)}"
    )

    print(
        f"UTF-8 byte count: {len(post.encode('utf-8'))}"
    )

    print(
        f"API version     : {version}"
    )

    print(
        f"Configured links: {len(guide_links)}"
    )

    print(
        f"Selected guide  : {selected_guide_link}"
    )

    print(
        f"Starts with     : {post[:180]!r}"
    )

    print(
        f"Ends with       : {post[-180:]!r}"
    )

    print("=" * 70)

    if len(post) > 3000:
        raise RuntimeError(
            f"Generated post is {len(post)} characters. "
            "Refusing to publish because it exceeds "
            "the 3000-character safety limit."
        )

    # Exactly one configured guide URL must exist in the post.
    matching_links = [
        link
        for link in guide_links
        if link in post
    ]

    if len(matching_links) != 1:
        raise RuntimeError(
            "Expected exactly one configured guide URL "
            f"in the generated post, found {len(matching_links)}."
        )

    # ---------------------------------------------------------
    # Resolve LinkedIn member
    # ---------------------------------------------------------

    if not person_urn:
        person_urn = get_member_urn(token)

        print(
            f"Resolved LinkedIn member URN: {person_urn}"
        )

    elif not person_urn.startswith(
        "urn:li:person:"
    ):
        person_urn = (
            f"urn:li:person:{person_urn}"
        )

    # ---------------------------------------------------------
    # LinkedIn link-card option
    # ---------------------------------------------------------

    use_link_card = (
        os.getenv(
            "LINKEDIN_GUIDE_LINK_CARD",
            "false",
        ).lower()
        == "true"
    )

    if use_link_card:
        print(
            "Guide link card : ENABLED"
        )
    else:
        print(
            "Guide link card : DISABLED"
        )

    print(
        f"Guide URL       : {selected_guide_link}"
    )

    # ---------------------------------------------------------
    # Publish
    # ---------------------------------------------------------

    result = create_text_post(
        token,
        person_urn,
        post,
        version,
        link_url=(
            selected_guide_link
            if use_link_card
            else None
        ),
    )

    if result.get("status") not in (
        200,
        201,
    ):
        raise RuntimeError(
            "LinkedIn did not return a successful status: "
            f"{result.get('status')}"
        )

    post_id = result.get("post_id")

    if not post_id:
        raise RuntimeError(
            "LinkedIn returned success but no post ID "
            "was found. "
            f"Response body: {result.get('response', '')}"
        )

    # ---------------------------------------------------------
    # Save publishing metadata
    # ---------------------------------------------------------

    metadata.update(
        {
            "published": True,
            "linkedin_post_id": post_id,
            "linkedin_status": result.get("status"),
            "linkedin_api_version": version,
            "published_character_count": len(post),
            "published_utf8_byte_count": len(
                post.encode("utf-8")
            ),
            "published_guide_link": selected_guide_link,
        }
    )

    meta_file.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=" * 70)
    print(
        "LinkedIn post published successfully."
    )
    print(
        f"Post ID: {post_id}"
    )
    print(
        f"Characters sent: {len(post)}"
    )
    print(
        f"Guide link used: {selected_guide_link}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()