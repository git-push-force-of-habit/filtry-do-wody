# -*- coding: utf-8 -*-
"""
Gallery builder for the "Filtry Do Wody - Gorzów" website.

What it does:
  * reads source photos from three folders (RO / water-treatment station / softener),
  * writes optimized WebP in two sizes:
      - thumbnail  (~500 px, for the grid),
      - full       (~1600 px, for the lightbox),
  * fixes rotation from EXIF and strips metadata (incl. GPS),
  * generates `galeria.html` (grid of tiles + native <dialog> lightbox).

Usage (run from anywhere):
    python tools/build_gallery.py                 # convert all categories + build page
    python tools/build_gallery.py --only STACJA   # convert one category only
    python tools/build_gallery.py --no-build      # convert, but don't rewrite galeria.html
    python tools/build_gallery.py --src "D:/path/to/originals"   # custom source folder

Conversion is idempotent: existing output files are skipped, so re-running is cheap.
The page is rebuilt from whatever currently exists under images/galeria/.
See tools/README.md for the full "how to add more photos" guide.

Requires: Pillow  (pip install pillow)
"""
import os, re, sys, glob, argparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image, ImageOps

# --- Paths (relative to this script, so the repo can live anywhere) ----------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                          # repo root (script is in tools/)
DST  = os.path.join(ROOT, "images", "galeria")        # optimized output (committed)
PAGE = os.path.join(ROOT, "galeria.html")             # generated page
DEFAULT_SRC = os.path.join(os.path.dirname(ROOT),     # originals live NEXT TO the repo
                           "filtry-do-wody-email2-zdjecia")

# (source subfolder, url slug, section title, short label for the jump nav) -- section order
CATS = [
    ("FILT_RO",    "ro",        "Filtry odwróconej osmozy (RO)",      "Filtry RO"),
    ("ZMIĘKCZACZ", "zmiekczacz","Zmiękczacze wody użytkowej",         "Zmiękczacze"),
    ("STACJA",     "stacja",    "Stacje uzdatniania wody studziennej","Stacje uzdatniania wody"),
]

THUMB_MAX = 500   # px, longest side of grid thumbnail
FULL_MAX  = 1600  # px, longest side of lightbox image
THUMB_Q   = 72    # WebP quality for thumbnails
FULL_Q    = 80    # WebP quality for full images


def natural_key(path):
    """Natural sort: use the number in '(12)' if present, else the first number,
    else the name. Keeps 1,2,...,10 order instead of 1,10,100."""
    name = os.path.basename(path)
    m = re.search(r"\((\d+)\)", name)
    if m:
        return (0, int(m.group(1)), name.lower())
    m = re.search(r"(\d+)", name)
    if m:
        return (0, int(m.group(1)), name.lower())
    return (1, 0, name.lower())


def convert_category(src_root, src_folder, slug):
    src_dir = os.path.join(src_root, src_folder)
    files = sorted(glob.glob(os.path.join(src_dir, "*.jpg")), key=natural_key) \
          + sorted(glob.glob(os.path.join(src_dir, "*.jpeg")), key=natural_key)
    files = sorted(files, key=natural_key)
    if not files:
        print(f"[{slug}] no source files in {src_dir}")
        return 0
    thumb_dir = os.path.join(DST, slug, "thumb")
    full_dir  = os.path.join(DST, slug, "full")
    os.makedirs(thumb_dir, exist_ok=True)
    os.makedirs(full_dir, exist_ok=True)
    done = 0
    for i, f in enumerate(files, start=1):
        stem = f"{i:03d}"
        tp = os.path.join(thumb_dir, stem + ".webp")
        fp = os.path.join(full_dir,  stem + ".webp")
        if os.path.exists(tp) and os.path.exists(fp):
            continue
        try:
            im = Image.open(f)
            im = ImageOps.exif_transpose(im)   # apply EXIF rotation
            im = im.convert("RGB")
        except Exception as e:
            print(f"  ERR reading {os.path.basename(f)}: {e}")
            continue
        full = im.copy(); full.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        full.save(fp, "WEBP", quality=FULL_Q, method=6)   # metadata is NOT copied
        th = im.copy(); th.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        th.save(tp, "WEBP", quality=THUMB_Q, method=6)
        done += 1
        if done % 20 == 0:
            print(f"  [{slug}] {done} converted...")
    total = len(glob.glob(os.path.join(thumb_dir, "*.webp")))
    print(f"[{slug}] done: {done} new, {total} total in folder")
    return total


def build_groups_html():
    groups = []
    chips = []
    total_all = 0
    for src_folder, slug, title, short in CATS:
        thumb_dir = os.path.join(DST, slug, "thumb")
        thumbs = sorted(glob.glob(os.path.join(thumb_dir, "*.webp")))
        if not thumbs:
            continue
        chips.append(f'        <a href="#galeria-{slug}">{short}</a>')
        items = []
        for t in thumbs:
            name = os.path.basename(t)
            n = os.path.splitext(name)[0]
            thumb_rel = f"images/galeria/{slug}/thumb/{name}"
            full_rel  = f"images/galeria/{slug}/full/{name}"
            alt = f"{title} – realizacja {int(n)}"
            items.append(
                f'          <button class="gallery-item" type="button" data-full="{full_rel}" aria-label="Powiększ zdjęcie: {alt}">\n'
                f'            <img src="{thumb_rel}" alt="{alt}" loading="lazy" decoding="async">\n'
                f'          </button>'
            )
        total_all += len(thumbs)
        group = (
            f'      <section class="gallery-group" id="galeria-{slug}" aria-label="{title}">\n'
            f'        <h3 class="gallery-group-title">{title}</h3>\n'
            f'        <div class="gallery-grid">\n'
            + "\n".join(items) +
            f'\n        </div>\n'
            f'      </section>'
        )
        groups.append(group)
    jumpnav = ""
    if len(chips) > 1:
        jumpnav = ('      <nav class="gallery-jump" aria-label="Przejdź do sekcji">\n'
                   + "\n".join(chips) + "\n      </nav>")
    return jumpnav, "\n\n".join(groups), total_all


