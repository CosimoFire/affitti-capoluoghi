"""Versioni statiche SVG di dotplot e mappa (stesso stile delle pagine interattive)."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output"; OUT.mkdir(exist_ok=True)
rows = json.loads(re.search(r"const ROWS = (\[.*?\]);", (ROOT / "dotplot.html").read_text(encoding="utf8"), re.S).group(1))
geo = json.loads(re.search(r"const GEO = (\{.*?\});", (ROOT / "mappa.html").read_text(encoding="utf8"), re.S).group(1))

BLU, GR, GRC, INK, INK2, MUT = "#169cdc", "#9b9b9b", "#d9d9d9", "#1a1a1a", "#444", "#6b6b6b"
FONT = "font-family=\"'Source Serif 4',Georgia,serif\""
it = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
esc = lambda s: s.replace("&", "&amp;").replace("'", "&#39;")

def head(W, H, title, sub):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
            f'<rect width="{W}" height="{H}" fill="#fff"/>',
            f'<text x="12" y="44" font-size="30" font-weight="700" fill="{INK}">{esc(title)}</text>',
            *[f'<text x="12" y="{72 + i*20}" font-size="15" fill="{INK2}">{esc(l)}</text>' for i, l in enumerate(sub)]]

def foot(W, y, text):
    return [f'<line x1="12" x2="{W-12}" y1="{y}" y2="{y}" stroke="{GRC}" stroke-width="2"/>',
            f'<text x="12" y="{y+20}" font-size="12.5" fill="{INK2}"><tspan font-weight="700">Fonte:</tspan> {esc(text)}</text>', "</svg>"]

# ---------- dotplot ----------
R = sorted(rows, key=lambda r: -r["sc"])
W, rh, l, r_, top = 620, 17, 120, 16, 160
ih = len(R) * rh; H = top + ih + 24 + 50
hi = -(-max(r["vc"] for r in R) // 10) * 10
x = lambda v: l + v / hi * (W - l - r_)
s = head(W, H, "Gli affitti corrono più degli stipendi",
         ["Capoluoghi di provincia ordinati per scarto tra crescita degli affitti e", "degli stipendi, 2025 rispetto al 2019"])
s += [f'<circle cx="18" cy="118" r="5.5" fill="{GR}"/><text x="29" y="123" font-size="14" fill="{INK2}">Aumento stipendi 2025 vs 2019</text>',
      f'<circle cx="250" cy="118" r="5.5" fill="{BLU}"/><text x="261" y="123" font-size="14" fill="{INK2}">Aumento dell&#39;affitto 2025 vs 2019</text>',
      f'<line x1="0" x2="{W}" y1="134" y2="134" stroke="{GRC}" stroke-width="2"/>']
for v in range(0, int(hi) + 1, 10):
    lab = f"+{v}%" if v else "0%"
    s += [f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top-4}" y2="{top+ih}" stroke="#e6e6e6"/>',
          f'<text x="{x(v):.1f}" y="{top-10}" font-size="12" fill="{MUT}" text-anchor="middle">{lab}</text>',
          f'<text x="{x(v):.1f}" y="{top+ih+16}" font-size="12" fill="{MUT}" text-anchor="middle">{lab}</text>']
for i, r in enumerate(R):
    y = top + i * rh + rh / 2
    s += [f'<text x="{l-8}" y="{y+4:.1f}" font-size="13" fill="{INK}" text-anchor="end">{esc(r["c"])}</text>',
          f'<line x1="{x(r["vr"]):.1f}" x2="{x(r["vc"]):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRC}" stroke-width="3"/>',
          f'<circle cx="{x(r["vr"]):.1f}" cy="{y:.1f}" r="4.5" fill="{GR}"/><circle cx="{x(r["vc"]):.1f}" cy="{y:.1f}" r="4.5" fill="{BLU}"/>']
s += foot(W, H - 34, "elaborazione CNA. Affitto medio di un'abitazione di 70 mq, stipendio netto medio mensile")
(OUT / "dotplot_affitti_stipendi_2019-2025.svg").write_text("\n".join(s), encoding="utf8")

# ---------- mappa ----------
STOPS = [(0xee, 0xf8, 0xfd), (0x16, 0x9c, 0xdc), (0x07, 0x3f, 0x5e)]
inc = [r["inc"] for r in rows]
LO, HI = int(min(inc) // 10 * 10), int(-(-max(inc) // 10) * 10)
def col(v):
    t = max(0, min(1, (v - LO) / (HI - LO))) * 2; i = min(1, int(t)); f = t - i
    return "#%02x%02x%02x" % tuple(round(a + (b - a) * f) for a, b in zip(STOPS[i], STOPS[i + 1]))
W, sc = 620, 520 / geo["w"]; mh = geo["h"] * sc; top = 170; H = int(top + mh + 60)
s = head(W, H, "Quanto pesa l'affitto sullo stipendio",
         ["Affitto medio di un'abitazione di 70 mq in percentuale dello stipendio", "netto medio, capoluoghi di provincia, 2025"])
s += [f'<text x="12" y="122" font-size="14" font-weight="600" fill="{INK2}">Incidenza affitto/stipendio</text>',
      '<defs><linearGradient id="g">' + "".join(f'<stop offset="{k/2}" stop-color="#%02x%02x%02x"/>' % c for k, c in enumerate(STOPS)) + "</linearGradient></defs>",
      f'<rect x="12" y="130" width="300" height="12" fill="url(#g)"/>']
for v in range(LO, HI + 1, 10):
    px = 12 + (v - LO) / (HI - LO) * 300
    anc = "start" if v == LO else "end" if v == HI else "middle"
    s.append(f'<text x="{px:.1f}" y="156" font-size="12" fill="{MUT}" text-anchor="{anc}">{v}%</text>')
s.append(f'<line x1="0" x2="{W}" y1="164" y2="164" stroke="{GRC}" stroke-width="2"/>')
s.append(f'<g transform="translate({(W-520)/2:.1f},{top}) scale({sc:.5f})">')
s += [f'<path d="{d}" fill="#f2f2f2" stroke="#fff" stroke-width="0.6"/>' for d in geo["d"]]
s += [f'<circle cx="{r["xy"][0]}" cy="{r["xy"][1]}" r="6.5" fill="{col(r["inc"])}" stroke="#9b9b9b" stroke-opacity="0.5" stroke-width="1.2"/>'
      for r in sorted(rows, key=lambda r: r["inc"])]
# etichette: prime 3 e ultime 3 per incidenza (lato dell'etichetta scelto per non coprire altri capoluoghi)
srt = sorted(rows, key=lambda r: r["inc"])
LATO = {"Vercelli": "end"}
# Milano sta in mezzo a molti capoluoghi: etichetta spostata nell'area vuota a nord-ovest, con linea di richiamo
FUORI = {"Milano": (-40, 52)}
fs = 13 / sc
lead = [f'<line x1="{r["xy"][0]}" y1="{r["xy"][1]}" x2="{FUORI[r["c"]][0] + 117}" y2="{FUORI[r["c"]][1] + 4}" stroke="{INK}" stroke-width="{1/sc:.2f}"/>'
        for r in srt[-3:] if r["c"] in FUORI]
i0 = next(i for i, x in enumerate(s) if x.startswith("<circle") and "r=\"6.5\"" in x)
s[i0:i0] = lead  # linee sotto i pallini
for r in srt[:3] + srt[-3:]:
    cx, cy = r["xy"]; a = LATO.get(r["c"], "start"); dx = -10 if a == "end" else 10
    s.append(f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    if r["c"] in FUORI:
        (tx, ty), dx, a = FUORI[r["c"]], 0, "start"; cx, cy = tx, ty - fs * 0.35
    s.append(f'<text x="{cx+dx}" y="{cy+fs*0.35:.1f}" font-size="{fs:.1f}" text-anchor="{a}" fill="{INK}" stroke="#fff" stroke-width="{4/sc:.1f}" '
             f'stroke-linejoin="round" paint-order="stroke"><tspan font-weight="700">{esc(r["c"])}</tspan> {it(r["inc"],1)}%</text>')
s.append("</g>")
s += foot(W, H - 34, "elaborazione CNA. Perugia non è presente nel dataset")
(OUT / "mappa_incidenza_affitto_stipendio_2025.svg").write_text("\n".join(s), encoding="utf8")
print("ok")
