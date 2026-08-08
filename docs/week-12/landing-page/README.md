# Landing page starter — how to use it

COMM 260 · Final Project

This is a working scaffold, not a design. It has the structure your landing page needs and nothing else. Making it yours is the assignment.

---

## What's in here

```
landing-page/
├── index.html     the structure — sections, players, comments telling you what to change
├── style.css      your style guide, as code — every value is a placeholder
├── images/        your 12 photographs, plus your logo and video poster
├── audio/         your MP3
└── video/         your MP4
```

Create `images/`, `audio/`, and `video/` yourself — they aren't in the starter because they'd be empty.

---

## Do this first

1. **Open `style.css`.** Every line marked `REPLACE` is a placeholder. Put your own hex codes and typefaces in. Do this before anything else — it is the fastest way to stop the page looking like everyone else's.
2. **Open `index.html`.** Replace your name, your `I make ___ for ___` line, and the page title.
3. **Add your media** as you finish each phase. The page fills up as the project goes.

If a value in `style.css` still says `REPLACE` when you hand this in, you have not applied your brand — and that is visible immediately.

---

## Choosing linear or non-linear

The starter is **linear** by default: a visitor scrolls through your work in the order you set.

To make it **non-linear**, uncomment the `<nav class="jump">` block near the top of `index.html`. A visitor can then jump straight to any section.

Neither is better. You have to choose one and write down what your choice makes possible *and what it costs you*. See the brief.

---

## Naming your files

```
comm260-lastname-photo-01.jpg
comm260-lastname-audio.mp3
comm260-lastname-video.mp4
comm260-lastname-poster.jpg
```

Lowercase, hyphens, no spaces. Spaces in filenames break on web servers even when they work on your laptop.

---

## Export settings

| File | Format | Notes |
|---|---|---|
| Photographs | JPEG, longest edge 2400 px, sRGB | Under 500 KB each or the page loads slowly |
| Audio | MP3 320 kbps | Keep your WAV — you hand that in separately |
| Video | H.264 MP4, 1080p, 24 fps | Under 100 MB — GitHub rejects files over 100 MB |
| Poster | JPEG, 1920 × 1080 | The still shown before someone presses play. Choose it. |

---

## Publishing to GitHub Pages

1. Create a free GitHub account.
2. Create a **public** repository named `lastname-presence`.
3. Upload the contents of this folder — `index.html` must sit at the top level, not inside another folder.
4. Settings → Pages → Source: deploy from branch `main`, folder `/ (root)`.
5. Wait about a minute. Your page is at `lastname.github.io/lastname-presence`.
6. **Open that URL yourself before you submit it.** If your images are missing there but fine on your laptop, your file paths or capitalisation are wrong — servers care about capital letters, your laptop does not.

---

## Two things that are not graded

**Your code.** No learning outcome in this course is about web development. Nobody is reading your HTML.

**Browser compatibility.** If it works in one current browser, that is enough.

## One thing that is

Whether the page holds your photography, audio, and video together so that **removing one would break it**. That is the removal test, and it is what the landing page is worth 20% for.
