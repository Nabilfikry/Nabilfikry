"""Render the futuristic profile SVGs (dashboard, insights, project cards).

Usage: GH_TOKEN=... python3 scripts/generate.py <out_dir>
Stdlib only, so it runs on a bare GitHub Actions runner.
"""
import base64
import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGIN = "Nabilfikry"
PROFILE = {
    "name": "Nabil Fikry Khaidar",
    "nick": "Nafi",
    "tagline": ["Information Systems Student", "UI/UX Designer & Software Engineer"],
    "location": "Indonesia",
    "site": "naabilfikry.vercel.app",
    "skills": ["UI/UX", "Figma", "System Analysis", "UML", "Next.js", "React",
               "Laravel", "Go", "PostgreSQL", "Docker"],
}
PROJECTS = [
    {"slug": "resora", "name": "Resora", "thumb": "resora.jpg",
     "desc": "Sistem Informasi Manajemen Senior Resident dan Asrama.",
     "stack": ["Next.js", "Express.js", "PostgreSQL"]},
    {"slug": "koneksa", "name": "KONEKSA", "thumb": "koneksa.jpg",
     "desc": "Platform kolaborasi mitra bisnis, UMKM, dan pemerintah daerah.",
     "stack": ["Laravel", "MySQL"]},
    {"slug": "pmc", "name": "PMC 2025", "thumb": "pmc.jpg",
     "desc": "Sistem Informasi Perlombaan dan Penjurian.",
     "stack": ["Laravel", "MySQL"]},
    {"slug": "simka", "name": "SIMKA-Panti", "thumb": "simka.jpg",
     "desc": "Sistem Informasi Donasi Panti Asuhan di Bandung.",
     "stack": ["React", "Laravel", "MySQL"]},
]
STACK_COLORS = {"Next.js": "#e5e7eb", "Express.js": "#a3a3a3", "PostgreSQL": "#4f8fd6",
                "Laravel": "#ff4f40", "MySQL": "#f29111", "React": "#61dafb"}

FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace"
BG, PANEL, CARD, LINE = "#14141c", "#1b1b26", "#22222f", "#2c2c3c"
TEXT, MUTED, ACCENT = "#f4f3ff", "#9b9bb4", "#a78bfa"
LEVELS = ["#262634", "#4c2a85", "#6d3fd1", "#9b6dff", "#d9c6ff"]

ICONS = {  # 16x16 octicon-style paths
    "repo": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 010-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 11-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8z",
    "star": "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z",
    "people": "M10.5 4.5a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zM8 8.5c-3.2 0-5.5 1.6-5.5 4.2V14h11v-1.3c0-2.6-2.3-4.2-5.5-4.2z",
    "pulse": "M0 8.75A.75.75 0 01.75 8h2.7l1.9-5.1a.75.75 0 011.41.02L9.6 11.6l1.3-3.1a.75.75 0 01.7-.5h3.65a.75.75 0 010 1.5h-3.15l-1.84 4.29a.75.75 0 01-1.4-.05L6.05 5.4 4.7 9.01a.75.75 0 01-.7.49H.75A.75.75 0 010 8.75z",
    "pin": "M8 0a5.5 5.5 0 00-5.5 5.5C2.5 9.6 8 16 8 16s5.5-6.4 5.5-10.5A5.5 5.5 0 008 0zm0 7.75a2.25 2.25 0 110-4.5 2.25 2.25 0 010 4.5z",
    "github": "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z",
    "flame": "M8 16c3.3 0 6-2.4 6-5.6 0-3.9-3.4-5.6-3.9-9.4C8 2.3 6.8 4.6 7 7 5.9 6.4 5.4 5.2 5.4 4 3.4 5.6 2 7.9 2 10.4 2 13.6 4.7 16 8 16z",
}

