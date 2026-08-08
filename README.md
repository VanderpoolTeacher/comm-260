# COMM 260 — Introduction to Digital Media Production

The **student-facing** course site. Live at
**https://vanderpoolteacher.github.io/comm-260/**

Generated from the course design folder by [`build.py`](build.py). Nothing in
`docs/` is written by hand — edit the markdown, run the build, commit the result.

---

## What is published, and what is not

The site carries only what a student should be able to read. The split follows
each file's own opening line.

**Published — 50 documents + 5 reference documents**

| Source | What it is |
|---|---|
| `02_source/week-NN/01-lesson.md` | Read before the session |
| `02_source/week-NN/04-lab.md` | What happens in the room |
| `02_source/week-NN/05-assignment.md` · `05-checkpoint.md` | What is handed in |
| `02_source/week-NN/05a-knowledge-check.md` | Week 10 review sheet |
| `02_source/week-NN/student-files/` | Sheets students fill in, and starter files |
| `01_design/glossary.md` | Every term, by module |
| `01_design/rubrics/competency-rubric.md` | The master rubric |
| `01_design/assessments/personal-brand-student-brief.md` | Final project brief |
| `01_design/assessments/personal-brand-rubric.md` | Final project rubric |
| `01_design/assessments/personal-brand-rubric-presentation.md` | Presentation rubric |

**Withheld — never copied into `docs/`**

| Source | Why |
|---|---|
| `week-NN/00-week-outline.md` | Instructor planning, links to internal design docs |
| `week-NN/02-slides.md` | Slide build spec, carries `SAY` and `WATCH FOR` cues |
| `week-NN/02a-interactive-*.md` | Build specs for interactives, not the interactives |
| `week-NN/03-demo.md` | Instructor run-through |
| `week-NN/06-instructor-guide.md` | **Holds the week 10 and week 15 question banks** |
| `01_design/course-specification.md`, `course-outline.md`, `assessment-evidence.md`, `module-plans/` | Design documents |
| `01_design/assessments/personal-brand-instructor-guide.md`, `summative-assessment-personal-brand.md` | Instructor and design documents |

### Links are resolved, not copied

Every markdown link is checked against the published set:

- a link to a **published** file is rewritten to its page in the site
- a link to a **withheld** file is unwrapped to plain text, so it neither dangles
  nor names a file students should not have
- internal `**Tracking card:**` lines are dropped

The build reports both counts. At the last run: **141 links kept, 21 unwrapped.**

---

## Build

```sh
python3 build.py
```

Requires [pandoc](https://pandoc.org). Reads from

```
~/Library/CloudStorage/GoogleDrive-…/DSGN Program/program-graphic-design/03_courses/COMM-260
```

Override with `COMM260_COURSE=/path/to/COMM-260 python3 build.py`.

The design folder is the source of truth. The markdown is **not** duplicated
into this repo — a copy that drifts is a fork, not a revision.

---

## Checks worth re-running after a build

```sh
# no withheld material reached the output
grep -ril "instructor-facing\|trello.com\|question bank\|02a-interactive" docs/

# no markdown links survived
grep -rho 'href="[^"]*\.md[^"]*"' docs/ | wc -l

# every internal link resolves
python3 - <<'EOF'
import pathlib, re, urllib.parse
bad = 0
for p in pathlib.Path('docs').rglob('*.html'):
    for h in re.findall(r'href="([^"]+)"', p.read_text()):
        if h.startswith(('http', 'mailto:', '#')): continue
        t = urllib.parse.urldefrag(h)[0]
        if t and not (p.parent / t).resolve().exists():
            print('DEAD', p, h); bad += 1
print('dead:', bad)
EOF
```
