"""Shared primitives for LinkedIn post + comment ingestion.

Single source of truth for cookie handling, Voyager API extraction,
the GraphQL comments-on-others fetch, and LinkedIn's relative-date parsing.

IMPORT PATTERN
    import os, sys
    sys.path.insert(0, os.path.expanduser('~/.claude/skills/linkedin-posts'))
    from linkedin_posts_lib import (
        get_linkedin_cookies, create_api, csrf_from_cookies,
        extract_post_data, compute_approx_post_date,
        fetch_person_comments, ensure_comments_migration,
        PROFILES_QUERY_ID, COMMENTS_QUERY_ID,
    )

WHAT'S IN HERE
    Cookies/auth      get_linkedin_cookies, create_api, csrf_from_cookies
    Post extraction   extract_post_data (silent reshare detection via
                      saveAction URN comparison)
    Date parsing      compute_approx_post_date (LinkedIn relative → YYYY-MM-DD)
    GraphQL comments  resolve_profile_urn, fetch_person_comments
    Schema migration  ensure_comments_migration (additive, idempotent)

WHAT'S NOT IN HERE (per-pipeline orchestration stays local)
    - Rate limiting loops (each pipeline sets its own cadence)
    - Database init / upsert (schema-specific to your project)
    - Raw JSON save paths
    - CSV enrichment

WHEN LINKEDIN ROTATES GRAPHQL QUERY IDS
    fetch_person_comments starts returning http 400. To re-capture using passe:

        chrome-debug                                      # launches debug Chrome
        PASSE_CDP=http://localhost:9223 passe run comments-probe.passe

    Then extract the new hashes from /tmp/comments-capture.jsonl and update
    PROFILES_QUERY_ID and COMMENTS_QUERY_ID below. See SKILL.md for manual
    re-capture via Chrome DevTools Network panel if you don't have passe.
"""

import re
import sys
from datetime import datetime, timedelta


# ─── GraphQL query IDs (rotate when LinkedIn updates queries) ────────────────

PROFILES_QUERY_ID = "voyagerIdentityDashProfiles.b5c27c04968c409fc0ed3546575b9b7a"
COMMENTS_QUERY_ID = "voyagerFeedDashProfileUpdates.8f05a4e5ad12d9cb2b56eaa22afbcab9"

GRAPHQL_HEADERS = {
    "x-restli-protocol-version": "2.0.0",
    "x-li-lang": "en_US",
    "accept": "application/vnd.linkedin.normalized+json+2.1",
}


# ─── Cookies and API client ───────────────────────────────────────────────────

def get_linkedin_cookies():
    """Extract li_at and JSESSIONID cookies from Chrome via browser_cookie3.

    Returns a dict with both cookie values. Exits with a clear message if
    the cookies can't be found or the library isn't installed.
    """
    try:
        import browser_cookie3
    except ImportError:
        print("ERROR: browser_cookie3 not installed.", file=sys.stderr)
        print("Run: pip3 install --user browser_cookie3", file=sys.stderr)
        sys.exit(1)

    cj = browser_cookie3.chrome(domain_name=".linkedin.com")
    cookies = {c.name: c.value for c in cj if c.name in ("li_at", "JSESSIONID")}
    if "li_at" not in cookies:
        print("ERROR: No li_at cookie found. Log into LinkedIn in Chrome.", file=sys.stderr)
        sys.exit(1)
    if "JSESSIONID" not in cookies:
        print("ERROR: No JSESSIONID cookie found.", file=sys.stderr)
        sys.exit(1)
    return cookies


def create_api(cookies):
    """Create an authenticated linkedin_api.Linkedin instance from a cookie dict."""
    try:
        from linkedin_api import Linkedin
    except ImportError:
        print("ERROR: linkedin-api not installed.", file=sys.stderr)
        print("Run: pip3 install --user linkedin-api", file=sys.stderr)
        sys.exit(1)

    from requests.cookies import RequestsCookieJar
    jar = RequestsCookieJar()
    jar.set("li_at", cookies["li_at"], domain=".linkedin.com", path="/")
    jar.set("JSESSIONID", cookies["JSESSIONID"], domain=".linkedin.com", path="/")
    return Linkedin("", "", cookies=jar)


def csrf_from_cookies(cookies):
    """Extract the csrf-token header value from a cookie dict.

    The JSESSIONID cookie value IS the csrf token, but LinkedIn wraps it in
    quotes in the Set-Cookie header which some browsers preserve. Strip them.
    """
    return cookies["JSESSIONID"].strip('"')


# ─── Post extraction (with API-level silent reshare detection) ───────────────

