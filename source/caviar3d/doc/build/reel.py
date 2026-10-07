#!/usr/bin/env python3
"""Reel shot list -> build/reel.json"""
import json
R = [
 (3.6, dict(type='title', k='Caviar Star', t='THE COLLECTION', s='in 3D', size=104)),
 (5.0, dict(type='prod', items=['kaluga-hybrid-caviar-limited-edition'], t='VIP Imperial Kaluga', sub='The Caviar Star OT tin')),
 (5.0, dict(type='prod', items=['dynasty-siberian-caviar', 'american-paddlefish-caviar', 'american-hackleback-sturgeon-caviar', 'american-salmon-caviar'], labels=['Siberian', 'Paddlefish', 'Hackleback', 'Salmon roe'], t='Caviar & roe', sub='Every jar under its own lid')),
 (5.0, dict(type='prod', items=['royal-california-white-sturgeon-caviar', 'golden-dynasty-imperial-osetra-caviar', 'albino-almas-caviar', 'golden-whitefish-roe'], labels=['White sturgeon', 'Golden osetra', 'Albino sterlet', 'Golden whitefish'])),
 (4.2, dict(type='prod', items=['fresh-black-burgundy-truffles'], t='Fresh Burgundy truffles', sub='Truffles')),
 (5.0, dict(type='prod', items=['black-truffle-paste', 'white-truffle-honey', 'whole-black-summer-truffles', 'black-truffle-olive-oil'], labels=['Truffle paste', 'Truffle honey', 'Summer truffles', 'Truffle oil'])),
 (4.2, dict(type='prod', items=['100-year-aged-balsamic-vinegar'], t='100 year balsamic', sub='Acetaia Reale, Modena')),
 (5.0, dict(type='prod', items=['unio-cava-wine-vinegar', 'leblanc-french-walnut-oil', 'pura-vida-pistachio-oil', 'il-casolare-italian-extra-virgin-olive-oil'], labels=['Cava vinegar', 'Walnut oil', 'Pistachio oil', 'Olive oil'], t='Oils & vinegars')),
 (5.0, dict(type='prod', items=['mother-of-pearl-mosaic-handle-spoon-4-75-inch', 'abalone-caviar-bowl-silver-accents', 'silver-fish-6-shot-glass-server', 'pink-mother-of-pearl-shell-plate-spoon-set'], labels=['Mosaic spoon', 'Abalone bowl', 'Shot-glass server', 'Shell plate'], t='Serveware')),
 (5.0, dict(type='prod', items=['bottarga-dried-and-cured-mullet-roe', 'mojama-hand-cured-tuna-in-sea-salt', 'irish-cold-smoked-atlantic-salmon', 'maine-lobster-meat-cooked-claw-and-knuckle'], labels=['Bottarga', 'Mojama', 'Smoked salmon', 'Maine lobster'], t='From the sea')),
 (4.4, dict(type='prod', items=['vip-kaluga-hybrid-caviar-250g'], t='VIP Kaluga', sub='250 g OT tin')),
 (4.4, dict(type='title', k='caviarstar.com', t='181 PIECES', s='Every one in 3D', size=110)),
]
XF = .5; t = 0; shots = []
for d, s in R:
    s = dict(s); s['start'] = round(t, 3); s['dur'] = d; shots.append(s); t += d - XF
json.dump({'dur': round(t + XF, 3), 'shots': shots}, open('build/reel.json', 'w'), indent=1)
print('reel', round(t + XF, 1), 's')
