from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import content_generator as cg


NUMBERED_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")


def all_questions():
    return [
        q
        for topic in cg.load_topics()
        for q in topic["questions"]
    ]


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
    source = set(all_questions())

    assert post == post.strip()
    assert len(post) <= max_chars

    assert meta["character_count"] == len(post)
    assert meta["question_count"] == len(meta["questions"])

    assert meta["guide_link"] in post
    assert re.search(r"https?://\S+", post, re.I)

    hashtags = re.findall(r"(?<!\w)#\w+", post)
    assert len(hashtags) == 5
    assert hashtags == meta["hashtags"]

    actual = numbered_questions(post)

    # The post must contain exactly the selected questions, in order.
    assert actual == meta["questions"] + [meta["followup"]]

    # Every numbered line must be an exact question-bank entry.
    assert all(q in source for q in actual)

    # Most important regression check:
    # no partial/truncated question such as "... average O".
    for q in actual:
        assert q in post
        assert q.strip() == q


def test_generated_posts_300_iterations():
    for _ in range(300):
        link = cg.choose_book_link()
        post, meta = cg.generate_post(
            link,
            max_chars=2850,
            record_history=False,
        )
        validate_one_post(post, meta)


def test_tight_limits_never_cut_questions():
    for limit in (2400, 2200, 2000, 1800, 1600):
        for _ in range(40):
            link = cg.choose_book_link()
            post, meta = cg.generate_post(
                link,
                max_chars=limit,
                record_history=False,
            )
            validate_one_post(post, meta, limit)


def test_special_character_questions_survive():
    candidates = [
        q for q in all_questions()
        if any(token in q for token in ("O(1)", "@Version", "GET", "++", "?", "%"))
    ]

    assert candidates, "Expected at least one special-character question"

    # Directly test the builder rather than waiting for random selection.
    topic = cg.load_topics()[0]
    followup = candidates[0]
    selected = topic["questions"][:5]

    post = cg._build_candidate(
        topic_name=topic["name"],
        questions=selected,
        followup=followup,
        book_link="https://example.com/book",
        template=cg.TEMPLATES[0],
        takeaway=cg.TAKEAWAYS[0],
        hashtags=cg.HASHTAG_SETS[0],
        hook="Test hook",
    )

    assert all(q in post for q in selected)
    assert followup in post


def test_over_limit_behavior_is_whole_question_only():
    # Force a tiny limit until generation fails. Failure is acceptable;
    # silent partial-question truncation is not.
    try:
        cg.generate_post(
            "https://example.com/book",
            max_chars=500,
            record_history=False,
        )
    except RuntimeError as exc:
        assert "without cutting a question" in str(exc)


def test_fingerprint_stability():
    topics = cg.load_topics()
    topic = topics[0]
    questions = topic["questions"][:5]
    followup = topics[1]["questions"][0]

    first = cg._fingerprint(topic["name"], questions, followup)
    second = cg._fingerprint(topic["name"], questions, followup)

    assert first == second
    assert len(first) == 20


def run_all():
    tests = [
        test_question_bank_integrity,
        test_every_question_is_single_line,
        test_book_links_are_valid,
        test_generated_posts_300_iterations,
        test_tight_limits_never_cut_questions,
        test_special_character_questions_survive,
        test_over_limit_behavior_is_whole_question_only,
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
