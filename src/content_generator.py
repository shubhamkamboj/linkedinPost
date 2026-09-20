from __future__ import annotations
import hashlib, json, os, random, re
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CONFIG=ROOT/'config'; OUTPUT=ROOT/'output'
RNG=random.SystemRandom(); QUESTION_COUNT=5; MAX_HISTORY=1200
GLOBAL_HOOKS=[
'🔥 Java Backend interviews are rarely about definitions alone.',
'⚡ If you are preparing for a Java Backend interview, practice questions like these.',
'🎯 Senior Java interviews often move from a simple concept to a production scenario.',
'💡 Knowing the syntax is only the beginning. The follow-up is where interviews get interesting.',
'🚨 One Java interview question can quickly turn into a discussion about performance, concurrency and design.',
'🔥 Preparing for a Java Backend interview? These are the kinds of questions worth practicing out loud.',
]
TOPIC_HOOKS={
'Core Java':['🔥 Core Java questions that expose whether you understand what happens under the hood:','🧠 Core Java looks simple until the interviewer asks the next "why".'],
'Java 8+ / Streams / Functional Programming':['⚡ Java Streams are easy to write. Explaining their behavior is the real interview test:','🧠 Revising Java 8+? These questions go beyond basic map/filter examples:'],
'Multithreading & Concurrency':['🔥 Concurrency questions often separate syntax knowledge from real backend experience.','⚠️ If an interviewer asks about threads, be ready for race conditions, locks and production failures.'],
'Spring Boot':['🚀 Spring Boot interviews often start with annotations and end with proxies, transactions and production behavior.','🧠 Do not stop at "what does this annotation do?" Spring Boot follow-ups usually go deeper.'],
'Microservices':['🌐 Microservices interviews are really about failure, communication and trade-offs.','🔥 A microservice can work perfectly in isolation and still fail as part of a distributed system.'],
'Kafka':['🔥 Kafka interviews become interesting when the interviewer asks what happens after a failure.','📨 If you work with Kafka, be ready to explain ordering, offsets, retries and duplicate processing.'],
'SQL & Hibernate / JPA':['🗄️ SQL and Hibernate interviews often reveal how well you understand performance and data consistency.','🔥 JPA can make database access easy—until production data volume exposes the hidden costs.'],
'System Design':['🏗️ System design interviews are less about drawing boxes and more about explaining trade-offs.','🔥 Practice scenarios where components can fail independently.'],
'Production Scenarios / Troubleshooting':['🚨 Production debugging questions are where theoretical Java knowledge meets real engineering.','🔥 Imagine this happens in production. What would you check first?'],
'Coding & DSA':['💻 Coding interviews become easier when you practice the pattern behind the problem.','🔥 Classic coding problems are still worth solving without looking at the solution.'],
'Project Discussion / Senior-Level':['🎯 Your project discussion can decide how deep the interviewer goes into architecture.','🔥 Senior interviews often move from "what did you build?" to "why did you build it this way?"'],
'Spring Security / APIs / Distributed Systems':['🔐 Backend security interviews are rarely limited to JWT definitions.','🔥 API design questions quickly become security, reliability and distributed-systems questions.'],
'Redis / Caching / Performance':['⚡ Caching can make a backend faster—or create a completely different production problem.','🔥 Redis interviews are about more than GET and SET. Be ready for consistency, eviction and failure.']}
TAKEAWAYS=[
'📌 Do not memorize the answer. Explain the concept, the trade-off, the failure mode and a real production use case.',
'📌 For senior roles, connect every answer to scalability, reliability, observability and the decision you would make.',
'📌 A strong interview answer usually covers: what it is, why it exists, when to use it and what can go wrong.',
'📌 Practice answering these without looking at notes. Then challenge yourself with the next "why?" question.',
'📌 The interviewer may start with one question and keep drilling deeper. Practice the follow-up, not just the first answer.',
]
HASHTAGS=[['#Java','#SpringBoot','#Microservices','#BackendDevelopment','#InterviewPreparation'],['#JavaDeveloper','#CoreJava','#SpringBoot','#SoftwareEngineering','#TechCareers'],['#Java','#JavaProgramming','#BackendDeveloper','#SystemDesign','#CodingInterview'],['#JavaBackend','#SpringBoot','#Microservices','#SystemDesign','#InterviewTips'],['#JavaDeveloper','#Kafka','#Microservices','#BackendEngineering','#JavaInterview']]
TEMPLATES=[
'{hook}\n\n🧠 {topic}\n\n{questions}\n\n🎯 FOLLOW-UP SCENARIO\n{n}. {followup}\n\n{takeaway}',
'{hook}\n\n🔥 5 QUESTIONS WORTH PREPARING\n\n{questions}\n\n💬 One more question:\n{n}. {followup}\n\n{takeaway}',
'{hook}\n\nWhat I would practice before the interview:\n\n{questions}\n\n🚨 EXPECT A FOLLOW-UP ON THIS\n{n}. {followup}\n\n{takeaway}',
'{hook}\n\n📝 INTERVIEW CHECKLIST\n\n{questions}\n\n🔥 Then prepare for this:\n{n}. {followup}\n\n{takeaway}',
'{hook}\n\nNo answers. No hints. Just questions to practice:\n\n{questions}\n\n💬 THE FOLLOW-UP\n{n}. {followup}\n\n{takeaway}',
'{hook}\n\nIf you can answer these clearly in under 60 seconds each, you are building a strong revision set:\n\n{questions}\n\n🎯 FOLLOW-UP\n{n}. {followup}\n\n{takeaway}',
]
def load_topics(): return json.loads((CONFIG/'topics.json').read_text(encoding='utf-8'))['topics']
def choose_book_link():
    links=[]
    for line in (CONFIG/'book_links.txt').read_text(encoding='utf-8').splitlines():
        v=line.strip()
        if v and not v.startswith('#') and re.match(r'^https?://',v,re.I): links.append(v)
    if not links: raise RuntimeError('config/book_links.txt must contain at least one URL')
    return RNG.choice(links)
