# usage: python -I review_diagrams.py OUT.png research/out/maps/M01.json [...]
# Draws every traced layout_diagram as the atlas will show it (y down, not to scale) on one contact sheet.
import sys, json
import numpy as np, cv2
recs = [(f, r) for f in sys.argv[2:] for r in json.load(open(f, encoding='utf-8')) if r.get('layout_diagram')]
tile, cols = 300, 5
rows = max(1, -(-len(recs) // cols))
img = np.full((rows * tile, cols * tile, 3), 255, np.uint8)
for k, (f, r) in enumerate(recs):
    ld = r['layout_diagram']; P = np.array(ld['points'], float)
    ox, oy = (k % cols) * tile, (k // cols) * tile
    mn, mx = P.min(0), P.max(0); sc = min((tile - 30) / max(mx[0] - mn[0], 1), (tile - 60) / max(mx[1] - mn[1], 1))
    Q = ((P - mn) * sc + [ox + 15, oy + 45]).astype(np.int32)
    cv2.polylines(img, [Q], bool(ld.get('closed')), (40, 40, 40), 6); cv2.polylines(img, [Q], bool(ld.get('closed')), (255, 255, 255), 1)
    cv2.circle(img, tuple(int(v) for v in Q[0]), 5, (0, 160, 0), -1); cv2.circle(img, tuple(int(v) for v in Q[-1]), 5, (0, 0, 220), -1)
    cv2.putText(img, f"{k} {r['id']}", (ox + 4, oy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.putText(img, f"{'closed' if ld.get('closed') else 'OPEN'} {ld.get('method','')} {(ld.get('note') or '')[:28]}", (ox + 4, oy + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (90, 90, 90), 1)
    cv2.rectangle(img, (ox, oy), (ox + tile - 1, oy + tile - 1), (200, 200, 200), 1)
cv2.imwrite(sys.argv[1], img); print(len(recs), 'diagrams')