def extract_post_data(post):
    """Extract readable fields from a raw Voyager /feed/updates post element.

    Returns a flat dict with the keys used by all downstream consumers:
        activity_id, permalink, date_text, text, likes, comments, shares,
        is_reshare, reshared_text, reshared_author, author_name, author_headline

    Silent reshare detection:
    LinkedIn's API doesn't flag Repost-without-commentary as a reshare. But the
    saveAction.entityUrn contains the ORIGINAL post's activity ID. If it differs
    from the post's own updateMetadata.urn, we have a silent repost and set
    is_reshare=True, putting the post's text into reshared_text.
    """
    val = post.get("value", {}).get("com.linkedin.voyager.feed.render.UpdateV2", {})

    commentary = val.get("commentary", {})
    text = commentary.get("text", {}).get("text", "") if commentary else ""

    social = val.get("socialDetail", {})
    counts = social.get("totalSocialActivityCounts", {})
    likes = counts.get("numLikes", 0)
    comments = counts.get("numComments", 0)
    shares = counts.get("numShares", 0)

    actor = val.get("actor", {})
    sub_desc = actor.get("subDescription", {})
    date_text = sub_desc.get("text", "").strip() if sub_desc else ""

    author_name = ""
    author_headline = ""
    image_attrs = actor.get("image", {}).get("attributes", [])
    if image_attrs:
        mini = image_attrs[0].get("miniProfile", {})
        author_name = f"{mini.get('firstName', '')} {mini.get('lastName', '')}".strip()
        author_headline = mini.get("occupation", "")

    # Explicit reshare (LinkedIn's resharedUpdate field)
    is_reshare = val.get("resharedUpdate") is not None
    reshared_text = ""
    reshared_author = ""
    if is_reshare:
        reshared = val.get("resharedUpdate", {}).get("value", {}).get(
            "com.linkedin.voyager.feed.render.UpdateV2", {}
        )
        rc = reshared.get("commentary", {})
        if rc:
            reshared_text = rc.get("text", {}).get("text", "")
        ra = reshared.get("actor", {})
        ri = ra.get("image", {}).get("attributes", [])
        if ri:
            rmini = ri[0].get("miniProfile", {})
            reshared_author = f"{rmini.get('firstName', '')} {rmini.get('lastName', '')}".strip()

    # Silent reshare (Repost-without-commentary) via saveAction URN comparison
    if not is_reshare:
        meta = val.get("updateMetadata", {})
        post_urn = meta.get("urn", "")
        save_urn = ""
        for action in meta.get("updateActions", {}).get("actions", []):
            if action.get("actionType") == "SAVE":
                save_urn = action.get("saveAction", {}).get("entityUrn", "")
                break
        if post_urn and save_urn:
            post_aid = post_urn.split(":")[-1]
            save_aid = save_urn.split(":")[-1].rstrip(")")
            if post_aid != save_aid:
                is_reshare = True
                reshared_text = text

    return {
        "activity_id": post.get("id", ""),
        "permalink": post.get("permalink", ""),
        "date_text": date_text,
        "text": text,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "is_reshare": is_reshare,
        "reshared_text": reshared_text,
        "reshared_author": reshared_author,
        "author_name": author_name,
        "author_headline": author_headline,
    }


# ─── Relative-date parsing ────────────────────────────────────────────────────

_DATE_RE = re.compile(r"(\d+)(mo|yr|m|h|d|w)")


def compute_approx_post_date(date_text, fetched_date):
    """Convert LinkedIn's relative date_text to an approximate absolute date.

    LinkedIn's Voyager API returns post dates as relative strings like "20h •",
    "3d •", "1w •", "2mo •", "1yr • Edited •". This function parses the
    leading count+unit and subtracts it from fetched_date.

    Args:
        date_text: e.g. "20h •", "3d •", "1w •", "2mo •", "1yr • Edited •"
        fetched_date: YYYY-MM-DD string (the date this post was fetched)

    Returns:
        YYYY-MM-DD string, or None if unparseable.

    Important: the regex tries "mo" before "m" via alternation order, so
    "11mo" parses as 11 months rather than 11 minutes. If you rewrite this
    as a hand-rolled parser, keep that ordering explicit.
    """
    if not date_text:
        return None
    clean = date_text.strip().split("•")[0].strip()
    m = _DATE_RE.match(clean)
    if not m:
        return None
    num, unit = int(m.group(1)), m.group(2)
    base = datetime.strptime(fetched_date, "%Y-%m-%d")
    deltas = {
        "m": timedelta(minutes=num),
        "h": timedelta(hours=num),
        "d": timedelta(days=num),
        "w": timedelta(weeks=num),
        "mo": timedelta(days=num * 30),
        "yr": timedelta(days=num * 365),
    }
    if unit not in deltas:
        return None
    return (base - deltas[unit]).strftime("%Y-%m-%d")


