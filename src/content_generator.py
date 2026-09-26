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
MIN_TARGET_CHARS = 1250
PRIMARY_QUESTION_COUNT = 5
MAX_HISTORY = 1200

GLOBAL_HOOKS = [
    "🔥 Java Backend engineering becomes much easier when you understand the reason behind the design.",
    "⚡ A strong backend developer does more than write code — they understand what happens when the system is under pressure.",
    "🎯 Preparing for a Java Backend role? Don't study isolated concepts. Connect them to real production behavior.",
    "💡 One useful shift in backend preparation: stop asking only 'what is it?' and start asking 'why was it designed this way?'.",
    "🚀 Java, Spring Boot and Microservices become much more valuable when you can connect them to real engineering decisions.",
]

HASHTAG_SETS = [
    ["#Java", "#SpringBoot", "#Microservices", "#BackendDevelopment", "#SoftwareEngineering"],
    ["#JavaDeveloper", "#CoreJava", "#SpringBoot", "#BackendEngineering", "#TechCareers"],
    ["#Java", "#JavaProgramming", "#BackendDeveloper", "#SystemDesign", "#SoftwareEngineering"],
    ["#JavaBackend", "#SpringBoot", "#Microservices", "#SystemDesign", "#InterviewPreparation"],
    ["#JavaDeveloper", "#Kafka", "#Microservices", "#BackendEngineering", "#JavaInterview"],
    ["#Java", "#Concurrency", "#SpringBoot", "#BackendDeveloper", "#InterviewPrep"],
]

TAKEAWAYS = [
    "📌 The goal is not to memorize more terms. The goal is to understand the trade-off, failure mode and production impact behind each decision.",
    "📌 For senior roles, connect your answer to scalability, reliability, observability, security and operational cost.",
    "📌 A strong backend answer usually covers: what it is → why it exists → when to use it → what can go wrong.",
    "📌 Keep asking the next 'why?'. That is often where framework knowledge turns into engineering understanding.",
]

# The question bank remains useful, but questions are now only ONE content format.
TOPIC_HOOKS = {
    "Core Java": [
        "🧠 Core Java is not just syntax. The interesting part starts when you ask what happens under the hood.",
        "☕ Strong Java fundamentals make almost every higher-level backend decision easier to reason about.",
    ],
    "Java 8+ / Streams / Functional Programming": [
        "⚡ Streams can make code expressive, but senior-level discussions quickly move into laziness, allocation and performance.",
        "🧠 Java 8+ is much more than map/filter. The real value is knowing when the abstraction helps and when it hides a cost.",
    ],
    "Multithreading & Concurrency": [
        "🧵 Concurrency problems are rarely visible in a happy-path test. They appear when timing, contention and shared state collide.",
        "⚠️ Threads are easy to create. Correctly controlling shared work is the harder engineering problem.",
    ],
    "Spring Boot": [
        "🚀 Spring Boot removes a lot of boilerplate, but understanding what it does behind the scenes becomes important at senior level.",
        "🧠 Spring Boot becomes much easier when you understand beans, proxies, auto-configuration and the application lifecycle.",
    ],
    "Microservices": [
        "🌐 Microservices are less about creating many services and more about managing distributed failure and communication.",
        "🔥 A service can be perfectly healthy by itself and still become part of a system-wide failure.",
    ],
    "Kafka": [
        "📨 Kafka looks simple at the API level. Production behavior gets interesting around ordering, retries, offsets and consumer lag.",
        "🔥 Messaging systems reward engineers who understand failure handling, not just producers and consumers.",
    ],
    "SQL & Hibernate / JPA": [
        "🗄️ Hibernate can make database access feel invisible. Production performance often starts when you make that hidden work visible.",
        "⚡ Database performance is usually about understanding the work being done, not just adding more hardware.",
    ],
    "System Design": [
        "🏗️ Good system design starts with requirements and trade-offs, not with drawing boxes on a whiteboard.",
        "🎯 At scale, every convenient decision eventually has a cost somewhere else in the system.",
    ],
    "Production Scenarios / Troubleshooting": [
        "🚨 Production debugging is where theoretical knowledge meets incomplete information, noisy logs and real users.",
        "🔍 When a production system breaks, the first skill is not guessing the cause. It is narrowing the search space.",
    ],
    "Coding & DSA": [
        "💻 Coding rounds become easier when you recognize the pattern instead of memorizing isolated solutions.",
        "🧠 A good coding answer explains both the solution and why the chosen complexity is acceptable.",
    ],
    "Project Discussion / Senior-Level": [
        "🎯 Senior interviews often move from 'what did you build?' to 'why did you build it this way?'.",
        "🏗️ Project discussions are really architecture discussions when the interviewer starts asking about trade-offs.",
    ],
    "Spring Security / APIs / Distributed Systems": [
        "🔐 Backend security is not just JWT. It is identity, authorization, trust boundaries and failure handling.",
        "🌐 API design becomes much more interesting when security, retries, idempotency and observability enter the conversation.",
    ],
    "Redis / Caching / Performance": [
        "⚡ Caching can reduce latency dramatically — and can also introduce stale data, invalidation and consistency problems.",
        "🔥 Redis is easy to start with. Designing the cache correctly is the real engineering work.",
    ],
}

