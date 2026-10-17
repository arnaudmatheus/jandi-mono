"""A corsiva for Jandí Mono's Italic, after Manuel de Andrade de Figueiredo.

Model: plate nº 7 of *Nova Escola para aprender a ler, escrever e contar*
(Lisboa Occidental, 1722; Biblioteca Nacional de Portugal, purl.pt/107,
page 91 of the digitised copy). Figueiredo, born in the Captaincy of Espírito
Santo, Brazil, taught this Portuguese cursive at the Lisbon court; by 1725
his models ornamented the brotherhood statute books of Minas Gerais.

What the plate gives, adapted to a monospace cell:
- looped ascenders on h k (and on l, kept above the x-height): a hairline
  rising to the right, turning over the top and coming down as the stem;
- the bastarda d, whose ascender curls back to the left;
- a descender that ends in a sweeping leftward rasgo (p), kept inside the
  cell so neighbours never collide;
- long rising exits and lead-ins: the cursive rhythm, with the hand still
  lifting between letters (no joins — the grid needs that).

Same skeleton grid as tools/pen.py; letters not listed here keep the roman
skeletons and become cursive through the italic's slant and contrast."""
from pen import path, T, B, A, D, BOWL_R, ARCH
import pen

# Corsiva lead-in and exit: longer, rising hairlines.
def ENTRY_C(x, top):
    return [('M', (x - 170, top - 240)), ('C', (x - 110, top - 120), (x - 50, top - 30), (x, top))]

def EXIT_C(x):
    return [('L', (x, 190)), ('C', (x, 80), (x + 60, 40), (x + 130, 70)), ('C', (x + 170, 90), (x + 200, 130), (x + 220, 180))]

def LOOP_UP(x, base_y=380):
    """Looped ascender opening to the right of the stem at x (plate 7: h k).
    The hairline starts low, crosses the stem near the x-height and the loop
    takes the whole ascender, so its counter stays open at 12 px."""
    return [('M', (x - 80, base_y)), ('C', (x + 80, 700), (x + 360, 1050), (x + 360, 1320)),
            ('C', (x + 360, 1440), (x + 270, A + 20), (x + 170, A + 20)),
            ('C', (x + 70, A + 20), (x, 1440), (x, 1300))]

def RASGO(x, end=170):
    """Descender ending in a leftward sweep (plate 7: p q f), inside the cell."""
    return [('L', (x, -190)), ('C', (x, -320), (x - 80, D), (x - 200, D)),
            ('C', (x - 290, D), (x - 340, -330), (x - 330, -280))]

def c_b():
    # b sem laçada (como na 1ª linha da folha nº 7): o laço fica para h k l, e é
    # justamente ele que separa o h do b — com os dois laçados, h/b mediam 0.97.
    return [path(*ENTRY_C(330, pen.A), ('L', (330, 110))), path(('M', (330, 620)), *BOWL_R)]

def c_d():
    bowl = pen.strokes_a()[0]
    # O d bastardo: a haste sobe e enrola de volta para a esquerda no topo.
    stem = path(('M', (590, 1330)), ('C', (600, 1450), (700, A + 30), (800, A + 30)), ('C', (880, A + 30), (905, 1440), (905, 1340)),
                *EXIT_C(905))
    return [bowl, stem]

def c_h():
    return [path(*LOOP_UP(330), ('L', (330, 40))), path(('M', (330, 640)), *ARCH, *EXIT_C(905))]

def c_k():
    stem = path(*LOOP_UP(330), ('L', (330, 40)))
    loop = path(('M', (330, 430)), ('C', (480, 650), (760, 990), (870, 885)), ('C', (950, 805), (830, 600), (470, 520)))
    leg = path(('M', (600, 545)), ('C', (720, 420), (790, 130), (880, 75)), ('C', (930, 45), (990, 70), (1050, 140)))
    return [stem, loop, leg]

def c_l():
    # Laço só acima da altura-x: cruzando a haste na altura-x, ele punha tinta
    # onde o t tem a barra (l/t 0.861 → 0.896).
    loop = [('M', (480, 1190)), ('C', (640, 1260), (940, 1280), (940, 1380)),
            ('C', (940, 1460), (830, A + 25), (720, A + 25)),
            ('C', (610, A + 25), (560, 1450), (560, 1340))]
    # A cauda é a do romano (longa, até 885): com a saída curta da corsiva, a
    # base do l ficava igual à do t.
    return [path(*loop, ('L', (560, 260)), ('C', (560, 110), (630, 45), (730, 55)),
                 ('C', (810, 65), (860, 120), (885, 190)))]