TEMPLATE = r"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Galeria realizacji – Filtry Do Wody Gorzów</title>
  <meta name="description" content="Galeria realizacji Filtry Do Wody – Gorzów: montaże filtrów odwróconej osmozy (RO), stacji uzdatniania wody studziennej i zmiękczaczy wody. Gorzów Wielkopolski i województwo lubuskie.">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Filtry Do Wody – Gorzów">

  <meta property="og:title" content="Galeria realizacji – Filtry Do Wody Gorzów">
  <meta property="og:description" content="Montaże filtrów RO, stacji uzdatniania wody studziennej i zmiękczaczy wody w Gorzowie Wielkopolskim i woj. lubuskim.">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pl_PL">

  <link rel="canonical" href="https://git-push-force-of-habit.github.io/filtry-do-wody/galeria.html">
  <link rel="icon" type="image/svg+xml" href="images/logo.svg">
  <link rel="icon" type="image/png" href="images/logo.png">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>

  <!-- ===================== HEADER ===================== -->
  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo-link" aria-label="Filtry Do Wody Gorzów – strona główna">
        <img src="images/logo.svg" alt="Logo Filtry Do Wody Gorzów" width="48" height="48">
        <div class="logo-text">
          <strong>Filtry Do Wody – Gorzów</strong>
          <span>Profesjonalne systemy uzdatniania wody</span>
        </div>
      </a>

      <button class="hamburger" aria-label="Otwórz menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>

      <nav class="main-nav" aria-label="Nawigacja główna">
        <ul>
          <li><a href="index.html#oferta">Oferta</a></li>
          <li><a href="index.html#ro">Filtry RO</a></li>
          <li><a href="index.html#zmiekczacz">Zmiękczacze</a></li>
          <li><a href="index.html#stacja">Stacje uzdatniania wody</a></li>
          <li><a href="index.html#o-nas">O&nbsp;nas</a></li>
          <li><a href="index.html#kontakt">Kontakt</a></li>
          <li><a href="galeria.html" aria-current="page">Galeria</a></li>
        </ul>
      </nav>
      <div class="nav-overlay"></div>
    </div>
  </header>

  <main>
    <section class="section gallery-page" aria-labelledby="galeria-heading">
      <div class="container">
        <div class="section-header">
          <h2 id="galeria-heading">Nasze realizacje</h2>
          <p>Wybrane montaże i realizacje. Kliknij zdjęcie, aby powiększyć.</p>
        </div>

__JUMPNAV__

__GROUPS__

      </div>
    </section>
  </main>

  <!-- ===================== FOOTER ===================== -->
  <footer class="site-footer">
    <div class="container footer-inner">
      <span><strong>Filtry Do Wody – Gorzów</strong></span>
      <span>Obr. Pokoju 69, 66-400 Gorzów Wielkopolski</span>
      <a href="tel:+48608666575">+48 608 666 575</a>
      <a href="mailto:filtrygorzow@gmail.com">filtrygorzow@gmail.com</a>
    </div>
  </footer>

  <!-- ===================== LIGHTBOX ===================== -->
  <dialog class="lightbox" id="lightbox">
    <img src="" alt="">
  </dialog>

  <!-- ===================== SCRIPTS ===================== -->
  <script>
    // Sticky header shadow
    const header = document.querySelector('.site-header');
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });

    // Hamburger menu
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.main-nav');
    const overlay = document.querySelector('.nav-overlay');

    function toggleMenu() {
      const isOpen = nav.classList.toggle('open');
      hamburger.classList.toggle('active');
      overlay.classList.toggle('active');
      hamburger.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    }
    hamburger.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (nav.classList.contains('open')) toggleMenu();
      });
    });

    // Lightbox (mechanizm jak w classicq: klik gdziekolwiek / Esc zamyka)
    const lightbox = document.getElementById('lightbox');
    const full = lightbox.querySelector('img');
    document.querySelectorAll('.gallery-item').forEach(btn => {
      btn.addEventListener('click', () => {
        full.src = btn.dataset.full;
        full.alt = btn.querySelector('img').alt;
        lightbox.showModal();
      });
    });
    lightbox.addEventListener('click', () => lightbox.close());
    lightbox.addEventListener('close', () => { full.src = ''; });
  </script>
</body>
</html>
"""


def build_page():
    jumpnav, groups_html, total = build_groups_html()
    html = TEMPLATE.replace("__JUMPNAV__", jumpnav).replace("__GROUPS__", groups_html)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {PAGE} — total photos on page: {total}")


def main():
    ap = argparse.ArgumentParser(description="Build the gallery page and optimized images.")
    ap.add_argument("--src", default=DEFAULT_SRC,
                    help=f"folder with the source photo subfolders (default: {DEFAULT_SRC})")
    ap.add_argument("--only", help="convert only this source subfolder (e.g. STACJA)")
    ap.add_argument("--no-build", action="store_true", help="skip regenerating galeria.html")
    args = ap.parse_args()

    print(f"Source: {args.src}")
    for src_folder, slug, title, short in CATS:
        if args.only and src_folder != args.only:
            continue
        convert_category(args.src, src_folder, slug)

    if not args.no_build:
        build_page()


if __name__ == "__main__":
    main()