TOPIC_CONTENT = {
    "Core Java": {
        "focus": ["OOP and object contracts", "Collections and data structures", "JVM memory and object lifecycle", "equals/hashCode and immutability", "exceptions and API design"],
        "mistakes": ["memorizing collection APIs without knowing their complexity", "using mutable objects as HashMap keys", "catching broad exceptions without a recovery strategy", "ignoring object allocation in hot paths", "treating Java syntax as the same thing as Java runtime behavior"],
        "production": ["unexpected memory growth", "high CPU caused by excessive object creation", "collection contention under concurrent traffic", "slow code caused by the wrong data structure", "bugs caused by broken equals/hashCode contracts"],
        "architecture": ["choose data structures based on access patterns", "keep domain objects predictable and immutable where useful", "make failure behavior explicit", "measure before optimizing", "treat API contracts as part of design"],
    },
    "Java 8+ / Streams / Functional Programming": {
        "focus": ["Streams and lazy evaluation", "Optional and API contracts", "Collectors and grouping", "parallel streams and their limits", "functional interfaces and method references"],
        "mistakes": ["using streams everywhere even when a loop is clearer", "assuming parallel streams automatically improve performance", "creating deeply nested stream pipelines", "using Optional as a universal replacement for null", "forgetting that terminal operations trigger execution"],
        "production": ["CPU spikes from expensive stream operations", "large collections causing memory pressure", "slow aggregation pipelines", "parallel work competing with application threads", "hard-to-debug pipelines with hidden side effects"],
        "architecture": ["prefer readable pipelines", "keep side effects at the edges", "benchmark parallelism with realistic data", "use collectors deliberately", "make performance-sensitive paths explicit"],
    },
    "Multithreading & Concurrency": {
        "focus": ["race conditions and visibility", "synchronized and locks", "Executors and thread pools", "CompletableFuture", "concurrent collections and back-pressure"],
        "mistakes": ["creating unbounded threads", "sharing mutable state without a clear ownership model", "using synchronized without understanding contention", "blocking inside async workflows", "ignoring executor queue saturation"],
        "production": ["thread-pool exhaustion", "deadlocks", "request latency caused by lock contention", "unbounded queues consuming memory", "tasks waiting indefinitely on downstream dependencies"],
        "architecture": ["bound concurrency", "separate CPU-bound and I/O-bound workloads", "make queue capacity explicit", "define timeout and cancellation behavior", "monitor active threads, queue depth and task latency"],
    },
    "Spring Boot": {
        "focus": ["auto-configuration", "dependency injection and bean lifecycle", "AOP proxies", "transactions", "Actuator and production configuration"],
        "mistakes": ["adding annotations without understanding proxy boundaries", "putting too much business logic in controllers", "assuming @Transactional works across every call path", "ignoring configuration precedence", "shipping without health and observability endpoints"],
        "production": ["transaction boundaries not behaving as expected", "slow startup", "connection-pool exhaustion", "misconfigured profiles", "memory or thread-pool pressure under load"],
        "architecture": ["keep controllers thin", "define transaction boundaries around business operations", "externalize environment-specific configuration", "use Actuator for operational visibility", "keep cross-cutting concerns out of business code"],
    },
    "Microservices": {
        "focus": ["service boundaries", "API contracts", "timeouts and retries", "circuit breakers", "distributed transactions and observability"],
        "mistakes": ["splitting services too early", "retrying every failure", "using synchronous calls for every workflow", "ignoring idempotency", "having no trace across service boundaries"],
        "production": ["cascading failures", "retry storms", "partial outages", "dependency timeouts", "inconsistent state after a failed workflow"],
        "architecture": ["define clear ownership boundaries", "use timeouts at every network boundary", "make retries selective and bounded", "design idempotent operations", "propagate correlation or trace context"],
    },
    "Kafka": {
        "focus": ["partitions and ordering", "consumer groups", "offsets", "retries and DLQ", "delivery semantics"],
        "mistakes": ["assuming global ordering", "using unlimited retries", "ignoring consumer lag", "committing offsets at the wrong point", "assuming exactly-once solves every business duplicate"],
        "production": ["consumer lag", "poison messages", "rebalance storms", "duplicate processing", "hot partitions"],
        "architecture": ["partition by the business ordering key", "make consumers idempotent", "measure lag and processing latency", "separate retryable and non-retryable failures", "define replay strategy before production"],
    },
    "SQL & Hibernate / JPA": {
        "focus": ["indexes and query plans", "transactions", "N+1 queries", "fetch strategies", "connection pools"],
        "mistakes": ["loading entire tables", "ignoring generated SQL", "using eager relationships casually", "missing indexes on real access paths", "keeping transactions open during slow external calls"],
        "production": ["N+1 query explosions", "database connection exhaustion", "lock contention", "slow queries after data growth", "unexpected transaction rollbacks"],
        "architecture": ["design queries around access patterns", "inspect execution plans", "keep transactions short", "size connection pools deliberately", "use pagination and batching for large datasets"],
    },
    "System Design": {
        "focus": ["requirements and scale", "data modeling", "caching", "queues and asynchronous processing", "availability and failure handling"],
        "mistakes": ["jumping into components before clarifying requirements", "using a cache without an invalidation strategy", "ignoring hot keys", "assuming retries are free", "forgetting operational concerns"],
        "production": ["traffic spikes", "dependency failures", "hot partitions or keys", "stale data", "regional or zone-level failures"],
        "architecture": ["start with functional and non-functional requirements", "estimate traffic and storage", "identify bottlenecks", "design for failure", "define observability and operational ownership"],
    },
    "Production Scenarios / Troubleshooting": {
        "focus": ["logs and metrics", "distributed tracing", "CPU and memory", "database and dependency health", "safe mitigation"],
        "mistakes": ["restarting services before collecting evidence", "changing multiple variables at once", "looking only at application logs", "ignoring recent deployments", "treating symptoms as the root cause"],
        "production": ["API timeouts", "high CPU", "memory pressure", "Kafka lag", "Redis failures"],
        "architecture": ["establish a baseline", "check recent changes", "correlate metrics with traces and logs", "mitigate user impact first", "document the root cause and prevention"],
    },
    "Coding & DSA": {
        "focus": ["hashing", "two pointers", "sliding window", "stacks and queues", "trees and graphs"],
        "mistakes": ["coding before clarifying constraints", "missing edge cases", "choosing a data structure by habit", "not stating complexity", "optimizing before getting a correct baseline"],
        "production": ["large input sizes", "memory limits", "latency-sensitive paths", "duplicate or malformed data", "unexpected boundary conditions"],
        "architecture": ["state assumptions", "build a correct simple solution first", "explain complexity", "test edge cases", "then optimize based on constraints"],
    },
    "Project Discussion / Senior-Level": {
        "focus": ["architecture decisions", "trade-offs", "ownership", "failure handling", "performance and observability"],
        "mistakes": ["describing only features", "not knowing why a technology was selected", "ignoring failure scenarios", "claiming team work without explaining personal ownership", "not knowing system bottlenecks"],
        "production": ["a feature that failed under load", "a difficult production incident", "a dependency outage", "a migration or rollout problem", "a performance bottleneck"],
        "architecture": ["explain the context", "state alternatives considered", "explain the trade-off", "describe the operational result", "say what you would change today"],
    },
    "Spring Security / APIs / Distributed Systems": {
        "focus": ["authentication and authorization", "JWT and token lifecycle", "OAuth2", "API validation", "idempotency and rate limiting"],
        "mistakes": ["treating authentication as authorization", "putting secrets in source code", "never expiring sensitive credentials", "trusting client input", "retrying non-idempotent requests blindly"],
        "production": ["token misuse", "credential leakage", "API abuse", "duplicate requests", "downstream authorization failures"],
        "architecture": ["define trust boundaries", "validate input at the edge", "separate identity from permissions", "protect sensitive operations", "log security events without leaking secrets"],
    },
    "Redis / Caching / Performance": {
        "focus": ["cache-aside", "TTL and eviction", "hot keys", "distributed locks", "cache consistency"],
        "mistakes": ["caching everything", "using unlimited TTLs", "ignoring stampedes", "treating Redis as the source of truth without a deliberate design", "using distributed locks without expiry and ownership"],
        "production": ["cache miss storms", "hot keys", "memory pressure", "stale values", "Redis availability issues"],
        "architecture": ["define the source of truth", "choose TTL based on business freshness", "protect expensive recomputation", "monitor hit rate and memory", "design a failure path when the cache is unavailable"],
    },
}

