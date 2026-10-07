# Caviar Atlas: connoisseur guide notes

Companion to `guide.json`. Compiled 2026-10-06. Lists what is uncertain, where sources disagree, and what was left out.

## How the guide was built

- **Caviar Star first.** About 65 Caviar Star blog posts were read in full: the 30 newest from the blog's Atom feed
  (`caviarstar.com/blogs/news.atom`), the older ones from their pages. The local copies in `doc/research/` were used for
  the FAQ, shipping, story, brand, sustainability and international pages, the product key and the 2026 catalog.
- **Outside sources:** FDA CPG Sec. 540.150 (caviar labeling); 50 CFR 23.71 (CITES caviar labels, read from eCFR);
  Codex Alimentarius CXS 291-2010, Standard for Sturgeon Caviar (read from a university-hosted copy of the official PDF,
  because fao.org/codex returned 403); USFWS 1999 and 2005 releases; IUCN 2010; FAO GLOBEFISH (2019 China article,
  2023 Highlights); EUMOFA 2021 caviar study (via the FEAP summary, see below); OEC trade profile for HS 160431;
  NBC/AP (2006, 2007); The Moscow Times (2010); TheFishSite (2008); Liu et al. 2024 (Food Chemistry: X); CIA Foodies.
- **Blocked:** cites.org, Wiley, MDPI, SCMP, SeafoodSource, Eurasianet and the Wayback Machine all refused access
  (Cloudflare or 403). Facts that depend on them are flagged below.
- Every `text` is 45 words or fewer. Sources are URLs separated by ` ; `. The JSON uses no em or en dashes.

## Flagged facts (check before publishing)

1. **2011 zero quotas** (`history_market`, "2011: Wild quotas reach zero"). The claim that CITES published zero export
   quotas for wild caviar from all shared stocks for the 2011 quota year comes from CITES document AC25 Doc. 16.1. It
   appeared in search-engine excerpts of that document and of AC28 Doc. 16.3, but cites.org could not be opened. The
   "no quotas in 2006 or 2009" part is verified (The Moscow Times, July 25, 2010).
2. **Your brief's "2008 near-zero quotas" premise is wrong.** 2008 quotas were not near zero. The Moscow Times
   (2010) says the 2010 quota of about 81 tonnes was "5 tons less than in 2008", and that there were no quotas in
   2006 and 2009. A search result citing CITES puts the 2008 beluga quota at 3,700 kg. The guide uses 2006, 2009 and 2011.
3. **China's share today.** Estimates disagree widely, and none comes from an official statistical body:
   - FAO GLOBEFISH (2019): Chinese farmed caviar 0.7 t (2006) rising to 135 t (2018). EUMOFA: about 380 t worldwide in 2018.
     Together that is about 36 percent for 2018 (my arithmetic from two sources; not stated by either).
   - Bronzi et al. 2019 (J. Appl. Ichthyol. 35:257) is reported to give more than 100 t of 364 t for 2017. Seen in search
     snippets only; Wiley was blocked.
   - SCMP (2024) is reported to say more than 50 percent of production, 276 t exported in 2023 and about 40 percent of
     the export market. Seen in search snippets only.
   - Liu et al. 2024 (peer-reviewed, Food Chemistry: X) states "China produces 70% of the world's caviar" **without a
     citation**. Chen et al. 2025 repeats it ("over 70%"), citing Liu. The guide uses this figure, attributed to "a 2024
     peer-reviewed study". If you want a safer line, use "a third or more" with FAO and EUMOFA as the sources.
4. **US as consumer.** OEC (2024 data) shows the US with the largest caviar *trade deficit* (about -$49.3M) and China with
   the largest surplus ($98M). That measures the trade balance, not consumption. Caviar Star's fact-check post says the
   US imports "roughly 15%" of the world's caviar ("14.7% ... in 2016, worth approximately $13.6 million"). That is
   unverified and the dollar value looks low, so it was not used.
5. **Farmed overtaking wild.** There is one source: TheFishSite (Sept. 18, 2008), citing the World Sturgeon Conservation
   Society. It says aquaculture made about 80 to 100 t in 2006, about four times the legal wild yield. No exact
   crossover year was found.
6. **EUMOFA figures** (380 t global in 2018; China supplying 65 to 84 percent of extra-EU imports in 2015 to 2020) were
   taken from FEAP's summary of the May 2021 EUMOFA report. The old eumofa.eu PDF link now redirects to the new EC site,
   and the PDF itself could not be retrieved.
7. **2022 Russia bans.** The source is FAO GLOBEFISH Highlights (2nd issue 2023): the US banned Russian seafood, and the
   EU and Canada banned Russian caviar. The US measure is Executive Order 14068 (March 2022), which was not opened.
   Caviar Star's "no Russian caviar" statement dates from March 2022.
8. **"Pure beluga not imported since 2005"** is Caviar Star's wording, so the guide attributes it. The USFWS 2005
   suspension covered the Caspian basin countries. Caviar Star's own 2022 post also mentions a Florida farm (Sturgeon
   Aquafarms) that raises pure beluga in the US.
9. **Hackleback "the only wild sturgeon commercially harvested in the US"** is a Caviar Star product-page claim. No
   independent source was checked.
10. **000 / 00 / 0 color scale.** There is one source, CIA Foodies (Culinary Institute of America, undated): "a scale of
    000 for the lightest colored caviar to 0 for the darkest". "00 = medium" comes from a search summary of the same page.

## Where Caviar Star's own pages disagree

