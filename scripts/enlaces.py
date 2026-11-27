import re, glob, os, sys, collections
os.chdir(sys.argv[1])
REGLAS = [
 (r"Rider Switch|cambio de padres", "cambio-de-padres-rider-switch"),
 (r"Lightning Lane", "vale-la-pena-lightning-lane"),
 (r"alturas? mínimas?", "alturas-minimas-disney"),
 (r"Express (?:Pass|Unlimited)", "express-pass-universal-hoteles"),
 (r"Epic Universe", "epic-universe-guia-primera-visita"),
 (r"Islands of Adventure", "mejores-atracciones-islands-of-adventure"),
 (r"Universal Studios Florida", "mejores-atracciones-universal-studios-florida"),
 (r"Magic Kingdom", "mejores-atracciones-magic-kingdom"),
 (r"EPCOT", "mejores-atracciones-epcot"),
 (r"Hollywood Studios", "mejores-atracciones-hollywood-studios"),
 (r"Animal Kingdom", "mejores-atracciones-animal-kingdom"),
 (r"hoteles? de Disney", "dormir-dentro-o-fuera-de-disney"),
 (r"menos gente|multitudes", "cuando-hay-menos-gente-disney"),
 (r"cuántos días", "cuantos-dias-disney-universal"),
 (r"presupuesto", "cuanto-cuesta-disney-2027"),
 (r"propinas|impuestos", "gastos-ocultos-disney-orlando"),
 (r"abuelos", "abuelos-en-disney"),
 (r"bebés?", "centro-cuidado-bebes-disney"),
 (r"hablar inglés|sin inglés", "disney-sin-hablar-ingles"),
 (r"primera vez", "disney-world-primera-vez-guia-familias"),
 (r"recuerdos", "truco-recuerdos-disney"),
 (r"errores", "errores-primera-vez-disney"),
]
MAX = 5
BLOQUE = re.compile(r"(<p>.*?</p>|<li>.*?</li>)", re.S)
total = collections.Counter()
for f in sorted(glob.glob("blog/*/index.html")):
    me = f.split("/")[1]
    s = open(f, encoding="utf-8").read()
    a, b = s.index('<div class="cuerpo">'), s.index('<aside class="lateral"')
    cuerpo = s[a:b]
    globals()["puestos"] = 0
    ya = set(re.findall(r'href="/blog/([^"/#]+)/?', cuerpo))
    puestos = 0
    def en_bloque(m):
        global puestos
        blk = m.group(0)
        if puestos >= MAX or 'class="btn"' in blk: return blk
        partes = re.split(r"(<a\b.*?</a>|<[^>]+>)", blk, flags=re.S)
        for i, p in enumerate(partes):
            if puestos >= MAX: break
            if not p or p.startswith("<"): continue
            for rx, dest in REGLAS:
                if dest == me or dest in ya: continue
                mm = re.search(r"(?<![\wáéíóúñ])(" + rx + r")(?![\wáéíóúñ])", p)
                if mm:
                    p = p[:mm.start()] + f'<a href="/blog/{dest}/">{mm.group(1)}</a>' + p[mm.end():]
                    ya.add(dest); puestos += 1; total[dest] += 1
                    partes[i] = p
                    break  # un enlace por fragmento de texto
        return "".join(partes)
    # no tocar tablas ni el párrafo de fecha
    trozos = re.split(r"(<table.*?</table>)", cuerpo, flags=re.S)
    for k, t in enumerate(trozos):
        if not t.startswith("<table"):
            trozos[k] = BLOQUE.sub(en_bloque, t)
    nuevo = "".join(trozos)
    if nuevo != cuerpo:
        open(f, "w", encoding="utf-8").write(s[:a] + nuevo + s[b:])
    globals()["puestos"] = 0
print(sum(total.values()), "enlaces nuevos")
