---
name: linkedin-posts
description: >-
  Fetch LinkedIn posts and comments for any person or configured list of people.
  Uses the Voyager API via browser cookies (no stored credentials, no API costs).
  Use when you want to check what someone is posting on LinkedIn, research a
  person's recent activity, or run batch monitoring for newsletter curation,
  competitive intelligence, or partner briefings.
user_invocable: true
---

# LinkedIn Posts

Fetch recent LinkedIn posts and comments-on-others for anyone on LinkedIn. Two modes:

* **Quick lookup** — single person, one-off fetch
* **Batch fetch** — configured list of people, dated JSON output, suitable for weekly cron jobs

## How it works

This skill calls LinkedIn's internal **Voyager API** — the same endpoint that powers linkedin.com itself — via the `linkedin-api` Python library. It authenticates by reading your Chrome browser cookies (`li_at` + `JSESSIONID`) through `browser_cookie3`. There are no passwords, OAuth flows, or API keys involved.

**Prerequisite:** You must be logged into LinkedIn in Chrome on the same machine. See `SETUP.md`.

**Legal / ToS note:** LinkedIn's Terms of Service prohibit automated scraping. This skill reads posts that are already visible to you as a logged-in user. Use it for personal research, newsletter curation, or briefings — not at scale, not for republication, and not for building third-party products. Rate-limit yourself.

## Shared library

All reusable primitives live in `linkedin_posts_lib.py` next to this file. It is the single source of truth for:

| Concern | Function(s) |
|---|---|
| Cookie extraction + auth | `get_linkedin_cookies`, `create_api`, `csrf_from_cookies` |
| Post extraction | `extract_post_data` (with silent-reshare detection) |
| Relative date parsing | `compute_approx_post_date` |
| Comments-on-others | `resolve_profile_urn`, `fetch_person_comments` |
| SQLite schema migration | `ensure_comments_migration` |

Any downstream pipeline you build (weekly digest, newsletter ingestion, partner tracker) should `import` from this library rather than copy-paste. When LinkedIn rotates its GraphQL `queryId` hashes, you update `PROFILES_QUERY_ID` and `COMMENTS_QUERY_ID` in one place.

## Quick lookup (single person)

When you want a one-off "what is X posting about?":

```python
from linkedin_posts_lib import get_linkedin_cookies, create_api, extract_post_data

api = create_api(get_linkedin_cookies())
raw = api.get_profile_updates(public_id='darrenperry', max_results=20)
posts = [extract_post_data(p) for p in raw]

for p in posts:
    marker = '[RESHARE]' if p['is_reshare'] else '[ORIGINAL]'
    print(f"{marker} {p['date_text']:<8} {p['likes']:>4} likes  {p['permalink']}")
    print(f"  {p['text'][:200]}")
```

The `public_id` is the URL slug: `linkedin.com/in/darrenperry` → `darrenperry`.

## Batch fetch (configured list)

For ongoing monitoring of multiple people, use `fetch_posts.py` with a `partners.json`:

```bash
python3 fetch_posts.py \
    --config partners.json \
    --output ./posts/ \
    --max-posts 50
```

### partners.json format

```json
{
  "partners": [
    {
      "name": "Darren Perry",
      "public_id": "darrenperry",
      "role": "Partner, Digital Practice",
      "location": "London"
    }
  ]
}
```

See `partners.example.json` for a working example.

### Options

| Flag | Description |
|---|---|
| `--max-posts N` | Max posts per person (default: 50) |
| `--person PUBLIC_ID` | Fetch only one person (for testing) |
| `--delay N` | Seconds between requests (default: 5) |
| `--no-comments` | Skip the GraphQL comments-on-others fetch |

### Output

Writes `posts/YYYY-MM-DD.json` with this shape:

```json
{
  "fetch_date": "2026-04-11",
  "partners": {
    "darrenperry": {
      "name": "Darren Perry",
      "role": "Partner, Digital Practice",
      "location": "London",
      "post_count": 12,
      "comment_count": 8,
      "posts": [ /* ... */ ],
      "comments": [ /* ... */ ]
    }
  }
}
```

## Post data shape

Each post from `extract_post_data` contains:

| Field | Description |
|---|---|
| `activity_id` | LinkedIn's internal post ID |
| `permalink` | Direct URL to the post |
| `text` | Full post content |
| `date_text` | LinkedIn's relative date ("4d", "1w", "2mo") |
| `likes` / `comments` / `shares` | Engagement counts |
| `is_reshare` | True if amplified content (including silent reshares) |
| `reshared_text` / `reshared_author` | If reshare, the original post and who wrote it |
| `author_name` / `author_headline` | The person posting |

