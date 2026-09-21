from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_generator import (
    choose_book_link,
    generate_post,
    validate_question_bank,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"


def main():
    max_chars = int(os.getenv("POST_MAX_CHARS", "2850"))

    bank = validate_question_bank()
    print(
        f"Question bank: {bank['question_count']} questions "
        f"across {bank['topic_count']} topics"
    )

    if bank["duplicate_question_count"]:
        raise RuntimeError(
            f"Question bank contains "
            f"{bank['duplicate_question_count']} duplicate questions"
        )

    link = choose_book_link()
    post, meta = generate_post(link, max_chars)

    OUT.mkdir(parents=True, exist_ok=True)

    try:
        date_key = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%Y-%m-%d")
    except Exception:
        date_key = datetime.now().strftime("%Y-%m-%d")

    (OUT / f"{date_key}.md").write_text(
        post + "\n",
        encoding="utf-8",
    )

    (OUT / "latest.txt").write_text(
        post + "\n",
        encoding="utf-8",
    )

    (OUT / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 70)
    print(post)
    print("=" * 70)
    print(f"Generated characters: {len(post)}")
    print(f"Topic: {meta['topic']}")
    print(f"Primary questions: {meta['question_count']}")
    print(f"Question bank: {meta['question_bank_size']}")
    print(f"Fingerprint: {meta['fingerprint']}")


if __name__ == "__main__":
    main()
