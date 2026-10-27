"""Textura de pintura amarilla a rodillo para rellenar letras (background-clip:text): pasadas horizontales de
rodillo con su veta, zonas con más y menos carga de pintura, grano fino y algún poro donde la capa es fina
(ahí asoma el fondo). Se repite en horizontal sin costura."""
import sys
import numpy as np
from PIL import Image, ImageFilter

W, H = 1600, 520
rng = np.random.default_rng(21)


def desenfoca(a, r):
    img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def norm(a):
    return (a - a.min()) / (a.max() - a.min())


def ruido_ciclico(escala_x, escala_y, radio):
    """Ruido suave que se repite en horizontal: se genera el doble de ancho y se funden los extremos."""
    base = rng.uniform(0, 1, (H // escala_y + 2, W // escala_x + 2)).astype(np.float32)
    img = Image.fromarray((base * 255).astype(np.uint8)).resize((W + escala_x * 2, H + escala_y * 2), Image.BICUBIC)
    a = np.asarray(img).astype(np.float32)[:H, :W] / 255
    a = desenfoca(a, radio)
    borde = W // 8
    t = np.linspace(0, 1, borde)[None, :]
    a[:, :borde] = a[:, :borde] * t + a[:, -borde:] * (1 - t)
    return norm(a)


# pasadas del rodillo: bandas horizontales de distinta carga
pasadas = np.zeros((H, W), np.float32)
y = 0
while y < H:
    alto = int(rng.uniform(60, 130))
    pasadas[y:y + alto] = rng.uniform(-.5, .5)
    y += alto
pasadas = desenfoca(norm(pasadas), 10)
veta = ruido_ciclico(90, 2, 1.2)          # vetas finas a lo largo de la pasada
carga = ruido_ciclico(260, 120, 30)      # zonas con más o menos pintura
grano = norm(desenfoca(rng.uniform(0, 1, (H, W)).astype(np.float32), .8))

luz = .5 * pasadas + .25 * veta + .25 * carga
luz = norm(luz)
# color: amarillo de obra con variaciones de tono (más cálido donde hay más carga)
r = 246 + 8 * (luz - .5) + 4 * (grano - .5)
g = 200 + 26 * (luz - .5) + 6 * (grano - .5) - 8 * (carga - .5)
b = 30 + 22 * (luz - .5) + 8 * (grano - .5)
# opacidad: casi opaca, con poros y zonas finas donde asoma el fondo
alfa = .97 - .1 * np.clip(.45 - carga, 0, 1) - .06 * (1 - veta) * (carga < .35)
poros = np.zeros((H, W), np.float32)
for _ in range(1400):
    px, py, rr = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(.6, 1.8)
    x0, x1, y0, y1 = int(max(0, px - 3)), int(min(W, px + 4)), int(max(0, py - 3)), int(min(H, py + 4))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
    poros[y0:y1, x0:x1] = np.maximum(poros[y0:y1, x0:x1], np.clip(rr - d + .5, 0, 1) * rng.uniform(.4, .9))
alfa = np.clip(alfa - .75 * poros, 0, 1)
rgba = np.dstack([np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255), alfa * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(sys.argv[1], 'WEBP', quality=86, method=6, alpha_quality=90)
print('pintura', rgba.shape)
