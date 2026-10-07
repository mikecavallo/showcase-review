#!/usr/bin/env python3
"""Catalog for the gallery page: web/catalog.json"""
import json, re, html
P = {p['handle']: p for p in json.load(open('src/products.json'))}
spec = json.load(open('work/spec.json'))
def cat(t, k):
    tl = t.lower()
    if k == 'tin' or 'gift' in tl or 'certificate' in tl or 'chocolate' in tl: return 'Gifts'
    if k == 'jar' or re.search(r'\broe\b|caviar(?!.*(spoon|server|cloche|key|dish|palette|plate))', tl) and not re.search(r'spoon|server|cloche|key|dish|palette|plate|fork|bowl', tl): return 'Caviar & Roe'
    if 'truffle' in tl and not re.search(r'slicer', tl): return 'Truffles'
    if re.search(r'vinegar|balsamic|glaze|saba|vincotto|sherry|pearls', tl): return 'Vinegars & Balsamic'
    if re.search(r'\boil\b', tl): return 'Oils'
    if re.search(r'spoon|fork|server|cloche|dish|palette|plate|bowl|platter|slicer|key|shell|abalone|keychain', tl): return 'Serveware'
    return 'Pantry & Sea'
def blurb(p):
    t = re.sub(r'<[^>]+>', ' ', p.get('body_html') or ''); t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
    s = re.split(r'(?<=[.!?])\s', t)
    out = ''
    for x in s:
        if len(out) + len(x) > 260: break
        out += (' ' if out else '') + x
    return out or t[:260]
items = []
for h, s in spec.items():
    p = P[h]
    items.append({'h': h, 't': p['title'], 'k': s['kind'], 'c': cat(p['title'], s['kind']), 'p': s['price'], 'a': s['available'],
                  'u': f'https://caviarstar.com/products/{h}', 'd': blurb(p)})
order = ['Caviar & Roe', 'Gifts', 'Truffles', 'Oils', 'Vinegars & Balsamic', 'Pantry & Sea', 'Serveware']
items.sort(key=lambda x: (order.index(x['c']), not x['a'], -float(x['p'])))
json.dump(items, open('web/catalog.json', 'w'))
from collections import Counter
print(Counter(i['c'] for i in items))
