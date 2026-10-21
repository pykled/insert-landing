"""sRGB <-> OKLab/OKLCH, WCAG contrast, gamut mapping. numpy only.

OKLab matrices from Björn Ottosson, https://bottosson.github.io/posts/oklab/ (public domain).
"""
import math
import numpy as np

_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1i = np.linalg.inv(_M1)
_M2i = np.linalg.inv(_M2)


def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(np.clip(c, 0, None), 1 / 2.4) - 0.055)


def rgb_to_oklab(rgb):
    """rgb in 0..1, shape (...,3) -> OKLab (...,3)."""
    lin = np.ascontiguousarray(srgb_to_linear(np.clip(rgb, 0, 1)))
    with np.errstate(all='ignore'):
        lms = np.cbrt(lin @ _M1.T)
        out = lms @ _M2.T
    return out


def oklab_to_rgb(lab):
    lms = np.asarray(lab, dtype=np.float64) @ _M2i.T
    lms = lms ** 3
    lin = lms @ _M1i.T
    return linear_to_srgb(lin)


def lab_to_lch(lab):
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b)
    h = (np.degrees(np.arctan2(b, a)) + 360) % 360
    return np.stack([L, C, h], axis=-1)


def lch_to_lab(lch):
    L, C, h = lch[..., 0], lch[..., 1], np.radians(lch[..., 2])
    return np.stack([L, C * np.cos(h), C * np.sin(h)], axis=-1)


def in_gamut(rgb, eps=1e-4):
    return bool(np.all(rgb >= -eps) and np.all(rgb <= 1 + eps))


def lch_to_hex(L, C, h):
    """Convert OKLCH to a hex string, reducing chroma until in sRGB gamut."""
    lo, hi = 0.0, float(C)
    rgb = oklab_to_rgb(lch_to_lab(np.array([L, hi, h])))
    if not in_gamut(rgb):
        for _ in range(24):
            mid = (lo + hi) / 2
            rgb = oklab_to_rgb(lch_to_lab(np.array([L, mid, h])))
            if in_gamut(rgb):
                lo = mid
            else:
                hi = mid
        rgb = oklab_to_rgb(lch_to_lab(np.array([L, lo, h])))
    rgb = np.clip(rgb, 0, 1)
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in rgb)


def hex_to_rgb(hx):
    hx = hx.lstrip('#')
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hex_to_lch(hx):
    return lab_to_lch(rgb_to_oklab(np.array(hex_to_rgb(hx))))


def luminance(hx):
    r, g, b = srgb_to_linear(np.array(hex_to_rgb(hx)))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg_hex, bg_hex):
    lf, lb = luminance(fg_hex), luminance(bg_hex)
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


def fit_lightness(C, h, bg_hex, min_ratio, darker=True, L_start=None):
    """Find the OKLCH lightness (at chroma C, hue h) nearest to L_start that reaches min_ratio against bg.
    darker=True searches downward from L_start (text on light paper); False searches upward (text on dark)."""
    if L_start is None:
        L_start = 0.5
    L = L_start
    step = -0.01 if darker else 0.01
    best = None
    for _ in range(100):
        hx = lch_to_hex(L, C, h)
        if contrast(hx, bg_hex) >= min_ratio:
            best = (L, hx)
            break
        L += step
        if L < 0.02 or L > 0.995:
            break
    if best is None:
        L = 0.08 if darker else 0.98
        return L, lch_to_hex(L, min(C, 0.03), h)
    return best


def hue_distance(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def is_warm(h):
    """Warm hues on the OKLCH wheel: reds through yellows (roughly 10..110)."""
    return 10 <= h <= 110