QUERY = """query($login:String!){user(login:$login){
  avatarUrl(size:320) followers{totalCount} following{totalCount}
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){totalCount nodes{
    isFork stargazerCount languages(first:10){edges{size node{name color}}}}}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""


# ---------------------------------------------------------------- data
def http(url, body=None, token=None):
    req = urllib.request.Request(url, data=body, headers={"User-Agent": LOGIN})
    if token:
        req.add_header("Authorization", f"bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    res = json.loads(http("https://api.github.com/graphql", body, token))
    if "errors" in res:
        raise SystemExit(f"GraphQL error: {res['errors']}")
    u = res["data"]["user"]
    repos = u["repositories"]
    langs = {}
    for repo in repos["nodes"]:
        if repo["isFork"]:
            continue
        for e in repo["languages"]["edges"]:
            n = e["node"]
            size, _ = langs.get(n["name"], (0, None))
            langs[n["name"]] = (size + e["size"], n["color"] or "#888")
    cal = u["contributionsCollection"]["contributionCalendar"]
    return {
        "avatar": "data:image/png;base64," + base64.b64encode(http(u["avatarUrl"])).decode(),
        "repos": repos["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos["nodes"]),
        "followers": u["followers"]["totalCount"],
        "following": u["following"]["totalCount"],
        "total": cal["totalContributions"],
        "weeks": [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]],
        "langs": sorted(((n, s, c) for n, (s, c) in langs.items()), key=lambda x: -x[1]),
        "today": dt.date.today(),
    }


def streaks(days):
    """days: daily counts, oldest first, last item = today. Returns (current, longest)."""
    longest = run = 0
    for c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # today with no contribution yet does not break the current streak
    tail = days[:-1] if days and not days[-1] else days
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def level(c, peak):
    return 0 if not c else min(4, 1 + int(3 * c / max(peak, 1)))


# ---------------------------------------------------------------- svg helpers
def icon(name, x, y, size, color):
    return (f'<path transform="translate({x} {y}) scale({size / 16})" '
            f'd="{ICONS[name]}" fill="{color}"/>')


def text(x, y, s, size=13, color=TEXT, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')


def wrap(s, limit):
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + len(w) + 1 > limit:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur] if cur else lines


def pill_width(s, size=10):
    return len(s) * size * 0.55 + 14


def svg(w, h, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'<style>{style}</style>{body}</svg>')


def short(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


# ---------------------------------------------------------------- dashboard
def render_dashboard(d):
    W, H, SB = 1000, 600, 270
    o = [f'''<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  <clipPath id="ava"><rect x="64" y="100" width="142" height="142" rx="26"/></clipPath>
  <clipPath id="ava-s"><circle cx="905" cy="32" r="15"/></clipPath>
  <linearGradient id="neon" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0" stop-color="#f472b6"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
  <linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#a855f7" stop-opacity="0"/><stop offset=".5" stop-color="#c084fc"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect y="64" width="{SB}" height="{H - 64}" fill="{PANEL}"/>
<rect class="scan" x="-300" width="300" height="2" fill="url(#bar)"/>''']

    # top nav
    o.append(icon("github", 28, 18, 28, TEXT))
    for i, s in enumerate(["Overview", "Projects", "Stack", "Contact"]):
        o.append(text(92 + i * 92, 37, s, 14, "#c9c9dc", 500))
    o.append(f'<rect x="520" y="16" width="280" height="32" rx="16" fill="{PANEL}" stroke="{LINE}"/>')
    o.append(text(540, 37, "Search or jump to", 12.5, MUTED))
    o.append(f'<rect class="caret" x="648" y="25" width="1.5" height="15" fill="{ACCENT}"/>')
    o.append(f'<rect x="772" y="23" width="18" height="18" rx="4" fill="none" stroke="{LINE}"/>'
             + text(781, 36, "/", 11, MUTED, anchor="middle"))
    o.append(f'<circle cx="905" cy="32" r="17" fill="url(#neon)"/>'
             f'<image href="{d["avatar"]}" x="890" y="17" width="30" height="30" clip-path="url(#ava-s)"/>')
    o.append(f'<circle cx="918" cy="44" r="5" fill="#34d399" stroke="{BG}" stroke-width="2"/>')
    o.append(f'<circle cx="958" cy="32" r="6" fill="none" stroke="#c9c9dc" stroke-width="1.6"/>'
             f'<path d="M958 20v3M958 41v3M946 32h3M967 32h3" stroke="#c9c9dc" stroke-width="1.6" stroke-linecap="round"/>')
    o.append(f'<line x1="0" y1="64" x2="{W}" y2="64" stroke="{LINE}"/>')

    # sidebar profile
    cx = SB / 2
    o.append(f'<rect class="halo" x="60" y="96" width="150" height="150" rx="30" fill="url(#neon)" filter="url(#glow)"/>')
    o.append('<rect x="60" y="96" width="150" height="150" rx="30" fill="url(#neon)"/>')
    o.append(f'<image href="{d["avatar"]}" x="64" y="100" width="142" height="142" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#ava)"/>')
    o.append(text(cx, 278, PROFILE["name"], 19, TEXT, 700, "middle"))
    o.append(text(cx, 300, f'@{LOGIN} · {PROFILE["nick"]}', 13, ACCENT, 500, "middle"))
    for i, line in enumerate(PROFILE["tagline"]):
        o.append(text(cx, 326 + i * 18, line, 12, MUTED, anchor="middle"))
    loc_w = len(PROFILE["location"]) * 7 + 16
    o.append(icon("pin", cx - loc_w / 2, 368, 12, "#f472b6")
             + text(cx - loc_w / 2 + 17, 379, PROFILE["location"], 12, "#c9c9dc"))
    o.append('<rect class="halo" x="66" y="400" width="138" height="36" rx="18" fill="#a855f7" filter="url(#glow)" opacity=".55"/>')
    o.append('<rect x="60" y="398" width="150" height="38" rx="19" fill="url(#btn)"/>')
    o.append(text(cx, 422, "FOLLOW", 12, "#fff", 700, "middle", 'letter-spacing="3"'))
    o.append(text(24, 468, "Skills", 13, "#c9c9dc", 600))
    x, y = 24, 478
    for s in PROFILE["skills"]:
        w = pill_width(s)
        if x + w > SB - 24:
            x, y = 24, y + 26
        o.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="20" rx="10" fill="{CARD}" stroke="{LINE}"/>'
                 + text(x + w / 2, y + 14, s, 10, "#c9c9dc", anchor="middle"))
        x += w + 5
    o.append(f'<line x1="24" y1="562" x2="{SB - 24}" y2="562" stroke="{LINE}"/>')
    o.append(text(28, 584, "↗  " + PROFILE["site"], 11.5, MUTED))

    # tabs
    X0, RW = 292, 688
    for i, (s, w) in enumerate([("Overview", 70), ("Repositories", 92), ("Projects", 64), ("Packages", 70)]):
        tx = X0 + sum([0, 100, 214, 300][i:i + 1])
        o.append(text(tx, 100, s, 13.5, TEXT if i == 0 else MUTED, 600 if i == 0 else 400))
        if i == 0:
            o.append(f'<rect x="{tx - 4}" y="110" width="{w + 8}" height="2.5" rx="1" fill="url(#btn)"/>')
    o.append(f'<line x1="{X0}" y1="112" x2="{X0 + RW}" y2="112" stroke="{LINE}"/>')

    # stat cards
    stats = [("Repositories", d["repos"], "repo", "#8b5cf6"), ("Stars", d["stars"], "star", "#f472b6"),
             ("Followers", d["followers"], "people", "#38bdf8"), ("Contributions", d["total"], "pulse", "#34d399")]
    for i, (label, val, ic, col) in enumerate(stats):
        x = X0 + i * 176
        o.append(f'<g class="rise" style="animation-delay:{i * 120}ms">'
                 f'<rect x="{x}" y="132" width="160" height="64" rx="14" fill="{CARD}" stroke="{LINE}"/>'
                 f'<rect x="{x + 14}" y="146" width="36" height="36" rx="10" fill="{col}"/>'
                 + icon(ic, x + 23, 155, 18, "#fff")
                 + text(x + 62, 159, label, 12, MUTED)
                 + text(x + 62, 182, short(val), 20, TEXT, 700) + '</g>')

    # code panel
    o.append(f'<rect x="{X0}" y="214" width="{RW}" height="146" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{X0 + 20 + i * 16}" cy="232" r="5" fill="{c}"/>')
    o.append(text(X0 + RW / 2, 236, "nafi.config.ts", 11.5, MUTED, anchor="middle"))
    K, S, P, C = "#c084fc", "#86efac", "#e2e8f0", "#7dd3fc"
    code = [
        [("const ", K), ("nafi", C), (" = {", P)],
        [("  role", P), (": [", P), ('"UI/UX Designer"', S), (", ", P), ('"Software Engineer"', S), ("],", P)],
        [("  study", P), (": ", P), ('"Information Systems"', S), (",", P)],
        [("  focus", P), (": [", P), ('"Design Systems"', S), (", ", P), ('"Full-Stack"', S), (", ", P), ('"System Analysis"', S), ("],", P)],
        [("  motto", P), (": ", P), ('"Design with purpose. Build with precision."', S)],
        [("};", P)],
    ]
    for i, parts in enumerate(code):
        y = 262 + i * 16
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in parts)
        o.append(text(X0 + 18, y, i + 1, 11, "#4b4b63", anchor="end", extra=f'font-family="{MONO}"'))
        o.append(f'<text x="{X0 + 30}" y="{y}" font-size="11.5" font-family="{MONO}" xml:space="preserve">{spans}</text>')
    o.append(f'<rect class="caret" x="{X0 + 46}" y="{262 + 5 * 16 - 10}" width="7" height="13" fill="{ACCENT}" opacity=".8"/>')

    # heatmap
    o.append(text(X0, 392, f'{d["total"]:,} contributions in the last year', 14, TEXT, 600))
    lx = X0 + RW - 150
    o.append(text(lx, 392, "Less", 11, MUTED))
    for i, c in enumerate(LEVELS):
        o.append(f'<rect x="{lx + 30 + i * 15}" y="382" width="11" height="11" rx="3" fill="{c}"/>')
    o.append(text(lx + 30 + 5 * 15 + 4, 392, "More", 11, MUTED))
    o.append(f'<rect x="{X0}" y="404" width="{RW}" height="118" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    weeks = d["weeks"][-53:]
    peak = max((c for w in weeks for c in w), default=0)
    pitch = (RW - 28) / 53
    cell = pitch - 2.6
    for wi, week in enumerate(weeks):
        for di, c in enumerate(week):
            o.append(f'<rect class="cell" style="animation-delay:{wi * 18}ms" x="{X0 + 14 + wi * pitch:.1f}" '
                     f'y="{418 + di * pitch:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" '
                     f'fill="{LEVELS[level(c, peak)]}"/>')
    o.append(text(X0, 560, "View Activity  →", 13, TEXT, 500)
             + f'<line x1="{X0}" y1="566" x2="{X0 + 104}" y2="566" stroke="{ACCENT}"/>')
    o.append(text(X0 + RW, 560, f'updated {d["today"]:%d %b %Y}', 11, "#5d5d78", anchor="end"))
    o.append(f'<circle cx="{X0 + RW / 2}" cy="572" r="14" fill="#5b21b6"/>'
             f'<path d="M{X0 + RW / 2 - 5} 570l5 5 5-5" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>')
    o.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{LINE}"/>')

    style = """