# Friendly aliases so topic additions do not break content generation.
DEFAULT_PROFILE = {
    "focus": ["core concepts", "performance", "reliability", "security", "observability"],
    "mistakes": ["learning syntax without understanding trade-offs", "ignoring production behavior", "not measuring performance", "missing failure handling", "not documenting decisions"],
    "production": ["latency spikes", "resource exhaustion", "dependency failures", "unexpected data growth", "partial outages"],
    "architecture": ["clarify requirements", "define boundaries", "measure bottlenecks", "design failure handling", "add observability"],
}

CONTENT_FORMATS = [
    "roadmap",
    "concept",
    "production",
    "architecture",
    "mistakes",
    "senior",
    "checklist",
    "comparison",
    "question_set",
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
                raise RuntimeError(f"Question in '{name}' contains a newline")
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


def _fingerprint(topic: str, content_format: str, body_seed: list[str]) -> str:
    raw = "||".join([topic, content_format, *body_seed])
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


def _profile(topic_name: str) -> dict:
    return TOPIC_CONTENT.get(topic_name, DEFAULT_PROFILE)


def _choose_topic(topics: list[dict], used: set[str]) -> dict:
    candidates = topics[:]
    RNG.shuffle(candidates)
    # Prefer a topic with an available content profile, but keep all question-bank topics eligible.
    candidates.sort(key=lambda t: t["name"] not in TOPIC_CONTENT)
    return candidates[0]


def _choose_format(history: list[dict]) -> str:
    recent = [item.get("content_format") for item in history[-6:]]
    available = [fmt for fmt in CONTENT_FORMATS if fmt not in recent]
    if not available:
        available = CONTENT_FORMATS[:]
    return RNG.choice(available)


def _numbered(items: list[str], start: int = 1) -> str:
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start))


