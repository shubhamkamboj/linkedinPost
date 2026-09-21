from __future__ import annotations

import hashlib
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
OUTPUT = ROOT / "output"

RNG = random.SystemRandom()

DEFAULT_MAX_CHARS = 2850
PRIMARY_QUESTION_COUNT = 5
MAX_HISTORY = 1200

GLOBAL_HOOKS = [
    "🔥 Java Backend interviews are rarely about definitions alone.",
    "⚡ If you are preparing for a Java Backend interview, practice questions like these.",
    "🎯 Senior Java interviews often move from a simple concept to a production scenario.",
    "💡 Knowing the syntax is only the beginning. The follow-up is where interviews get interesting.",
    "🚨 One Java interview question can quickly turn into a discussion about performance, concurrency and design.",
    "🔥 Preparing for a Java Backend interview? These are the kinds of questions worth practicing out loud.",
]

TOPIC_HOOKS = {
    "Core Java": [
        "🔥 Core Java questions that expose whether you understand what happens under the hood:",
        "🧠 If you are revising Core Java for a senior interview, start with questions like these:",
        "⚡ Core Java looks simple until the interviewer asks the next 'why'.",
    ],
    "Java 8+ / Streams / Functional Programming": [
        "⚡ Java Streams are easy to write. Explaining their behavior is the real interview test.",
        "🧠 Revising Java 8+? These questions go beyond basic map/filter examples:",
        "🔥 Stream API questions that can quickly turn into performance and design discussions:",
    ],
    "Multithreading & Concurrency": [
        "🔥 Concurrency questions often separate syntax knowledge from real backend experience.",
        "⚠️ If an interviewer asks about threads, be ready for follow-ups around race conditions, locks and production failures.",
        "🧠 Java concurrency is less about creating threads and more about controlling shared work safely.",
    ],
    "Spring Boot": [
        "🚀 Spring Boot interviews often start with annotations and end with proxies, transactions and production behavior.",
        "🧠 Don't stop at 'what does this annotation do?' Spring Boot follow-ups usually go deeper.",
        "🔥 Spring Boot questions worth practicing before a senior backend interview:",
    ],
    "Microservices": [
        "🌐 Microservices interviews are really about failure, communication and trade-offs.",
        "🔥 A microservice can work perfectly in isolation and still fail as part of a distributed system.",
        "🧠 Preparing for a Microservices interview? Practice these architecture questions:",
    ],
    "Kafka": [
        "🔥 Kafka interviews become interesting when the interviewer asks what happens after a failure.",
        "📨 If you work with Kafka, be ready to explain ordering, offsets, retries and duplicate processing.",
        "🧠 Kafka questions that go beyond 'what is a topic and partition?':",
    ],
    "SQL & Hibernate / JPA": [
        "🗄️ SQL and Hibernate interviews often reveal how well you understand performance and data consistency.",
        "🔥 JPA can make database access easy—until production data volume exposes the hidden costs.",
        "🧠 These SQL + Hibernate questions are worth practicing for backend interviews:",
    ],
    "System Design": [
        "🏗️ System design interviews are less about drawing boxes and more about explaining trade-offs.",
        "🔥 Before your next system design round, practice scenarios where components can fail independently.",
        "🧠 Strong system design answers usually connect scale, consistency, availability and failure handling.",
    ],
    "Production Scenarios / Troubleshooting": [
        "🚨 Production debugging questions are where theoretical Java knowledge meets real engineering.",
        "🔥 Imagine this happens in production. What would you check first?",
        "🧠 Senior backend interviews often test how you investigate a problem, not just how you code.",
    ],
    "Coding & DSA": [
        "💻 Coding interviews become easier when you practice the pattern behind the problem.",
        "🔥 A few classic coding problems are still worth solving without looking at the solution.",
        "🧠 Preparing for a Java coding round? Practice these problems and explain the complexity:",
    ],
    "Project Discussion / Senior-Level": [
        "🎯 Your project discussion can decide how deep the interviewer goes into architecture.",
        "🔥 Senior interviews often move from 'what did you build?' to 'why did you build it this way?'",
        "🧠 If you have 5+ years of experience, be ready to defend your technical decisions.",
    ],
    "Spring Security / APIs / Distributed Systems": [
        "🔐 Backend security interviews are rarely limited to JWT definitions.",
        "🔥 API design questions quickly become security, reliability and distributed-systems questions.",
        "🧠 Preparing for Spring Security and backend API interviews? Practice these:",
    ],
    "Redis / Caching / Performance": [
        "⚡ Caching can make a backend faster—or create a completely different production problem.",
        "🔥 Redis interviews are about more than GET and SET. Be ready for consistency, eviction and failure.",
        "🧠 Performance-focused backend interviews often come back to caching decisions:",
    ],
}

