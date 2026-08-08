#!/usr/bin/env python3
"""
Build the COMM 260 student site.

Reads student-facing markdown from the COMM 260 design folder and writes a
static HTML site into docs/, which GitHub Pages serves.

The design folder is the source of truth. Nothing in docs/ is edited by hand;
run this again after the markdown changes.

PUBLISHED
  02_source/week-NN/  01-lesson · 04-lab · 05-assignment · 05-checkpoint
                      · 05a-knowledge-check · student-files/
  01_design/          glossary · rubrics/competency-rubric
                      · assessments/personal-brand-{student-brief,rubric,rubric-presentation}

WITHHELD
  02_source/week-NN/  00-week-outline · 02-slides · 02a-interactive-* · 03-demo
                      · 06-instructor-guide
  01_design/          course-specification · course-outline · assessment-evidence
                      · module-plans/ · assessments/…-instructor-guide
                      · assessments/summative-assessment-…

Every link is resolved against the published set. A link to a withheld file is
unwrapped to plain text rather than left dangling, and internal tracking links
are dropped, so nothing in docs/ points at material students should not have.
"""

import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
DOCS = HERE / "docs"

DEFAULT_COURSE_DIR = (
    pathlib.Path.home()
    / "Library/CloudStorage/GoogleDrive-mvanderpool.edu@gmail.com/My Drive"
    / "_0 2026/DSGN Program/program-graphic-design/03_courses/COMM-260"
)
COURSE_DIR = pathlib.Path(os.environ.get("COMM260_COURSE", DEFAULT_COURSE_DIR)).resolve()
SRC = COURSE_DIR / "02_source"
DESIGN = COURSE_DIR / "01_design"

COURSE = "COMM 260"
COURSE_LONG = "Introduction to Digital Media Production"

WEEK_DOCS = [
    ("01-lesson.md", "lesson", "Lesson"),
    ("04-lab.md", "lab", "Lab"),
    ("05-assignment.md", "assignment", "Assignment"),
    ("05-checkpoint.md", "checkpoint", "Checkpoint"),
    ("05a-knowledge-check.md", "knowledge-check", "Knowledge check"),
]

REFERENCE = [
    ("glossary.md", "reference/glossary.html", "Glossary",
     "Every term the course uses, by module."),
    ("rubrics/competency-rubric.md", "reference/competency-rubric.html", "Competency rubric",
     "The master rubric behind every assignment."),
    ("assessments/personal-brand-student-brief.md", "reference/final-project-brief.html",
     "Final project brief", "What the final project is and what it must contain."),
    ("assessments/personal-brand-rubric.md", "reference/final-project-rubric.html",
     "Final project rubric", "How the final project is marked."),
    ("assessments/personal-brand-rubric-presentation.md",
     "reference/final-project-presentation-rubric.html",
     "Presentation rubric", "How the final presentation is marked."),
]

LINK_RE = re.compile(r"\[([^\]\[]*)\]\(([^)\s]+)\)")
TRACKING_RE = re.compile(r"^\*\*Tracking card:\*\*.*$", re.M)
DROP_HOSTS = ("trello.com",)


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def first_h1(text):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def collect():
    """Map every publishable source file to its output path in docs/."""
    pub = {}
    weeks = []

    for wdir in sorted(SRC.glob("week-*")):
        wnum = int(wdir.name.split("-")[1])
        items = []
        for fname, slug, label in WEEK_DOCS:
            f = wdir / fname
            if f.exists():
                out = f"{wdir.name}/{slug}.html"
                pub[f.resolve()] = out
                items.append((f, out, label, None))
        sfdir = wdir / "student-files"
        if sfdir.is_dir():
            for f in sorted(sfdir.glob("*.md")):
                out = f"{wdir.name}/{slugify(f.stem)}.html"
                pub[f.resolve()] = out
                items.append((f, out, "Sheet", None))
            for sub in sorted(p for p in sfdir.iterdir() if p.is_dir()):
                out = f"{wdir.name}/{sub.name}/index.html"
                pub[sub.resolve()] = out
                meta = {}
                mf = sub / "meta.json"
                if mf.exists():
                    meta = json.loads(mf.read_text())
                # a built artifact stands in for its withheld build spec, so the
                # lesson's existing link resolves to the thing instead of the spec
                if meta.get("spec"):
                    pub[(wdir / meta["spec"]).resolve()] = out
                items.append((sub, out, meta.get("label", "Starter files"),
                              meta.get("title", sub.name.replace("-", " "))))
        weeks.append((wdir, wnum, items))

    for rel, out, label, blurb in REFERENCE:
        f = DESIGN / rel
        if f.exists():
            pub[f.resolve()] = out

    return pub, weeks