**Silent reshare detection** is the non-obvious bit. LinkedIn's API doesn't flag "Repost without commentary" in the `resharedUpdate` field. But the `saveAction.entityUrn` in the post metadata contains the *original* activity ID — if it differs from the post's own URN, we're looking at an amplification rather than an original post. `extract_post_data` handles this automatically.

## Comments on others' posts

`fetch_posts.py` also pulls the comments a person has left on *other* people's posts. This is a separate capability from the main posts fetch and uses LinkedIn's GraphQL endpoint rather than the REST Voyager endpoint that serves `get_profile_updates`.

**Why this matters for newsletter curation and intelligence work:** someone's comments on other people's posts are often a better signal of what they actually engage with than their own posts, which tend to be more polished. Commenting patterns reveal interests, relationships, and priorities.

**How it works.** Two GraphQL calls per person:

1. `voyagerIdentityDashProfiles` — resolves a `public_id` URL slug to an `fsd_profile` URN
2. `voyagerFeedDashProfileUpdates` — fetches the comments collection using that URN

The response contains a denormalised `included` array; the library filters for `social.Comment` entities where `commenter.commenterProfileId` equals the target URN (excluding threaded replies from other people on the same posts).

### Comment data shape

| Field | Description |
|---|---|
| `id` | The comment's `entityUrn` |
| `text` | Full comment content |
| `permalink` | Direct link to the comment on its parent post |
| `created_at_ms` | Epoch milliseconds |
| `parent_activity_urn` | The parent post's activity URN |
| `is_comment_on_other` | Always `True` for these entries |

## When LinkedIn rotates GraphQL query IDs

LinkedIn periodically rotates the hash-suffixed `queryId` values on their GraphQL endpoint. When this happens, the comments fetch starts returning HTTP 400. To re-capture:

1. Launch Chrome with remote debugging (any method — the `comments-probe.passe` script assumes [passe](https://github.com/spm1001/passe) on port 9223)
2. Run `PASSE_CDP=http://localhost:9223 passe run comments-probe.passe`
3. Extract the new query IDs from `/tmp/comments-capture.jsonl`:

```bash
python3 -c "
import json
for line in open('/tmp/comments-capture.jsonl'):
    r = json.loads(line)
    u = r.get('url', '')
    if 'voyagerFeedDashProfileUpdates' in u:
        print('COMMENTS_QUERY_ID =', u.split('queryId=')[1])
    if 'voyagerIdentityDashProfiles.' in u and 'memberIdentity' in u:
        print('PROFILES_QUERY_ID =', u.split('queryId=')[1])
"
```

4. Update `PROFILES_QUERY_ID` and `COMMENTS_QUERY_ID` constants at the top of `linkedin_posts_lib.py`.

If you don't want to install passe, you can re-capture manually: open LinkedIn with Chrome DevTools → Network tab → visit a profile's `/recent-activity/comments/` page → filter for `voyager/api/graphql` → copy the `queryId` from the request URL.

## Cookie lifecycle

The `li_at` cookie typically lasts 6-12 months. If fetches start failing with auth errors:

1. Check you're still logged into LinkedIn in Chrome
2. Sign out and sign back in to force a new cookie
3. Next fetch will automatically pick up the refreshed cookie

## Rate limiting

Default is 5 seconds between requests. For 8-10 people, a full fetch takes about a minute. Recommended limits:

* No more than 20 profiles per session
* No faster than one profile every 5 seconds
* No more than one full-batch run per day for the same people

LinkedIn's anti-scraping systems are real. Aggressive use will result in your account being challenged or temporarily restricted.

## Use cases

This skill underpins three kinds of workflow:

1. **Newsletter curation.** Pull what a curated list of thought leaders is posting, feed into an LLM summariser, produce a weekly digest of what matters. Commenting patterns are often the strongest signal.
2. **Relationship intelligence.** For sales, partnerships, or account management — know what your contacts are engaging with before a meeting.
3. **Competitive monitoring.** Track what competitors' leadership is saying publicly without relying on expensive third-party platforms.

For a complete working example, build a small `ingest.py` around `fetch_posts.py` that writes to SQLite using `ensure_comments_migration` for schema evolution. That keeps your fetched data queryable over time.