def norm(s): return re.sub(r'\s+',' ',s.lower()).strip()
def fp(topic,qs,follow): return hashlib.sha256(norm('||'.join([topic,*qs,follow])).encode()).hexdigest()[:20]
def load_history():
    p=OUTPUT/'history.json'
    try: return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []
    except Exception: return []
def save_history(h):
    OUTPUT.mkdir(parents=True,exist_ok=True); (OUTPUT/'history.json').write_text(json.dumps(h[-MAX_HISTORY:],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def generate_post(book_link,max_chars=2850):
    topics=load_topics(); history=load_history(); used={x.get('fingerprint') for x in history}
    for _ in range(100):
        main=RNG.choice(topics); qs=RNG.sample(main['questions'],k=min(QUESTION_COUNT,len(main['questions'])))
        other=RNG.choice([t for t in topics if t['name']!=main['name']]); follow=RNG.choice(other['questions']); fingerprint=fp(main['name'],qs,follow)
        if fingerprint not in used: break
    hook=RNG.choice(TOPIC_HOOKS.get(main['name'],[])+GLOBAL_HOOKS); takeaway=RNG.choice(TAKEAWAYS); tags=RNG.choice(HASHTAGS); template=RNG.choice(TEMPLATES)
    qtext='\n'.join(f'{i}. {q}' for i,q in enumerate(qs,1))
    post=template.format(hook=hook,topic=main['name'].upper(),questions=qtext,n=len(qs)+1,followup=follow,takeaway=takeaway).strip()
    post += f'\n\n📘 You can get the complete guide from here: {book_link}\n\n{" ".join(tags)}'
    if len(post)>max_chars:
        # Keep questions + CTA + hashtags; remove prose lines first.
        lines=post.splitlines()
        while len('\n'.join(lines))>max_chars:
            idx=next((i for i,l in enumerate(lines) if l.strip() and not re.match(r'^\d+\. ',l) and not l.startswith('#') and 'complete guide from here' not in l),None)
            if idx is None: break
            lines.pop(idx)
        post='\n'.join(lines).strip()
    if len(post)>max_chars: raise RuntimeError(f'Post is {len(post)} chars; limit is {max_chars}')
    if book_link not in post: raise RuntimeError('Guide link missing from generated post')
    if len(tags)!=5: raise RuntimeError('Post must contain exactly five hashtags')
    now=datetime.now(timezone.utc).isoformat(); history.append({'fingerprint':fingerprint,'topic':main['name'],'questions':qs,'followup':follow,'generated_at_utc':now}); save_history(history)
    return post,{'topic':main['name'],'question_count':len(qs),'guide_link':book_link,'character_count':len(post),'hashtags':tags,'fingerprint':fingerprint,'generated_at_utc':now,'history_size':len(history),'question_bank_size':sum(len(t['questions']) for t in topics),'generator':'python-standard-library-template-engine-v2'}
