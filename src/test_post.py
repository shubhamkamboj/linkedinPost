from __future__ import annotations

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from linkedin_client import create_text_post, get_member_urn

if __name__ == "__main__":
    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("Set LINKEDIN_ACCESS_TOKEN before running this test.")
    urn = os.getenv("LINKEDIN_PERSON_URN", "").strip() or get_member_urn(token)
    if not urn.startswith("urn:li:person:"):
        urn = "urn:li:person:" + urn
    text = "LinkedIn automation test from my Java interview post generator."
    print(create_text_post(token, urn, text))
