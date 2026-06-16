import re
import requests


def parse_github_pr_url(url):
    """Parse a GitHub PR URL and extract owner, repo, and PR number."""
    patterns = [
        r'github\.com/([^/]+)/([^/]+)/pull/(\d+)',
        r'github\.com/([^/]+)/([^/]+)/pulls/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return {
                'owner': match.group(1),
                'repo': match.group(2),
                'pr_number': int(match.group(3))
            }
    return None


def fetch_pr_diff(url, token=None):
    """
    Fetch the diff content of a GitHub Pull Request.
    Returns a dict with pr_info and diff text.
    """
    parsed = parse_github_pr_url(url)
    if not parsed:
        raise ValueError(
            "Invalid GitHub PR URL. Expected format: "
            "https://github.com/owner/repo/pull/123"
        )

    owner = parsed['owner']
    repo = parsed['repo']
    pr_number = parsed['pr_number']

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'ReviewPilot/1.0'
    }
    if token:
        headers['Authorization'] = f'token {token}'

    # Fetch PR metadata
    api_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
    response = requests.get(api_url, headers=headers, timeout=30)

    if response.status_code == 404:
        raise ValueError(
            "Pull request not found. Make sure the repository is public "
            "or provide a valid GitHub token."
        )
    elif response.status_code == 403:
        raise ValueError(
            "GitHub API rate limit exceeded. Please provide a GitHub token "
            "or try again later."
        )
    elif response.status_code != 200:
        raise ValueError(
            f"GitHub API error (HTTP {response.status_code}): {response.text}"
        )

    pr_data = response.json()

    # Fetch the diff
    diff_headers = headers.copy()
    diff_headers['Accept'] = 'application/vnd.github.v3.diff'
    diff_response = requests.get(api_url, headers=diff_headers, timeout=30)

    if diff_response.status_code != 200:
        raise ValueError("Failed to fetch PR diff from GitHub.")

    diff_text = diff_response.text

    # Truncate extremely large diffs to avoid API token limits
    max_chars = 30000
    if len(diff_text) > max_chars:
        diff_text = diff_text[:max_chars] + "\n\n... [DIFF TRUNCATED — too large for analysis]"

    return {
        'pr_info': {
            'title': pr_data.get('title', ''),
            'author': pr_data.get('user', {}).get('login', 'unknown'),
            'base_branch': pr_data.get('base', {}).get('ref', ''),
            'head_branch': pr_data.get('head', {}).get('ref', ''),
            'changed_files': pr_data.get('changed_files', 0),
            'additions': pr_data.get('additions', 0),
            'deletions': pr_data.get('deletions', 0),
            'url': url.strip(),
        },
        'diff': diff_text
    }


def fetch_pr_files(url, token=None):
    """Fetch the list of changed files in a PR."""
    parsed = parse_github_pr_url(url)
    if not parsed:
        return []

    owner = parsed['owner']
    repo = parsed['repo']
    pr_number = parsed['pr_number']

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'ReviewPilot/1.0'
    }
    if token:
        headers['Authorization'] = f'token {token}'

    api_url = (
        f'https://api.github.com/repos/{owner}/{repo}'
        f'/pulls/{pr_number}/files'
    )
    response = requests.get(api_url, headers=headers, timeout=30)

    if response.status_code == 200:
        return [
            {
                'filename': f.get('filename', ''),
                'status': f.get('status', ''),
                'additions': f.get('additions', 0),
                'deletions': f.get('deletions', 0),
                'patch': f.get('patch', ''),
            }
            for f in response.json()
        ]
    return []
