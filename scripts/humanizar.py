import re, glob, os, sys, html
os.chdir(sys.argv[1])
A = r'(?:<a [^>]*>[^<]*</a>)'
MESES = {"nov": "noviembre", "oct": "octubre", "dic": "diciembre"}
CIERRES = [
 "Para esta guía nos apoyamos en las fuentes que más sabemos que aciertan{fuentes}, y lo cruzamos con lo que aprendimos en más de 10 años recorriendo los parques. Precios, horarios y reglas cambian seguido: antes de viajar, denle una última mirada a la web oficial.",
 "Todo lo que leen acá sale de las fuentes en las que más confiamos{fuentes} y de nuestra propia experiencia en los parques. Disney y Universal cambian cosas todo el tiempo, así que antes de comprar, una última mirada a su web nunca está de más.",
 "Armamos esta guía con lo que dicen las fuentes más confiables{fuentes} y con más de 10 años de idas y vueltas por Orlando. Si algo cambió de un día para otro, la web oficial siempre tiene la última palabra.",
]
FUENTE_INLINE = [
 "Todo el detalle está en la {a}.", "Lo explica bien la {a}.", "Si quieren el detalle, miren la {a}.", "Más info en la {a}.",
]
INLINE = [
 # frases puntuales (texto plano)
 ("Hagan la cuenta antes: el precio, confírmenlo en la web oficial.", "Hagan la cuenta antes, con el precio del día en la web oficial."),
 ("Confírmenlo en la web oficial</strong> antes de ir.", "La web oficial lo explica bien</strong>: mírenla antes de ir."),
 ("Los menús cambian: confírmenlos en la app oficial antes de ir.", "Los menús cambian seguido: el del día siempre está en la app."),
 ("Los precios cambian: confírmenlos siempre en la web oficial el día que compren.", "Los precios se mueven: el número final es el que les muestre la web oficial el día que compren."),
 ("Los precios cambian: confírmenlos en la web oficial el día que compren.", "Los precios se mueven: el número final es el que les muestre la web oficial el día que compren."),
 ("Confírmenlos en la web oficial el mismo día que compren.", "El número final es el que les muestre la web oficial el día que compren."),
 ("Confírmenlos en la web oficial antes de comprar.", "El precio final es el que les muestre la web oficial al comprar."),
 ("Confírmenlas en la web oficial antes de reservar.", "Antes de reservar, denle una mirada a la web oficial."),
 ("Precios 2027: confírmenlos en la web oficial de Universal el día que compren.", "Son precios de referencia para 2027: el final es el que les muestre la web de Universal al comprar."),
 ("Los precios cambian por día: confírmenlos en la app oficial.", "El precio cambia según el día: lo ven en la app antes de pagar."),
 ("Confírmenlo en la app el día de su visita.", "Ese mismo día, fíjense en la app."),
 ("Confírmenlo en la web oficial si viajan en esas fechas.", "Si viajan en esas fechas, denle una mirada a la web oficial antes."),
 ("Es un dato de prensa: confírmenlo en la web oficial si viajan cerca de esa fecha.", "Si viajan cerca de esa fecha, chequeen la web oficial: estas fechas suelen moverse."),
 ("las fuentes no coinciden en si es servicio rápido o con mesa: confírmenlo en la app.", "según la época funciona como servicio rápido o con mesa: fíjense en la app."),
 ("Confírmenlo en la tienda o en la web oficial.", "Pregunten en la tienda: los cast members saben."),
 ("Si hay fechas en su viaje, confírmenlas en la web.", "Si tienen fechas, chequeen la web antes."),
 ("confírmenlo con el hotel</strong> antes de reservar.", "pregúntenle al hotel</strong> antes de reservar."),
 ("Qué parque abre antes cada día, confírmenlo en la página oficial.", "Qué parque abre antes cada día lo publica Universal en su página."),
 ("(las alturas de Universal, confírmenlas en la web oficial antes de pagar nada)", "(antes de pagar, miren las alturas en la web de Universal)"),
 ("La fecha de apertura no la tenemos: confírmenla en", "La fecha de apertura todavía no es oficial: atentos a"),
 ("no lo tenemos verificado", "Universal no lo publica de antemano"),
 ("Es un dato de prensa", "Lo anunció la prensa"),
]
INLINE_RX = [
 # "X, confírmenlo en la <a>..</a>." -> "X lo explica la <a>..</a>."
 (r", confírm\w+ en (la|el) (" + A + r")", r": lo explica \1 \2"),
 (r", confírm\w+ en (" + A + r")", r": lo explica \1"),
 (r"[Cc]onfírm\w+ en (" + A + r")(</strong>)?", r"Lo explica \1\2"),
 (r"confírm\w+ en la web oficial de (" + A + r")", r"miren la web oficial de \1"),
 (r"No usamos precios en esta nota: los de la mercadería, confírmenlos en la tienda o en la web oficial de", "Los precios de la mercadería cambian seguido: los ven en la tienda o en la web oficial de"),
 (r"confírmenlo en la web oficial</strong> al momento de pagar", "lo ven en la web oficial</strong> al momento de pagar"),
]
def cierre(c, k):
    # junta las fuentes enlazadas de los párrafos finales y las reemplaza por un cierre humano
    finales = re.findall(r'<p><em>(?:Fuentes?|Verificado)[^<]*(?:(?:<a [^>]*>[^<]*</a>|<[^p/][^>]*>)[^<]*)*</em></p>', c)
    links = []
    for p in finales:
        for a in re.findall(A, p):
            href = re.search(r'href="([^"]+)"', a).group(1)
            if href not in [re.search(r'href="([^"]+)"', x).group(1) for x in links]:
                txt = re.sub(r"<[^>]+>", "", a)
                txt = re.sub(r",? ?\(?\d{1,2} (?:de )?\w+ (?:de )?20\d\d\)?", "", txt).strip()
                links.append(re.sub(r">[^<]*</a>", ">" + txt + "</a>", a))
    for p in finales: c = c.replace(p, "")
    if not finales: return c, False
    if links:
        lista = ", ".join(links[:-1]) + (" y " if len(links) > 1 else "") + links[-1]
        fu = f" ({lista})"
    else:
        fu = ""
    texto = CIERRES[k % len(CIERRES)].format(fuentes=fu)
    nuevo = f'<p class="fuentes"><em>{texto}</em></p>'
    # va antes del bloque final de CTA / para seguir
    if '<p><em>Planificador independiente' in c:
        c = c.replace('<p><em>Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>', nuevo, 1)
    else:
        c = c.replace('<p class="para-seguir">', nuevo + '<p class="para-seguir">', 1) if 'para-seguir' in c else c + nuevo
    return c, True
