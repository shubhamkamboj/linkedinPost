from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from linkedin_client import create_text_post, get_member_urn

ROOT = Path(__file__).resolve().parents[1]


def main():
    enabled = os.getenv("AUTO_POST_ENABLED", "false").lower() == "true"
    if not enabled:
        print("AUTO_POST_ENABLED is not true. Skipping LinkedIn publish.")
        return

    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
    person_urn = os.getenv("LINKEDIN_PERSON_URN", "").strip()
    version = os.getenv("LINKEDIN_VERSION", "202604").strip()
    if not token:
        raise RuntimeError("Missing LINKEDIN_ACCESS_TOKEN GitHub Secret.")

    post_file = ROOT / "output" / "latest.txt"
    if not post_file.exists():
        raise RuntimeError("output/latest.txt does not exist. Run generate_post.py first.")
    post = post_file.read_text(encoding="utf-8").strip()
    if not post:
        raise RuntimeError("Generated post is empty.")

    if not person_urn:
        person_urn = get_member_urn(token)
        print(f"Resolved LinkedIn member URN: {person_urn}")
    elif not person_urn.startswith("urn:li:person:"):
        person_urn = f"urn:li:person:{person_urn}"

    result = create_text_post(token, person_urn, post, version)
    meta_file = ROOT / "output" / "metadata.json"
    metadata = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    metadata.update({"published": True, "linkedin_post_id": result.get("post_id"), "linkedin_status": result.get("status")})
    meta_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LinkedIn post published successfully. ID: {result.get('post_id')}")

if __name__ == "__main__":
    main()
