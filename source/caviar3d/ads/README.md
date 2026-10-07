# Caviar Star sale ads

Two ways to make sale videos that always show the store's real price.

## Ad Studio (in the browser, no setup)

Open the Ad Studio page, pick a product and a size. It reads today's price and compare-at
price from caviarstar.com, so the badge can only show a saving the store really has. Edit the
headline, pick 9:16, 4:5 or 1:1, and export an MP4 or a PNG. Tick "Catalog version" for a
price-free video to use in catalog ads, where Meta or TikTok shows the live price beside it.

## Batch generator (one sheet, every ad)

    python3 ads/make.py                 # render every active row of ads/sheet.csv
    python3 ads/make.py --check         # is every rendered video still priced right?
    python3 ads/make.py --discover      # everything on sale right now, as sheet rows
    python3 ads/make.py --sheet URL     # use a Google Sheet (File > Share > Publish to web > CSV)

The sheet (`ads/sheet.csv`) holds what people decide: which product, which size, the headline
and the sub line. It never holds prices. Columns:

| column | what it does |
|---|---|
| active | y to render, n to skip |
| handle | the product's address on caviarstar.com, e.g. `amber-dynasty-royal-kaluga-caviar` |
| size | the size to feature, as the store names it (`4oz`, `One Spoon`). Blank = the biggest real saving |
| headline, sub | the words on the ad. Keep percentages out: the badge carries the saving |
| name | optional product name override |
| badge | `percent` (Save 31%), `dollars` (Save $30 on 1 oz) or `none` |
| code, code_pct | a promo code, e.g. `CAVIAR15` and `15`: the badge becomes "Extra 15% / code CAVIAR15" |
| cta | button text (default "Shop the sale") |
| formats | any of `9x16 4x5 1x1` |
| catalog | y to also render a price-free version for catalog ads |
| dur | seconds (default 8, at least 6) |
| foot | the legal line (default "Prices as shown on caviarstar.com. Subject to change.") |

Each run fetches every price from the store, rounds percentages down, and re-renders only the
ads whose content changed. A size whose sale has ended renders without a badge or a strike
price; a sold-out size is skipped and reported.

Every MP4 and PNG carries what it shows in its metadata (product, size, price, was-price,
saving, the date it was checked). `--check` reads that back and compares it with the store:

    dynasty-siberian-caviar-2oz-9x16.mp4    STALE       video $99/$150, site $109/$150

Run `python3 ads/make.py` again and the stale ones re-render. Instagram, Facebook and TikTok
strip file metadata on upload, so the metadata is for your files, not the platforms.

Outputs land in `ads/out/gen/` with `manifest.csv` listing every file and its price.
Needs: Python 3, Node 18+, Playwright Chromium, ffmpeg, OpenCV (`pip install opencv-python`).
