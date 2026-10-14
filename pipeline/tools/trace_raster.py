# Trace a kart-track centre line from a raster track graphic (PNG/JPG/WebP).
# usage: python -I trace_raster.py IMAGE OUT_PREFIX [--color R,G,B] [--tol 60] [--light] [--dark]
#                                  [--open 3] [--close 0] [--points 110] [--maxside 900]
# Writes OUT_PREFIX.json ({"points", "closed", "coverage", "pixels"}) and OUT_PREFIX_overlay.png
# (the source dimmed, with the traced line in red) so the result can be checked visually.
# Pick the mask with --color (the track's colour), --light (white/very light strokes) or --dark.
# --close R joins the two edge lines of an outlined "ribbon" into one band before thinning.
import sys, json, argparse
import numpy as np, cv2
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument('image'); ap.add_argument('out')
ap.add_argument('--color'); ap.add_argument('--tol', type=float, default=60)
ap.add_argument('--light', action='store_true'); ap.add_argument('--dark', action='store_true')
ap.add_argument('--open', type=int, default=3); ap.add_argument('--close', type=int, default=0)
ap.add_argument('--points', type=int, default=110); ap.add_argument('--maxside', type=int, default=900)
a = ap.parse_args()

src = cv2.imread(a.image, cv2.IMREAD_UNCHANGED)
if src is None: sys.exit('cannot read image')
if src.ndim == 2: src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGRA)
if src.shape[2] == 3: src = cv2.cvtColor(src, cv2.COLOR_BGR2BGRA)
s = a.maxside / max(src.shape[:2])
if s < 1: src = cv2.resize(src, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
bgr, alpha = src[:, :, :3].astype(int), src[:, :, 3]
if a.color:
    r, g, b = map(int, a.color.split(','))
    m = np.sqrt(((bgr - [b, g, r]) ** 2).sum(2)) < a.tol
elif a.light: m = bgr.min(2) > 215
elif a.dark: m = bgr.max(2) < 70
else: sys.exit('choose --color, --light or --dark')
m &= alpha > 128
m = m.astype(np.uint8)
disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
if a.close: m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(a.close))
if a.open: m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(a.open))
lab, n = ndimage.label(m, structure=np.ones((3, 3)))
if not n: sys.exit('mask is empty: adjust --color/--tol')
sizes = ndimage.sum(m, lab, range(1, n + 1))  # keep every substantial piece: artwork often has hairline gaps
m = np.isin(lab, 1 + np.nonzero(sizes >= 0.15 * sizes.max())[0]).astype(np.uint8)
# fill tiny holes (labels, dashes) inside the band, not the infield
holes = ndimage.binary_fill_holes(m) & ~m.astype(bool)
hl, hn = ndimage.label(holes)
if hn:
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    for i, sz in enumerate(hs):
        if sz < 0.002 * m.size: m[hl == i + 1] = 1
sk = cv2.ximgproc.thinning(m * 255) // 255 if hasattr(cv2, 'ximgproc') else None
if sk is None:  # Zhang-Suen, vectorised
    sk = m.copy()
    while True:
        changed = False
        for step in (0, 1):
            P = [np.roll(np.roll(sk, -dy, 0), -dx, 1) for dy, dx in ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))]
            B = sum(P); A = sum(((P[k] == 0) & (P[(k + 1) % 8] == 1)) for k in range(8))
            c1 = (P[0] * P[2] * P[4] == 0) if step == 0 else (P[0] * P[2] * P[6] == 0)
            c2 = (P[2] * P[4] * P[6] == 0) if step == 0 else (P[0] * P[4] * P[6] == 0)
            d = (sk == 1) & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if d.any(): sk[d] = 0; changed = True
        if not changed: break
K = np.ones((3, 3), int); K[1, 1] = 0
def nb(img): return ndimage.convolve(img.astype(int), K, mode='constant')
order = ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1))
H, W = sk.shape
def nbrs(img, x, y): return [(x + dx, y + dy) for dx, dy in order if 0 <= x + dx < W and 0 <= y + dy < H and img[y + dy, x + dx]]
# prune side spurs only: short branches from a loose end that reach a junction. Loose ends at
# artwork gaps (no junction nearby) are kept so the walk can bridge the gap.
L = int(0.05 * max(H, W))
for _ in range(3):
    n = nb(sk) * sk; cut = False
    for y0, x0 in zip(*np.nonzero(n == 1)):
        branch, x, y, prev = [(x0, y0)], x0, y0, None
        while len(branch) <= L:
            nx = [q for q in nbrs(sk, x, y) if q != prev and q not in branch]
            if len(nx) != 1 or n[nx[0][1], nx[0][0]] >= 3: break
            prev, (x, y) = (x, y), nx[0]; branch.append((x, y))
        nx = [q for q in nbrs(sk, x, y) if q not in branch]
        if len(branch) <= L and any(n[q[1], q[0]] >= 3 for q in nx):
            for bx, by in branch: sk[by, bx] = 0
            cut = True
    if not cut: break
ys, xs = np.nonzero(sk)
if len(xs) < 20: sys.exit('skeleton too small')
ends = [(x, y) for x, y in zip(xs, ys) if nb(sk)[y, x] == 1]
rem = sk.copy(); x, y = ends[0] if ends else (xs[0], ys[0])
path = [(x, y)]; rem[y, x] = 0
J = int(0.08 * max(H, W))  # largest gap the walk may bridge
while True:
    nx = nbrs(rem, x, y)
    nxt = nx[0] if nx else None
    if nxt is None:  # stuck: jump to the nearest remaining loose end, else nearest pixel
        rn = nb(rem) * rem
        for want in (1, None):
            yy, xx = np.nonzero((rn == 1) if want else rem)
            if len(xx):
                d2 = (xx - x) ** 2 + (yy - y) ** 2; k = int(np.argmin(d2))
                if d2[k] <= J * J: nxt = (int(xx[k]), int(yy[k])); break
        if nxt is None: break
    x, y = nxt; rem[y, x] = 0; path.append((x, y))
coverage = len(path) / len(xs)
P = np.array(path, float)
closed = np.hypot(*(P[0] - P[-1])) < 0.06 * max(m.shape)
k = 3; Ps = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))])
seg = np.hypot(*np.diff(np.vstack([Ps, Ps[:1]]) if closed else Ps, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
tt = np.linspace(0, cum[-1], a.points, endpoint=not closed)
Q = np.vstack([Ps, Ps[:1]]) if closed else Ps
pts = np.c_[np.interp(tt, cum, Q[:, 0]), np.interp(tt, cum, Q[:, 1])]
json.dump({'points': [[round(float(px), 1), round(float(py), 1)] for px, py in pts], 'closed': bool(closed),
           'coverage': round(coverage, 3), 'pixels': int(len(xs))}, open(a.out + '.json', 'w'))
ov = (bgr * 0.35 + 160 * 0.65).astype(np.uint8)
cv2.polylines(ov, [pts.astype(np.int32)], bool(closed), (0, 0, 255), 2)
cv2.imwrite(a.out + '_overlay.png', ov)
print(json.dumps({'closed': bool(closed), 'coverage': round(coverage, 3), 'skeleton_px': int(len(xs)), 'size': list(m.shape[::-1])}))