# ─── GraphQL: public_id → fsd_profile URN → comments-on-others ───────────────

def resolve_profile_urn(api, public_id, csrf):
    """public_id (URL slug) → fsd_profile URN like 'ACoAAAAutwgB8qhC...'.

    Uses the Voyager GraphQL endpoint voyagerIdentityDashProfiles with
    memberIdentity=public_id. Returns None on failure (404, no match, etc.).
    """
    url = (
        "https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true"
        f"&variables=(memberIdentity:{public_id})"
        f"&queryId={PROFILES_QUERY_ID}"
    )
    headers = {**GRAPHQL_HEADERS, "csrf-token": csrf}
    res = api.client.session.get(url, headers=headers)
    if res.status_code != 200:
        return None
    data = res.json()
    elements = (
        data.get("data", {}).get("data", {})
        .get("identityDashProfilesByMemberIdentity", {})
        .get("*elements", [])
    )
    if not elements:
        return None
    return elements[0].replace("urn:li:fsd_profile:", "")


def fetch_person_comments(api, public_id, csrf, max_results=20):
    """Fetch comments the person has left on other people's posts.

    Uses voyagerFeedDashProfileUpdates with a profileUrn variable. The response
    is denormalised — we parse `data.included` for social.Comment entities
    where commenter.commenterProfileId matches the target URN (filtering out
    threaded replies from other people on the same posts).

    Returns a list of comment dicts in the same shape as posts from
    extract_post_data, with these differences:
        - is_reshare: False
        - is_comment_on_other: True
        - parent_activity_urn: URN of the post the person commented on
        - date_text: epoch milliseconds string (not LinkedIn relative text)
        - author_headline: blank (not fetched for comments)

    On any error, returns [] and prints a warning. Never raises — comments are
    additive and must not stop the main posts fetch.
    """
    try:
        urn = resolve_profile_urn(api, public_id, csrf)
        if not urn:
            print(f"  [comments] could not resolve URN for {public_id}", file=sys.stderr)
            return []
        url = (
            "https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true"
            f"&variables=(count:{max_results},start:0,profileUrn:urn%3Ali%3Afsd_profile%3A{urn})"
            f"&queryId={COMMENTS_QUERY_ID}"
        )
        headers = {**GRAPHQL_HEADERS, "csrf-token": csrf}
        res = api.client.session.get(url, headers=headers)
        if res.status_code != 200:
            print(f"  [comments] http {res.status_code} for {public_id}", file=sys.stderr)
            return []
        data = res.json()
    except Exception as e:
        print(f"  [comments] {type(e).__name__}: {e}", file=sys.stderr)
        return []

    included = data.get("included", []) or []
    out = []
    for c in included:
        if not c.get("$type", "").endswith("social.Comment"):
            continue
        if c.get("commenter", {}).get("commenterProfileId") != urn:
            continue
        commentary = c.get("commentary", {}) or {}
        text = commentary.get("text", "") if isinstance(commentary, dict) else ""
        permalink = c.get("permalink", "")
        comment_urn = c.get("entityUrn", "") or c.get("urn", "")
        created_at_ms = c.get("createdAt", 0)
        m = re.search(r"urn%3Ali%3Aactivity%3A(\d+)|urn:li:activity:(\d+)", permalink)
        parent_activity_id = (m.group(1) or m.group(2)) if m else ""
        out.append({
            "activity_id": comment_urn or f"comment:{public_id}:{permalink}",
            "permalink": permalink,
            "date_text": str(created_at_ms) if created_at_ms else "",
            "text": text,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "is_reshare": False,
            "is_comment_on_other": True,
            "parent_activity_urn": f"urn:li:activity:{parent_activity_id}" if parent_activity_id else "",
            "created_at_ms": created_at_ms,
            "reshared_text": "",
            "reshared_author": "",
            "author_name": "",
            "author_headline": "",
        })
    return out


# ─── Schema migration helper ──────────────────────────────────────────────────

def ensure_comments_migration(conn, table="posts"):
    """Additive schema migration to add comments-on-others columns.

    Idempotent — only adds columns that don't already exist. Does not touch
    existing is_reshare semantics. Call from each project's ingest entry point
    after opening the SQLite connection.
    """
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if "is_comment_on_other" not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN is_comment_on_other INTEGER DEFAULT 0")
    if "parent_activity_urn" not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN parent_activity_urn TEXT DEFAULT ''")
