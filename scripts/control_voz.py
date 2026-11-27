#!/usr/bin/env python3
"""Control de voz de Bruno: frena textos que suenan a informe o a máquina.
Uso: python3 scripts/control_voz.py web   (sale con error si encuentra algo)"""
import re, glob, html, sys, os
os.chdir(sys.argv[1] if len(sys.argv) > 1 else "web")
PROHIBIDO = {
 "fecha de auditoría (leímos/chequeo/verificado el...)": r"[Ll]eímos el|[Cc]onsultamos el \d|chequeo del|chequead[oa]s? el|[Vv]erificad[oa]s? el|revisad[oa]s? el \d|leíd[oa] el",
 "'revisado/verificado contra fuentes oficiales'": r"(?:revisad|verificad|chequead)[oa]s? contra",
 "'confírmenlo' (máximo 0: usar 'denle una mirada a la web oficial')": r"[Cc]onfírm|[Cc]onfirmen en",
 "'Fuente:' suelto": r"\bFuentes?:",
 "fecha entre paréntesis en el texto": r"\([^()]{0,40}\b\d{1,2} (?:de )?\w+\.? (?:de )?20\d\d\)",
 "'base verificada' / 'a confirmar' / 'no lo tenemos'": r"base verificada|(?<!par)a confirmar|no l[oa] tenemos",
 "'la respuesta corta' / 'en resumen' / 'en conclusión'": r"[Ll]a respuesta corta|[Ee]n resumen,|[Ee]n conclusión",
 "jerga de sistema (porcentaje exacto, garantía, estimación)": r"no es un porcentaje|no una garantía|es una estimación",
 "nombre de ranking ajeno con fecha": r"ranking de \w+ \(",
}
fallas = 0
for f in sorted(glob.glob("**/index.html", recursive=True)):
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<figcaption.*?</figcaption>|<head.*?</head>", "", s, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", s))
    for nombre, rx in PROHIBIDO.items():
        for m in re.finditer(rx, t):
            fallas += 1
            print(f"✗ {f}: {nombre}\n    …{re.sub(r'\s+', ' ', t[max(0, m.start()-70):m.end()+50])}…")
print("OK: sin marcas de máquina" if not fallas else f"\n{fallas} frases para reescribir")
sys.exit(1 if fallas else 0)
