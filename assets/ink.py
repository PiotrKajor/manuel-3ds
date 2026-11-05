"""Menuel - a small inking engine. Shapes are smooth splines. Each part gets a thick outer contour, thin inner lines
and automatic cel shading from one light direction (upper left), which is what makes the characters read as drawn."""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ni

SS = 5
INK = (20, 14, 30)


def S(x, y):
    """A sharp corner in a spline."""
    return (x, y, True)


def _cr(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        t = i / n
        t2, t3 = t * t, t * t * t
        out.append((.5 * (2 * p1[0] + (p2[0] - p0[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (3 * p1[0] - p0[0] - 3 * p2[0] + p3[0]) * t3),
                    .5 * (2 * p1[1] + (p2[1] - p0[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (3 * p1[1] - p0[1] - 3 * p2[1] + p3[1]) * t3)))
    return out


def spline(pts, closed=True, n=8):
    """Catmull-Rom through the points; S() points break the tangent to make a clean corner."""
    pts = list(pts)
    k = len(pts)
    out = []
    rng = range(k) if closed else range(k - 1)
    for i in rng:
        p1, p2 = pts[i], pts[(i + 1) % k]
        p0 = pts[(i - 1) % k] if (closed or i > 0) else p1
        p3 = pts[(i + 2) % k] if (closed or i + 2 < k) else p2
        if len(p1) == 3:
            p0 = p1
        if len(p2) == 3:
            p3 = p2
        out += _cr(p0, p1, p2, p3, n)
    if not closed:
        out.append(pts[-1][:2])
    return out


def poly_rot(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    out = []
    for p in pts:
        x, y = p[0] - cx, p[1] - cy
        q = (cx + x * c - y * s, cy + x * s + y * c)
        out.append(q + (True,) if len(p) == 3 else q)
    return out


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Part:
    """One body part. fill() builds the silhouette; shade() and line() stay inside it."""

    def __init__(self, art, ink):
        self.art = art
        self.ink = ink
        w, h = art.w * SS, art.h * SS
        self.size = (w, h)
        self.mask = Image.new('L', (w, h), 0)
        self.md = ImageDraw.Draw(self.mask)
        self.paint = Image.new('RGB', (w, h), (0, 0, 0))
        self.pd = ImageDraw.Draw(self.paint)
        self.after = []

    def _p(self, pts):
        return [(p[0] * SS, p[1] * SS) for p in pts]

    def fill(self, pts, col, smooth=True):
        q = self._p(spline(pts) if smooth else pts)
        self.md.polygon(q, fill=255)
        self.pd.polygon(q, fill=col)
        return self

    def circle(self, x, y, rx, ry=None, col=(255, 255, 255)):
        ry = rx if ry is None else ry
        b = ((x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS)
        self.md.ellipse(b, fill=255)
        self.pd.ellipse(b, fill=col)
        return self

    def shade(self, pts, col, smooth=True):
        self.pd.polygon(self._p(spline(pts) if smooth else pts), fill=col)
        return self

    def dot(self, x, y, rx, ry=None, col=INK):
        ry = rx if ry is None else ry
        self.pd.ellipse(((x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS), fill=col)
        return self

    def line(self, pts, col=INK, w=.8, smooth=True):
        q = self._p(spline(pts, closed=False) if smooth and len(pts) > 2 else pts)
        self.pd.line(q, fill=col, width=max(1, int(w * SS)), joint='curve')
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            self.pd.ellipse((x - r, y - r, x + r, y + r), fill=col)
        return self

    def cel(self, col, dx=2.2, dy=2.6, strength=1.0):
        """Shadow on the side away from the light: everything not covered by the shape moved towards the light."""
        self.after.append(('cel', col, dx, dy, strength))
        return self

    def rim(self, col, dx=-1.0, dy=-1.1, strength=1.0):
        """Thin light along the edge that faces the light."""
        self.after.append(('cel', col, dx, dy, strength))
        return self


class Art:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h * SS, w * SS, 4), dtype=np.float32)   # premultiplied

    def part(self, ink=1.5):
        return Part(self, ink)

    def add(self, p):
        m = np.asarray(p.mask, dtype=np.uint8) > 0
        if not m.any():
            return
        ys, xs = np.where(m)
        pad = int(p.ink * SS) + 12
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, m.shape[0])
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, m.shape[1])
        crop = m[y0:y1, x0:x1]
        col = np.asarray(p.paint, dtype=np.float32)[y0:y1, x0:x1].copy()
        for kind, c, dx, dy, st in p.after:
            sx, sy = int(round(dx * SS)), int(round(dy * SS))
            moved = ni.shift(crop.astype(np.uint8), (-sy, -sx), order=0, cval=0) > 0
            band = crop & ~moved
            band = ni.gaussian_filter(band.astype(np.float32), 1.2) * crop > .5
            col[band] = col[band] * (1 - st) + np.array(c, dtype=np.float32) * st
        # contour: dilate the silhouette, rounded by the blur
        if p.ink > 0:
            d = ni.distance_transform_edt(~crop)
            cont = (d <= p.ink * SS) & ~crop
        else:
            cont = np.zeros_like(crop)
        dst = self.px[y0:y1, x0:x1]
        ink = np.array((*INK, 255), dtype=np.float32)
        dst[cont] = ink
        dst[crop] = np.dstack([col, np.full(col.shape[:2], 255, dtype=np.float32)])[crop]

    def glow(self, pts, col, alpha, smooth=True):
        """Translucent shape behind everything drawn later, used for swing smears and auras."""
        im = Image.new('L', (self.w * SS, self.h * SS), 0)
        ImageDraw.Draw(im).polygon([(p[0] * SS, p[1] * SS) for p in (spline(pts) if smooth else pts)], fill=255)
        a = (np.asarray(im, dtype=np.float32) / 255 * alpha)[..., None]
        src = np.dstack([np.full(a.shape[:2], c, dtype=np.float32) for c in col] + [np.full(a.shape[:2], 255, dtype=np.float32)])
        self.px = self.px * (1 - a) + src * a

    def done(self):
        h, w = self.h, self.w
        a = self.px[:, :, 3:4] / 255
        rgb = np.where(a > 0, self.px[:, :, :3] / np.maximum(a, 1e-3), 0)
        arr = np.dstack([rgb, self.px[:, :, 3]]).clip(0, 255).astype(np.uint8)
        im = Image.fromarray(arr, 'RGBA')
        return im.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')


def ease(t):
    return t * t * (3 - 2 * t)


def tau(t):
    return math.sin(t * math.tau)
