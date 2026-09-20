# Java LinkedIn Daily Post Automation — 100% Free Python Version

This project generates an original Java/Spring Boot interview-style LinkedIn post every morning and publishes it to your personal LinkedIn profile using LinkedIn's official API.

## What is free?

- Python: free
- GitHub Actions: uses GitHub Actions; public repositories generally have included Actions minutes, while private repositories are subject to GitHub's current Actions quota/billing rules.
- LinkedIn Share on LinkedIn API: no paid API subscription is required for the self-service `w_member_social` permission.
- No OpenAI/Gemini/Claude API is used.
- No paid content-generation API is used.
- No Python third-party packages are required.

## Important LinkedIn requirement

Automatic publishing uses LinkedIn OAuth and the official Posts API. Your LinkedIn developer app must have the **Share on LinkedIn** product / `w_member_social` permission. LinkedIn documents `w_member_social` as the permission for posting on behalf of an authenticated member.

LinkedIn access tokens currently have a 60-day lifespan by default. Programmatic refresh tokens are available to approved Marketing Developer Platform partners; therefore, for a normal self-service app, plan to re-authorize and replace the GitHub secret when the access token expires.

## Repository structure

```text
.
├── .github/workflows/daily-linkedin-post.yml
├── config/
│   ├── book_links.txt
│   └── topics.json
├── output/
├── src/
│   ├── content_generator.py
│   ├── generate_post.py
│   ├── linkedin_client.py
│   ├── linkedin_oauth.py
│   ├── post_to_linkedin.py
│   └── test_post.py
├── requirements.txt
└── README.md
```

## 1. Create the LinkedIn developer app

Create an application in the LinkedIn Developer Portal.

Under **Products**, enable:

- Share on LinkedIn
- Sign In with LinkedIn using OpenID Connect (recommended because this project can resolve your member identifier automatically)

Under **Auth**, add this redirect URL:

```text
http://localhost:8765/callback
```

The app must have the scopes used by the OAuth script: `openid profile w_member_social`.

## 2. Generate the LinkedIn access token

On your own computer:

```bash
python src/linkedin_oauth.py
```

Set your credentials first.

Windows PowerShell:

```powershell
$env:LINKEDIN_CLIENT_ID="YOUR_CLIENT_ID"
$env:LINKEDIN_CLIENT_SECRET="YOUR_CLIENT_SECRET"
python src/linkedin_oauth.py
```

The browser will open. Authorize the app. The script prints an access token.

Do NOT commit your client secret or access token to GitHub.

## 3. Add GitHub Secrets

Repository → Settings → Secrets and variables → Actions → Secrets → New repository secret

Add:

```text
LINKEDIN_ACCESS_TOKEN = <token from OAuth>
```

Optional:

```text
LINKEDIN_PERSON_URN = urn:li:person:<your-member-id>
```

If `LINKEDIN_PERSON_URN` is omitted, the script tries `https://api.linkedin.com/v2/userinfo` and builds the Person URN from the returned `sub` value.

## 4. Add GitHub Variables

Repository → Settings → Secrets and variables → Actions → Variables

Required:

```text
AUTO_POST_ENABLED=true
```

Optional:

```text
POST_MAX_CHARS=2850
LINKEDIN_VERSION=202604
```

### Turn automation OFF

```text
AUTO_POST_ENABLED=false
```

### Turn automation ON

```text
AUTO_POST_ENABLED=true
```

## 5. Guide links

Edit:

```text
config/book_links.txt
```

Put one URL per line:

```text
https://your-guide-link-1.example
https://your-guide-link-2.example
https://your-guide-link-3.example
```

The generator randomly chooses one link on each run.

## 6. Daily schedule

Default schedule:

```text
08:10 AM Asia/Kolkata every day
```

Change the cron/timezone in `.github/workflows/daily-linkedin-post.yml` if required.

## 7. Manual test

Generate locally:

```bash
python src/generate_post.py
```

Publish locally only after setting the access token:

```bash
# Windows PowerShell
$env:LINKEDIN_ACCESS_TOKEN="YOUR_TOKEN"
$env:AUTO_POST_ENABLED="true"
python src/post_to_linkedin.py
```

For a minimal API smoke test:

```bash
python src/test_post.py
```

## What gets generated?

The generator uses a large local question bank and multiple layouts. It randomly mixes:

- Core Java
- Java 8 / Streams
- Multithreading / Concurrency
- Spring Boot
- Spring Security
- Microservices
- Kafka
- SQL / Hibernate
- System Design
- Production scenarios
- Coding
- Project discussion

Each post contains:

- an interview-style hook
- 5 main questions
- a follow-up scenario
- a practical takeaway
- one randomly selected guide link
- exactly 5 hashtags
- a configurable character limit

Company names from the source examples are intentionally not hard-coded into generated posts.

## Publishing behavior

The workflow does:

```text
GitHub Actions
   ↓
AUTO_POST_ENABLED check
   ↓
Generate local post
   ↓
Select random guide link
   ↓
Validate character count / CTA / hashtags
   ↓
POST /rest/posts to LinkedIn
   ↓
Save post + metadata in output/
   ↓
Commit generated output to GitHub
```

If LinkedIn rejects the request, the workflow fails instead of silently claiming that the post was published.

## Token expiry

LinkedIn currently states that access tokens are issued with a 60-day lifespan by default. A normal self-service setup should therefore be expected to require periodic reauthorization. Approved Marketing Developer Platform partners can use programmatic refresh tokens; this project does not pretend that refresh is universally available.

## Security

Never put these into source code:

- LinkedIn client secret
- LinkedIn access token
- GitHub PAT

Use GitHub Secrets for credentials.
