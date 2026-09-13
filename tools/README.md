# Gallery build tool

`build_gallery.py` turns the raw installation photos into the optimized
**Galeria** page (`galeria.html`) of the website.

It:
- reads the original JPGs from three source folders,
- writes optimized **WebP** in two sizes — `thumb` (~500 px, grid) and `full` (~1600 px, lightbox),
- fixes rotation from EXIF and **strips metadata (including GPS)**,
- regenerates `galeria.html` (tile grid + native `<dialog>` lightbox).

## Requirements

- Python 3
- Pillow: `pip install pillow`

## Folder layout

```
Projects-Code/
├─ filtry-do-wody/                     ← this repo
│  ├─ galeria.html                     ← GENERATED — do not edit by hand
│  ├─ images/galeria/<slug>/thumb|full/NNN.webp   ← GENERATED (committed)
│  └─ tools/build_gallery.py
└─ filtry-do-wody-email2-zdjecia/      ← ORIGINALS (kept out of the repo)
   ├─ FILT_RO/        *.jpg
   ├─ STACJA/         *.jpg
   └─ ZMIĘKCZACZ/     *.jpg
```

The originals live **next to** the repo (not inside it) so the repo stays small.
Section order and titles are defined in the `CATS` list near the top of the script.

## Add more photos later

1. Drop the new JPGs into the matching source folder (`FILT_RO`, `STACJA` or `ZMIĘKCZACZ`).
   Keep the `(N)` number in the filename incrementing — new photos then sort **after**
   the existing ones and keep a natural order.
2. Run:
   ```bash
   python tools/build_gallery.py
   ```
   Already-optimized images are skipped, the new ones are converted, and `galeria.html`
   is rebuilt.
3. Commit the new files under `images/galeria/…` together with `galeria.html`.

## Rebuild from scratch

If you **replace, reorder or remove** existing photos (not just append), delete the
output first so the numbering is clean, then re-run:

```bash
rm -rf images/galeria           # or just images/galeria/<slug> for one category
python tools/build_gallery.py
```

## Options

| Flag | Meaning |
|------|---------|
| `--only FILT_RO` | Convert just one source folder. |
| `--src "D:/path/to/originals"` | Use a different originals location. |
| `--no-build` | Convert images but don't rewrite `galeria.html`. |

## Tuning

Quality/size constants are at the top of the script:
`THUMB_MAX`, `FULL_MAX`, `THUMB_Q`, `FULL_Q`.

## Preview locally

```bash
python -m http.server 8123
```
then open <http://127.0.0.1:8123/galeria.html>.
(Opening `galeria.html` straight from disk can skip the CSS in some in-app previews.)
