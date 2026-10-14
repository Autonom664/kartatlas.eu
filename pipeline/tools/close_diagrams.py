# usage: python -I close_diagrams.py research/out/maps/M01.json [...]
# Post-processes traced layout diagrams in place: an open trace whose ends nearly meet is closed, and a
# short pit-lane stub at either end (the line runs out to a dead end and back to the loop) is trimmed first.
import sys, json
import numpy as np
for f in sys.argv[1:]:
    recs = json.load(open(f, encoding='utf-8')); changed = 0
    for r in recs:
        ld = r.get('layout_diagram')
        if not ld or ld.get('closed'): continue
        P = np.array(ld['points'], float); n = len(P)
        tol = 0.07 * np.ptp(P, 0).max()
        best = None
        for i in range(0, n // 4):            # trim up to 25% from the start ...
            for j in range(n - 1, n - 1 - n // 4, -1):  # ... and/or from the end
                d = np.hypot(*(P[i] - P[j]))
                if d < tol and (best is None or i + (n - 1 - j) < best[0]): best = (i + (n - 1 - j), i, j)
            if best and best[0] <= i: break
        if not best and np.hypot(*(P[0] - P[-1])) < 0.15 * np.ptp(P, 0).max():
            best = (0, 0, n - 1)  # ends close together: a short missing straight, close as is
        if best:
            _, i, j = best
            ld['points'] = [[round(float(x), 1), round(float(y), 1)] for x, y in P[i:j + 1]]
            ld['closed'] = True
            ld['note'] = ((ld.get('note') or '') + f'; closed after trimming {i} start / {n - 1 - j} end points (pit stub or gap)').lstrip('; ')
            changed += 1
    json.dump(recs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f, 'closed', changed)