TAKEAWAYS = [
    "📌 Don't memorize the answer. Explain the concept, the trade-off, the failure mode and a real production use case.",
    "📌 For senior roles, connect every answer to scalability, reliability, observability and the decision you would make.",
    "📌 A strong interview answer usually covers: what it is, why it exists, when to use it and what can go wrong.",
    "📌 Practice answering these without looking at notes. Then challenge yourself with the next 'why?' question.",
    "📌 The interviewer may start with one question and keep drilling deeper. Practice the follow-up, not just the first answer.",
]

HASHTAG_SETS = [
    ["#Java", "#SpringBoot", "#Microservices", "#BackendDevelopment", "#InterviewPreparation"],
    ["#JavaDeveloper", "#CoreJava", "#SpringBoot", "#SoftwareEngineering", "#TechCareers"],
    ["#Java", "#JavaProgramming", "#BackendDeveloper", "#SystemDesign", "#CodingInterview"],
    ["#JavaBackend", "#SpringBoot", "#Microservices", "#SystemDesign", "#InterviewTips"],
    ["#JavaDeveloper", "#Kafka", "#Microservices", "#BackendEngineering", "#JavaInterview"],
    ["#Java", "#Concurrency", "#SpringBoot", "#BackendDeveloper", "#InterviewPrep"],
]

TEMPLATES = [
    "{hook}\n\n🧠 {topic_upper}\n\n{questions}\n\n🎯 FOLLOW-UP SCENARIO\n{followup_number}. {followup}\n\n{takeaway}",
    "{hook}\n\nHere are {count} questions I would practice before the interview:\n\n{questions}\n\n💬 One follow-up worth preparing:\n{followup_number}. {followup}\n\n{takeaway}",
    "{hook}\n\nIf you can answer these clearly in under 60 seconds each, you are building a strong revision set:\n\n{questions}\n\n🔥 Then prepare for this:\n{followup_number}. {followup}\n\n{takeaway}",
    "{hook}\n\n📝 QUICK INTERVIEW CHECKLIST\n\n{questions}\n\n🚨 EXPECT A FOLLOW-UP ON THIS\n{followup_number}. {followup}\n\n{takeaway}",
    "{hook}\n\nNo answers. No hints. Just interview questions:\n\n{questions}\n\n💬 THE FOLLOW-UP\n{followup_number}. {followup}\n\n{takeaway}",
    "{hook}\n\nA simple practice routine:\n\n{questions}\n\nNow explain this one with a real production example:\n{followup_number}. {followup}\n\n{takeaway}",
]