def rewrite(text, src_file, out_path, pub):
    """Resolve links against the published set; unwrap anything withheld."""
    text = TRACKING_RE.sub("", text)
    srcdir = src_file.parent if src_file.is_file() else src_file
    outdir = pathlib.PurePosixPath(out_path).parent
    stats = {"kept": 0, "unwrapped": 0}

    def sub(m):
        label, target = m.group(1), m.group(2)
        if target.startswith("#"):
            return m.group(0)
        if target.startswith(("http://", "https://", "mailto:")):
            if any(h in target for h in DROP_HOSTS):
                stats["unwrapped"] += 1
                return label
            stats["kept"] += 1
            return m.group(0)
        try:
            resolved = (srcdir / target).resolve()
        except OSError:
            stats["unwrapped"] += 1
            return label
        dest = pub.get(resolved)
        if dest is None:
            stats["unwrapped"] += 1
            return label
        rel = os.path.relpath(dest, str(outdir)) if str(outdir) != "." else dest
        stats["kept"] += 1
        return f"[{label}]({rel})"

    return LINK_RE.sub(sub, text), stats


def md_to_html(text):
    out = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--no-highlight"],
        input=text, capture_output=True, text=True, check=True,
    )
    # let wide tables scroll inside their own container
    return out.stdout.replace("<table>", '<div class="tbl"><table>').replace(
        "</table>", "</table></div>"
    )


def page(title, crumb, body, depth):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} &middot; {COURSE}</title>
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="bar">
  <a class="home" href="{up}index.html"><b>{COURSE}</b> <span>{COURSE_LONG}</span></a>
</header>
<main>
{crumb}
{body}
</main>
<footer>
  <p>{COURSE} &middot; {COURSE_LONG}</p>
  <p class="fine">Student materials, generated from course source.</p>
