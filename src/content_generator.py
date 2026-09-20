from __future__ import annotations

import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
RNG = random.SystemRandom()

HOOKS = [
    "🔥 Java Backend interviews are rarely about definitions alone.",
    "🚨 The follow-up question is often harder than the first Java question.",
    "⚡ If you are preparing for a Java Backend interview, practice questions like these.",
    "🎯 Strong Java interviews test how you think about real production problems.",
    "💡 Memorizing Java answers is easy. Explaining what happens internally is harder.",
    "🔥 A Java Backend interview can move from Core Java to production scenarios very quickly.",
]

TAKEAWAYS = [
    "📌 The goal is not to memorize the answer. Explain the trade-offs, failure modes, and production impact.",
    "📌 For senior roles, connect the concept to a real application, its bottleneck, and the decision you would make.",
    "📌 Practice the follow-up: what happens internally, what can fail, and how would you monitor it?",
    "📌 A strong answer usually covers the concept, a real use case, and the trade-off behind the choice.",
]

HASHTAGS = [
    ["#Java", "#SpringBoot", "#Microservices", "#BackendDevelopment", "#InterviewPreparation"],
    ["#JavaDeveloper", "#CoreJava", "#SpringBoot", "#SoftwareEngineering", "#TechCareers"],
    ["#Java", "#JavaProgramming", "#BackendDeveloper", "#SystemDesign", "#CodingInterview"],
    ["#JavaBackend", "#SpringBoot", "#Microservices", "#SystemDesign", "#InterviewTips"],
]


def load_topics():
    data = json.loads((CONFIG / "topics.json").read_text(encoding="utf-8"))
    return data["topics"]


def choose_book_link() -> str:
    links = []
    for line in (CONFIG / "book_links.txt").read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#") and re.match(r"^https?://", value, re.I):
            links.append(value)
    if not links:
        raise RuntimeError("config/book_links.txt must contain at least one URL")
    return RNG.choice(links)


def generate_post(book_link: str, max_chars: int = 2850):
    topics = load_topics()
    main = RNG.choice(topics)
    questions = RNG.sample(main["questions"], k=min(5, len(main["questions"])))

    # Add one cross-topic follow-up to reproduce the mixed interview style seen in the examples.
    other_topics = [t for t in topics if t["name"] != main["name"]]
    other = RNG.choice(other_topics)
    follow_up = RNG.choice(other["questions"])

    hook = RNG.choice(HOOKS)
    takeaway = RNG.choice(TAKEAWAYS)
    hashtags = RNG.choice(HASHTAGS)

    styles = [
        f"{hook}\n\n🧠 {main['name'].upper()}\n\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1)) +
        f"\n\n🎯 FOLLOW-UP SCENARIO\n{len(questions)+1}. {follow_up}\n\n{takeaway}",
        f"{hook}\n\nHere are 5 questions worth preparing:\n\n" +
        "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1)) +
        f"\n\n🔥 One more question:\n{follow_up}\n\n{takeaway}",
        f"{hook}\n\nWhat I would prepare before the interview:\n\n" +
        "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1)) +
        f"\n\n💬 Follow-up:\n{follow_up}\n\n{takeaway}",
    ]

    post = RNG.choice(styles).strip()
    post += f"\n\n📘 You can get the complete guide from here: {book_link}\n\n{' '.join(hashtags)}"

    # Remove optional prose first if the post is too long. Keep questions, CTA and hashtags.
    if len(post) > max_chars:
        lines = post.splitlines()
        while len("\n".join(lines)) > max_chars:
            idx = next((i for i, line in enumerate(lines)
                        if line.strip() and not re.match(r"^\d+\. ", line)
                        and not line.startswith("#")
                        and "complete guide from here" not in line), None)
            if idx is None:
                break
            lines.pop(idx)
        post = "\n".join(lines).strip()

    if len(post) > max_chars:
        raise RuntimeError(f"Post is {len(post)} chars; limit is {max_chars}")
    if book_link not in post:
        raise RuntimeError("Guide link missing from generated post")
    if len(hashtags) != 5:
        raise RuntimeError("Post must contain exactly five hashtags")

    return post, {
        "topic": main["name"],
        "guide_link": book_link,
        "character_count": len(post),
        "hashtags": hashtags,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "python-standard-library-template-engine",
    }
