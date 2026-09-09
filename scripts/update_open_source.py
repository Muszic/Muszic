#!/usr/bin/env python3
"""Refresh the visual Open Source Journey in the profile README.

Only standard-library modules are used. The script updates the content between
OSS-JOURNEY markers plus four generated SVG assets:

- assets/open-source-stats.svg
- assets/open-source-stats-mobile.svg
- assets/open-source-map.svg
- assets/open-source-map-mobile.svg

The repository map embeds vector project/company marks while all counts and rows
are rebuilt from the current GitHub API response.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from build_brand_visuals import google_icon, microsoft_icon, tenstorrent_icon, vscode_icon

API = "https://api.github.com"
START = "<!-- OSS-JOURNEY:START -->"
END = "<!-- OSS-JOURNEY:END -->"
DAY = dt.timedelta(days=1)


@dataclass(frozen=True)
class PullRequest:
    repository: str
    number: int
    title: str
    url: str
    created_at: str
    updated_at: str
    state: str
    merged: bool
    draft: bool

    @property
    def status(self) -> str:
        if self.merged:
            return "Merged"
        if self.state == "open":
            return "Draft" if self.draft else "Open"
        return "Closed"


def api_get(url: str, token: str | None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Muszic-profile-readme-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach the GitHub API: {exc.reason}") from exc


def _query_url(username: str, start: dt.date, end: dt.date, page: int) -> str:
    query = (
        f"is:pr author:{username} is:public -user:{username} "
        f"created:{start.isoformat()}..{end.isoformat()}"
    )
    return (
        f"{API}/search/issues?q={urllib.parse.quote(query)}"
        f"&sort=created&order=asc&per_page=100&page={page}"
    )


def fetch_search_window(
    username: str,
    token: str | None,
    start: dt.date,
    end: dt.date,
) -> list[dict[str, Any]]:
    first = api_get(_query_url(username, start, end, 1), token)
    if first.get("incomplete_results"):
        raise RuntimeError("GitHub returned incomplete search results; README was not changed.")

    total = int(first.get("total_count", 0))
    if total > 1000:
        if start >= end:
            raise RuntimeError("More than 1,000 matching PRs were created in one day.")
        middle = start + dt.timedelta(days=(end - start).days // 2)
        return (
            fetch_search_window(username, token, start, middle)
            + fetch_search_window(username, token, middle + DAY, end)
        )

    items = list(first.get("items") or [])
    page = 2
    while len(items) < total:
        payload = api_get(_query_url(username, start, end, page), token)
        if payload.get("incomplete_results"):
            raise RuntimeError("GitHub returned incomplete search results; README was not changed.")
        if int(payload.get("total_count", 0)) != total:
            raise RuntimeError("GitHub search changed during pagination; run the workflow again.")
        page_items = payload.get("items") or []
        if not page_items:
            raise RuntimeError("A GitHub search page was unexpectedly empty.")
        items.extend(page_items)
        page += 1

    if len(items) != total:
        raise RuntimeError(f"Expected {total} PRs but received {len(items)}.")
    return items


def fetch_prs(username: str, token: str | None) -> list[PullRequest]:
    items = fetch_search_window(username, token, dt.date(2008, 1, 1), dt.date.today())
    if not items:
        raise RuntimeError("No public upstream PRs were returned; existing README preserved.")

    seen: set[int] = set()
    output: list[PullRequest] = []
    for item in items:
        identifier = int(item["id"])
        if identifier in seen:
            raise RuntimeError("Duplicate PR returned by GitHub search.")
        seen.add(identifier)

        match = re.fullmatch(
            r"https://api\.github\.com/repos/([\w.-]+)/([\w.-]+)",
            str(item.get("repository_url", "")),
        )
        if not match:
            raise RuntimeError(f"Unexpected repository URL: {item.get('repository_url')}")
        owner, repo = match.groups()
        if owner.lower() == username.lower():
            continue

        state = str(item["state"])
        merged = False
        if state == "closed":
            pull = api_get(str(item["pull_request"]["url"]), token)
            merged = bool(pull.get("merged_at"))

        output.append(
            PullRequest(
                repository=f"{owner}/{repo}",
                number=int(item["number"]),
                title=str(item["title"]),
                url=str(item["html_url"]),
                created_at=str(item["created_at"]),
                updated_at=str(item["updated_at"]),
                state=state,
                merged=merged,
                draft=bool(item.get("draft", False)),
            )
        )

    if not output:
        raise RuntimeError("The validated public PR set was empty; existing README preserved.")
    return output


def md_escape(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;")


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def repo_focus(repository: str) -> str:
    known = {
        "microsoft/vscode": "Correctness fixes, terminal suggestions, and regression tests",
        "google/googletest": "UTF-8 output, flag parsing, and timestamp correctness",
        "ollama/ollama": "OpenAI-compatible response IDs and streaming behavior",
        "tenstorrent/polaris": "ONNX workloads and fused-operator support",
        "microsoft/SharePoint-Embedded-VS-Code-Extension": "Clearer non-admin development experience",
    }
    return known.get(repository, "Upstream fixes, tests, and product improvements")


def display_repo(repository: str) -> str:
    if repository == "microsoft/SharePoint-Embedded-VS-Code-Extension":
        return "microsoft / SharePoint Embedded"
    return repository.replace("/", " / ")


def status_count(prs: list[PullRequest], status: str) -> int:
    return sum(
        1
        for pr in prs
        if pr.status == status or (status == "Open" and pr.status == "Draft")
    )


def status_link(repository: str, username: str, status: str, count: int) -> str:
    if not count:
        return "0"
    filters = {
        "Merged": "is:merged",
        "Open": "is:open",
        "Closed": "is:closed is:unmerged",
    }
    query = urllib.parse.quote(f"is:pr author:{username} {filters[status]}")
    return f"[{count}](https://github.com/{repository}/pulls?q={query})"


def group_rows(prs: list[PullRequest]) -> list[tuple[str, list[PullRequest]]]:
    grouped: dict[str, list[PullRequest]] = defaultdict(list)
    for pr in prs:
        grouped[pr.repository].append(pr)
    return sorted(
        grouped.items(),
        key=lambda pair: (
            -status_count(pair[1], "Merged"),
            -len(pair[1]),
            pair[0].lower(),
        ),
    )


def render_section(prs: list[PullRequest], username: str) -> str:
    rows = group_rows(prs)
    merged = status_count(prs, "Merged")
    open_count = status_count(prs, "Open")
    closed = status_count(prs, "Closed")
    recent = sorted(prs, key=lambda pr: (pr.updated_at, pr.number), reverse=True)[:8]
    search_query = urllib.parse.quote(f"is:pr author:{username} is:public -user:{username}")

    lines = [
        '<p align="center">',
        '  <picture>',
        '    <source media="(max-width: 680px)" srcset="./assets/open-source-stats-mobile.svg" />',
        '    <img src="./assets/open-source-stats.svg" alt="Open-source contribution totals" width="100%" />',
        '  </picture>',
        '</p>',
        "",
        '<p align="center">',
        '  <picture>',
        '    <source media="(max-width: 680px)" srcset="./assets/open-source-map-mobile.svg" />',
        '    <img src="./assets/open-source-map.svg" alt="Repositories in the open-source journey" width="100%" />',
        '  </picture>',
        '</p>',
        "",
        '<p align="center">',
        f"  <strong>{len(rows)} repositories · {len(prs)} pull requests · {merged} merged · {open_count} open · {closed} closed without merge</strong><br/>",
        f'  <a href="https://github.com/search?q={search_query}&type=pullrequests"><strong>Explore every public upstream pull request ↗</strong></a>',
        '</p>',
        "",
        "<details>",
        "<summary><strong>Open exact repository counts and recent PR links</strong></summary>",
        "<br/>",
        "",
        "| Repository | My work | Merged | Open | Closed |",
        "| :--- | :--- | ---: | ---: | ---: |",
    ]

    for repository, repo_prs in rows:
        repo_merged = status_count(repo_prs, "Merged")
        repo_open = status_count(repo_prs, "Open")
        repo_closed = status_count(repo_prs, "Closed")
        lines.append(
            f"| [**{repository}**](https://github.com/{repository}) | {repo_focus(repository)} | "
            f"{status_link(repository, username, 'Merged', repo_merged)} | "
            f"{status_link(repository, username, 'Open', repo_open)} | "
            f"{status_link(repository, username, 'Closed', repo_closed)} |"
        )

    lines.extend(
        [
            "",
            "#### Recent pull-request activity",
            "",
            "| Pull request | Status |",
            "| :--- | :--- |",
        ]
    )
    for pr in recent:
        title = md_escape(pr.title)
        if len(title) > 88:
            title = title[:85] + "..."
        status = f"**{pr.status}**" if pr.status == "Merged" else pr.status
        lines.append(f"| [{pr.repository}#{pr.number} · {title}]({pr.url}) | {status} |")

    lines.extend(
        [
            "",
            "</details>",
            "",
            "<sub>Counts cover public PRs authored by me in repositories I do not own. Issues, reviews, direct commits, private work, and PRs to my own repositories are intentionally excluded.</sub>",
        ]
    )
    return "\n".join(lines)


def orb_svg(cx: int, cy: int, r: int) -> str:
    q = int(r * 0.52)
    return f'''<g transform="translate({cx} {cy})">
<circle cy="6" r="{r}" fill="#234B31" opacity=".16"/>
<circle r="{r}" fill="url(#metal)" stroke="#1B5337" stroke-width="2"/>
<circle r="{int(r*0.76)}" fill="#13282A" stroke="#B8F29E"/>
<path d="M{-q} {-q}H{q}L{int(q*.28)} 0L{q} {q}H{-q}L{int(-q*.28)} 0Z" fill="#82E35B"/>
<path d="M{-int(r*.55)} {-int(r*.55)}A{int(r*.72)} {int(r*.72)} 0 0 1 {int(r*.46)} {-int(r*.61)}" fill="none" stroke="#FFFFFF" stroke-opacity=".7" stroke-width="3" stroke-linecap="round"/>
</g>'''


def repo_logo_svg(repository: str, cx: int, cy: int, radius: int) -> str:
    """Render a project/company mark inside a consistent glass logo puck."""
    if repository == "microsoft/vscode":
        icon = vscode_icon(radius * 1.18)
        inner = "#F7FBFF"
        glow = "#2EA8E6"
    elif repository == "google/googletest":
        # GoogleTest has no standalone mark in its main repository; use Google G + label.
        icon = google_icon(radius * 1.10)
        inner = "#FFFFFF"
        glow = "#65C774"
    elif repository == "tenstorrent/polaris":
        icon = tenstorrent_icon(radius * 1.10)
        inner = "#171B1D"
        glow = "#FFD10A"
    elif repository == "microsoft/SharePoint-Embedded-VS-Code-Extension":
        icon = microsoft_icon(radius * 1.02)
        inner = "#FFFFFF"
        glow = "#57B8F0"
    elif repository == "ollama/ollama":
        icon = (
            f'<g fill="#111827" transform="translate(0 1)">'
            f'<path d="M{-radius*.36:.1f} {-radius*.14:.1f}L{-radius*.29:.1f} {-radius*.49:.1f}'
            f'L{-radius*.08:.1f} {-radius*.31:.1f}H{radius*.08:.1f}L{radius*.29:.1f} {-radius*.49:.1f}'
            f'L{radius*.36:.1f} {-radius*.14:.1f}V{radius*.25:.1f}Q0 {radius*.55:.1f} '
            f'{-radius*.36:.1f} {radius*.25:.1f}Z"/>'
            f'<circle cx="{-radius*.14:.1f}" cy="{radius*.02:.1f}" r="{radius*.045:.1f}" fill="#FFFFFF"/>'
            f'<circle cx="{radius*.14:.1f}" cy="{radius*.02:.1f}" r="{radius*.045:.1f}" fill="#FFFFFF"/>'
            '</g>'
        )
        inner = "#FFFFFF"
        glow = "#87919B"
    else:
        initials = "".join(part[:1].upper() for part in repository.split("/")[-1].split("-")[:2]) or "OS"
        icon = (
            f'<text x="0" y="{radius*.18:.1f}" text-anchor="middle" '
            f'font-family="Inter,Segoe UI,Arial" font-size="{radius*.70:.1f}" font-weight="800" '
            f'fill="#0A7A43">{xml_escape(initials)}</text>'
        )
        inner = "#FFFFFF"
        glow = "#82E35B"

    return f'''<g transform="translate({cx} {cy})">
<circle r="{radius*1.30:.1f}" fill="{glow}" opacity=".10"/>
<circle cy="{radius*.12:.1f}" r="{radius:.1f}" fill="#234B31" opacity=".14"/>
<circle r="{radius:.1f}" fill="url(#metal)" stroke="#315E43" stroke-width="1.4"/>
<circle r="{radius*.76:.1f}" fill="{inner}" stroke="#D9E3D5"/>
<path d="M{-radius*.52:.1f} {-radius*.53:.1f}A{radius*.71:.1f} {radius*.71:.1f} 0 0 1 {radius*.44:.1f} {-radius*.58:.1f}" fill="none" stroke="#FFFFFF" stroke-opacity=".78" stroke-width="2.3" stroke-linecap="round"/>
{icon}
</g>'''


def render_stats_svg(prs: list[PullRequest]) -> str:
    values = [
        (len({pr.repository for pr in prs}), "REPOSITORIES", "DISCOVERED"),
        (len(prs), "PULL REQUESTS", "AUTHORED"),
        (status_count(prs, "Merged"), "MERGED", "LANDED"),
        (status_count(prs, "Open"), "OPEN", "IN REVIEW"),
    ]
    cards = []
    for index, (number, label, note) in enumerate(values):
        x = 24 + index * 290
        tint = "#F0F7EA" if index in (1, 3) else "#FEFFF9"
        cards.append(
            f'''<g transform="translate({x} 78)">
<rect y="7" width="266" height="142" rx="24" fill="#31553B" opacity=".09"/>
<rect width="266" height="142" rx="24" fill="{tint}" stroke="#D2DEC9"/>
<circle cx="235" cy="29" r="5" fill="#65DA57"/>
<text x="24" y="78" class="number">{number}</text>
<text x="26" y="111" class="label">{xml_escape(label)}</text>
<text x="238" y="113" text-anchor="end" class="note">{xml_escape(note)}</text>
</g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="242" viewBox="0 0 1200 242" role="img" aria-labelledby="title">
<title id="title">Open-source contribution statistics</title>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#FAFCF7"/><stop offset="1" stop-color="#EAF3E5"/></linearGradient>
  <radialGradient id="metal" cx="28%" cy="18%"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#718477"/></radialGradient>
  <filter id="cardShadow"><feDropShadow dx="0" dy="7" stdDeviation="9" flood-color="#31553B" flood-opacity=".13"/></filter>
  <filter id="orbShadow"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#2D6A3D" flood-opacity=".28"/></filter>
</defs>
<style>
  text {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; }}
  .number {{ font-size: 58px; font-weight: 750; letter-spacing: -2px; fill: #13282A; }}
  .label {{ font-size: 14px; font-weight: 750; letter-spacing: 1.4px; fill: #0A7A43; }}
  .note {{ font-size: 10px; font-weight: 700; letter-spacing: 1.1px; fill: #728078; }}
</style>
<rect width="1200" height="242" rx="28" fill="url(#bg)"/>
{orb_svg(52, 42, 27)}
<text x="92" y="37" font-family="Inter,Segoe UI,Arial" font-size="13" font-weight="750" letter-spacing="1.5" fill="#0A7A43">UPSTREAM SIGNAL / ONLINE</text>
<text x="92" y="59" font-family="Inter,Segoe UI,Arial" font-size="14" fill="#66736A">Live public pull-request telemetry</text>
<text x="1168" y="48" text-anchor="end" font-family="Inter,Segoe UI,Arial" font-size="11" font-weight="700" letter-spacing="1.2" fill="#66736A">OMNITRIX NETWORK</text>
{''.join(cards)}
</svg>'''


def _fit_svg_text(value: str, max_chars: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip() + "…"


def render_map_svg(prs: list[PullRequest]) -> str:
    rows = group_rows(prs)
    row_h = 84
    height = 108 + row_h * len(rows) + 24
    row_svg = []
    for index, (repository, repo_prs) in enumerate(rows):
        y = 94 + index * row_h
        merged = status_count(repo_prs, "Merged")
        open_count = status_count(repo_prs, "Open")
        closed = status_count(repo_prs, "Closed")
        fill = "#F0F7EB" if merged else "#FEFFF9"
        display = _fit_svg_text(display_repo(repository), 38)
        focus = _fit_svg_text(repo_focus(repository), 60)
        row_svg.append(
            f'''<g transform="translate(24 {y})">
<rect y="5" width="1152" height="68" rx="19" fill="#31553B" opacity=".07"/>
<rect width="1152" height="68" rx="19" fill="{fill}" stroke="#D3DFCC"/>
{repo_logo_svg(repository, 36, 34, 24)}
<text x="74" y="29" class="repo">{xml_escape(display)}</text>
<text x="74" y="50" class="focus">{xml_escape(focus)}</text>
<g transform="translate(875 14)"><rect width="74" height="40" rx="16" fill="#E2F5DC" stroke="#B8DDB0"/><text x="37" y="18" class="chipLabel" text-anchor="middle">MERGED</text><text x="37" y="34" class="chipValue" text-anchor="middle">{merged}</text></g>
<g transform="translate(958 14)"><rect width="74" height="40" rx="16" fill="#F0F4EC" stroke="#D4DED0"/><text x="37" y="18" class="chipLabel" text-anchor="middle">OPEN</text><text x="37" y="34" class="chipValue" text-anchor="middle">{open_count}</text></g>
<g transform="translate(1041 14)"><rect width="86" height="40" rx="16" fill="#F7F8F4" stroke="#DADFD7"/><text x="43" y="18" class="chipLabel" text-anchor="middle">CLOSED</text><text x="43" y="34" class="chipValue" text-anchor="middle">{closed}</text></g>
</g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title">
<title id="title">Repositories in the open-source journey</title>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#FAFCF7"/><stop offset="1" stop-color="#EAF3E5"/></linearGradient>
  <radialGradient id="metal" cx="28%" cy="18%"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#718477"/></radialGradient>
  <filter id="rowShadow"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#31553B" flood-opacity=".10"/></filter>
  <filter id="orbShadow"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#2D6A3D" flood-opacity=".28"/></filter>
</defs>
<style>
  text {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; }}
  .repo {{ font-size: 18px; font-weight: 750; fill: #13282A; }}
  .focus {{ font-size: 13px; fill: #66736A; }}
  .chipLabel {{ font-size: 8px; font-weight: 750; letter-spacing: .8px; fill: #66736A; }}
  .chipValue {{ font-size: 14px; font-weight: 750; fill: #0A7A43; }}
</style>
<rect width="1200" height="{height}" rx="28" fill="url(#bg)"/>
{orb_svg(52, 45, 28)}
<text x="92" y="38" font-family="Inter,Segoe UI,Arial" font-size="13" font-weight="750" letter-spacing="1.5" fill="#0A7A43">UPSTREAM MAP</text>
<text x="92" y="62" font-family="Inter,Segoe UI,Arial" font-size="22" font-weight="750" fill="#13282A">Where the work is happening</text>
<text x="1168" y="50" text-anchor="end" font-family="Inter,Segoe UI,Arial" font-size="12" fill="#66736A">Sorted by merged work, then total PRs</text>
{''.join(row_svg)}
</svg>'''


def render_stats_mobile_svg(prs: list[PullRequest]) -> str:
    values = [
        (len({pr.repository for pr in prs}), "REPOSITORIES"),
        (len(prs), "PULL REQUESTS"),
        (status_count(prs, "Merged"), "MERGED"),
        (status_count(prs, "Open"), "OPEN"),
    ]
    cards: list[str] = []
    for index, (number, label) in enumerate(values):
        x = 18 + (index % 2) * 288
        y = 82 + (index // 2) * 132
        tint = "#F0F7EA" if index in (1, 3) else "#FEFFF9"
        cards.append(
            f'''<g transform="translate({x} {y})">
<rect y="5" width="270" height="116" rx="20" fill="#31553B" opacity=".08"/>
<rect width="270" height="116" rx="20" fill="{tint}" stroke="#D2DEC9"/>
<circle cx="240" cy="25" r="4" fill="#65DA57"/>
<text x="22" y="66" class="number">{number}</text>
<text x="24" y="94" class="label">{xml_escape(label)}</text>
</g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="354" viewBox="0 0 600 354" role="img" aria-labelledby="title">
<title id="title">Open-source contribution statistics</title>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#FAFCF7"/><stop offset="1" stop-color="#EAF3E5"/></linearGradient><radialGradient id="metal" cx="28%" cy="18%"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#718477"/></radialGradient></defs>
<style>text{{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}.number{{font-size:48px;font-weight:750;letter-spacing:-2px;fill:#13282A}}.label{{font-size:12px;font-weight:750;letter-spacing:1.2px;fill:#0A7A43}}</style>
<rect width="600" height="354" rx="25" fill="url(#bg)"/>
{orb_svg(40, 40, 24)}
<text x="76" y="35" font-family="Inter,Segoe UI,Arial" font-size="11" font-weight="750" letter-spacing="1.2" fill="#0A7A43">UPSTREAM SIGNAL / ONLINE</text>
<text x="76" y="55" font-family="Inter,Segoe UI,Arial" font-size="12" fill="#66736A">Public PR telemetry</text>
{''.join(cards)}
</svg>'''


def render_map_mobile_svg(prs: list[PullRequest]) -> str:
    rows = group_rows(prs)
    row_h = 116
    height = 92 + row_h * len(rows) + 18
    row_svg: list[str] = []
    for index, (repository, repo_prs) in enumerate(rows):
        y = 80 + index * row_h
        merged = status_count(repo_prs, "Merged")
        open_count = status_count(repo_prs, "Open")
        closed = status_count(repo_prs, "Closed")
        fill = "#F0F7EB" if merged else "#FEFFF9"
        display = _fit_svg_text(display_repo(repository), 34)
        focus = _fit_svg_text(repo_focus(repository), 58)
        row_svg.append(
            f'''<g transform="translate(18 {y})">
<rect y="5" width="564" height="100" rx="18" fill="#31553B" opacity=".07"/>
<rect width="564" height="100" rx="18" fill="{fill}" stroke="#D3DFCC"/>
{repo_logo_svg(repository, 31, 28, 21)}
<text x="66" y="26" class="repo">{xml_escape(display)}</text>
<text x="66" y="47" class="focus">{xml_escape(focus)}</text>
<g transform="translate(66 61)"><rect width="104" height="27" rx="12" fill="#E2F5DC" stroke="#B8DDB0"/><text x="52" y="18" class="chip" text-anchor="middle">MERGED {merged}</text></g>
<g transform="translate(176 61)"><rect width="94" height="27" rx="12" fill="#F0F4EC" stroke="#D4DED0"/><text x="47" y="18" class="chip" text-anchor="middle">OPEN {open_count}</text></g>
<g transform="translate(280 61)"><rect width="110" height="27" rx="12" fill="#F7F8F4" stroke="#DADFD7"/><text x="55" y="18" class="chip" text-anchor="middle">CLOSED {closed}</text></g>
</g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{height}" viewBox="0 0 600 {height}" role="img" aria-labelledby="title">
<title id="title">Repositories in the open-source journey</title>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#FAFCF7"/><stop offset="1" stop-color="#EAF3E5"/></linearGradient><radialGradient id="metal" cx="28%" cy="18%"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#718477"/></radialGradient></defs>
<style>text{{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}.repo{{font-size:15px;font-weight:750;fill:#13282A}}.focus{{font-size:10px;fill:#66736A}}.chip{{font-size:9px;font-weight:750;fill:#0A7A43}}</style>
<rect width="600" height="{height}" rx="25" fill="url(#bg)"/>
{orb_svg(40, 39, 23)}
<text x="75" y="35" font-family="Inter,Segoe UI,Arial" font-size="11" font-weight="750" letter-spacing="1.2" fill="#0A7A43">UPSTREAM MAP</text>
<text x="75" y="55" font-family="Inter,Segoe UI,Arial" font-size="17" font-weight="750" fill="#13282A">Where the work is happening</text>
{''.join(row_svg)}
</svg>'''


def replace_section(readme: str, replacement: str) -> str:
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise RuntimeError("README must contain exactly one OSS-JOURNEY marker pair.")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if start >= end:
        raise RuntimeError("OSS-JOURNEY markers are out of order.")
    return readme[:start] + "\n\n" + replacement.rstrip() + "\n\n" + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="Muszic")
    parser.add_argument("--readme", default="readme.md")
    parser.add_argument("--stats", default="assets/open-source-stats.svg")
    parser.add_argument("--map", default="assets/open-source-map.svg")
    parser.add_argument("--stats-mobile", default="assets/open-source-stats-mobile.svg")
    parser.add_argument("--map-mobile", default="assets/open-source-map-mobile.svg")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    readme_path = Path(args.readme)
    stats_path = Path(args.stats)
    map_path = Path(args.map)
    stats_mobile_path = Path(args.stats_mobile)
    map_mobile_path = Path(args.map_mobile)
    original = readme_path.read_text(encoding="utf-8")

    prs = fetch_prs(args.username, token)
    updated = replace_section(original, render_section(prs, args.username))
    stats_svg = render_stats_svg(prs)
    map_svg = render_map_svg(prs)
    stats_mobile_svg = render_stats_mobile_svg(prs)
    map_mobile_svg = render_map_mobile_svg(prs)

    changed = (
        updated != original
        or not stats_path.exists()
        or stats_path.read_text(encoding="utf-8") != stats_svg
        or not map_path.exists()
        or map_path.read_text(encoding="utf-8") != map_svg
        or not stats_mobile_path.exists()
        or stats_mobile_path.read_text(encoding="utf-8") != stats_mobile_svg
        or not map_mobile_path.exists()
        or map_mobile_path.read_text(encoding="utf-8") != map_mobile_svg
    )
    if args.check:
        print("update required" if changed else "already current")
        return 1 if changed else 0

    if changed:
        readme_path.write_text(updated, encoding="utf-8")
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.parent.mkdir(parents=True, exist_ok=True)
        stats_mobile_path.parent.mkdir(parents=True, exist_ok=True)
        map_mobile_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(stats_svg, encoding="utf-8")
        map_path.write_text(map_svg, encoding="utf-8")
        stats_mobile_path.write_text(stats_mobile_svg, encoding="utf-8")
        map_mobile_path.write_text(map_mobile_svg, encoding="utf-8")
        print(f"updated visual open-source journey using {len(prs)} PRs")
    else:
        print("already current")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - CLI safety boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
