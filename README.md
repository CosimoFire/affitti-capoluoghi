# Affitti e stipendi nei capoluoghi di provincia (2019-2025)

Due grafici interattivi su dati CNA (foglio `Dataset_109`, 109 capoluoghi di provincia).

- `dotplot.html`: aumento degli stipendi e degli affitti 2025 rispetto al 2019, città ordinate per scarto (punti percentuali).
- `mappa.html`: incidenza dell'affitto medio (70 mq) sullo stipendio netto medio, 2025.

Medie semplici sui 109 capoluoghi: stipendi +8,9%, affitti +23,9%, scarto 15,0 punti.

## Embed

```html
<iframe src="https://cosimofire.github.io/affitti-capoluoghi/dotplot.html"
        title="Gli affitti corrono più degli stipendi"
        style="width:100%;border:0;height:2250px" scrolling="no"></iframe>
```

```html
<iframe src="https://cosimofire.github.io/affitti-capoluoghi/mappa.html"
        title="Quanto pesa l'affitto sullo stipendio"
        style="width:100%;border:0;height:1100px" scrolling="no"></iframe>
```

Altezza automatica: aggiungere una volta nella pagina (stesso script di golden power, sirene e Michelin):

```html
<script>
window.addEventListener('message', function (e) {
  if (e.origin !== 'https://cosimofire.github.io') return;
  if (!e.data || !e.data.gpEmbed || !e.data.height) return;
  document.querySelectorAll('iframe').forEach(function (f) {
    if (f.contentWindow === e.source) f.style.height = e.data.height + 'px';
  });
});
</script>
```

## Rigenerare

```
python src/build.py affitti_capoluoghi_provincia.xlsx dati/province_geo.json
```

## Note

- Perugia non è presente nel dataset CNA.
- Geometrie e posizioni dei capoluoghi riprese dalla mappa del repo stelle-michelin; Cesena posizionata tra Forlì e Rimini.
- Nella lettura dell'Excel la sigla "NA" (Napoli) va trattata come testo, non come valore mancante.
