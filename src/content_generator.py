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
    "I used to think knowing the technology was the hard part. It isn't.",
    "Here is a backend decision that looks small until production gets involved.",
    "The easiest answer is not always the best engineering answer.",
    "One question can expose whether someone understands a backend system deeply.",
    "This is one of those backend topics that makes more sense after you see the failure mode.",
    "If I had to explain this to a senior interviewer in one minute, I would start here.",
    "A lot of backend advice sounds right until you add real traffic, failures and operational constraints.",
    "The interesting part of backend engineering is usually what happens after the happy path.",
    "There is a big difference between knowing a tool and knowing when not to use it.",
    "This is the kind of trade-off I would want an engineer to explain, not just define.",
]

TAKEAWAYS = [
    "The useful part is not memorizing the rule. It is knowing when the rule stops being true.",
    "Good backend decisions make the trade-off explicit: performance, reliability, consistency, complexity or cost.",
    "If you can explain the happy path and the failure path, you understand the design much better.",
    "Senior-level answers become stronger when they connect implementation details to production consequences.",
    "A practical way to learn: build it, break it, observe it, then explain why it behaved that way.",
]

CTA_LINES = [
    "📘 I keep my Java Backend preparation material here:",
    "📘 If you're preparing for a Java Backend role, this guide may help:",
    "📘 I put the complete Java Backend preparation path here:",
    "📘 For Java + Spring Boot + Microservices interview preparation:",
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
    "story",
    "opinion",
    "production",
    "concept",
    "architecture",
    "comparison",
    "mistakes",
    "senior",
    "roadmap",
    "checklist",
    "myth_vs_reality",
    "interview_story",
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
    """Load guide links and rotate through them sequentially.

    The links are intentionally kept in config/book_links.txt so the user can
    change destinations without changing Python code. The most recently used
    configured link is found in history and the next configured link is chosen.
    Rotation wraps around, so any number of configured links is supported.
    """
    path = CONFIG / "book_links.txt"
    if not path.exists():
        raise RuntimeError(f"Missing book link file: {path}")

    links = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#"):
            if not URL_RE.fullmatch(value):
                raise RuntimeError(f"Invalid guide URL: {value}")
            links.append(value)

    if not links:
        raise RuntimeError(
            "config/book_links.txt must contain at least one guide URL."
        )

    # Remove duplicates while preserving the order configured by the user.
    links = list(dict.fromkeys(links))

    if not links:
        raise RuntimeError(
            "No unique guide URLs were found in config/book_links.txt."
        )

    history = _load_history()

    # Find the most recently used link that still exists in the current
    # configuration. This also handles links being added/removed over time.
    previous = None
    for item in reversed(history):
        candidate = str(item.get("guide_link", "")).strip()
        if candidate in links:
            previous = candidate
            break

    # First run, or no previous configured link found.
    if previous is None:
        return links[0]

    # Sequential rotation:
    # [A, B, C] -> A -> B -> C -> A -> ...
    current_index = links.index(previous)
    next_index = (current_index + 1) % len(links)
    return links[next_index]



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
    hook_pool = TOPIC_HOOKS.get(topic_name, []) + GLOBAL_HOOKS
    hook = RNG.choice(hook_pool)

    focus = RNG.sample(profile["focus"], k=min(5, len(profile["focus"])))
    mistakes = RNG.sample(profile["mistakes"], k=min(5, len(profile["mistakes"])))
    production = RNG.sample(profile["production"], k=min(4, len(profile["production"])))
    architecture = RNG.sample(profile["architecture"], k=min(5, len(profile["architecture"])))

    if content_format == "story":
        problem = RNG.choice(production)
        decision = RNG.choice(architecture)
        body = f"""I learned something about {topic_name} the hard way.

The system looked fine in the happy path.

Then we hit a situation where:
→ {problem}

The first instinct is usually to fix the visible symptom.

But the better question is:

"What changed in the system's behavior?"

For this kind of problem, I would work through it in this order:

1. Establish what changed — deployment, traffic, data volume or dependency behavior.
2. Find the first signal that moved — latency, errors, queue depth, CPU, memory or throughput.
3. Separate the symptom from the bottleneck.
4. Apply the smallest safe mitigation.
5. Only then decide whether the architecture needs to change.

One design principle I would keep in mind here:

→ {decision}

That sounds obvious.

It becomes much harder when the system is already under pressure and every change has a blast radius.

The real engineering lesson is not "always do X."

It is knowing what evidence would make you choose X, Y or nothing at all.

That is the kind of reasoning I try to bring into senior backend discussions."""
        seed = [problem, decision, *production, *architecture]

    elif content_format == "opinion":
        statement = RNG.choice([
            f"You probably don't need a more complicated {topic_name} design.",
            f"Knowing {topic_name} is not the same as knowing when to use it.",
            f"The biggest {topic_name} mistake is usually not a syntax mistake.",
            f"If the only argument for a {topic_name} decision is 'it scales', I would ask more questions.",
        ])
        body = f"""{statement}

My default approach is to start with the simplest design that satisfies the current constraints.

Then ask:

• What is the expected scale?
• What is the failure mode?
• What needs independent scaling?
• What consistency is actually required?
• What will the team have to operate at 2 AM?

For {topic_name}, I would pay particular attention to:

→ {focus[0]}
→ {focus[1]}
→ {production[0]}
→ {architecture[0]}

The important part is the trade-off.

A solution can be technically impressive and still be the wrong solution if it adds operational complexity without solving a real constraint.

I would rather see a simple design with clear boundaries, metrics and a documented reason for each decision than a complex design assembled from every popular technology.

Good engineering is often less about adding capabilities and more about refusing unnecessary complexity.

That's also how I would answer a senior-level interview question:

"I chose this because of the constraint. If the constraint changes, I would revisit the decision."

That answer shows judgment, not just knowledge."""
        seed = [statement, *focus, *architecture]

    elif content_format == "production":
        scenario = RNG.choice(production)
        body = f"""Your backend is slow.

The database looks healthy.
CPU looks normal.
The service is technically "up."

But users are still waiting.

One possible signal is:

→ {scenario}

This is where production debugging becomes different from interview theory.

I would not start by changing configuration.

I would start by narrowing the search space.

CHECK 1 — What changed?
• deployment
• traffic
• data volume
• dependency behavior
• configuration

CHECK 2 — Where did latency start?
Look at request traces and downstream timings.

CHECK 3 — Is the resource saturated?
• threads
• connection pools
• queues
• CPU
• memory

CHECK 4 — Is a dependency amplifying the problem?
Retries and timeouts can turn a small slowdown into a large incident.

CHECK 5 — Can we mitigate without hiding the root cause?

The biggest mistake is changing several variables at once.

If you do that, you may recover the system without learning what actually broke it.

A production engineer should be able to say:

"Here is the evidence, here is my current hypothesis, and here is the next measurement I need."

That is much stronger than guessing quickly."""
        seed = [scenario, *production, *architecture]

    elif content_format == "concept":
        concept = RNG.choice(focus)
        body = f"""Let's make {concept} practical.

Instead of starting with the definition, imagine you are reviewing a production system that uses it.

The first questions I would ask are:

Why does it exist?
What problem does it solve?
What does it cost?
When does that cost become visible?
What happens when the surrounding system is under pressure?

For {topic_name}, the useful learning loop is:

Understand
→ implement a tiny example
→ inspect what happens
→ break the happy path
→ measure it
→ explain the trade-off

For example, one implementation decision may look harmless during local testing but become expensive when:

• data volume grows
• concurrency increases
• a dependency becomes slow
• retries start stacking up
• memory pressure changes the runtime behavior

That is why I prefer learning concepts through behavior rather than definitions.

If I cannot explain both the normal path and the failure path, I don't consider the topic finished.

And that is exactly where senior interviews often move: away from "what is it?" and toward "what happens when it goes wrong?"."""
        seed = [concept, *focus, *production]

    elif content_format == "architecture":
        body = f"""A backend architecture should answer one uncomfortable question:

What happens when one part of the system becomes slow, unavailable or overloaded?

For a {topic_name} system, I would reason through these boundaries:

1. REQUEST
Validation, authentication, idempotency and rate limits.

2. BUSINESS LOGIC
Clear ownership, transaction boundaries and predictable failure behavior.

3. DATA
Access patterns, indexes, caching, consistency and connection limits.

4. ASYNC WORK
Queues, Kafka, retries, DLQ and replay strategy.

5. OBSERVABILITY
Metrics, logs, traces and alerts that tell us where the problem started.

6. RECOVERY
Timeouts, circuit breakers, graceful degradation and recovery paths.

The technology list is the easy part.

The harder part is explaining why each boundary exists.

For example:

→ {architecture[0]}
→ {architecture[1]}
→ {architecture[2]}

If a design cannot explain its failure behavior, it is not finished.

I also prefer an evolutionary design.

Start with the simplest architecture that satisfies today's constraints.

Then define the signal that would justify the next level of complexity.

That keeps architecture driven by evidence instead of fashion."""
        seed = architecture + [topic_name]

    elif content_format == "comparison":
        a, b = RNG.sample(focus, 2)
        body = f"""Two backend approaches can both be correct.

The interesting question is not:

"Which one is better?"

It is:

"Which one fits the constraints?"

For {topic_name}, compare:

OPTION A
→ {a}

OPTION B
→ {b}

I would evaluate them against:

• latency
• throughput
• consistency
• failure behavior
• operational complexity
• team expertise
• observability
• cost

A faster solution can be worse if it is difficult to operate.

A simpler solution can be better until a specific scale or reliability requirement changes.

For me, a strong engineering answer sounds like:

"I would choose A because of these constraints. If the constraints change, I would move toward B."

That is more useful than memorizing a comparison table.

Technology decisions are conditional.

The context is part of the answer.

One more test I like to use: imagine the traffic, consistency requirement or team size changes tomorrow. If the decision would still be correct, you probably chose a robust boundary. If not, be explicit about the trigger that would make you switch.

That makes a comparison useful in design reviews, not just interview preparation."""
        seed = [a, b, *architecture]

    elif content_format == "mistakes":
        body = f"""One of the easiest ways to improve your {topic_name} skills is to study the mistakes engineers repeatedly make.

Here are five I would watch for:

1. {mistakes[0]}.
2. {mistakes[1]}.
3. {mistakes[2]}.
4. {mistakes[3]}.
5. {mistakes[4]}.

But spotting the mistake is only half the skill.

For each one, ask:

→ What signal would expose it?
→ What is the safest mitigation?
→ What is the long-term fix?
→ What trade-off does the fix introduce?

For example, a system may appear healthy until {production[0]}.

That is why I like this learning loop:

learn → implement → break → observe → measure → explain.

It produces a much stronger engineering instinct than collecting definitions.

The goal is not to design a perfect system.

The goal is to recognize risky decisions early enough to do something about them."""
        seed = mistakes + production

    elif content_format == "senior":
        body = f"""There is a difference between answering a backend question and answering it like an engineer who owns the system.

For {topic_name}, I would prepare at three levels.

LEVEL 1 — Correctness
Can I explain how it works?

LEVEL 2 — Trade-offs
Can I explain why I would choose it over an alternative?

LEVEL 3 — Production
Can I explain what happens when load increases, dependencies fail or data grows?

That third level is where many senior discussions become interesting.

For example:

Instead of:
"Use caching for performance."

Ask:
• What can become stale?
• How is invalidation handled?
• What happens during a cache miss storm?
• What happens if the cache disappears?

Instead of:
"Use retries."

Ask:
• Which failures are retryable?
• How many times?
• With what backoff?
• Can retries create a retry storm?
• Is the operation idempotent?

That is the mindset I would bring to a senior interview.

Don't just explain the happy path.

Explain the decision, the evidence, the failure mode and the operational consequence."""
        seed = [topic_name, *architecture, *production]

    elif content_format == "roadmap":
        body = f"""If I had to prepare for a Java Backend role again, I would not start by collecting hundreds of interview questions.

I would build depth in layers.

1. FUNDAMENTALS
→ {focus[0]}
→ {focus[1]}
→ {focus[2]}

2. BACKEND ENGINEERING
→ {architecture[0]}
→ {architecture[1]}
→ {architecture[2]}

3. PRODUCTION THINKING
→ {production[0]}
→ {production[1]}
→ {production[2]}

4. INTERVIEW THINKING
For every important concept, prepare:
→ what it is
→ why it exists
→ trade-offs
→ failure mode
→ one production example

The biggest mistake is treating Java, Spring Boot, Kafka, SQL and System Design as separate islands.

They connect.

A slow database can create thread contention.
Thread contention can increase request latency.
Latency can trigger retries.
Retries can amplify load on the same dependency.

That chain is what you should learn to reason about.

The goal is not to know every tool.

The goal is to know how the pieces behave together."""
        seed = focus + architecture + production

    elif content_format == "checklist":
        body = f"""Before I call a {topic_name} topic "prepared", I want to be able to answer more than its definition.

I should be able to explain:

□ the core idea
□ how it works internally
□ the performance implications
□ the common production use case
□ the failure mode
□ the security implications
□ what I would monitor
□ what alternative I considered
□ what trade-off I accepted

Then I would do one final exercise:

Explain it in 30 seconds.

Explain it to another Java developer.

Explain what changes when traffic becomes 10x larger.

Explain what you would monitor in production.

Explain what you would do if a dependency fails.

If those answers are clear, you are preparing for engineering discussions rather than only definition-based interviews.

The last step is the most useful:

Take one thing you learned and intentionally break it.

That's where the real understanding usually starts.

For an interview, this also gives you a concrete story: what you expected, what actually happened, what you measured and what you changed. Specific reasoning is much easier to defend than a memorized definition."""
        seed = focus + production

    elif content_format == "myth_vs_reality":
        myth = RNG.choice([
            "More technology automatically means a more scalable system.",
            "More threads automatically mean more throughput.",
            "A cache automatically makes an application faster.",
            "Retries automatically make a distributed system more reliable.",
            "Microservices automatically make a system easier to scale.",
        ])
        reality = RNG.choice([
            production[0],
            production[1],
            architecture[0],
        ])
        body = f"""MYTH vs REALITY — {topic_name}

MYTH:
"{myth}"

REALITY:
The result depends on the bottleneck and the constraints.

For example, in a real backend system you may actually run into:

→ {reality}

Adding more components without removing the bottleneck can make the system harder to operate without making it faster.

A better way to reason about {topic_name} is:

1. Identify the constraint.
2. Measure the current behavior.
3. Change one variable.
4. Measure again.
5. Check the new failure mode.

This matters because optimizations move complexity.

A cache can introduce invalidation problems.
Retries can create load amplification.
Async processing can introduce ordering and observability challenges.
More services can introduce network failure.

The mature engineering question is not "Does this technology work?"

It is:

"Under which constraints does this decision make sense?"

That is the difference between using a tool and engineering a system."""
        seed = [myth, reality, *architecture]

    elif content_format == "interview_story":
        question = RNG.choice(questions)
        follow = RNG.choice([q for t in ALL_TOPICS_CACHE for q in t["questions"] if q != question]) if ALL_TOPICS_CACHE else question
        body = f"""An interview question can look easy until the follow-up arrives.

The question:

"{question}"

A shallow answer can stop after the definition.

A stronger answer continues:

→ How does it work?
→ Why would you choose it?
→ What is the trade-off?
→ What happens under high load?
→ What happens when a dependency fails?

And then comes the follow-up:

"{follow}"

That is where preparation becomes useful.

I don't think senior interview preparation should be about memorizing 500 perfect answers.

It should train you to stay calm when the interviewer changes one constraint.

Traffic becomes 10x larger.

A dependency becomes slow.

Data becomes much bigger.

The requirement changes from eventual consistency to stronger consistency.

Your answer should evolve with the constraint.

That's the skill worth practicing.

A useful exercise is to answer the original question, then deliberately introduce one failure or scale constraint and answer it again. If your design changes for a good reason, you are practicing the kind of adaptive thinking that senior interviews are trying to measure."""
        seed = [question, follow]

    elif content_format == "question_set":
        selected = questions[:PRIMARY_QUESTION_COUNT]
        followup = RNG.choice([q for t in ALL_TOPICS_CACHE if t["name"] != topic_name for q in t["questions"]]) if ALL_TOPICS_CACHE else selected[0]
        body = f"""A good interview question is not valuable because it has a memorized answer.

It is valuable because it creates a useful follow-up discussion.

Try these today:

{_numbered(selected)}

FOLLOW-UP
{len(selected) + 1}. {followup}

For each answer, cover:
• what it is
• how it works
• why you would use it
• trade-offs
• failure mode
• what you would monitor

Then change one constraint.

What if traffic becomes 10x larger?
What if the dependency becomes slow?
What if the operation is retried?
What if the data becomes 100x larger?

The goal is not to finish another list of questions.

The goal is to become comfortable reasoning when the interviewer changes the problem.

A strong answer should also make your assumptions visible. Say what you are optimizing for, what constraint matters most and what you would monitor after the system goes live."""
        seed = selected + [followup]

    else:
        body = hook
        seed = [hook]

    return body.strip(), seed


ALL_TOPICS_CACHE: list[dict] = []


def _append_cta(body: str, book_link: str, hashtags: list[str]) -> str:
    return (
        f"{body.strip()}\n\n"
        f"{RNG.choice(TAKEAWAYS)}\n\n"
        f"{RNG.choice(CTA_LINES)}\n"
        f"{book_link}\n\n"
        f"{' '.join(hashtags)}"
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
                "guide_link": book_link,
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
            "generator": "python-standard-library-content-engine-v5",
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
