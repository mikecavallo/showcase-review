#!/usr/bin/env python3
"""Shot list for "Great Atlantic: From the Docks to the Tin". Follows the VISUAL notes in doc/script.md.
Each scene: list of (weight, shot). Timing is fitted to the narration length in build/audio/durations.json.
Writes build/timeline.json."""
import json

P = lambda *items, **k: dict(type='product', items=list(items), **k)
PH = lambda src, **k: dict(type='photo', src=src, **k)
T = lambda **k: dict(type='title', **k)
Q = lambda text, by=None, **k: dict(type='quote', text=text, by=by, **k)
N = lambda big, sub, **k: dict(type='number', big=big, sub=sub, **k)
LN = lambda items, **k: dict(type='lines', items=items, **k)
M = lambda view, **k: dict(type='map', view=view, **k)
D = lambda kind, **k: dict(type='diagram', kind=kind, **k)

PORTLAND = dict(lon=-70.255, lat=43.66, label='Portland, Maine')
OIB = dict(lon=-78.43, lat=33.89, label='Ocean Isle Beach, NC')
TOKYO = dict(lon=139.77, lat=35.68, label='Tokyo')
KALUGA_TIN = 'kaluga-hybrid-caviar-limited-edition'

S = {
 '0.1': [(1.2, PH('cs_home_caviar-macro-hero.jpg', kb=[[1.18, .03, .02], [1.32, -.03, -.01]])),
         (1.6, P(KALUGA_TIN)),
         (.7, PH('archival_dana-leavitt-drysuit-on-boat_SCAN0024.jpg', mono=True, kb=[[1.05, 0, 0], [1.15, .01, -.01]])),
         (.7, PH('archival_japan-street_dana_date-stamp-4-18-9x.jpg', mono=True)),
         (.8, PH('catalog2026_page13.jpg', fit='contain', kb=[[1, 0, 0], [1.05, 0, 0]]))],
 '0.2': [(1, T(logo='gat_logo_estd-1991.png', title='GREAT ATLANTIC', sub='From the Docks to the Tin', kicker='Great Atlantic Trading Inc. · Caviar Star'))],
 '1.1': [(1, M('gulf-maine', pins=[dict(PORTLAND, at=.8)], label='Portland, Maine · late 1980s', zoom=[1, 1.1])),
         (1, D('urchin', title='Before 1985: about 45 metric tons a year'))],
 '1.2': [(1.3, M('pacific', pins=[dict(TOKYO, at=.3), dict(lon=-120.5, lat=34.5, label='California', at=1.4), dict(lon=-127, lat=51, label='British Columbia', at=2.2, dx=-24, anchor='end'), dict(PORTLAND, at=3.6, label='Maine')],
                     arcs=[dict(from_=0)] and [dict(**{'from': [139.77, 35.68], 'to': [-120.5, 34.5], 'at': 1.0}), dict(**{'from': [139.77, 35.68], 'to': [-127, 51], 'at': 1.8}), dict(**{'from': [139.77, 35.68], 'to': [-70.25, 43.66], 'at': 3.2, 'dur': 2.2})],
                     label='Uni: sea urchin roe', zoom=[1, 1.04]))],
 '1.3': [(1.4, dict(type='chart', title='Maine urchin landings', bars=[dict(label='1987', value=1.4, text='1.4 million lb'), dict(label='1992', value=26, text='over 26 million lb')], src='Maine Department of Marine Resources; Christian Science Monitor, 1994')),
         (1, LN(['1990 value: almost $15 million', 'Hand-fishing urchin licenses: 807 (1992)', '1,439 (1993)'], src='Maine Department of Marine Resources; Christian Science Monitor, 1994')),
         (.7, PH('archival_dana-leavitt-drysuit-on-boat_SCAN0024.jpg', mono=True))],
 '2.1': [(1.6, PH('archival_dana-leavitt-drysuit-on-boat_SCAN0024.jpg', mono=True, kb=[[1.02, 0, 0], [1.2, .02, -.02]], lower=['Dana Leavitt', 'Photo: Caviar Star'])),
         (1, M('gulf-maine', pins=[dict(PORTLAND, at=.4, label='Great Atlantic Seafood · Portland')], zoom=[1.05, 1.18], label='Portland docks'))],
 '2.2': [(1, D('urchin', title='Prime season: November to March'))],
 '2.3': [(1, D('grades')),
         (1.3, Q('The Maine market did not get off the ground until Japanese representatives came to Maine to explain what is required to satisfy their market.', 'Maine Department of Marine Resources'))],
 '2.4': [(1.2, PH('archival_japan-group-photo_dana-denise_SCAN0069.jpg', mono=True, lower=['Dana and Denise Leavitt in Japan', 'Photo: Caviar Star'])),
         (1, PH('archival_japan-dinner-toast_dana-denise_gat-about.jpg', mono=True, kb=[[1.05, 0, 0], [1.15, -.02, 0]]))],
 '2.5': [(.8, PH('archival_japan-dinner-toast_dana-denise_gat-about.jpg', mono=True, kb=[[1.15, -.02, 0], [1.2, -.03, .01]])),
         (1.4, PH('archival_japan-street_dana_date-stamp-4-18-9x.jpg', mono=True, kb=[[1.02, 0, 0], [1.6, -.18, -.12]], cap='Japan, 1990s')),
         (.7, PH('archival_japan-street_SCAN0052.jpg', mono=True))],
 '3.1': [(1, T(title='1991', kicker='Great Atlantic Trading', sub='established')),
         (1, T(logo='gat_logo_estd-1991.png', title='ESTD 1991'))],
 '3.2': [(1.2, M('mississippi', states=True, rivers=[dict(name='mississippi', at=.3), dict(name='missouri', at=1.2), dict(name='white', at=2.0), dict(name='ohio', at=2.2), dict(name='arkansas', at=2.4)], label='The rivers of American wild caviar', zoom=[1, 1.06])),
         (.8, PH('gat_fish-drawing_hackleback.jpg', fit='contain', lower=['Hackleback', 'Scaphirhynchus platorynchus'])),
         (.8, PH('gat_fish-drawing_paddlefish.jpg', fit='contain', lower=['Paddlefish', 'Polyodon spathula'])),
         (.8, PH('gat_fish-drawing_bowfin-black.jpg', fit='contain', lower=['Bowfin', 'Amia calva']))],
 '3.3': [(1.2, dict(type='chart', title='Maine urchin landings', bars=[dict(label='1987', value=1.4, text='1.4 million lb'), dict(label='1992', value=26, text='over 26 million lb')], stall=True, src="1994: 'some say has peaked' · Christian Science Monitor")),
         (1, PH('gat_caviar-macro_partner-page.jpg'))],
 '3.4': [(1.4, M('east-coast', pins=[dict(PORTLAND, at=.3), dict(OIB, at=2.4)], arcs=[{'from': [-70.25, 43.66], 'to': [-78.43, 33.89], 'via': [[-69.8, 40.5], [-74.5, 35.6]], 'at': .8, 'dur': 2.0}], label='563 Seaside Rd SW · Ocean Isle Beach, NC', states=True)),
         (1, PH('catalog2026_page53.jpg', fit='contain'))],
 '4.1': [(1.1, M('caspian', pins=[dict(lon=50.5, lat=42.0, label='Caspian Sea', at=.4), dict(lon=34.0, lat=43.5, label='Black Sea', at=1.0, anchor='end', dx=-24)], label='The wild sturgeon seas')),
         (1, PH('baldor_cs_sturgeon-swimming.jpg', cap='Sturgeon can live up to 100 years'))],
 '4.2': [(1, LN(['April 1, 1998: all sturgeon and paddlefish listed under CITES', 'October 21, 2004: beluga sturgeon listed as threatened (U.S.)', 'September 30, 2005: U.S. suspends Caspian beluga caviar imports'], typed=True, src='U.S. Fish and Wildlife Service'))],
 '4.3': [(1, N('85%', 'of sturgeon species at risk of extinction · IUCN, 2010', count=True))],
 '4.4': [(1.3, M('world', highlight=['China', 'Italy', 'France', 'Poland', 'Israel', 'United States of America'], pins=[dict(lon=110, lat=31, label='China', at=.5), dict(lon=12.5, lat=42.5, label='Italy', at=.9, dy=40), dict(lon=2.3, lat=46.5, label='France', at=1.2, anchor='end', dx=-24), dict(lon=19.4, lat=52.2, label='Poland', at=1.5, dy=-18), dict(lon=35, lat=31.5, label='Israel', at=1.8), dict(lon=-120.5, lat=37.5, label='California', at=2.1)], label='China: the largest caviar producer')),
         (.9, PH('cs_polish-caviar-farm.png')),
         (.9, PH('catalog2026_page05.jpg', fit='contain'))],
 '4.5': [(1.3, P('american-hackleback-sturgeon-caviar', note=['Every lot, documented', 'CITES number on the label. Permit copy on file.'])),
         (1, D('label', title='Fish and Wildlife Service · NOAA · Department of Agriculture'))],
 '4.6': [(1.2, M('mississippi', states=True, rivers=[dict(name='mississippi', at=.2, color='#3e6a8f'), dict(name='white', at=.6, color='#3e6a8f')], pins=[dict(lon=-91.6, lat=30.9, label='Louisiana bowfin', at=1.5)], label='2022/23 season: bowfin catch under 10% of usual quota (Caviar Star’s fishing partners)', zoom=[1.1, 1.2])),
         (1, PH('cs_product_bowfin-styled.jpg'))],
 '4.7': [(1, LN(["March 28, 2022 · 'Do we still get caviar from Russia?'", 'No.'], per=2.4)),
         (1.2, P('lyna-polska-royal-osetra-caviar', note=['Osetra', 'The "Russian sturgeon", farmed in Poland']))],
 '5.1': [(.8, T(logo='cs_logo_caviar-star-black.png', title='CAVIAR STAR', kicker='The house brand')),
         (1.3, P(KALUGA_TIN))],
 '5.2': [(.8, T(title='December 26, 2011', sub='The Wandering Eater', kicker='A Christmas Eve dinner')),
         (1.4, P('classic-california-white-sturgeon-caviar', 'american-paddlefish-caviar', 'lyna-polska-royal-osetra-caviar', labels=['American white sturgeon', 'Paddlefish', 'Osetra']))],
 '5.3': [(1, Q("Caviar is a luxury, but at Caviar Star, it's a luxury meant to be enjoyed.", 'Caviar Star', bg='baldor_cs_circle-of-spoons.jpg'))],
 '5.4': [(1, PH('gat_caviar-tins-production-line_2020.jpg', cap='8,500 sq ft · 3 walk-in coolers · 2 freezers (company figures)')),
         (1.3, P('american-hackleback-sturgeon-caviar', 'american-paddlefish-caviar', 'golden-whitefish-roe', 'american-salmon-caviar', labels=['Hackleback', 'Paddlefish', 'Golden whitefish', 'Salmon roe'], cap='1 oz to 1 kg, packed daily to order'))],
 '5.5': [(1, T(kicker='The Local Palate · November 21, 2021', title='NEARLY 10 TONS', sub='of caviar a year · family-owned and operated'))],
 '5.6': [(1, D('box', title='2018: recycled cotton and denim insulation · 2023: carbon-neutral shipping'))],
 '6.1': [(1.2, dict(type='pages', srcs=['catalog2026_page01.jpg', 'catalog2026_page06.jpg', 'catalog2026_page13.jpg'])),
         (1.1, M('world', highlight=['United States of America', 'France', 'Spain', 'Italy', 'Poland', 'Bulgaria', 'China', 'Denmark', 'Romania', 'Taiwan', 'Germany', 'Norway', 'Canada', 'Turkey'], label='14 countries in the 2026 catalog')),
         (1.3, P('caviar-cloche-with-silver-sturgeon-handle', 'mother-of-pearl-spoon-3-5', 'fresh-summer-black-truffles', labels=['Caviar cloche', 'Mother of pearl spoon', 'Black summer truffles']))],
 '6.2': [(1, P('american-hackleback-sturgeon-caviar', note=['Hackleback', 'Missouri and Mississippi rivers'])),
         (1, P('american-paddlefish-caviar', note=['Paddlefish', 'The spoonbill'])),
         (1, P('american-bowfin-caviar', note=['Bowfin', 'Louisiana'])),
         (1, P('royal-california-white-sturgeon-caviar', note=['White sturgeon', 'Farmed in California']))],
 '6.3': [(1, P('caviar-house-prunier-osetra-caviar', note=['Prunier', 'Caviar house: 1921'])),
         (1, P('lyna-polska-siberian-caviar', note=['Lyna River farm', 'Since 1967'])),
         (.9, PH('catalog2026_page05.jpg', fit='contain')),
         (1, P(KALUGA_TIN))],
 '6.4': [(1.3, P('bourbon-barrel-smoked-trout-roe', note=['Cold-smoked', 'Bourbon barrel stave chips · no liquid smoke'])),
         (.8, PH('cs_product_bourbon-smoked-trout-roe.jpg'))],
 '6.5': [(1.2, P('100-year-aged-balsamic-vinegar', note=['Acetaia Reale, Modena', 'Recipe since 1896 · aged 100 years'])),
         (1.1, P('maine-lobster-meat-cooked-claw-and-knuckle', note=['Maine lobster', 'Cooked claw and knuckle'])),
         (.7, M('gulf-maine', pins=[dict(PORTLAND, at=.2)], zoom=[1.1, 1.14]))],
 '6.6': [(1, D('recipe')), (1.1, P('caviar-star-black-ot-gift-bag', note=['Chubby Fish', 'Charleston, SC']))],
 '7.1': [(1, PH('archival_japan-group-photo_dana-denise_SCAN0069.jpg', mono=True)), (1, PH('catalog2026_page04.jpg', fit='contain'))],
 '7.2': [(1.2, LN(['Dana C. Leavitt · 2015', 'Derek Leavitt · 2018', 'Deanna Leavitt · 2026 catalog'], typed=True)),
         (1, Q('Life is too short for mediocre caviar.', 'Deanna Leavitt'))],
 '7.3': [(1.1, P('american-salmon-caviar', note=['2026', 'A low Alaska salmon catch'])), (1, PH('baldor_cs_osetra-and-white-sturgeon.jpg'))],
 '7.4': [(1, Q('QUOTE74', None, mark='gat_logo_trident-2022.png'))],
 '8.1': [(.8, M('east-coast', pins=[dict(OIB, at=.2)], states=True, zoom=[1.1, 1.16])), (.8, PH('gat_caviar-tins-production-line_2020.jpg')),
         (.6, N('85%', 'of sturgeon species at risk of extinction', count=False)), (.8, PH('archival_japan-street_dana_date-stamp-4-18-9x.jpg', mono=True)),
         (1, PH('archival_dana-leavitt-drysuit-on-boat_SCAN0024.jpg', mono=True, kb=[[1.2, .02, -.02], [1.04, 0, 0]]))],
 '8.2': [(1.4, P(KALUGA_TIN)), (1, T(logo='gat_logo_estd-1991.png', title='GREAT ATLANTIC', sub='Great Atlantic Trading Inc. · Caviar Star · Ocean Isle Beach, North Carolina'))],
}

