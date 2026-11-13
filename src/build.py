"""Genera dotplot.html e mappa.html dal dataset CNA (foglio Dataset_109)."""
import json, sys, pathlib
import pandas as pd

XLSX = sys.argv[1]
GEO = sys.argv[2]  # geometrie province (dalla mappa Michelin, già proiettate)
OUT = pathlib.Path(__file__).resolve().parent.parent

d = pd.read_excel(XLSX, sheet_name="Dataset_109", header=2, keep_default_na=False, na_values=[""]).dropna(subset=["Regione"])  # "NA" = Napoli
d.columns = ["citta", "sigla", "regione", "area", "profilo", "a19", "a25", "vc", "stip", "vr", "inc", "annuo", "mesi", "scarto"]

G = json.load(open(GEO, encoding="utf8"))
alias = {"Reggio Calabria": "Reggio Di Calabria", "Reggio Emilia": "Reggio Nell'Emilia",
         "Verbano-Cusio-Ossola": "Verbania", "Sud Sardegna": "Carbonia"}
xy = {c["nome"]: c["xy"] for f in G["f"] for c in f["caps"]}
xy["Cesena"] = [286.3, 209.8]  # tra Forlì e Rimini, assente nella base Michelin

rows = []
for r in d.itertuples():
    p = xy.get(alias.get(r.citta, r.citta))
    if p is None:
        raise SystemExit(f"coordinate mancanti: {r.citta}")
    rows.append({"c": r.citta, "s": r.sigla, "r": r.regione, "a19": int(r.a19), "a25": int(r.a25),
                 "vc": float(r.vc), "vr": float(r.vr), "st": int(r.stip), "inc": float(r.inc),
                 "m": float(r.mesi), "sc": float(r.scarto), "xy": p})

geo = {"w": G["w"], "h": G["h"], "d": [f["d"] for f in G["f"]]}
for name in ("dotplot", "mappa"):
    t = (OUT / "src" / f"{name}.tpl.html").read_text(encoding="utf8")
    t = t.replace("/*ROWS*/", json.dumps(rows, ensure_ascii=False)).replace("/*GEO*/", json.dumps(geo))
    (OUT / f"{name}.html").write_text(t, encoding="utf8")
print(len(rows), "capoluoghi")
