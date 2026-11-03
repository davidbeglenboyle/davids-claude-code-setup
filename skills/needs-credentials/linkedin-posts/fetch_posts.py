"""
Fetch LinkedIn posts AND comments-on-others for a list of people using the Voyager API.
Authenticates via Chrome browser cookies (no stored credentials).

Usage:
    python3 fetch_posts.py --config /path/to/partners.json --output /path/to/output/
    python3 fetch_posts.py --config /path/to/partners.json --output /path/to/output/ --max-posts 20
    python3 fetch_posts.py --config /path/to/partners.json --output /path/to/output/ --person example-slug
    python3 fetch_posts.py --config /path/to/partners.json --output /path/to/output/ --no-comments

All reusable primitives (cookies, extraction, silent-reshare detection, GraphQL
comments fetch, relative-date parsing) live in linkedin_posts_lib.py alongside
this file. Downstream pipelines should import from that library rather than
copy-paste.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

# linkedin_posts_lib is in the same directory as this script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linkedin_posts_lib import (
    get_linkedin_cookies,
    create_api,
    csrf_from_cookies,
    extract_post_data,
    fetch_person_comments,
)


def fetch_person_posts(api, public_id, max_posts=50):
    """Thin wrapper: fetch raw posts for a public_id and extract structured dicts."""
    try:
        raw_posts = api.get_profile_updates(public_id=public_id, max_results=max_posts)
        return [extract_post_data(p) for p in raw_posts]
    except Exception as e:
        print(f"  ERROR fetching {public_id}: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Fetch LinkedIn posts for configured partners')
    parser.add_argument('--config', required=True, help='Path to partners.json')
    parser.add_argument('--output', required=True, help='Output directory for dated JSON files')
    parser.add_argument('--max-posts', type=int, default=50, help='Max posts per person (default: 50)')
    parser.add_argument('--person', help='Fetch only this public_id (for testing)')
    parser.add_argument('--delay', type=int, default=5, help='Seconds between requests (default: 5)')
    parser.add_argument('--no-comments', action='store_true',
                        help='Skip the comments-on-others GraphQL fetch')
    args = parser.parse_args()

    # Load config
    with open(args.config) as f:
        config = json.load(f)

    partners = config.get('partners', [])
    if args.person:
        partners = [p for p in partners if p['public_id'] == args.person]
        if not partners:
            print(f"No partner found with public_id: {args.person}")
            sys.exit(1)

    print(f"Fetching posts for {len(partners)} partner(s), max {args.max_posts} each")

    # Auth
    print("Extracting LinkedIn cookies from Chrome...")
    cookies = get_linkedin_cookies()
    api = create_api(cookies)
    csrf_token = csrf_from_cookies(cookies)
    print("Authenticated!")

    # Fetch
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    results = {
        'fetch_date': today,
        'partners': {}
    }

    for i, partner in enumerate(partners):
        pid = partner['public_id']
        name = partner.get('name', pid)
        print(f"\n[{i+1}/{len(partners)}] {name} ({pid})...")

        posts = fetch_person_posts(api, pid, max_posts=args.max_posts)
        comments = [] if args.no_comments else fetch_person_comments(api, pid, csrf_token)
        results['partners'][pid] = {
            'name': name,
            'role': partner.get('role', ''),
            'location': partner.get('location', ''),
            'post_count': len(posts),
            'comment_count': len(comments),
            'posts': posts,
            'comments': comments,
        }
        print(f"  Got {len(posts)} posts, {len(comments)} comments-on-others")

        # Rate limiting pause between requests
        if i < len(partners) - 1:
            print(f"  Waiting {args.delay}s...")
            time.sleep(args.delay)

    # Save
    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(args.output, f'{today}.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total_posts = sum(p['post_count'] for p in results['partners'].values())
    total_cmts = sum(p.get('comment_count', 0) for p in results['partners'].values())
    print(f"\nDone! {total_posts} posts + {total_cmts} comments from {len(results['partners'])} partners saved to {output_path}")

    # Print summary
    print("\nSummary:")
    for pid, data in results['partners'].items():
        originals = sum(1 for p in data['posts'] if not p['is_reshare'])
        reshares = sum(1 for p in data['posts'] if p['is_reshare'])
        total_likes = sum(p['likes'] for p in data['posts'])
        n_comments = data.get('comment_count', 0)
        print(f"  {data['name']}: {originals} original, {reshares} reshares, {n_comments} comments, {total_likes:,} likes")


if __name__ == '__main__':
    main()
