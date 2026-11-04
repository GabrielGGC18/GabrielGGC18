#!/usr/bin/env python3
"""Gera as peças SVG animadas do README do perfil em ``assets/``.

Uso (da raiz do repositório)::

    python scripts/gerar_svgs.py

Só biblioteca padrão. O GitHub mostra SVG dentro de ``<img>``, então:
nada de JavaScript, ``<foreignObject>`` ou arquivo externo (a logo entra
inline, com ids prefixados), animação só em SMIL, só fontes do sistema e
no máximo ~80 KB por arquivo. O "3D" vem de quadros calculados aqui.

Peças:
- ``assets/midia63-3d.svg``: card do Mídia 63 com a logo girando como uma
  moeda 3D (com espessura), anéis em órbita que passam por trás e pela
  frente dela, piso em perspectiva e sombra pulsando;
- ``assets/divisor.svg``: linha de separação entre seções.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
LOGO = ASSETS / "marca" / "midia63.svg"
LIMITE_BYTES = 80 * 1024

# Paleta do perfil (a mesma do banner e dos badges do README)
FUNDO = "#0a0e14"
PAINEL = "#161b22"
TEAL = "#5eead4"
CEU = "#38bdf8"
VIOLETA = "#a78bfa"
AMBAR = "#fbbf24"
TEXTO = "#e8edf4"
CINZA = "#8b97a8"
# Cores da marca Mídia 63 (frontend/src/styles/tailwind.css do projeto)
M63_AZUL = "#2563eb"
M63_CAMPO = "#172554"

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
SERIF = "Georgia, 'Times New Roman', serif"


def n(v: float, casas: int = 1) -> str:
    s = f"{v:.{casas}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def svg(largura: int, altura: int, titulo: str, desc: str, corpo: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}" role="img" aria-labelledby="t d">'
        f'<title id="t">{titulo}</title><desc id="d">{desc}</desc>{corpo}</svg>\n'
    )


def suave(dur: float, valores: str, attr: str, extra: str = "") -> str:
    """Animação de ida e volta com easing."""
    return (
        f'<animate attributeName="{attr}" values="{valores}" dur="{n(dur, 2)}s" repeatCount="indefinite" '
        f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"{extra}/>'
    )


def logo_inline(prefixo: str) -> tuple[str, float, float]:
    """Corpo da logo sem o <svg> externo, sem comentários e com ids prefixados."""
    fonte = LOGO.read_text(encoding="utf-8")
    fonte = re.sub(r"<!--.*?-->", "", fonte, flags=re.S)
    abertura = re.search(r"<svg\b[^>]*>", fonte)
    vb = re.search(r'viewBox="([\d.\s-]+)"', abertura.group(0)).group(1).split()
    largura, altura = float(vb[2]), float(vb[3])
    corpo = fonte[abertura.end() : fonte.rindex("</svg>")]
    for id_ in re.findall(r'\bid="([^"]+)"', corpo):
        corpo = corpo.replace(f'id="{id_}"', f'id="{prefixo}{id_}"')
        corpo = corpo.replace(f"url(#{id_})", f"url(#{prefixo}{id_})")
        corpo = corpo.replace(f'href="#{id_}"', f'href="#{prefixo}{id_}"')
    corpo = re.sub(r'\sdata-[\w-]+="[^"]*"', "", corpo)
    corpo = re.sub(r">\s+<", "><", corpo).strip()
    return corpo, largura, altura


# --------------------------------------------------------------------------- #
# card do Mídia 63 — 1000 × 340
# --------------------------------------------------------------------------- #
def card_midia63() -> str:
    W, H = 1000, 340
    cx, cy = 215.0, 150.0  # centro da moeda
    defs = [
        f'<linearGradient id="c-bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{FUNDO}"/><stop offset="0.55" stop-color="#0c1220"/>'
        f'<stop offset="1" stop-color="#0f1630"/></linearGradient>',
        f'<linearGradient id="c-borda" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">'
        f'<stop offset="0" stop-color="{TEAL}"/><stop offset="0.5" stop-color="{CEU}"/>'
        f'<stop offset="1" stop-color="{VIOLETA}"/></linearGradient>',
        f'<clipPath id="c-clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        f'<radialGradient id="c-halo" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CEU}" stop-opacity="0.32"/>'
        f'<stop offset="0.6" stop-color="{VIOLETA}" stop-opacity="0.08"/>'
        f'<stop offset="1" stop-color="{VIOLETA}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="c-sombra" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#000" stop-opacity="0.85"/>'
        f'<stop offset="0.55" stop-color="{M63_CAMPO}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="c-borda-moeda" gradientUnits="userSpaceOnUse" '
        f'x1="0" y1="{cy - 60}" x2="0" y2="{cy + 60}">'
        f'<stop offset="0" stop-color="#2a3f86"/><stop offset="0.5" stop-color="{M63_CAMPO}"/>'
        f'<stop offset="1" stop-color="#0b1330"/></linearGradient>',
        f'<filter id="c-glow" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="7" flood-color="{AMBAR}" flood-opacity="0.55"/></filter>',
        f'<filter id="c-ponto" x="-200%" y="-200%" width="500%" height="500%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="2.4" flood-color="{AMBAR}" flood-opacity="1"/></filter>',
        f'<linearGradient id="c-fade" gradientUnits="userSpaceOnUse" x1="0" y1="232" x2="0" y2="{H}">'
        f'<stop offset="0" stop-color="#000"/><stop offset="0.35" stop-color="#fff"/></linearGradient>',
        '<linearGradient id="c-fade-x" gradientUnits="userSpaceOnUse" x1="20" y1="0" x2="410" y2="0">'
        '<stop offset="0" stop-color="#000"/><stop offset="0.25" stop-color="#fff"/>'
        '<stop offset="0.75" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>',
        f'<mask id="c-piso-mask"><rect width="{W}" height="{H}" fill="url(#c-fade)"/></mask>',
        f'<mask id="c-piso-mask-x"><rect width="{W}" height="{H}" fill="url(#c-fade-x)"/></mask>',
        f'<linearGradient id="c-titulo" gradientUnits="userSpaceOnUse" x1="440" y1="0" x2="760" y2="0">'
        f'<stop offset="0" stop-color="{TEAL}"/>'
        f'<stop offset="0.45" stop-color="{CEU}">'
        f'<animate attributeName="offset" values="0.2;0.7;0.2" dur="8s" repeatCount="indefinite"/></stop>'
        f'<stop offset="1" stop-color="{VIOLETA}"/></linearGradient>',
    ]
    partes: list[str] = []

    # --- piso em perspectiva sob a moeda ------------------------------------ #
    y_h, y_b, vy = 236.0, float(H), 214.0
    piso = []
    for i in range(-9, 10):
        xb = cx + i * 70
        t = (y_h - vy) / (y_b - vy)
        piso.append(
            f'<line x1="{n(cx + (xb - cx) * t)}" y1="{y_h}" x2="{n(xb)}" y2="{y_b}"/>'
        )
    # linhas horizontais que vêm na direção de quem olha
    z_longe = (y_b + 10 - vy) / (y_h - vy)
    for i in range(6):
        fase = i / 6
        tempos = [k / 20 for k in range(21)]
        t_volta = (1 - fase) % 1
        chaves = [(t, (t + fase) % 1 if t < 1 else fase) for t in tempos]
        if 0 < t_volta < 1:
            chaves = [c for c in chaves if abs(c[0] - t_volta) > 0.002]
            chaves += [(t_volta - 0.0005, 0.9999), (t_volta + 0.0005, 0.0)]
            chaves.sort()

        def y_de(s: float) -> float:
            z = z_longe + (1 - z_longe) * s
            return vy + (y_b + 10 - vy) / z

        kt = ";".join(n(t, 4) for t, _ in chaves)
        ys = ";".join(n(y_de(s)) for _, s in chaves)
        os_ = ";".join(n(0 if s > 0.999 else min(1, s / 0.2), 2) for _, s in chaves)
        y0 = y_de(chaves[0][1])
        piso.append(
            f'<line x1="0" x2="440" y1="{n(y0)}" y2="{n(y0)}">'
            f'<animate attributeName="y1" values="{ys}" keyTimes="{kt}" dur="4s" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{ys}" keyTimes="{kt}" dur="4s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{os_}" keyTimes="{kt}" dur="4s" repeatCount="indefinite"/>'
            f"</line>"
        )
    partes.append(
        f'<g clip-path="url(#c-clip)"><g mask="url(#c-piso-mask-x)"><g mask="url(#c-piso-mask)" '
        f'stroke="{TEAL}" stroke-opacity="0.35" stroke-width="1">{"".join(piso)}</g></g>'
        f'<line x1="20" y1="{y_h}" x2="410" y2="{y_h}" stroke="{TEAL}" stroke-opacity="0.45" '
        f'mask="url(#c-piso-mask-x)"/></g>'
    )

    # halo e sombra
    partes.append(f'<ellipse cx="{cx}" cy="{cy}" rx="185" ry="140" fill="url(#c-halo)"/>')
    partes.append(
        f'<ellipse cx="{cx}" cy="262" rx="74" ry="11" fill="url(#c-sombra)">'
        + suave(4, "74;56;74", "rx")
        + suave(4, "1;0.55;1", "opacity")
        + "</ellipse>"
    )

    # estrelinhas piscando
    for k, (sx, sy, r) in enumerate([(70, 60, 1.6), (360, 48, 1.3), (335, 210, 1.5), (95, 205, 1.2), (300, 90, 1)]):
        partes.append(
            f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{TEXTO}">'
            f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{n(2.2 + 0.7 * k, 1)}s" '
            f'begin="{n(0.4 * k, 1)}s" repeatCount="indefinite"/></circle>'
        )

    # --- moeda 3D ------------------------------------------------------------ #
    corpo_logo, lw, lh = logo_inline("c-logo-")
    escala = 0.5
    raio = 118 * escala  # o disco da logo tem r = 118 no viewBox 240 × 256
    meia_espessura = 7.0
    quadros, dur_moeda = 48, 7.0
    lista_borda, lista_pos, lista_esc = [], [], []
    for k in range(quadros + 1):
        t = 2 * math.pi * k / quadros
        c, s = math.cos(t), math.sin(t)
        rx = max(abs(c) * raio, 0.01)
        # faces a ±e no eixo de profundidade; a borda é o casco entre as duas
        xa, xb = sorted((cx - meia_espessura * s, cx + meia_espessura * s))
        lista_borda.append(
            f"M{n(xa)},{n(cy - raio)}L{n(xb)},{n(cy - raio)}"
            f"A{n(rx)},{n(raio)} 0 0 1 {n(xb)},{n(cy + raio)}"
            f"L{n(xa)},{n(cy + raio)}A{n(rx)},{n(raio)} 0 0 1 {n(xa)},{n(cy - raio)}Z"
        )
        # face visível: a da frente (z = +e) quando cos > 0, a de trás quando cos < 0
        x_face = cx + (meia_espessura * s if c >= 0 else -meia_espessura * s)
        lista_pos.append(f"{n(x_face)} {n(cy)}")
        esc = c if abs(c) >= 0.04 else (0.04 if c >= 0 else -0.04)
        lista_esc.append(f"{n(esc, 3)} 1")

    def aneis(meio: str) -> str:
        """Metade de trás ('tras') ou da frente ('frente') dos dois anéis."""
        saida = []
        for rx_, ry_, ang, cor, sentido, dash in ((110, 27, -16, AMBAR, -1, "5 8"), (94, 34, 22, VIOLETA, 1, "3 7")):
            if meio == "tras":
                d = f"M{-rx_},0A{rx_},{ry_} 0 0 1 {rx_},0"
            else:
                d = f"M{rx_},0A{rx_},{ry_} 0 0 1 {-rx_},0"
            saida.append(
                f'<path d="{d}" transform="rotate({ang})" fill="none" stroke="{cor}" stroke-width="1.5" '
                f'stroke-opacity="{0.45 if meio == "tras" else 0.85}" stroke-dasharray="{dash}" stroke-linecap="round">'
                f'<animate attributeName="stroke-dashoffset" values="0;{sentido * 130}" dur="5s" '
                f'repeatCount="indefinite"/>'
                f"</path>"
            )
        return "".join(saida)

    def pontos() -> str:
        """Um ponto correndo em cada anel; some atrás da moeda."""
        saida = []
        for rx_, ry_, ang, cor, sentido, dur in ((110, 27, -16, AMBAR, 1, 5.0), (94, 34, 22, TEAL, -1, 6.5)):
            a = math.radians(ang)
            xs, ys, ops = [], [], []
            for k in range(41):
                f = sentido * 2 * math.pi * k / 40 + math.pi
                x0, y0 = rx_ * math.cos(f), ry_ * math.sin(f)
                x = x0 * math.cos(a) - y0 * math.sin(a)
                y = x0 * math.sin(a) + y0 * math.cos(a)
                xs.append(n(x))
                ys.append(n(y))
                ops.append("1" if math.sin(f) > -0.05 else "0.12")
            saida.append(
                f'<circle cx="{xs[0]}" cy="{ys[0]}" r="3.4" fill="{cor}" filter="url(#c-ponto)">'
                f'<animate attributeName="cx" values="{";".join(xs)}" dur="{n(dur)}s" repeatCount="indefinite"/>'
                f'<animate attributeName="cy" values="{";".join(ys)}" dur="{n(dur)}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{";".join(ops)}" dur="{n(dur)}s" '
                f'calcMode="discrete" repeatCount="indefinite"/></circle>'
            )
        return "".join(saida)

    moeda = (
        f'<path d="{lista_borda[0]}" fill="url(#c-borda-moeda)" stroke="{AMBAR}" stroke-opacity="0.55" '
        f'stroke-width="1">'
        f'<animate attributeName="d" values="{";".join(lista_borda)}" dur="{n(dur_moeda)}s" repeatCount="indefinite"/>'
        f"</path>"
        f'<g filter="url(#c-glow)"><g transform="translate({lista_pos[0]})">'
        f'<animateTransform attributeName="transform" type="translate" values="{";".join(lista_pos)}" '
        f'dur="{n(dur_moeda)}s" repeatCount="indefinite"/><g>'
        f'<animateTransform attributeName="transform" type="scale" values="{";".join(lista_esc)}" '
        f'dur="{n(dur_moeda)}s" repeatCount="indefinite"/>'
        f'<g transform="scale({escala}) translate({n(-lw / 2)} {n(-lh / 2)})">{corpo_logo}</g></g></g></g>'
    )
    flutua = (
        '<animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" '
        'dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
        'keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
    )
    # anéis de trás → moeda → anéis da frente → pontos (todos flutuam juntos)
    partes.append(
        f"<g>{flutua}"
        f'<g transform="translate({cx} {cy})">{aneis("tras")}</g>'
        f"{moeda}"
        f'<g transform="translate({cx} {cy})">{aneis("frente")}{pontos()}</g>'
        f"</g>"
    )

    # --- texto à direita ----------------------------------------------------- #
    x0 = 440
    itens = [
        "Painel editorial e API REST em Django 5.2 + DRF",
        "Site em React 19 com SEO pré-renderizado na Vercel",
        "Fábrica de Cortes: Shorts e Reels renderizados no FFmpeg",
        "Agentes de IA na curadoria, sempre com aprovação humana",
    ]
    texto = [
        f'<text x="{x0}" y="62" font-family="{MONO}" font-size="12" letter-spacing="4" fill="{CINZA}">'
        f"EM PRODUÇÃO · PORTAL DE NOTÍCIAS</text>",
        f'<text x="{x0 + 3}" y="123" font-family="{SANS}" font-weight="800" font-size="56" '
        f'fill="{M63_AZUL}" fill-opacity="0.35">Mídia 63</text>',
        f'<text x="{x0}" y="120" font-family="{SANS}" font-weight="800" font-size="56" '
        f'fill="url(#c-titulo)">Mídia 63</text>',
        f'<text x="{x0}" y="152" font-family="{SERIF}" font-style="italic" font-size="18" fill="{TEXTO}">'
        f"Notícias do Tocantins, do rascunho ao feed.</text>",
    ]
    for k, item in enumerate(itens):
        y = 192 + k * 28
        texto.append(
            f'<rect x="{x0 + 1}" y="{y - 9}" width="7" height="7" fill="{AMBAR}" '
            f'transform="rotate(45 {x0 + 4.5} {y - 5.5})"/>'
            f'<text x="{x0 + 20}" y="{y}" font-family="{SANS}" font-size="15" fill="{TEXTO}" fill-opacity="0.88">'
            f"{item}</text>"
        )
    texto.append(
        f'<text x="{x0}" y="318" font-family="{MONO}" font-size="13" fill="{TEAL}">midia63.com.br'
        f'<tspan fill="{CINZA}">  ·  Django · React · PostgreSQL · VPS + Vercel</tspan></text>'
    )
    partes.append("".join(texto))

    fundo = (
        f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="16" fill="url(#c-bg)" '
        f'stroke="url(#c-borda)" stroke-opacity="0.55" stroke-width="1.5"/>'
    )
    return svg(
        W,
        H,
        "Mídia 63 — portal de notícias do Tocantins",
        "Card do projeto Mídia 63 com a logo girando como uma moeda 3D, anéis em órbita e a lista do que o "
        "sistema faz.",
        f"<defs>{''.join(defs)}</defs>{fundo}{''.join(partes)}",
    )


# --------------------------------------------------------------------------- #
# divisor — 1000 × 24
# --------------------------------------------------------------------------- #
def divisor() -> str:
    W, H = 1000, 24
    defs = (
        f'<linearGradient id="d-linha" gradientUnits="userSpaceOnUse" x1="0" y1="12" x2="{W}" y2="12">'
        f'<stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset="0.25" stop-color="{TEAL}"/>'
        f'<stop offset="0.5" stop-color="{CEU}"/><stop offset="0.75" stop-color="{VIOLETA}"/>'
        f'<stop offset="1" stop-color="{VIOLETA}" stop-opacity="0"/></linearGradient>'
        f'<filter id="d-glow" x="-200%" y="-200%" width="500%" height="500%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="2.4" flood-color="{CEU}" flood-opacity="1"/></filter>'
    )
    corpo = (
        f'<line x1="0" y1="12" x2="{W}" y2="12" stroke="url(#d-linha)" stroke-width="1.2" stroke-opacity="0.8"/>'
        f'<circle cx="40" cy="12" r="2.4" fill="{CEU}" filter="url(#d-glow)" opacity="0">'
        f'<animate attributeName="cx" values="40;{W - 40}" dur="5s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="5s" '
        f'repeatCount="indefinite"/>'
        f"</circle>"
        f'<g transform="translate({W // 2} 12)"><rect x="-5.5" y="-5.5" width="11" height="11" fill="{FUNDO}" '
        f'stroke="{AMBAR}" stroke-width="1.6"><animateTransform attributeName="transform" type="rotate" '
        f'values="45;225;405" dur="6s" repeatCount="indefinite"/></rect>'
        f'<rect x="-1.8" y="-1.8" width="3.6" height="3.6" fill="{TEAL}" transform="rotate(45)"/></g>'
    )
    return svg(W, H, "Divisor", "Linha em gradiente com um losango girando no centro.", f"<defs>{defs}</defs>{corpo}")


def main() -> None:
    pecas = {
        ASSETS / "midia63-3d.svg": card_midia63(),
        ASSETS / "divisor.svg": divisor(),
    }
    for caminho, conteudo in pecas.items():
        dados = conteudo.encode("utf-8")
        if len(dados) > LIMITE_BYTES:
            raise SystemExit(f"{caminho.name}: {len(dados)} bytes passa do limite de {LIMITE_BYTES}")
        for proibido in ("<script", "<foreignObject", "@import", 'href="http'):
            if proibido in conteudo:
                raise SystemExit(f"{caminho.name}: contém {proibido!r}")
        caminho.write_bytes(dados)
        print(f"{caminho.relative_to(RAIZ)!s:<24} {len(dados) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
