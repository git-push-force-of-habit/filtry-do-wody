# CLAUDE.md

Static marketing site for **Filtry Do Wody – Gorzów** (water-treatment business:
reverse-osmosis filters, water softeners, well-water treatment stations).
Plain HTML/CSS/vanilla JS, **no build step**, hosted on GitHub Pages.

## Structure

- `index.html` — single-page site (hero, oferta, RO, zmiękczacze, stacja, o nas, kontakt).
- `galeria.html` — **generated** gallery page. Do not hand-edit; see below.
- `css/styles.css` — all styles (shared by both pages).
- `images/` — site images; `images/galeria/<slug>/{thumb,full}/*.webp` are generated.
- `tools/build_gallery.py` + `tools/README.md` — the gallery generator and its docs.

## Gallery

The gallery is generated from originals kept **outside** the repo
(`../filtry-do-wody-email2-zdjecia/`) by `tools/build_gallery.py`
(optimizes to WebP, strips EXIF/GPS, builds `galeria.html`).
To change gallery content, edit the source photos and re-run the script — **do not
edit `galeria.html` directly**. Full guide: `tools/README.md`.

## Conventions

- Keep the nav in sync between `index.html` and `galeria.html` (same items; on
  `galeria.html` the links point to `index.html#...`). The gallery nav lives in the
  `TEMPLATE` string inside `tools/build_gallery.py`.
- Language: Polish UI copy. Local SEO leans on `<title>`, `<h1>`, meta description and
  schema.org data rather than keyword-stuffed headings.
- Preview: `python -m http.server 8123` then open http://127.0.0.1:8123/ .

## Notes

- Open follow-ups for this project are tracked in
  `../filtry-do-wody-do-zrobienia/do-zrobienia.md`.