</footer>
</body>
</html>
"""


def write(out_path, text):
    p = DOCS / out_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def main():
    if not SRC.is_dir():
        sys.exit(f"source not found: {SRC}\nSet COMM260_COURSE to override.")

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    (DOCS / ".nojekyll").write_text("")
    (DOCS / "style.css").write_text(STYLE)

    pub, weeks = collect()
    kept = unwrapped = pages = 0
    index_rows = []

    for wdir, wnum, items in weeks:
        lesson = wdir / "01-lesson.md"
        wtitle = f"Week {wnum}"
        if lesson.exists():
            h1 = first_h1(lesson.read_text()) or ""
            h1 = re.sub(r"\s*—\s*Lesson\s*$", "", h1)
            h1 = re.sub(r"^Week\s+\d+\s*·\s*", "", h1)
            if h1:
                wtitle = h1

        cards = []
        for f, out, label, override in items:
            if f.is_dir():
                shutil.copytree(f, DOCS / pathlib.PurePosixPath(out).parent,
                                dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("meta.json"))
                cards.append((os.path.relpath(out, wdir.name), label, override))
                continue
            text = f.read_text()
            title = override or first_h1(text) or label
            text, st = rewrite(text, f, out, pub)
            kept += st["kept"]; unwrapped += st["unwrapped"]
            crumb = (
                f'<nav class="crumb"><a href="../index.html">All weeks</a>'
                f'<span>/</span><a href="index.html">Week {wnum}</a>'
                f'<span>/</span><em>{html.escape(label)}</em></nav>'
            )
            write(out, page(title, crumb, f'<article class="doc">{md_to_html(text)}</article>', 1))
            cards.append((os.path.relpath(out, wdir.name), label, title))
            pages += 1

        lis = "\n".join(
            f'<li><a href="{h}"><span class="kind">{html.escape(k)}</span>'
            f'<span class="t">{html.escape(t)}</span></a></li>' for h, k, t in cards
        )
        crumb = (f'<nav class="crumb"><a href="../index.html">All weeks</a>'
                 f'<span>/</span><em>Week {wnum}</em></nav>')
        body = (f'<h1>Week {wnum}<span class="sub">{html.escape(wtitle)}</span></h1>'
                f'<ul class="cards">{lis}</ul>')
        write(f"{wdir.name}/index.html", page(f"Week {wnum}", crumb, body, 1))
        index_rows.append((wdir.name, wnum, wtitle, len(cards)))
        pages += 1

    # reference documents
    ref_rows = []
    for rel, out, label, blurb in REFERENCE:
        f = DESIGN / rel
        if not f.exists():
            print(f"  ! missing reference doc: {rel}")
            continue
        text = f.read_text()
        title = first_h1(text) or label
        text, st = rewrite(text, f, out, pub)
        kept += st["kept"]; unwrapped += st["unwrapped"]
        crumb = ('<nav class="crumb"><a href="../index.html">Course home</a>'
                 f'<span>/</span><em>{html.escape(label)}</em></nav>')
        write(out, page(title, crumb, f'<article class="doc">{md_to_html(text)}</article>', 1))
        ref_rows.append((out, label, blurb))
        pages += 1

    wk = "\n".join(
        f'<li><a href="{s}/index.html"><span class="wk">{n:02d}</span>'
        f'<span class="t">{html.escape(t)}</span>'
        f'<span class="c">{c} item{"s" if c != 1 else ""}</span></a></li>'
        for s, n, t, c in index_rows
    )
    rf = "\n".join(
        f'<li><a href="{o}"><span class="t">{html.escape(l)}</span>'
        f'<span class="c">{html.escape(b)}</span></a></li>' for o, l, b in ref_rows
    )
    body = (
        f'<h1>{COURSE}<span class="sub">{COURSE_LONG}</span></h1>'
        f'<p class="lede">Everything to read, do and hand in — week by week.</p>'
        f'<h2 class="sec">Reference</h2><ul class="cards ref">{rf}</ul>'
        f'<h2 class="sec">The fifteen weeks</h2><ul class="weeks">{wk}</ul>'
    )
    write("index.html", page(COURSE, "", body, 0))
    pages += 1

    print(f"pages          : {pages}")
    print(f"weeks          : {len(index_rows)}")
    print(f"reference docs : {len(ref_rows)}")
    print(f"links kept     : {kept}")
    print(f"links unwrapped: {unwrapped}  (targets not published)")
    print(f"source         : {COURSE_DIR}")


STYLE = """
:root{
  --ground:#E9E6DE; --panel:#F2F0EA; --ink:#1A1D1F;
  --soft:rgba(26,29,31,.66); --faint:rgba(26,29,31,.45);
  --rule:rgba(26,29,31,.16); --accent:#2F5D50; --alert:#7A3B52;
}
@media (prefers-color-scheme:dark){
  :root{
    --ground:#15191A; --panel:#1D2223; --ink:#E9E6DE;
    --soft:rgba(233,230,222,.66); --faint:rgba(233,230,222,.42);
    --rule:rgba(233,230,222,.16); --accent:#7FB3A0; --alert:#C98BA0;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.62 'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--accent)}
a:focus-visible{outline:3px solid var(--accent);outline-offset:2px}

.bar{border-bottom:1px solid var(--rule);background:var(--panel)}
.home{display:block;max-width:52rem;margin:0 auto;padding:.9rem clamp(1rem,4vw,2rem);
  text-decoration:none;color:var(--ink)}
.home span{color:var(--faint);margin-left:.5rem;font-size:.9rem}

main{max-width:52rem;margin:0 auto;padding:clamp(1.4rem,5vw,3rem) clamp(1rem,4vw,2rem)}

.crumb{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;
  font-size:.82rem;color:var(--faint);margin-bottom:1.6rem}
.crumb a{color:var(--soft)}
.crumb em{font-style:normal;color:var(--ink)}

h1{font-size:clamp(1.8rem,5.5vw,2.7rem);line-height:1.12;letter-spacing:-.022em;
  margin:0 0 1.3rem;text-wrap:balance}
h1 .sub{display:block;font-size:.46em;font-weight:400;color:var(--soft);
  margin-top:.5rem;letter-spacing:0}
.lede{font-size:1.06rem;color:var(--soft);max-width:44ch;margin:0 0 2.4rem}
h2.sec{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--faint);font-weight:400;margin:2.4rem 0 .8rem}
h2.sec:first-of-type{margin-top:0}

ul.weeks,ul.cards{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.5rem}
ul.weeks a,ul.cards a{display:flex;gap:1rem;align-items:baseline;padding:.9rem 1.1rem;
  background:var(--panel);border:1px solid var(--rule);text-decoration:none;color:var(--ink)}
ul.weeks a:hover,ul.cards a:hover{border-color:var(--accent)}
.wk{font-variant-numeric:tabular-nums;color:var(--accent);font-weight:700;min-width:2ch}
.t{flex:1;min-width:0}
.c{color:var(--faint);font-size:.85rem}
ul.weeks .c{white-space:nowrap}
.kind{color:var(--accent);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;min-width:9ch}

.doc{font-size:1.02rem}
.doc h1{font-size:clamp(1.7rem,5vw,2.4rem)}
.doc h2{font-size:1.35rem;line-height:1.25;margin:2.4rem 0 .8rem;letter-spacing:-.012em}
.doc h3{font-size:1.1rem;margin:1.8rem 0 .6rem}
.doc p,.doc li{max-width:64ch}
.doc ul,.doc ol{padding-left:1.3rem}
.doc li{margin:.35rem 0}
.doc hr{border:0;border-top:1px solid var(--rule);margin:2.2rem 0}
.doc blockquote{margin:1.4rem 0;padding:.2rem 0 .2rem 1.1rem;
  border-left:3px solid var(--accent);color:var(--soft)}
.doc code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em;
  background:var(--panel);padding:.1em .35em;border:1px solid var(--rule)}
.doc pre{background:var(--panel);border:1px solid var(--rule);padding:1rem;overflow-x:auto}
.doc pre code{background:none;border:0;padding:0}
.tbl{overflow-x:auto;margin:1.4rem 0}
.doc table{border-collapse:collapse;width:100%;min-width:28rem;font-size:.94rem}
.doc th,.doc td{text-align:left;padding:.55em .7em;border-bottom:1px solid var(--rule);
  vertical-align:top}
.doc th{font-size:.8rem;letter-spacing:.05em;text-transform:uppercase;
  color:var(--faint);font-weight:400}
.doc img{max-width:100%;height:auto}

footer{border-top:1px solid var(--rule);margin-top:4rem;padding:1.6rem clamp(1rem,4vw,2rem) 3rem}
footer p{max-width:52rem;margin:0 auto;color:var(--faint);font-size:.85rem}
footer .fine{margin-top:.3rem}

@media (max-width:34rem){
  ul.cards a{flex-direction:column;gap:.25rem}
  .kind{min-width:0}
}
"""

if __name__ == "__main__":
    main()
