# Caviar Atlas: product research notes

Companion to `products.json` (31 Caviar & Roe products). Compiled 2026-10-06.

## How the data was built

- **Primary source:** `src/products.json` (Shopify catalog snapshot). Prices and availability come from it; the live
  pages fetched on 2026-10-06 showed the same prices and the same sold-out products.
- **Live product pages** (caviarstar.com/products/<handle>) carry extra store data that is not in `body_html`: a
  species line ("Caviar of ... - Latin name"), tasting tags, and an "Additional Nutritional Info" block
  (common names, country of origin, ingredients, product type, grade, sourcing). `origin_country`, `wild_or_farmed`
  and several `malossol` values come from that block. Where a field came only from a page title or meta
  description, the field value says so.
- **2026 wholesale catalog** (Flipsnack text plus page images in `doc/research/img/`): country flags, the W/F
  (wild/farmed) mark, Latin names, and partner farms (p.3).
- **Producer sites and press:** Dieckmann & Hansen (dieckmann-hansen.com), Kaluga Queen (Wikipedia), Gosławice
  farm (Eurofish 2016, Antonius Caviar profile), Prunier farm (fineandwild.com), Caviar Galilee (Wikipedia "Dan,
  Israel"), Peconic Escargot (Dan's Papers, Dec 2023).
- **Sizes:** `grams` is net weight from the variant label. The label's own gram figure is used when it gives one
  (so "1oz (28g)" is 28 g); otherwise oz × 28.35. The Shopify variant `grams` field is ignored: it is shipping
  weight (a 1 oz jar is listed as 104 g).
- **Price per gram:** smallest available size; if nothing is available, the smallest size. Prices are the
  regular prices in the catalog. The live pages also show "sale" prices that are *higher* than the regular
  price (a compare-at quirk), so those were not used.
- **`malossol`:** `true` when the store uses the word malossol (description, info block, page title or meta
  description), or, for snail caviar and rainbow trout roe, says "low salt" (the store's FAQ defines malossol as
  "little salt"). `false` only for the two bottargas (dried and pressed, a different cure). `null` when the
  store says nothing.

## Fields left null most often

| Field | Nulls | Why |
|---|---|---|
| grain_size_mm | 28 of 31 | The store gives millimetres for only two products: Dieckmann & Hansen Reserve Osetra (3.3 to 3.6 mm) and snail caviar (about 4 mm). Paddlefish (about 2 mm) comes from Caviar Star's own blog. Producer and retailer figures for *other* grades were not applied (see below). |
| producer | 19 | The store does not name the farm for the California and Italian white sturgeon, the Romanian and Bulgarian hybrids, Premier Kaluga, Dynasty Siberian, Dynasty Amur, or any wild American roe, the trout roes, or the bottargas. |
| malossol | 13 | No malossol or low-salt wording for these products. |
| origin_region | 10 | Country only (for example Romania, Bulgaria, China, France/Denmark trout). |
| texture | 5 | The description gives flavor but no texture (white sturgeon grades, Karat). |
| grain_label, color | 4 and 3 | Not described (bottargas, smoked salmon roe, Dynasty Royal Osetra size). |

Counting every field, 1 product (snail caviar) has no nulls; 5 have no nulls apart from `grain_size_mm`.

## Not confirmed

- **Grain sizes in mm.** Figures found elsewhere apply to other products, so they were left out:
  Dieckmann & Hansen's own Oscietra Germany is "über 2,7 mm" and Baerii "mindestens 2,0 mm" (dieckmann-hansen.com);
  Gosławice eggs reach "2.5 or 2.6 mm" (Eurofish 2016, generic); Galilee/Karat grades sold elsewhere are listed at 2.2 to 2.7 mm
  (Prime) and 2.5 to 3 mm (Royal) by Browne Trading (seen in search results only), a different grading from
  Caviar Star's.
- **Royal Beluga Bester (Romania) and Reserve Beluga Sevruga (Bulgaria):** farm not named anywhere. The Bester
  copy says "farmed, sustainable, and organic"; the organic claim is unverified.
- **Premier Kaluga Hybrid, Dynasty Siberian, Dynasty Imperial Amur:** producer not stated. The catalog says "The
  finest Kaluga Hybrid caviar available in the World comes from our partners at Kaluga Queen," and the OT gift bag
  page says the *Imperial* Kaluga Hybrid is "Farmed by the caviar masters of Kaluga Queen". That supports Kaluga
  Queen for the Imperial grade only, so Premier was left null. Origin region for both Kaluga hybrids is left null:
  Kaluga Queen farms at Qiandao Lake, but no page ties these products to that site.
- **Dieckmann & Hansen Reserve Osetra and Albino Sterlet, origin_region:** the store says only "Germany".
  Dieckmann & Hansen's German farm is its "Mutterbetrieb in Fulda" (Hesse), but the company also farms Oscietra in
  Italy (Tavazzano) and Hungary (Komádi), and the current Dieckmann & Hansen shop does not list an albino sterlet.
  Left null.
- **Lyna Polska producer:** the name comes from the 2026 catalog (p.3): "Goslawice aquaculture farm of Poland has
  been in operation since 1967. Caviar Star Polska Osetra and Siberian caviars are farmed here along the Lyna
  river." The product pages do not name it. Gosławice's main farm is near Konin in central Poland; the Łyna River
  site is near Olsztyn (Eurofish 2016 describes fish moving between the two). Gosławice sells its own caviar as
  "Antonius". Founding year differs: catalog 1967, Eurofish "50 years ago" (about 1966), an Antonius Caviar profile
  (seen via search results) says sturgeon farming began in 1992.
- **Tuna bottarga origin:** "Spain" appears only in the page's SEO title ("... Tuna Fish Roe, Spain"). The
  description says "Mediterranean caviar", which is a nickname, not an origin. Wild or farmed is not stated (left
  null); producer not stated.
- **Mullet bottarga producer:** "artisanally hand-cured grey mullet roe from Clearwater, Florida", no maker named.
  Cortez Conservas (Cortez/Anna Maria Island, FL) is a known Florida bottarga maker but is not in Clearwater and
  nothing links it to this product.
- **Smoked salmon roe region:** the page says only USA, wild, chum (keta). "Alaska" rests on "Also available in the
  non-smoked variation: American Salmon Roe", which is the Alaskan product.
- **Who smokes the roe:** the Bourbon Barrel trout page says "Our signature cold-smoked trout caviar" and "We were
  the first company to smoke fish roe in the 2000s", so it is recorded as smoked in house. The smoked whitefish and
  smoked salmon pages describe the same bourbon-barrel cold smoke but do not say who does it (producer null).
- **Trout roe origin:** rainbow trout roe page: "France, Denmark"; smoked trout page: "France"; tags on both list
  Denmark and France. The supplier is not named. (GAT's ocean import records list Aquapri A/S, a Danish trout
  company, among shippers; that suggests but does not confirm a Danish source.)
- **Genki tobiko:** "Genki" is the brand on the product; the manufacturer behind it was not identified. Species is
  given only as the family Exocoetidae.
- **Hackleback, paddlefish, bowfin, whitefish, salmon:** wild-caught by partner fishermen; no producer named
  (bowfin fishermen work "from Baton Rouge, Louisiana, to as far north as Illinois").
- **Company claims that cannot be checked:** "exclusively imported into the United States by Great Atlantic
  Trading" (Prunier and Dieckmann & Hansen pages); "first company to smoke fish roe in the 2000s" (smoked trout);
  Albino Sterlet "Only available through Caviar Star".

## Contradictions between sources

- **Reserve Beluga Sevruga species.** Description and catalog: Huso huso × *Acipenser stellatus* (Sevruga). The
  live page's species line says "Beluga Sturgeon and Sterlet Sturgeon - Huso Huso x Acipenser Ruthenus", which
  looks copied from the Bester page. The JSON uses the description and catalog.
- **Albino Sterlet species.** Product page: *Acipenser ruthenus* (sterlet). 2026 catalog p.8: "Acipenser
  stellatus" (that is sevruga). The JSON uses *A. ruthenus*. The handle and page title also say "Almas", a name
  usually used for albino beluga, while the product is sold as sterlet.
- **Italian White Sturgeon species.** Product page: *Acipenser transmontanus*. Catalog p.8: "Acipenser
  schrenckii" (a catalog error). Its meta description also calls it "Classic California White Sturgeon Caviar ...
  farm-raised in Northern Italy".
- **Bester flavor line.** "a rich, creamy, slightly nutty flavor unique to Beluga and Osetra": the hybrid is Beluga
  × Sterlet, not Osetra (the Sevruga page has the same sentence with "Beluga and Sevruga").
- **Kaluga Queen location.** Dynasty Royal Osetra says "Thousand Island Lakes of Northern China". Thousand Island
  Lake (Qiandao Lake) is in Zhejiang, eastern China (Wikipedia). The JSON gives Qiandao Lake, Zhejiang.
- **Dieckmann & Hansen founding.** Caviar Star: "For over 150 years" and "the oldest caviar company in the world".
  The company's own history says it has traded "since 1839" and was entered in the commercial register in 1869
  (Monocle 2009 also gives 1869). "Oldest" is the store's claim; the 2026 catalog instead calls the Prunier farm
  "the oldest caviar farm in existence".
- **Prunier maturation time.** Product page: care "spanning more than a decade"; catalog: "12 years to 20 years";
  fineandwild.com: fish reared "a minimum of eight years" for Oscietra and "a minimum of twelve years for larger,
  lighter grain". The farm itself opened in 1990 (fineandwild.com), so the 1921 date in the store copy belongs to
  the Prunier house, not to this farm.
- **Karat naming.** The store says "Caviar Galilee, now Karat Caviar". Wikipedia: the Caviar Galilee Company
  "exports caviar under the brand name 'Karat Caviar'"; Karat is the brand, not a renamed company.
- **Peconic Escargot.** Store: "one of the few snail farms in the United States". Owner Taylor Knapp (Dan's Papers,
  Dec 2023): "the first and only USDA-sanctioned snail farm in the country". Species: page "Helix Aspersa Muller",
  catalog "Petit Gris (Cornu aspersum)"; these are the same species (Cornu aspersum, syn. Helix aspersa).
- **Classic California White Sturgeon color and size.** The same description says "brown to black hues and
  generously sized pearls" and "medium-sized grains, ranging in color from dark gray to light brown"; the meta
  description says "Platinum to brown hues".
- **Smoked trout roe smoke.** Description: Pappy Van Winkle bourbon-barrel stave chips. Page title and meta
  description: "Natural Hickory Smoked".
- **Hackleback size.** Product page: "the smallest of the sturgeon species". Caviar Star's 2023 blog: "the smallest
  sturgeon in North America" (the narrower claim).
- **Bowfin age.** Product page: Bowfin "predates even the sturgeon". Caviar Star's own blog: bowfin "around for about
  150 million years", sturgeon family "over 200 million years". The page also claims adaptability "to both fresh and
  saltwater", which was not verified.
- **Bottarga weights.** Tuna: description "6 to 8 oz" and "Net Weight: 6 to 8 oz bag", variants "approx 12 oz"
  (whole) and "approx 6 oz" (half), catalog "10-12oz". Mullet: description "3.5 to 6oz", variants "approx 4.5 to
  5.5 oz" and "approx 2 to 3 oz", catalog "4-6oz". The JSON uses the variant labels; mullet grams are range
  midpoints (5.0 oz, 2.5 oz).
- **Tobiko jar size.** Description: "2 oz. glass jars or 500 g plastic containers"; variants are 50 g (1.76 oz) and
  500 g.
- **Smoked salmon roe pricing.** 1 oz and 2 oz are both $25.00 in the catalog and on the live page; likely a data
  error, recorded as listed. The description calls it "#1 grade"; the info block says "Grade A".
- **Whitefish Latin name.** Live page spells it "Coregonus clupeiformis"; the catalog and GAT export page use the
  standard *Coregonus clupeaformis* (used in the JSON).
- **Paddlefish Latin name.** The store blog writes "Polydon spathula"; the product page and catalog use the correct
  *Polyodon spathula*.