def c_f():
    # Descendente reto com um corte para a direita: com o rasgo para a esquerda
    # o f virava j a 12 px (o j fica com o gancho grande).
    hook = path(('M', (1000, 1330)), ('C', (950, 1450), (850, 1482), (750, 1482)), ('C', (620, 1482), (560, 1400), (560, 1250)),
                ('L', (560, -250)), ('C', (560, -320), (590, D), (660, -340)))
    bar = path(('M', (300, T - 10)), ('L', (880, T - 10)))
    return [hook, bar]

def c_p():
    return [path(*ENTRY_C(330, T), *RASGO(330)), path(('M', (330, 620)), *BOWL_R)]

def c_n():
    entry = path(*ENTRY_C(330, T), ('L', (330, 40)))
    # O arco sai alto da haste, como no romano. Saindo de baixo (do jeito que a
    # mão bastarda escreve o n de um gesto só), fechava o canto inferior
    # esquerdo e o n virava u: n/u 0.898 → 0.934.
    # Saída curta do romano: com a saída longa da corsiva o n ficava espelho
    # do u, que entra reto e sai longo.
    arch = path(('M', (330, 760)), ('C', (390, 930), (520, T), (650, T)), ('C', (810, T), (905, 880), (905, 700)),
                ('L', (905, 170)), ('C', (905, 90), (950, 55), (1030, 95)))
    return [entry, arch]

def c_m():
    first = path(*ENTRY_C(250, T), ('L', (250, 40)))
    arch1 = path(('M', (250, 640)), ('C', (300, 890), (380, T), (450, T)), ('C', (560, T), (600, 880), (600, 700)), ('L', (600, 40)))
    arch2 = path(('M', (600, 640)), ('C', (650, 890), (730, T), (800, T)), ('C', (910, T), (950, 880), (950, 700)),
                 ('L', (950, 190)), ('C', (950, 80), (1000, 40), (1060, 70)), ('C', (1090, 90), (1110, 130), (1120, 170)))
    return [first, arch1, arch2]

def c_u():
    # Sem a entrada longa: n e u com a mesma entrada e a mesma saída viram
    # espelhos (n/u 0.898 → 0.94). O u entra reto, como na folha nº 7.
    left = path(('M', (330, T)), ('L', (330, 300)), ('C', (330, 140), (430, B), (560, B)), ('C', (700, B), (830, 150), (905, 320)))
    stem = path(('M', (905, T)), *EXIT_C(905))
    return [left, stem]

def c_a():
    bowl, _ = pen.strokes_a()
    return [bowl, path(('M', (905, T)), *EXIT_C(905))]

def c_i_dotless():
    return [path(*ENTRY_C(560, T), *EXIT_C(560))]

def c_i():
    return c_i_dotless() + [path(('M', (557, 1267)), ('L', (593, 1303)))]

def c_t():
    return [path(('M', (560, 1180)), *EXIT_C(560)), path(('M', (430, T - 10)), ('L', (880, T - 10)))]

def c_c():
    # Sem gota: na pena de pressão ela quase fechava o c (c/o 0.900 → 0.944).
    return [path(('M', (890, 870)), ('C', (830, 960), (740, T), (630, T)), ('C', (430, T), (320, 760), (320, 520)),
                 ('C', (320, 240), (440, B), (620, B)), ('C', (760, B), (860, 130), (935, 240)))]

def c_r():
    # Braço curto, sem gota, deixando aberto o canto de cima à direita: é ali
    # que o n tem o ombro. Com o braço longo, r/n piorava.
    return [path(*ENTRY_C(330, T), ('L', (330, 40))),
            path(('M', (330, 700)), ('C', (390, 900), (500, T), (620, T)), ('C', (720, T), (790, 950), (815, 905)))]

CORSIVA = {
    'a': c_a, 'b': c_b, 'c': c_c, 'd': c_d, 'f': c_f, 'h': c_h, 'i': c_i, 'k': c_k, 'l': c_l,
    'm': c_m, 'n': c_n, 'p': c_p, 'r': c_r, 'u': c_u, 'dotlessi': c_i_dotless,
}