def _bullets(items: list[str]) -> str:
    return "\n".join(f"• {item}" for item in items)


def _build_body(topic_name: str, content_format: str, questions: list[str]) -> tuple[str, list[str]]:
    profile = _profile(topic_name)
    hook = RNG.choice(TOPIC_HOOKS.get(topic_name, []) + GLOBAL_HOOKS)
    focus = RNG.sample(profile["focus"], k=min(5, len(profile["focus"])))
    mistakes = RNG.sample(profile["mistakes"], k=min(5, len(profile["mistakes"])))
    production = RNG.sample(profile["production"], k=min(4, len(profile["production"])))
    architecture = RNG.sample(profile["architecture"], k=min(5, len(profile["architecture"])))

    if content_format == "roadmap":
        body = f"""{hook}

If I had to prepare for a Java Backend role today, I would not start by collecting hundreds of random interview questions.

I would build the preparation in layers:

🧩 1. FOUNDATION
{_bullets(focus)}

🏗️ 2. BACKEND ENGINEERING
{_bullets(architecture)}

🚨 3. PRODUCTION THINKING
{_bullets(production)}

🎯 4. INTERVIEW PRACTICE
For every concept, prepare four things:
• What is it?
• Why does it exist?
• What trade-off does it introduce?
• What can go wrong in production?

The biggest mistake is studying Java, Spring Boot, Kafka, SQL and System Design as separate subjects.

They are connected.
A slow API can become a database problem.
A database problem can become a thread-pool problem.
A thread-pool problem can become a microservices timeout problem.

That connection is what turns technology knowledge into backend engineering."""
        seed = focus + architecture + production

    elif content_format == "concept":
        concept = RNG.choice(focus)
        body = f"""{hook}

Let's take one backend concept that looks simple on paper:

👉 {concept}

The useful way to study a concept is not to stop at the definition.

Ask these questions instead:

1. Why was this designed this way?
2. What problem does it solve?
3. What does it cost in CPU, memory, latency or complexity?
4. What happens when traffic or data volume grows?
5. What happens when a dependency fails?

For {topic_name}, this mindset is especially useful because the same implementation can behave very differently under production load.

A good learning loop is:

📚 Understand the abstraction
→ 🔍 Understand the implementation
→ ⚙️ Test the behavior
→ 📈 Measure the performance
→ 🚨 Study the failure mode
→ 🏗️ Decide when you would actually use it

That is a much stronger preparation strategy than memorizing definitions.

💡 A useful rule: if you cannot explain the failure mode, you probably do not understand the concept deeply enough yet.

For interview preparation, keep one small runnable example for every important concept. It gives you something concrete to reason about instead of relying only on memorized wording."""
        seed = [concept, *focus]

    elif content_format == "production":
        scenario = RNG.choice(production)
        body = f"""🚨 PRODUCTION SCENARIO — {topic_name.upper()}

Imagine the application was healthy yesterday.
Today, users suddenly start reporting slow requests.

One of the symptoms is:
👉 {scenario}

What should you do first?

Don't immediately restart the service.
Don't immediately increase the instance size.
Don't change five things at once.

Start by narrowing the search space:

🔎 CHECK 1 — Recent changes
• deployment
• configuration
• traffic pattern
• database/schema changes

📊 CHECK 2 — Metrics
• latency
• throughput
• CPU
• memory
• thread pools / queues

🧵 CHECK 3 — Dependencies
• database
• cache
• Kafka
• downstream APIs

📝 CHECK 4 — Logs + traces
Look for the first component where the latency or error rate changes.

🛠️ CHECK 5 — Mitigate safely
Reduce user impact first, then continue the root-cause investigation.

The important lesson:
Production debugging is a process of elimination.
The goal is not to guess the root cause faster.
The goal is to collect the right evidence faster."""
        seed = [scenario, *production]

    elif content_format == "architecture":
        body = f"""🏗️ JAVA BACKEND ARCHITECTURE — {topic_name}

A scalable design is not just a collection of technologies.
It is a set of decisions about boundaries, failure and trade-offs.

For a backend system, I would think through these layers:

1️⃣ API LAYER
• validation
• authentication
• rate limiting
• idempotency

2️⃣ BUSINESS LAYER
• clear responsibilities
• transaction boundaries
• domain rules

3️⃣ DATA LAYER
• access patterns
• indexes
• caching
• consistency

4️⃣ ASYNC LAYER
• Kafka / queues
• retries
• dead-letter handling
• replay strategy

5️⃣ OBSERVABILITY
• metrics
• logs
• traces
• alerts

6️⃣ FAILURE HANDLING
• timeouts
• circuit breakers
• graceful degradation
• recovery

The technology choice matters.
But the more important question is:

👉 What happens when this component becomes slow, unavailable or overloaded?

That question should be part of every senior backend design discussion.

Before finalizing a design, ask one more question: "What is the simplest version that can handle today's scale, and what signal tells me it is time to evolve it?"

Good architecture leaves room to grow without introducing unnecessary complexity on day one."""
        seed = architecture + [topic_name]

    elif content_format == "mistakes":
        body = f"""⚠️ 5 COMMON MISTAKES WHEN LEARNING {topic_name.upper()}

A lot of backend preparation focuses on collecting more concepts.
Sometimes the bigger improvement comes from removing bad habits.

1. {mistakes[0].capitalize()}.

2. {mistakes[1].capitalize()}.

3. {mistakes[2].capitalize()}.

4. {mistakes[3].capitalize()}.

5. {mistakes[4].capitalize()}.

Instead, try this approach:

✅ Learn the concept
✅ Build a tiny example
✅ Break the example intentionally
✅ Observe the logs/metrics
✅ Measure the behavior
✅ Write down the trade-off

For senior interviews, this becomes even more important.

You are not only expected to know how something works.
You may be asked why you chose it, what alternative you rejected and what happens when it fails.

That is where practical engineering thinking becomes visible.

The objective is not to avoid every mistake. It is to recognize the risk early, measure it and build guardrails around it.

A production-ready engineer thinks about the unhappy path before the incident forces the conversation."""
        seed = mistakes

    elif content_format == "senior":
        body = f"""🎯 WHAT CHANGES WHEN YOU PREPARE FOR A SENIOR JAVA BACKEND ROLE?

At junior level, the question is often:
👉 Can you implement this correctly?

At senior level, the discussion often expands to:
👉 Can you make the system reliable when the environment is not perfect?

For {topic_name}, prepare to discuss:

• scalability
• performance
• concurrency
• security
• observability
• failure handling
• operational cost
• maintainability

A useful answer structure is:

1. State the simplest correct approach.
2. Explain the trade-off.
3. Mention the bottleneck.
4. Explain how you would observe it.
5. Explain what you would do when it fails.

For example, instead of saying:
"We use caching for performance."

Go one level deeper:

"What data can be stale?"
"What is the invalidation strategy?"
"What happens during a cache miss storm?"
"What happens if Redis is unavailable?"

The second style demonstrates engineering thinking, not just terminology.

A senior-level discussion also benefits from one concrete example: mention the constraint, the decision you made, the trade-off you accepted and how you verified the result.

That makes the answer specific without turning it into a memorized script."""
        seed = [topic_name, *architecture, *production]

    elif content_format == "checklist":
        body = f"""📋 JAVA BACKEND PREPARATION CHECKLIST — {topic_name}

Before calling a topic 'prepared', check whether you can explain all of these without opening your notes:

☐ Core concept
☐ Internal working
☐ Time / space or runtime implications
☐ Common production use case
☐ Common failure mode
☐ Performance bottleneck
☐ Security consideration
☐ Monitoring / observability
☐ Alternative approach
☐ Trade-off

Then test yourself with this exercise:

🎯 Explain the concept in 30 seconds.

🎯 Explain it again to a teammate who knows Java but not this topic.

🎯 Explain what changes when traffic becomes 10x larger.

🎯 Explain what you would monitor in production.

🎯 Explain what you would do if the dependency fails.

If you can answer those five layers, you are no longer studying only for a definition-based interview.

You are preparing to discuss how software behaves in the real world.

That is the shift from "I know this technology" to "I can own this part of a production system."

Keep the checklist practical: explain, implement, break, measure and improve."""
        seed = focus + production

    elif content_format == "comparison":
        a, b = RNG.sample(focus, 2)
        body = f"""⚖️ BACKEND ENGINEERING: DON'T ASK ONLY 'WHICH IS BETTER?'

A better question is:
👉 Which option fits the problem and constraints?

Today, compare two ideas from {topic_name}:

🔹 OPTION A
{a}

🔹 OPTION B
{b}

Evaluate them across:

• performance
• complexity
• scalability
• failure behavior
• operational cost
• team familiarity
• observability
• future maintenance

There is rarely one universal winner.

For example, a solution that is faster may introduce more operational complexity.
A simpler solution may be perfectly adequate until traffic or data volume changes.

A senior engineer should be able to explain:

"I would choose X because of these constraints. If the constraints change, I would reconsider the decision."

That is much more useful than memorizing a technology comparison table.

The right comparison changes with traffic, consistency requirements, team size, operational maturity and failure tolerance. Context is part of the answer."""
        seed = [a, b, *architecture]

    elif content_format == "question_set":
        selected = questions[:PRIMARY_QUESTION_COUNT]
        followup = RNG.choice([q for t in ALL_TOPICS_CACHE if t["name"] != topic_name for q in t["questions"]]) if ALL_TOPICS_CACHE else selected[0]
        body = f"""🔥 INTERVIEW PRACTICE — {topic_name}

Don't just read the answers.
Pause after each question and explain your reasoning out loud.

{_numbered(selected)}

🎯 FOLLOW-UP
{len(selected) + 1}. {followup}

For every answer, try to cover:
• what it is
• how it works
• when to use it
• trade-offs
• production failure mode

If you can explain the first answer but struggle with the follow-up, that's usually a signal that the concept needs another layer of study.

The goal is not to memorize 500 questions.
The goal is to become comfortable with the next question.

🎯 Senior angle: explain not only the answer, but also the trade-off and what you would monitor in production.

🔥 Bonus practice: take the question that felt easiest and ask yourself what would change if traffic, data volume or failure rate became 10x larger."""
        seed = selected + [followup]

    else:
        body = hook
        seed = [hook]

    return body.strip(), seed