QUESTION_LINE_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
HASHTAG_RE = re.compile(r"(?<!\w)#\w+")
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def load_topics() -> list[dict]:
    path = CONFIG / "topics.json"
    if not path.exists():
        raise RuntimeError(f"Missing topic bank: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    topics = data.get("topics")

    if not isinstance(topics, list) or not topics:
        raise RuntimeError("config/topics.json must contain a non-empty 'topics' list")

    for topic in topics:
        if not isinstance(topic, dict):
            raise RuntimeError("Every topic must be an object")
        name = str(topic.get("name", "")).strip()
        questions = topic.get("questions")

        if not name:
            raise RuntimeError("Every topic must have a non-empty name")
        if not isinstance(questions, list) or not questions:
            raise RuntimeError(f"Topic '{name}' has no questions")

        for q in questions:
            if not isinstance(q, str) or not q.strip():
                raise RuntimeError(f"Topic '{name}' contains an empty question")
            if "\n" in q or "\r" in q:
                raise RuntimeError(
                    f"Question in '{name}' contains a newline; "
                    "questions must be single-line strings"
                )

    return topics


def choose_book_link() -> str:
    path = CONFIG / "book_links.txt"
    if not path.exists():
        raise RuntimeError(f"Missing book link file: {path}")

    links = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#") and URL_RE.fullmatch(value):
            links.append(value)

    if not links:
        raise RuntimeError("config/book_links.txt must contain at least one valid URL")

    return RNG.choice(links)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _fingerprint(topic: str, questions: list[str], followup: str) -> str:
    raw = "||".join([topic, *questions, followup])
    return hashlib.sha256(_normalize(raw).encode("utf-8")).hexdigest()[:20]


def _load_history() -> list[dict]:
    path = OUTPUT / "history.json"
    if not path.exists():
        return []

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    return value if isinstance(value, list) else []


def _save_history(history: list[dict]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "history.json").write_text(
        json.dumps(history[-MAX_HISTORY:], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _pick_unique_combination(
    main: dict,
    topics: list[dict],
    used_fingerprints: set[str],
) -> tuple[list[str], str, str]:
    other_topics = [t for t in topics if t["name"] != main["name"]]
    if not other_topics:
        raise RuntimeError("At least two topics are required")

    question_count = min(PRIMARY_QUESTION_COUNT, len(main["questions"]))

    for _ in range(100):
        questions = RNG.sample(main["questions"], k=question_count)
        follow_topic = RNG.choice(other_topics)
        followup = RNG.choice(follow_topic["questions"])
        fingerprint = _fingerprint(main["name"], questions, followup)

        if fingerprint not in used_fingerprints:
            return questions, followup, fingerprint

    # Extremely unlikely fallback after a very large history.
    questions = RNG.sample(main["questions"], k=question_count)
    followup = RNG.choice(RNG.choice(other_topics)["questions"])
    fingerprint = _fingerprint(main["name"], questions, followup)
    return questions, followup, fingerprint


def _choose_hook(topic_name: str) -> str:
    options = TOPIC_HOOKS.get(topic_name, []) + GLOBAL_HOOKS
    return RNG.choice(options)


def _build_candidate(
    *,
    topic_name: str,
    questions: list[str],
    followup: str,
    book_link: str,
    template: str,
    takeaway: str,
    hashtags: list[str],
    hook: str,
) -> str:
    question_text = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(questions, 1)
    )

    post = template.format(
        hook=hook,
        topic_upper=topic_name.upper(),
        questions=question_text,
        count=len(questions),
        followup_number=len(questions) + 1,
        followup=followup,
        takeaway=takeaway,
    ).strip()

    post += (
        f"\n\n📘 You can get the complete guide from here: {book_link}"
        f"\n\n{' '.join(hashtags)}"
    )

    return post


def _validate_structure(
    post: str,
    *,
    source_questions: list[str],
    followup: str,
    book_link: str,
    max_chars: int,
) -> None:
    if not post.strip():
        raise RuntimeError("Generated post is empty")

    if len(post) > max_chars:
        raise RuntimeError(
            f"Generated post is {len(post)} characters; max is {max_chars}"
        )

    if post != post.strip():
        raise RuntimeError("Generated post has unexpected leading/trailing whitespace")

    if book_link not in post:
        raise RuntimeError("Guide link is missing from generated post")

    if not URL_RE.search(post):
        raise RuntimeError("Generated post does not contain a URL")

    hashtags = HASHTAG_RE.findall(post)
    if len(hashtags) != 5:
        raise RuntimeError(f"Expected exactly 5 hashtags; found {len(hashtags)}")

    # Every numbered line must be a complete source question or the exact
    # follow-up. This catches partial strings such as "...average O".
    numbered_lines = []
    for line in post.splitlines():
        match = QUESTION_LINE_RE.match(line)
        if match:
            numbered_lines.append(match.group(2))

    expected = [_normalize(q) for q in source_questions]
    expected.append(_normalize(followup))

    for actual in numbered_lines:
        if _normalize(actual) not in expected:
            raise RuntimeError(
                "A numbered question was modified/truncated.\n"
                f"Generated: {actual!r}"
            )

    # Every selected primary question and follow-up must appear exactly.
    for question in source_questions:
        if question not in post:
            raise RuntimeError(
                f"Selected question is missing or altered:\n{question}"
            )

    if followup not in post:
        raise RuntimeError(
            f"Selected follow-up is missing or altered:\n{followup}"
        )


def generate_post(
    book_link: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    *,
    record_history: bool = True,
):
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    topics = load_topics()
    history = _load_history()
    used = {item.get("fingerprint") for item in history}

    # Try multiple topics/templates so a long candidate does not cause us
    # to cut text. We only remove WHOLE questions if absolutely necessary.
    topic_order = topics[:]
    RNG.shuffle(topic_order)

    best = None

    for main in topic_order:
        try:
            questions, followup, fingerprint = _pick_unique_combination(
                main, topics, used
            )
        except RuntimeError:
            continue

        hooks = TOPIC_HOOKS.get(main["name"], []) + GLOBAL_HOOKS
        templates = TEMPLATES[:]
        RNG.shuffle(templates)

        for template in templates:
            # Try the normal 5-question post first.
            for count in range(len(questions), 0, -1):
                selected = questions[:count]
                post = _build_candidate(
                    topic_name=main["name"],
                    questions=selected,
                    followup=followup,
                    book_link=book_link,
                    template=template,
                    takeaway=RNG.choice(TAKEAWAYS),
                    hashtags=RNG.choice(HASHTAG_SETS),
                    hook=RNG.choice(hooks),
                )

                if len(post) <= max_chars:
                    try:
                        _validate_structure(
                            post,
                            source_questions=selected,
                            followup=followup,
                            book_link=book_link,
                            max_chars=max_chars,
                        )
                    except RuntimeError:
                        continue

                    best = (
                        post,
                        main["name"],
                        selected,
                        followup,
                        fingerprint,
                    )
                    break

            if best:
                break

        if best:
            break

    if not best:
        raise RuntimeError(
            "Could not build a valid LinkedIn post within the character limit "
            "without cutting a question."
        )

    post, topic_name, questions, followup, fingerprint = best
    generated_at = datetime.now(timezone.utc).isoformat()

    if record_history:
        history.append(
            {
                "fingerprint": fingerprint,
                "topic": topic_name,
                "questions": questions,
                "followup": followup,
                "generated_at_utc": generated_at,
            }
        )
        _save_history(history)

    metadata = {
        "topic": topic_name,
        "question_count": len(questions),
        "questions": questions,
        "followup": followup,
        "guide_link": book_link,
        "character_count": len(post),
        "hashtags": HASHTAG_RE.findall(post),
        "fingerprint": fingerprint,
        "generated_at_utc": generated_at,
        "history_size": len(history),
        "question_bank_size": sum(len(t["questions"]) for t in topics),
        "generator": "python-standard-library-template-engine-v3",
    }

    return post, metadata


def validate_question_bank() -> dict:
    topics = load_topics()
    questions = [q for topic in topics for q in topic["questions"]]

    normalized = [_normalize(q) for q in questions]
    duplicates = sorted(
        {q for q in normalized if normalized.count(q) > 1}
    )

    return {
        "topic_count": len(topics),
        "question_count": len(questions),
        "duplicate_question_count": len(duplicates),
        "duplicates": duplicates,
    }
