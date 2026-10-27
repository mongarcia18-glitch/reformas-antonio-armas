"""Textura de rayas de carretera pintadas: cuatro tramos distintos (para que no se repitan iguales) con bordes
algo irregulares, vetas del rodillo, poros por donde asoma el suelo, zonas gastadas y salpicaduras finas.
Se dibuja a 3x (cada tramo ocupa 150x20 px de CSS) y se guarda como webp con transparencia."""
import sys
import numpy as np
from PIL import Image, ImageFilter

S = 3                      # escala de dibujo
TRAMO_W, TRAMO_H = 150 * S, 20 * S
RAYA_X0, RAYA_X1 = 3 * S, 121 * S
RAYA_Y0, RAYA_Y1 = 3 * S, 17 * S
N_TRAMOS = 4


def suave(rng, n, paso, amp):
    """Ruido 1D suave: valores aleatorios cada «paso» píxeles, interpolados."""
    puntos = rng.uniform(-amp, amp, n // paso + 3)
    x = np.arange(n) / paso
    i = x.astype(int)
    f = x - i
    f = f * f * (3 - 2 * f)
    return puntos[i] * (1 - f) + puntos[i + 1] * f


def desenfoca(a, radio):
    img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radio))).astype(np.float32) / 255


def tramo(semilla):
    rng = np.random.default_rng(semilla)
    h, w = TRAMO_H, TRAMO_W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # bordes: casi rectos, con la irregularidad de la pintura sobre el asfalto
    arriba = RAYA_Y0 + suave(rng, w, 40, 1.1) + suave(rng, w, 6, .45)
    abajo = RAYA_Y1 + suave(rng, w, 40, 1.1) + suave(rng, w, 6, .45)
    izq = RAYA_X0 + suave(rng, h, 12, 1.4) + rng.uniform(-1, 1) * (yy[:, 0] - h / 2) * .05
    der = RAYA_X1 + suave(rng, h, 12, 1.4) + rng.uniform(-1, 1) * (yy[:, 0] - h / 2) * .05
    dentro = (yy >= arriba[None, :]) & (yy <= abajo[None, :]) & (xx >= izq[:, None]) & (xx <= der[:, None])
    alfa = desenfoca(dentro.astype(np.float32), .9)
    # vetas del rodillo a lo largo de la raya
    vetas = np.repeat(rng.normal(0, 1, (h, w // 60 + 2)), 60, axis=1)[:, :w]
    vetas = desenfoca((vetas - vetas.min()) / (vetas.max() - vetas.min()), 4)
    alfa *= .95 + .05 * vetas
    # grano fino
    grano = desenfoca(rng.uniform(0, 1, (h, w)), .7)
    grano = (grano - grano.min()) / (grano.max() - grano.min())
    alfa *= .95 + .05 * grano
    # relieve del asfalto bajo la pintura: luces y sombras suaves, no agujeros
    relieve = desenfoca(rng.uniform(0, 1, (h, w)), 1.6)
    relieve = (relieve - relieve.min()) / (relieve.max() - relieve.min())
    # zonas gastadas, más hacia los extremos
    for _ in range(rng.integers(2, 5)):
        cx = rng.choice([rng.uniform(RAYA_X0, RAYA_X0 + 60), rng.uniform(RAYA_X0, RAYA_X1), rng.uniform(RAYA_X1 - 60, RAYA_X1)])
        cy = rng.uniform(RAYA_Y0, RAYA_Y1)
        r = rng.uniform(10, 26)
        alfa *= 1 - rng.uniform(.04, .1) * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    # poros: el suelo asoma por agujeritos de la pintura
    poros = np.zeros((h, w), np.float32)
    for _ in range(int((RAYA_X1 - RAYA_X0) * (RAYA_Y1 - RAYA_Y0) / 520)):
        px, py, r = rng.uniform(RAYA_X0, RAYA_X1), rng.uniform(RAYA_Y0, RAYA_Y1), rng.uniform(.6, 1.7)
        x0, x1, y0, y1 = int(px - 3), int(px + 4), int(py - 3), int(py + 4)
        d = np.sqrt((xx[y0:y1, x0:x1] - px) ** 2 + (yy[y0:y1, x0:x1] - py) ** 2)
        poros[y0:y1, x0:x1] = np.maximum(poros[y0:y1, x0:x1], np.clip(r - d + .5, 0, 1) * rng.uniform(.2, .45))
    alfa *= 1 - poros
    # salpicaduras finas junto a los bordes
    for _ in range(rng.integers(6, 12)):
        lado = rng.integers(4)
        if lado < 2:
            px = rng.uniform(RAYA_X0, RAYA_X1)
            py = (RAYA_Y0 - rng.uniform(1.5, 5)) if lado == 0 else (RAYA_Y1 + rng.uniform(1.5, 5))
        else:
            py = rng.uniform(RAYA_Y0, RAYA_Y1)
            px = (RAYA_X0 - rng.uniform(1.5, 5)) if lado == 2 else (RAYA_X1 + rng.uniform(1.5, 5))
        r = rng.uniform(.5, 1.2)
        d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        alfa = np.maximum(alfa, np.clip(r - d + .5, 0, 1) * rng.uniform(.35, .8))
    # color: blanco de pintura vial, apenas cálido, con algo de variación
    tono = 236 + 16 * relieve + 4 * vetas - 10 * poros
    rgb = np.stack([tono + 2, tono + 2, tono - 3], -1)
    return np.dstack([np.clip(rgb, 0, 255), np.clip(alfa, 0, 1) * 255]).astype(np.uint8)


if __name__ == '__main__':
    salida = sys.argv[1]
    tira = np.concatenate([tramo(11 + k * 7) for k in range(N_TRAMOS)], axis=1)
    Image.fromarray(tira, 'RGBA').save(salida, 'WEBP', quality=88, method=6, alpha_quality=92)
    print('raya', tira.shape)