ALL_TOPICS_CACHE: list[dict] = []


def _append_cta(body: str, book_link: str, hashtags: list[str]) -> str:
    # Keep the raw URL on its own line. LinkedIn documents external-link
    # engagement for post links, and a standalone URL is easiest to detect.
    return (
        f"{body.strip()}\n\n{RNG.choice(TAKEAWAYS)}"
        f"\n\n📘 Get the Java Backend Guide here:\n{book_link}"
        f"\n\n{' '.join(hashtags)}"
    ).strip()


def _validate_structure(post: str, *, book_link: str, max_chars: int, content_format: str) -> None:
    if not post.strip():
        raise RuntimeError("Generated post is empty")
    if len(post) > max_chars:
        raise RuntimeError(f"Generated post is {len(post)} characters; max is {max_chars}")
    if post != post.strip():
        raise RuntimeError("Generated post has unexpected leading/trailing whitespace")
    if book_link not in post:
        raise RuntimeError("Guide link is missing")
    if not URL_RE.search(post):
        raise RuntimeError("Generated post does not contain a URL")
    if len(HASHTAG_RE.findall(post)) != 5:
        raise RuntimeError("Expected exactly 5 hashtags")
    if content_format not in CONTENT_FORMATS:
        raise RuntimeError(f"Unknown content format: {content_format}")

    # Numbered lines are validated as question-bank entries only for the
    # question-set format. Other formats may legitimately use numbered lists.
    if content_format == "question_set":
        source = {_normalize(q) for t in ALL_TOPICS_CACHE for q in t["questions"]}
        for line in post.splitlines():
            match = QUESTION_LINE_RE.match(line)
            if match and _normalize(match.group(2)) not in source:
                raise RuntimeError(f"A numbered question was modified/truncated: {match.group(2)!r}")