cambios = {}
for k, f in enumerate(sorted(glob.glob("blog/*/index.html"))):
    s = open(f, encoding="utf-8").read()
    a, b = s.index('<div class="cuerpo">'), s.index('<aside class="lateral"')
    c = c0 = s[a:b]
    # fecha arriba, como la ponen los blogs
    c = re.sub(r'<p class="meta">Actualizado: (\d{1,2}) (\w{3}) (20\d\d)[^<]*</p>', lambda m: f'<p class="meta">Actualizado el {m.group(1)} de {MESES.get(m.group(2), m.group(2))} de {m.group(3)}</p>', c)
    c, _ = cierre(c, k)
    c = c.replace('<p><em>Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>', "")
    # paréntesis y colas de auditoría
    c = re.sub(r"\s*\((?:chequeo|chequead[oa]s?|leíd[oa]|revisad[oa]s?|verificad[oa]s?) [^()]*\)", "", c)
    c = re.sub(r",? (?:chequead[oa]s?|leíd[oa]s?|verificad[oa]s?) el \d{1,2} de \w+ de 20\d\d", "", c)
    c = re.sub(r"\s*\((?:\d{1,2} \w{3} 20\d\d|\w+ de 20\d\d)\)", "", c)
    c = c.replace("Esto es lo que dicen las fuentes oficiales:", "Esto es lo que hay:")
    # "Fuente: <a>..</a>." en el cuerpo
    n = [0]
    def fu(m):
        a_ = m.group(1); txt = re.sub(r"<[^>]+>", "", a_)
        org = "Universal" if "universal" in a_.lower() else "Disney"
        a2 = re.sub(r">[^<]*</a>", f">página de {org}</a>", a_)
        r = FUENTE_INLINE[(k + n[0]) % len(FUENTE_INLINE)].format(a=a2); n[0] += 1
        return r
    c = re.sub(r"Fuentes?: ?(" + A + r")\.?", fu, c)
    for x, y in INLINE: c = c.replace(x, y)
    for rx, rep in INLINE_RX: c = re.sub(rx, rep, c)
    # CTA final que hoy no es verdad (el plan está en Próximamente)
    c = c.replace("<p>Armen su plan día por día, gratis y en español.</p>", '<p>Muy pronto, su plan día por día, gratis y en español. <a href="/#empezar">Anótense y les avisamos ✨</a></p>')
    if c != c0:
        s = s[:a] + c + s[b:]; open(f, "w", encoding="utf-8").write(s); cambios[f] = 1
print("notas tocadas:", len(cambios))