The guide uses the most recent dedicated post in each case.

| Topic | Values found | Used |
|---|---|---|
| Storage temperature | 26 to 38°F (FAQ), 27 to 37°F (2022 and May 2026 storage posts), 26 to 36°F (processing post), 28 to 32°F (malossol post), 28 to 38°F (July 4 post) | 27 to 37°F |
| Serving temperature | 26 to 34°F ("How to Eat and Serve Caviar Like a Pro", June 2025); other posts just say "well chilled" | 26 to 34°F |
| Unopened shelf life | 2 to 4 weeks and 4 to 6 weeks (both FAQ), about 4 weeks (2022), 3 to 5 weeks from packing (May 2026), up to two months (processing post) | 3 to 5 weeks |
| Opened shelf life | about 3 days, within 7 days, 5 to 7 days (all FAQ), 3 to 5 days (2022 post), "a few days" (malossol post) | 3 to 5 days |
| Malossol salt | under 5%, often about 3% (2025); 2 to 4% (May 2026); about 3% (2025 fact check); 3 to 5% (Local Palate; Codex standard) | under 5%, often about 3 |
| Box stays cold for | 48 hours (FAQ; 2018 post) vs 72 hours (shipping page) | 72, attributed to the shop |
| Same-day cutoff | 2 PM ET (FAQ) vs 1 PM ET (shipping page) | not used |

For comparison, the Codex standard (CXS 291-2010) sets +2 to +4°C (35.6 to 39.2°F) for packaging, storage and retail,
and 0 to -4°C (32 to 24.8°F) for wholesale storage and transport. Both are warmer at the top end than Caviar Star's
advice. Codex also bans freezing "unless the deterioration of quality is avoided".

## Brief items adjusted or left out

- **Stainless steel.** The brief grouped silver and stainless together. Caviar Star says silver is the real problem:
  stainless is less reactive, is used in packing rooms, and is "fine" for casual scooping. Its fact-check post quotes
  America's Test Kitchen on the silver and salt reaction. The guide follows Caviar Star.
- **"Staple"** was not found as a caviar trade term in any source, so it was left out. Trade terms that are sourced and
  included: OT, green eggs, pressed, hybrid, CITES code, Grade 1/2. "Banded tins" appears in Caviar Star posts, but no
  post defines it, so it was not included.
- **Health claims** were not used, including Caviar Star's line that pasteurized caviar is the best option for pregnant
  people.
- Garden & Gun (2024) quotes a retailer saying wild caviar exports have been "closed since 2005 by CITES". That
  conflicts with the 2007 to 2010 quotas, so it was not used.

## Caviar Star facts: status

All eight items are company-stated, except "Ten tons a year" (The Local Palate, Nov 21, 2021; independent press, but
the figure probably came from the company). The yearly inspections (USFWS, APHIS, NOAA, HACCP), the bowfin
partnership "for over a decade" and the Chubby Fish relationship are single-source company claims. The guide words
them as "the company says" or states them only where the company is the natural source.

Byline note for the dossier: the Atom feed lists post authors as "Tory D Manning", "Derek Leavitt" and "Deanna
Leavitt", while the pages show "D Leavitt". The feed author is probably the Shopify account that posted it, not the
writer.

## Quiz design notes

- **Caviar Star already has a quiz.** `caviarstar.com/pages/caviar-quiz` embeds Typeform `sqbKR2lZ`. It has 10
  questions: familiarity, favorite basic taste, coffee, liquor, beer, wine, value vs rarity, serving style, texture,
  and a restaurant dish. A single running `score` routes to five result screens (Fancy: Imperial Osetra / Beluga
  Hybrid / Royal Osetra; Great Taste: Kaluga; America: White Sturgeon / Paddlefish / Bowfin; Delicious: Hackleback /
  Smoked Trout / Italian White Sturgeon; Good Choices: Smoked Trout / Salmon / Paddlefish). **Bug:** two jump rules
  can never be true (`score == 4 AND score == 3`, `score == -1 AND score == 2`). Scores of 2, 3, 4 and -1 therefore
  match no result and fall through to Typeform's default end screen. The Atlas quiz could replace it. Its texture
  question and its value-vs-rarity question map directly onto the proposed `pearl` and `budget` axes.
- **Price bands** split the October 2026 catalog roughly evenly: under $40/oz (roes, paddlefish), $40 to $100
  (hackleback, Siberian, the Dynasty and Polska lines), $100 to $140 (white sturgeon, German Osetra), $140+ (Bester
  hybrid; Prunier and Albino Almas, both sold out on 2026-10-06). Thresholds are on `price_per_gram_usd`. The VIP
  Imperial Kaluga "OT" tins (30 g for $175, about $165/oz) are not in `products.json` and may be filed as a gift item.
- **Flavor and pearl matching** uses keywords in the `flavor`, `grain_label` and `texture` fields. `grain_label` is empty
  for a few products (Bourbon Barrel trout roe, Dynasty Royal Osetra, the bottargas), so they get no pearl weight.
  Bottargas and snail caviar are not real matches for most answers; consider excluding `kind` = cured roe and snail
  caviar unless the user picks "Surprise me".
- **Optional sixth axis: experience** (first time / some / seasoned). Caviar Star's "Choose the Right Caviar" post
  (July 2026) recommends hackleback and paddlefish for beginners and Osetra and Kaluga for the more experienced.
- A small price mismatch: the Sept 2026 price-guide post says hackleback "starts at around $62 for a 1-ounce tin",
  but the catalog lists $59.