if __name__ == '__main__':
    import re
    scenes = json.load(open('build/scenes.json'))
    dur = json.load(open('build/audio/durations.json'))
    script = open('script.md').read()
    XF = 0.7
    out = []
    WORDS = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight'}
    last = 0
    for s in scenes:
        if s['chapter'] != last and s['chapter'] > 0:
            out.append({'id': f"ch{s['chapter']}", 'dur': 4.0, 'audio': None, 'chapter': s['chapter'], 'chapter_title': s['chapter_title'],
                        'shots': [dict(type='title', kicker=f"Chapter {WORDS[s['chapter']]}", title=s['chapter_title'].upper(), start=0, dur=4.0)]})
        last = s['chapter']
        sid = s['id']; spec = S[sid]
        D_ = dur[sid] + 1.1  # narration + breath
        n = len(spec); tot = D_ + (n - 1) * XF; wsum = sum(w for w, _ in spec)
        t = 0; shots = []
        for w, sh in spec:
            d = tot * w / wsum
            sh = dict(sh); sh['start'] = round(t, 3); sh['dur'] = round(d, 3)
            if sh.get('text') == 'QUOTE74':
                m = re.search(r'### Scene 7\.4.*?NARRATION:\n(.*?)\n\s*\n', script, re.S)
                q = re.findall(r'"([^"]+)"', m.group(1)) if m else []
                sh['text'] = q[0] if q else s['narration'].split('. ')[0]
            shots.append(sh); t += d - XF
        out.append({'id': sid, 'dur': round(D_, 3), 'shots': shots, 'audio': f'build/audio/{sid}.wav', 'chapter': s['chapter'], 'chapter_title': s['chapter_title']})
    json.dump(out, open('build/timeline.json', 'w'), indent=1)
    print(len(out), 'scenes', round(sum(x['dur'] for x in out) / 60, 2), 'min')
