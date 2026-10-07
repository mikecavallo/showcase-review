# Showcase review

Spec work made for Caviar Star (Great Atlantic Trading Inc., Ocean Isle Beach, NC), collected in one place so each page can be shared and reviewed.

## Sites

Each folder is a static site with an `index.html`. Serve the repo root with any static host (Vercel, GitHub Pages, `python3 -m http.server`).

| Folder | What it is |
|---|---|
| `showcase/` | Start here: one page linking everything below |
| `collection/` | All 181 Caviar Star products in 3D, turnable by hand |
| `film/` | *From the Docks to the Tin*, a 15-minute documentary on the company |
| `atlas/` | The Caviar Atlas: every caviar by origin, species and pearl size |
| `turntables/` | A 10-second turning loop of every product |
| `ads/` | 11 sale ads in 9:16, 4:5 and 1:1 with paste-ready copy |
| `ad-studio/` | Make a sale ad in the browser from the store's live price; exports MP4/PNG |

## Deliverables

`deliverables/` holds the final files: the film (720p, 480p, captions), the two 3D reels, and every sale ad as MP4 and PNG.

## Source

`source/caviar3d/` is the full pipeline: the three.js product studio (`web/studio.js`), asset and render tools (`tools/`), the sale-ad stage, generator and sheet (`ads/`, see `ads/README.md`), the Atlas build (`atlas/`), the documentary research, script and build scripts (`doc/`), and the product catalog (`src/products.json`). The product photos are not included.

Left out because they are regenerable or over GitHub's 100 MB file limit: `node_modules`, the documentary's intermediate video and audio, the full-resolution 570 MB film master, photo cutouts and QC renders.