.cell{transform-box:fill-box;transform-origin:center;animation:pop .5s ease-out both}
.rise{animation:rise .6s ease-out both}
.caret{animation:blink 1s steps(1) infinite}
.halo{animation:pulse 3s ease-in-out infinite}
.scan{animation:scan 6s linear infinite}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{50%{opacity:.25}}
@keyframes scan{to{transform:translateX(1300px)}}"""
    return svg(W, H, "\n".join(o), style)


# ---------------------------------------------------------------- insights
def render_insights(d):
    W, H = 1000, 210
    days = [c for w in d["weeks"] for c in w]
    current, longest = streaks(days)
    o = [f'''<defs><linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter></defs>''']
    for x in (0, 510):
        o.append(f'<rect x="{x + .5}" y=".5" width="489" height="{H - 1}" rx="20" fill="{BG}" stroke="{LINE}"/>')

    # streak panel
    o.append(text(24, 36, "Contribution Streak", 15, TEXT, 600))
    cols = [(90, f'{d["total"]:,}', "Total (1 year)"), (245, str(current), "Current Streak"),
            (400, str(longest), "Longest Streak")]
    r = 40
    circ = 2 * 3.1416 * r
    frac = min(1, current / max(longest, 1))
    o.append(f'<circle cx="245" cy="112" r="{r}" fill="none" stroke="{CARD}" stroke-width="7"/>')
    o.append(f'<circle class="halo" cx="245" cy="112" r="{r}" fill="none" stroke="#a855f7" stroke-width="7" filter="url(#glow)" opacity=".5"/>')
    o.append(f'<circle class="ring" cx="245" cy="112" r="{r}" fill="none" stroke="url(#btn)" stroke-width="7" '
             f'stroke-linecap="round" stroke-dasharray="{circ * frac:.1f} {circ:.1f}" transform="rotate(-90 245 112)"/>')
    o.append(icon("flame", 237, 62, 16, "#f472b6"))
    for x, val, label in cols:
        o.append(text(x, 122, val, 26 if x != 245 else 24, TEXT, 700, "middle"))
        o.append(text(x, 182, label, 12, ACCENT if x == 245 else MUTED, 500, "middle"))
    o.append(f'<line x1="167" y1="80" x2="167" y2="170" stroke="{LINE}"/><line x1="323" y1="80" x2="323" y2="170" stroke="{LINE}"/>')

    # languages panel
    X = 534
    o.append(text(X, 36, "Most Used Languages", 15, TEXT, 600))
    langs = d["langs"][:6]
    total = sum(s for _, s, _ in langs) or 1
    bx, bw = X, 442
    o.append(f'<clipPath id="lb"><rect x="{bx}" y="56" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lb)">'
             f'<rect x="{bx}" y="56" width="{bw}" height="10" fill="{CARD}"/>')
    for name, size, color in langs:
        w = bw * size / total
        o.append(f'<rect x="{bx:.1f}" y="56" width="{w:.1f}" height="10" fill="{color}"/>')
        bx += w
    o.append("</g>")
    for i, (name, size, color) in enumerate(langs):
        x, y = X + (i % 2) * 226, 100 + (i // 2) * 34
        o.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="6" fill="{color}"/>'
                 + text(x + 20, y, name, 13, "#d6d6e7", 500)
                 + text(x + 200, y, f"{100 * size / total:.1f}%", 12.5, MUTED, anchor="end"))
    if not langs:
        o.append(text(X, 110, "No public language data yet", 13, MUTED))

    style = """