def generate_post(book_link: str, max_chars: int = DEFAULT_MAX_CHARS, *, record_history: bool = True):
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    global ALL_TOPICS_CACHE
    ALL_TOPICS_CACHE = load_topics()
    topics = ALL_TOPICS_CACHE
    # Test/preview generations must not inherit production rotation state.
    # This keeps record_history=False deterministic and allows the mixed-format
    # test suite to exercise every supported content format.
    history = _load_history() if record_history else []
    used = {item.get("fingerprint") for item in history}

    for _ in range(160):
        main = _choose_topic(topics, used)
        content_format = _choose_format(history)
        questions = RNG.sample(main["questions"], k=min(PRIMARY_QUESTION_COUNT, len(main["questions"])))
        body, seed = _build_body(main["name"], content_format, questions)
        fingerprint = _fingerprint(main["name"], content_format, seed)
        if fingerprint in used:
            continue

        hashtags = RNG.choice(HASHTAG_SETS)
        post = _append_cta(body, book_link, hashtags)
        if len(post) < MIN_TARGET_CHARS and content_format != "question_set":
            # The formats above are intentionally substantial; regenerate if a future
            # content block becomes too short.
            continue
        if len(post) > max_chars:
            continue

        _validate_structure(post, book_link=book_link, max_chars=max_chars, content_format=content_format)

        generated_at = datetime.now(timezone.utc).isoformat()
        if record_history:
            history.append({
                "fingerprint": fingerprint,
                "topic": main["name"],
                "content_format": content_format,
                "questions": questions if content_format == "question_set" else [],
                "generated_at_utc": generated_at,
            })
            _save_history(history)

        metadata = {
            "topic": main["name"],
            "content_format": content_format,
            "question_count": len(questions) if content_format == "question_set" else 0,
            "questions": questions if content_format == "question_set" else [],
            "guide_link": book_link,
            "character_count": len(post),
            "hashtags": HASHTAG_RE.findall(post),
            "fingerprint": fingerprint,
            "generated_at_utc": generated_at,
            "history_size": len(history),
            "question_bank_size": sum(len(t["questions"]) for t in topics),
            "generator": "python-standard-library-content-engine-v4",
        }
        return post, metadata

    raise RuntimeError("Could not build a unique post within the character limit")


def validate_question_bank() -> dict:
    topics = load_topics()
    questions = [q for topic in topics for q in topic["questions"]]
    normalized = [_normalize(q) for q in questions]
    duplicates = sorted({q for q in normalized if normalized.count(q) > 1})
    return {
        "topic_count": len(topics),
        "question_count": len(questions),
        "duplicate_question_count": len(duplicates),
        "duplicates": duplicates,
    }
