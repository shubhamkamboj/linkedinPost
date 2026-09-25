from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import content_generator as cg


NUMBERED_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
ALLOWED_FORMATS = {
    "roadmap",
    "concept",
    "production",
    "architecture",
    "mistakes",
    "senior",
    "checklist",
    "comparison",
    "question_set",
}


def all_questions():
    return [q for topic in cg.load_topics() for q in topic["questions"]]


def numbered_questions(post: str):
    values = []
    for line in post.splitlines():
        match = NUMBERED_RE.match(line)
        if match:
            values.append(match.group(2))
    return values


def test_question_bank_integrity():
    result = cg.validate_question_bank()
    assert result["topic_count"] >= 2
    assert result["question_count"] >= 100
    assert result["duplicate_question_count"] == 0, result["duplicates"]


def test_every_question_is_single_line():
    for topic in cg.load_topics():
        for question in topic["questions"]:
            assert isinstance(question, str)
            assert question.strip() == question
            assert "\n" not in question
            assert "\r" not in question
            assert len(question) >= 10


def test_book_links_are_valid():
    path = cg.CONFIG / "book_links.txt"
    links = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert links
    assert all(re.fullmatch(r"https?://\S+", link, re.I) for link in links)


def validate_one_post(post, meta, max_chars=2850):
    assert post == post.strip()
    assert 1200 <= len(post) <= max_chars
    assert meta["character_count"] == len(post)
    assert meta["content_format"] in ALLOWED_FORMATS
    assert meta["guide_link"] in post
    assert re.search(r"https?://\S+", post, re.I)

    hashtags = re.findall(r"(?<!\w)#\w+", post)
    assert len(hashtags) == 5
    assert hashtags == meta["hashtags"]

    # The guide CTA is always present.
    assert "📘 Get the Java Backend Guide here:" in post

    if meta["content_format"] == "question_set":
        assert meta["question_count"] == 5
        actual = numbered_questions(post)
        assert actual == meta["questions"] + [actual[-1]]
        source = set(all_questions())
        assert all(q in source for q in actual)
        for q in meta["questions"]:
            assert q in post


def test_generated_posts_500_iterations():
    formats = set()
    for _ in range(500):
        link = cg.choose_book_link()
        post, meta = cg.generate_post(link, max_chars=2850, record_history=False)
        validate_one_post(post, meta)
        formats.add(meta["content_format"])

    # The generator must genuinely support mixed content, not only question posts.
    assert len(formats) >= 5, formats
    assert "question_set" in formats
    assert len(formats - {"question_set"}) >= 4


def test_each_content_format_is_long_enough():
    cg.ALL_TOPICS_CACHE = cg.load_topics()
    topic = cg.ALL_TOPICS_CACHE[0]
    link = cg.choose_book_link()
    for fmt in cg.CONTENT_FORMATS:
        body, _ = cg._build_body(topic["name"], fmt, topic["questions"][:5])
        post = cg._append_cta(body, link, cg.HASHTAG_SETS[0])
        assert 1200 <= len(post) <= 2850, (fmt, len(post))
        cg._validate_structure(
            post,
            book_link=link,
            max_chars=2850,
            content_format=fmt,
        )


def test_tight_limit_fails_without_truncation():
    try:
        cg.generate_post(
            "https://example.com/book",
            max_chars=900,
            record_history=False,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected generation to fail below the minimum content size")


def test_special_character_questions_survive():
    candidates = [
        q
        for q in all_questions()
        if any(token in q for token in ("O(1)", "@Version", "GET", "++", "?", "%"))
    ]
    assert candidates
    assert all("\n" not in q and "\r" not in q for q in candidates)


def test_fingerprint_stability():
    topics = cg.load_topics()
    topic = topics[0]
    seed = topic["questions"][:5]
    first = cg._fingerprint(topic["name"], "question_set", seed)
    second = cg._fingerprint(topic["name"], "question_set", seed)
    assert first == second
    assert len(first) == 20


def run_all():
    tests = [
        test_question_bank_integrity,
        test_every_question_is_single_line,
        test_book_links_are_valid,
        test_generated_posts_500_iterations,
        test_each_content_format_is_long_enough,
        test_tight_limit_fails_without_truncation,
        test_special_character_questions_survive,
        test_fingerprint_stability,
    ]

    for test in tests:
        print(f"RUN  {test.__name__}")
        test()
        print(f"PASS {test.__name__}")

    print()
    print(f"ALL TESTS PASSED: {len(tests)}/{len(tests)}")


if __name__ == "__main__":
    run_all()