.halo{animation:pulse 3s ease-in-out infinite}
.ring{animation:draw 1.4s ease-out both}
@keyframes pulse{50%{opacity:.15}}
@keyframes draw{from{stroke-dasharray:0 999}}"""
    return svg(W, H, "\n".join(o), style)


# ---------------------------------------------------------------- project card
def render_project(p):
    W, H = 490, 170
    thumb = base64.b64encode((ROOT / "assets" / "thumbs" / p["thumb"]).read_bytes()).decode()
    o = [f'''<defs><clipPath id="t"><rect x="20" y="20" width="130" height="130" rx="14"/></clipPath>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{PANEL}" stroke="{LINE}"/>
<rect class="edge" x="24" y="0" width="{W - 48}" height="1.5" fill="url(#edge)"/>
<image href="data:image/jpeg;base64,{thumb}" x="20" y="20" width="130" height="130" preserveAspectRatio="xMidYMid slice" clip-path="url(#t)"/>
<rect x="20" y="20" width="130" height="130" rx="14" fill="none" stroke="#ffffff22"/>''']
    o.append(text(170, 50, p["name"], 18, TEXT, 700))
    o.append(f'<path d="M{W - 36} 46l10-10M{W - 34} 36h8v8" fill="none" stroke="{ACCENT}" stroke-width="1.8" stroke-linecap="round"/>')
    for i, line in enumerate(wrap(p["desc"], 44)[:3]):
        o.append(text(170, 76 + i * 18, line, 12.5, MUTED))
    x = 170
    for s in p["stack"]:
        o.append(f'<circle cx="{x + 5}" cy="136" r="5" fill="{STACK_COLORS.get(s, ACCENT)}"/>'
                 + text(x + 15, 140, s, 11.5, "#c9c9dc"))
        x += len(s) * 6.6 + 30
    style = ".edge{animation:pulse 3s ease-in-out infinite}@keyframes pulse{50%{opacity:.2}}"
    return svg(W, H, "\n".join(o), style)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required")
    data = fetch(token)
    (out / "dashboard.svg").write_text(render_dashboard(data), encoding="utf-8")
    (out / "insights.svg").write_text(render_insights(data), encoding="utf-8")
    for p in PROJECTS:
        (out / f"project-{p['slug']}.svg").write_text(render_project(p), encoding="utf-8")
    print(f"wrote {len(PROJECTS) + 2} SVGs to {out}")


if __name__ == "__main__":
    main()
