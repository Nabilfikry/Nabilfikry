"""Render the futuristic profile SVGs (dashboard, tech-stack, insights, project cards).

Usage: GH_TOKEN=... python3 scripts/generate.py <out_dir>
Stdlib only, bare GitHub Actions runner compatible.
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

ICONS = {  # 16x16 octicon paths
    "repo": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 010-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 11-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8z",
    "star": "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z",
    "people": "M10.5 4.5a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zM8 8.5c-3.2 0-5.5 1.6-5.5 4.2V14h11v-1.3c0-2.6-2.3-4.2-5.5-4.2z",
    "pulse": "M0 8.75A.75.75 0 01.75 8h2.7l1.9-5.1a.75.75 0 011.41.02L9.6 11.6l1.3-3.1a.75.75 0 01.7-.5h3.65a.75.75 0 010 1.5h-3.15l-1.84 4.29a.75.75 0 01-1.4-.05L6.05 5.4 4.7 9.01a.75.75 0 01-.7.49H.75A.75.75 0 010 8.75z",
    "pin": "M8 0a5.5 5.5 0 00-5.5 5.5C2.5 9.6 8 16 8 16s5.5-6.4 5.5-10.5A5.5 5.5 0 008 0zm0 7.75a2.25 2.25 0 110-4.5 2.25 2.25 0 010 4.5z",
    "flame": "M8 16c3.3 0 6-2.4 6-5.6 0-3.9-3.4-5.6-3.9-9.4C8 2.3 6.8 4.6 7 7 5.9 6.4 5.4 5.2 5.4 4 3.4 5.6 2 7.9 2 10.4 2 13.6 4.7 16 8 16z",
}

QUERY = """query($login:String!){user(login:$login){
  avatarUrl(size:320) followers{totalCount} following{totalCount}
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){totalCount nodes{
    isFork stargazerCount languages(first:10){edges{size node{name color}}}}}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""

IGNORED_LANGS = {"Jupyter Notebook"}


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
            if n["name"] in IGNORED_LANGS:
                continue
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
    longest = run = 0
    for c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    tail = days[:-1] if days and not days[-1] else days
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def level(c, peak):
    return 0 if not c else min(4, 1 + int(3 * c / max(peak, 1)))


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
    W, H, SB = 1000, 580, 270
    o = [f'''<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <clipPath id="ava"><rect x="64" y="80" width="142" height="142" rx="26"/></clipPath>
  <linearGradient id="neon" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0" stop-color="#f472b6"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
  <linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#a855f7" stop-opacity="0"/><stop offset=".5" stop-color="#c084fc"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect y="48" width="{SB}" height="{H - 48}" fill="{PANEL}"/>
<rect class="scan" x="-300" width="300" height="2" fill="url(#bar)"/>''']

    # sleek window titlebar
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{24 + i * 16}" cy="24" r="5" fill="{c}"/>')
    o.append(text(W / 2, 28, "nabilfikry.dev // profile-dashboard", 12, MUTED, 500, "middle", f'font-family="{MONO}"'))
    o.append(f'<circle cx="{W - 146}" cy="24" r="4" fill="#34d399"/>')
    o.append(text(W - 134, 28, "ACTIVE • INDONESIA", 10.5, "#34d399", 600, extra=f'font-family="{MONO}" letter-spacing="1"'))
    o.append(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{LINE}"/>')

    # sidebar profile
    cx = SB / 2
    o.append(f'<rect class="halo" x="60" y="76" width="150" height="150" rx="30" fill="url(#neon)" filter="url(#glow)"/>')
    o.append('<rect x="60" y="76" width="150" height="150" rx="30" fill="url(#neon)"/>')
    o.append(f'<image href="{d["avatar"]}" x="64" y="80" width="142" height="142" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#ava)"/>')
    o.append(text(cx, 252, PROFILE["name"], 18, TEXT, 700, "middle"))
    o.append(text(cx, 273, f'@{LOGIN} · {PROFILE["nick"]}', 12.5, ACCENT, 500, "middle"))
    for i, line in enumerate(PROFILE["tagline"]):
        o.append(text(cx, 298 + i * 17, line, 11.5, MUTED, anchor="middle"))
    loc_w = len(PROFILE["location"]) * 7 + 16
    o.append(icon("pin", cx - loc_w / 2, 338, 12, "#f472b6")
             + text(cx - loc_w / 2 + 17, 349, PROFILE["location"], 11.5, "#c9c9dc"))

    # follow button
    o.append('<rect class="halo" x="66" y="370" width="138" height="34" rx="17" fill="#a855f7" filter="url(#glow)" opacity=".55"/>')
    o.append('<rect x="60" y="368" width="150" height="36" rx="18" fill="url(#btn)"/>')
    o.append(text(cx, 391, "FOLLOW", 11.5, "#fff", 700, "middle", 'letter-spacing="3"'))

    # skills
    o.append(text(24, 432, "Skills & Focus", 12, "#c9c9dc", 600))
    x, y = 24, 444
    for s in PROFILE["skills"]:
        w = pill_width(s, 9.5)
        if x + w > SB - 24:
            x, y = 24, y + 25
        o.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="20" rx="10" fill="{CARD}" stroke="{LINE}"/>'
                 + text(x + w / 2, y + 14, s, 10, "#c9c9dc", anchor="middle"))
        x += w + 5
    o.append(f'<line x1="24" y1="538" x2="{SB - 24}" y2="538" stroke="{LINE}"/>')
    o.append(text(cx, 558, "↗  " + PROFILE["site"], 11, ACCENT, 500, "middle"))

    # right main panel
    X0, RW = 292, 684
    # section header
    o.append(text(X0, 78, "METRICS & ACTIVITY", 12, ACCENT, 700, extra=f'font-family="{MONO}" letter-spacing="1.5"'))
    o.append(f'<rect x="{X0 + 170}" y="67" width="60" height="16" rx="8" fill="#a855f722" stroke="#a855f755"/>'
             + text(X0 + 200, 79, "LIVE", 9.5, ACCENT, 700, "middle", f'font-family="{MONO}"'))
    o.append(f'<line x1="{X0}" y1="88" x2="{X0 + RW}" y2="88" stroke="{LINE}"/>')

    # 4 stat cards (accurate, positive metrics!)
    stats = [
        ("Repositories", d["repos"], "repo", "#8b5cf6"),
        ("Contributions", d["total"], "pulse", "#ec4899"),
        ("Followers", d["followers"], "people", "#38bdf8"),
        ("Following", d["following"], "flame", "#34d399")
    ]
    for i, (label, val, ic, col) in enumerate(stats):
        x = X0 + i * 175
        o.append(f'<g class="rise" style="animation-delay:{i * 100}ms">'
                 f'<rect x="{x}" y="102" width="160" height="62" rx="12" fill="{CARD}" stroke="{LINE}"/>'
                 f'<rect x="{x + 12}" y="115" width="34" height="34" rx="9" fill="{col}"/>'
                 + icon(ic, x + 21, 124, 16, "#fff")
                 + text(x + 56, 126, label, 11, MUTED)
                 + text(x + 56, 148, short(val), 18, TEXT, 700) + '</g>')

    # code panel
    o.append(f'<rect x="{X0}" y="180" width="{RW}" height="142" rx="12" fill="{PANEL}" stroke="{LINE}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{X0 + 18 + i * 14}" cy="196" r="4.5" fill="{c}"/>')
    o.append(text(X0 + RW / 2, 199, "nafi.config.ts", 11, MUTED, anchor="middle", extra=f'font-family="{MONO}"'))
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
        y = 224 + i * 16
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in parts)
        o.append(text(X0 + 16, y, i + 1, 10.5, "#4b4b63", anchor="end", extra=f'font-family="{MONO}"'))
        o.append(f'<text x="{X0 + 28}" y="{y}" font-size="11" font-family="{MONO}" xml:space="preserve">{spans}</text>')
    o.append(f'<rect class="caret" x="{X0 + 44}" y="{224 + 5 * 16 - 10}" width="7" height="13" fill="{ACCENT}" opacity=".8"/>')

    # heatmap
    o.append(text(X0, 350, f'{d["total"]:,} contributions in the last year', 13.5, TEXT, 600))
    lx = X0 + RW - 140
    o.append(text(lx, 350, "Less", 10.5, MUTED))
    for i, c in enumerate(LEVELS):
        o.append(f'<rect x="{lx + 28 + i * 14}" y="341" width="10" height="10" rx="2.5" fill="{c}"/>')
    o.append(text(lx + 28 + 5 * 14 + 4, 350, "More", 10.5, MUTED))
    o.append(f'<rect x="{X0}" y="362" width="{RW}" height="114" rx="12" fill="{PANEL}" stroke="{LINE}"/>')
    weeks = d["weeks"][-53:]
    peak = max((c for w in weeks for c in w), default=0)
    pitch = (RW - 24) / 53
    cell = pitch - 2.5
    for wi, week in enumerate(weeks):
        for di, c in enumerate(week):
            o.append(f'<rect class="cell" style="animation-delay:{wi * 15}ms" x="{X0 + 12 + wi * pitch:.1f}" '
                     f'y="{374 + di * pitch:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" '
                     f'fill="{LEVELS[level(c, peak)]}"/>')

    o.append(text(X0, 508, "Activity Heatmap Overview", 12, MUTED, 500))
    o.append(text(X0 + RW, 508, f'updated {d["today"]:%d %b %Y}', 11, "#5d5d78", anchor="end"))
    o.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{LINE}"/>')

    style = """
.cell{transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.rise{animation:rise .5s ease-out both}
.caret{animation:blink 1s steps(1) infinite}
.halo{animation:pulse 3s ease-in-out infinite}
.scan{animation:scan 6s linear infinite}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{50%{opacity:.25}}
@keyframes scan{to{transform:translateX(1300px)}}"""
    return svg(W, H, "\n".join(o), style)


