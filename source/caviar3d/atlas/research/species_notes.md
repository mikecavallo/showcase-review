# Species research notes

Companion to `species.json` (compiled 2026-10-06). Each field's source is in that entry's `field_sources`, keyed to `source_index`. This file covers how the numbers were chosen, where sources disagree, and what is still open.

## Method

- **Size, weight and lifespan:** FishBase species summaries throughout, so every species is measured the same way. Exceptions: bluefin weight (ICCAT's official record) and white sturgeon (FishBase agrees with CDFW).
- **Female age at maturity:** FAO, state and federal agency, or peer-reviewed figures where they exist, then FishBase maturity tables. Where a source doesn't separate the sexes, the entry has a `female_maturity_note`.
- **Egg diameter:** For six sturgeons, one source with a consistent method: Chapman & Van Eenennaam, UF/IFAS EDIS FA153. It gives typical ripe-egg ranges for beluga, osetra, sevruga, white, Siberian and sterlet. Other species have their own sources.
- **IUCN status:** Category, criteria and assessment date come from FishBase, which cites Red List version 2025-2. Publication year and assessment ID come from the published IUCN citation where one was found. iucnredlist.org returned HTTP 403 to every automated request, so no status was read from IUCN directly.
- **Map points:** Approximate points placed by hand on well-known rivers, seas and lakes inside each native range. Use them as display anchors only. They are not occurrence data.

## Conflicts and the figure chosen

| Species | Field | Figures found | Chosen, and why |
|---|---|---|---|
| Beluga | max length / weight | FishBase 8 m, 3,200 kg (Kottelat & Freyhof 2007); Guinness 7.3 m, 1,474 kg (Volga female, 1827); Wikipedia (citing Berg 1962 and Guinness) 7.2 m, 1,571 kg for the same fish; FAO TP558 says 4.6 m and "in excess of 2,000 kg" | FishBase was kept for consistency, with a `max_size_note`. **For a museum label, use the 1827 specimen figures (about 7.2 to 7.3 m, about 1,500 kg).** The 3,200 kg figure is a historical published maximum that hasn't been verified. |
| Beluga | lifespan | FishBase 118 y; FAO TP558 "up to 100 years" | 118 (FishBase max reported age) |
| Beluga | female maturity | FAO 16 to 18; FishBase 13 to 22 and 14 to 20; Wikipedia 16 to 22 | FAO 16 to 18 |
| Beluga | fecundity (fact) | FAO 200,000 to 8 million eggs; FishBase 360,000 to 7.7 million | FAO |
| Beluga | spawning interval | FishBase: eggs only every 5 to 7 years; FAO: "generation interval 4 to 5 years" | Not used in the data because of the conflict |
| Russian sturgeon | lifespan | FishBase 46; FAO "may reach 50" | 46 |
| Russian sturgeon | egg size | EDIS 3.2 to 3.8; Lenhardt 2005 (Danube oocytes) 3.36 x 3.69 mm; FAO gives 3.2 to 3.8 for Persian sturgeon | EDIS |
| Siberian sturgeon | egg size | EDIS 2.4 to 3.0; FAO fact sheet "longest measurement 3.0 to 3.8 mm" (eggs are oval) | EDIS. The FAO figure measures the long axis only. |
| Siberian sturgeon | female maturity | FAO fact sheet 12 to 20 (wild), about 7 farmed; FishBase records 9 to 34 (Lake Baikal 26 to 34) | FAO 12 to 20 |
| White sturgeon | female maturity | Chapman et al. 1996: females 15 to 32; CDFW 10 to 19 (sexes combined, California); FishBase Fraser River females 11 to 34 | Chapman (the only female-specific figure). The CDFW range is in the note. |
| White sturgeon | egg size | EDIS 3.2 to 4.0; Chapman 1996: Sacramento 3.4 to 4.0, Columbia 2.6 to 3.6, hatchery mean 3.7 | EDIS |
| White sturgeon | lifespan | FishBase 104; CDFW "oldest on record 103" | 104. The one_fact avoids age so the two don't clash. |
| Sterlet | size | FishBase 125 cm, 16 kg; FAO TP558 says 70 to 90 cm and 2 to 4 kg, yet reports a 92 cm, 5.6 kg sterlet caught in 2001 | FishBase |
| Sterlet | egg size | EDIS 2.0 to 2.8; FAO 1.9 to 2.0; Lenhardt 2005 ovulated eggs 2.4 x 2.7 | EDIS |
| Sterlet | lifespan | FishBase 36; FAO "20 or more" | 36 |
| Stellate sturgeon | max length | FishBase 250 cm; CITES ID guide (via FAO TP558) 220 cm | 250 |
| Stellate sturgeon | female maturity | FAO 8 to 10; FishBase/Kottelat & Freyhof 8 to 14 | FAO |
| Kaluga | female maturity | NOAA 14 to 23 (sexes combined); CMS proposal "average 14 to 23"; FishBase females 11 to 16 (middle Amur) and 17 to 23 (estuary) | NOAA |
| Amur sturgeon | lifespan | FishBase 65; USFWS "up to 60" | 65 |
| Shovelnose | lifespan | FishBase 43; Fishes of Texas 30 (Kennedy et al. 2007) | 43 |
| Shovelnose | egg size | Population means: 2.40 mm (Platte River, Hamel et al. 2015), 2.45 (South Dakota, only via search summary), 2.58 (Illinois, Stahl 2008) | Range of the two verified means, [2.40, 2.58] |
| Paddlefish | egg size | Reed et al. 1992: 2.1 to 3.1 mm; Purkett 1961 and others: 2.0 to 3.9 | Reed et al. (a direct measurement range; also FishBase's main egg reference) |
| Paddlefish | female maturity | Fishes of Texas (Pitman 1992): 6 to 12; SRAC 437: at least 7 years, 7 to 9 in the southern US; FishBase 9 | 6 to 12 |
| Lake whitefish | female maturity | FishBase Ontario 4 to 7 (sexes combined); Eastmain River females 7+; Tuktoyaktuk 10+; Upper Great Lakes female A50 of 5.0 y (DeCosta 2016 MSc thesis, search summary only) | 4 to 7, with a note |
| Lake whitefish | egg size | Paufve et al. 2020: mean 3.21 mm, SD 0.20 (fertilized, water-hardened); an unsourced 1.0 to 2.7 mm range appeared in search summaries | Paufve mean. Unfertilized roe will be a little smaller. |
| Chum salmon | egg size | Myoung & Kim 1993: mean 7.2 mm (fertilized, Korea); a "6.7 mm" figure attributed to FishBase couldn't be found on FishBase; USFWS says eggs reach "1/2 inch" (too rough to use) | 7.2 as the mean only |
| Rainbow trout | female maturity | FAO "usually 3 to 4 years"; FishBase Ontario female 3 to 5 | FAO |
| Atlantic bluefin | max weight | ICCAT official 726 kg (427 cm, Gulf of Maine); FishBase 684 kg; FishBase text and ICCAT mention reports up to 900 kg; NOAA "up to 2,000 lb" | ICCAT 726 kg |
| Atlantic bluefin | lifespan | FishBase 32; FishBase text "up to 40 years in the western Atlantic"; NOAA "20 years or more" | 32 (FishBase max reported age) |
| Atlantic bluefin | maturity | ICCAT: 50 percent mature at age 4 (east), about 8 (west); some authors put the west at 5 to 12 | [4, 8] |
| Yellowfin | lifespan | FishBase 18 (recent reference); ICCAT 2006 quotes FishBase at the time as 8 | 18 |
| Flathead grey mullet | max weight | FishBase reports 12 kg but flags it as unconfirmed | null |
| Garden snail | egg size | CFIA "about 3 mm"; UF/IFAS "about 1/8 inch" (3.2 mm); an unattributed "4 mm" in search results | 3 |
| Garden snail | shell size | CFIA 32 to 38 mm; UF/IFAS (Burch 1960) 28 to 32 mm | 38 mm (CFIA upper value), stored as max_length_m 0.038 |

## Open questions to flag for Caviar Star

1. **Tobiko species.** No authoritative source names "the" tobiko species. Pappalardo et al. 2021 say tobiko comes from *Cheilopogon* and *Hirundichthys*. Of their 12 Italian samples, 6 were *H. affinis*, 1 *H. oxycephalus*, 1 *H. coromandelensis* and 4 were capelin. The entry uses *H. affinis* as the representative species, but its egg size is from *H. oxycephalus*. Ask Caviar Star's supplier which species and origin they use.
2. **Bowfin taxonomy.** In 2022 bowfin west of the Pearl River was split off as *Amia ocellicauda*, the eyetail bowfin. FishBase follows the split. Louisiana's Atchafalaya Basin, the center of "choupique" caviar, is in the *A. ocellicauda* range, so the store's *Amia calva* label is probably out of date for Louisiana roe. All size, age and egg numbers come from pre-split studies.
3. **Huso vs Acipenser.** FishBase now lists beluga and kaluga as *Acipenser huso* and *Acipenser dauricus*. The JSON keeps *Huso* as the display name and adds a `taxonomy_note`. Decide which to show.
4. **Kaluga and US law.** NOAA lists kaluga as endangered under the ESA, effective 2 July 2014. How that applies to kaluga and kaluga-hybrid caviar sold in the US is a legal question that wasn't researched here. Caviar Star should confirm its import paperwork covers it.
5. **Amur sturgeon ESA status.** USFWS proposed endangered status in August 2021. Whether a final rule was published couldn't be confirmed.
6. **Beluga x sevruga.** FAO (1971, citing Berg 1948) records *H. huso x A. stellatus* only as a natural hybrid. No source on why or where it is farmed was found, so `why_farmed` is null. Commercial "beluga hybrid" caviar is often beluga x Siberian or beluga x ship sturgeon, so confirm the parents with the supplier.
7. **Caspian wild caviar.** The statement that the Caspian states set no commercial fishing or wild-caviar export quotas in 2014 and pledged none for 2015 to 2016 comes from CITES AC28 Doc. 16.1. The PDF returned 403, so it was read only through search-engine text. Re-check before publishing, and look for a current CITES export-quota page.
8. **Bronzi et al. 2019 shares.** The 2016 figures (Siberian 31 percent, Russian 20 percent, kaluga x Amur 13 percent, white 12 percent) come from the paper's abstract as quoted in search results. The publisher page returned 403.
9. **Pacific salmon IUCN dates.** FishBase gives an assessment date of 23 July 2020 for chum and pink (28 July 2020 for trout). The Wikipedia citations give publication in Red List 2024-2. Both are recorded.
10. **Sterlet IUCN.** FishBase shows no IUCN line for the sterlet. The Endangered status and assessment ID come from the IUCN citation on Wikipedia (Gessner et al. 2022). The assessment date is unknown.
11. **Snail IUCN.** Only a European regional assessment was found (Neubert 2011, Least Concern). No global assessment was confirmed.
12. **Tuna bottarga in the US market.** Peer-reviewed work (Scano et al. 2013) ties traditional Mediterranean tuna bottarga to bluefin. Nothing was found on whether the bottarga Caviar Star sells is bluefin or yellowfin. Check the supplier label.
13. **"Salmon caviar = chum."** Chum is treated as the usual salmon-caviar species, as the brief said. No authoritative market-share source was found. FishBase says chum is "utilized for caviar" and that pink roe is "valued for caviar, especially in Japan".

## Numbers that could not be sourced (left null)

- Kaluga egg diameter. Only retailer claims (about 3 to 4 mm) were found.
- Kaluga hybrid, bester and beluga x sevruga egg diameters. Only a company document claims the kaluga hybrid gives "over 3.4 mm" eggs.
- Beluga x sevruga `why_farmed`.
- Pink salmon egg diameter.
- Chum salmon egg diameter **range**. Only a mean (7.2 mm) was found.
- Yellowfin upper age at maturity.
- Flathead grey mullet max weight.
- Flying fish (*H. affinis*) max weight.
- Garden snail lifespan and weight.
- IUCN assessment IDs or publication years for Russian sturgeon, Amur sturgeon, lake whitefish, grey mullet and *H. affinis*. Category and assessment date are filled from FishBase.

## Values that are single means rather than ranges

`egg_diameter_mm` holds a mean as both min and max for lake whitefish (3.21), chum (7.2), Atlantic bluefin (about 1.0) and garden snail (about 3). Each has an `egg_diameter_note`. A UI should show these as one value, not a range.

## Facts checked for the one_fact labels

- Russian sturgeon x paddlefish: Kaldy et al. 2020, *Genes* 11:753. Survival of 62 to 74 percent at 30 days is from the abstract. The 184.4 million year divergence is from the full text (Europe PMC).
- Paddlefish rostrum as an "electrosensory antenna": the title and abstract of Wilkens et al. 1997, which describes responses to signals from *Daphnia*.
- Shovelnose "similarity of appearance" protection: 75 FR 53598, effective 1 October 2010, and the Missouri Department of Conservation page.
- Tobiko and capelin: Table 1 of Pappalardo et al. 2021 (4 of 12 tobiko samples were *Mallotus villosus*).
- The facts deliberately leave out the beluga "every 5 to 7 years" spawning interval because FAO and FishBase disagree.

## Context, not used as fields

- The IUCN reassessment of all sturgeons and paddlefish was published on 21 July 2022 (IGB Berlin press release). Most sturgeon assessments in it are dated September 2019.
- China: five farmed sturgeons, including the kaluga x Amur hybrid, made up 90 percent of national sturgeon production in 2010 to 2012, with 56.6 t of caviar in 2012, 90 percent exported (Shen et al. 2014).
- DNA testing has found high levels of concealed hybridization in caviar sold as Amur or kaluga (Boscari et al. 2017).