# ---------------------------------------------------------------- tech stack card
def render_tech_stack():
    W, H = 1000, 230
    o = [f'''<defs>
  <clipPath id="f-ts"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  <linearGradient id="edge-ts" x1="0" x2="1"><stop offset="0" stop-color="#a855f7"/><stop offset=".5" stop-color="#38bdf8"/><stop offset="1" stop-color="#34d399"/></linearGradient>
</defs>
<g clip-path="url(#f-ts)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="0" y="0" width="{W}" height="2" fill="url(#edge-ts)"/>''']

    # 4 columns
    cols = [
        {"title": "UI/UX & DESIGN", "accent": "#c084fc", "items": ["Figma", "UI/UX Design", "Wireframing", "Design Systems", "Prototyping"]},
        {"title": "FRONTEND", "accent": "#38bdf8", "items": ["Next.js", "React.js", "TypeScript", "JavaScript", "Tailwind CSS", "HTML5 & CSS3"]},
        {"title": "BACKEND & ARCH", "accent": "#f472b6", "items": ["Laravel", "PHP", "Express.js", "Python", "Go", "System Analysis & UML"]},
        {"title": "DATABASE & DEVOPS", "accent": "#34d399", "items": ["PostgreSQL", "MySQL", "Docker", "Git & GitHub", "Linux CLI"]},
    ]

    cw = 226
    gap = 14
    start_x = 22

    for ci, col in enumerate(cols):
        cx = start_x + ci * (cw + gap)
        # card background
        o.append(f'<rect x="{cx}" y="20" width="{cw}" height="{H - 40}" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
        # card top glow line
        o.append(f'<rect x="{cx + 16}" y="20" width="{cw - 32}" height="1.5" fill="{col["accent"]}"/>')
        # card title
        o.append(f'<circle cx="{cx + 18}" cy="42" r="4" fill="{col["accent"]}"/>')
        o.append(text(cx + 28, 46, col["title"], 11, TEXT, 700, extra=f'font-family="{MONO}" letter-spacing="1"'))
        o.append(f'<line x1="{cx + 14}" y1="58" x2="{cx + cw - 14}" y2="58" stroke="{LINE}"/>')

        # items as clean badges
        bx, by = cx + 14, 72
        for it in col["items"]:
            tw = len(it) * 6.2 + 16
            if bx + tw > cx + cw - 14:
                bx = cx + 14
                by += 26
            o.append(f'<rect x="{bx}" y="{by}" width="{tw:.0f}" height="20" rx="10" fill="{CARD}" stroke="{LINE}"/>'
                     + text(bx + tw / 2, by + 13.5, it, 9.5, "#d6d6e7", anchor="middle"))
            bx += tw + 6

    o.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{LINE}"/>')
    return svg(W, H, "\n".join(o))


# ---------------------------------------------------------------- insights
def render_insights(d):
    W, H = 1000, 200
    days = [c for w in d["weeks"] for c in w]
    current, longest = streaks(days)
    o = [f'''<defs><linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter></defs>''']
    for x in (0, 510):
        o.append(f'<rect x="{x + .5}" y=".5" width="489" height="{H - 1}" rx="18" fill="{BG}" stroke="{LINE}"/>')

    # streak panel
    o.append(text(24, 34, "Contribution Streak", 14.5, TEXT, 600))
    cols = [(90, f'{d["total"]:,}', "Total (1 year)"), (245, str(current), "Current Streak"),
            (400, str(longest), "Longest Streak")]
    r = 38
    circ = 2 * 3.1416 * r
    frac = max(0.12, min(1.0, current / max(longest, 1)))
    o.append(f'<circle cx="245" cy="108" r="{r}" fill="none" stroke="{CARD}" stroke-width="7"/>')
    o.append(f'<circle class="halo" cx="245" cy="108" r="{r}" fill="none" stroke="#a855f7" stroke-width="7" filter="url(#glow)" opacity=".4"/>')
    o.append(f'<circle class="ring" cx="245" cy="108" r="{r}" fill="none" stroke="url(#btn)" stroke-width="7" '
             f'stroke-linecap="round" stroke-dasharray="{circ * frac:.1f} {circ:.1f}" transform="rotate(-90 245 108)"/>')
    o.append(icon("flame", 237, 60, 16, "#f472b6"))
    for x, val, label in cols:
        o.append(text(x, 118, val, 24 if x != 245 else 22, TEXT, 700, "middle"))
        o.append(text(x, 172, label, 11.5, ACCENT if x == 245 else MUTED, 500, "middle"))
    o.append(f'<line x1="167" y1="74" x2="167" y2="162" stroke="{LINE}"/><line x1="323" y1="74" x2="323" y2="162" stroke="{LINE}"/>')

    # languages panel (filtered, no bloated notebooks!)
    X = 534
    o.append(text(X, 34, "Most Used Languages", 14.5, TEXT, 600))
    langs = [l for l in d["langs"] if l[0] not in IGNORED_LANGS][:6]
    total = sum(s for _, s, _ in langs) or 1
    bx, bw = X, 442
    o.append(f'<clipPath id="lb"><rect x="{bx}" y="52" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lb)">'
             f'<rect x="{bx}" y="52" width="{bw}" height="10" fill="{CARD}"/>')
    for name, size, color in langs:
        w = bw * size / total
        o.append(f'<rect x="{bx:.1f}" y="52" width="{w:.1f}" height="10" fill="{color}"/>')
        bx += w
    o.append("</g>")
    for i, (name, size, color) in enumerate(langs):
        x, y = X + (i % 2) * 226, 94 + (i // 2) * 32
        o.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="5.5" fill="{color}"/>'
                 + text(x + 18, y, name, 12.5, "#d6d6e7", 500)
                 + text(x + 200, y, f"{100 * size / total:.1f}%", 12, MUTED, anchor="end"))
    if not langs:
        o.append(text(X, 105, "No public language data yet", 12.5, MUTED))

    style = """
.halo{animation:pulse 3s ease-in-out infinite}
.ring{animation:draw 1.2s ease-out both}
@keyframes pulse{50%{opacity:.15}}
@keyframes draw{from{stroke-dasharray:0 999}}"""
    return svg(W, H, "\n".join(o), style)


# ---------------------------------------------------------------- project card
def render_project(p):
    W, H = 490, 160
    thumb = base64.b64encode((ROOT / "assets" / "thumbs" / p["thumb"]).read_bytes()).decode()
    o = [f'''<defs><clipPath id="t"><rect x="18" y="18" width="124" height="124" rx="12"/></clipPath>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#a855f7"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{PANEL}" stroke="{LINE}"/>
<rect class="edge" x="20" y="0" width="{W - 40}" height="1.5" fill="url(#edge)"/>
<image href="data:image/jpeg;base64,{thumb}" x="18" y="18" width="124" height="124" preserveAspectRatio="xMidYMid slice" clip-path="url(#t)"/>
<rect x="18" y="18" width="124" height="124" rx="12" fill="none" stroke="#ffffff1a"/>''']
    o.append(text(160, 46, p["name"], 17, TEXT, 700))
    o.append(f'<path d="M{W - 32} 42l8-8M{W - 30} 34h6v6" fill="none" stroke="{ACCENT}" stroke-width="1.8" stroke-linecap="round"/>')
    for i, line in enumerate(wrap(p["desc"], 42)[:3]):
        o.append(text(160, 70 + i * 17, line, 12, MUTED))
    x = 160
    for s in p["stack"]:
        o.append(f'<circle cx="{x + 4}" cy="130" r="4.5" fill="{STACK_COLORS.get(s, ACCENT)}"/>'
                 + text(x + 14, 134, s, 11, "#c9c9dc"))
        x += len(s) * 6.4 + 28
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
    (out / "tech-stack.svg").write_text(render_tech_stack(), encoding="utf-8")
    (out / "insights.svg").write_text(render_insights(data), encoding="utf-8")
    for p in PROJECTS:
        (out / f"project-{p['slug']}.svg").write_text(render_project(p), encoding="utf-8")
    print(f"wrote {len(PROJECTS) + 3} SVGs to {out}")


if __name__ == "__main__":
    main()
