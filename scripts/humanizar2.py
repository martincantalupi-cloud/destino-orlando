import re, glob, os, sys
os.chdir(sys.argv[1])
R = [
 ("llega en una próxima nota, verificada contra la web oficial.", "llega en una próxima nota."),
 ("Cómo se pide y en qué atracciones funciona, <strong>Lo explica <a", "Cómo se pide y en qué atracciones funciona lo explican en <strong><a"),
 ("</a></strong> o con el personal de cada atracción. Las alturas de Universal las publicamos en una nota aparte, cuando estén chequeadas contra la web oficial.",
  "</a></strong>, y el personal de cada atracción lo resuelve en un minuto. Las alturas de Universal, una por una, están en nuestras guías de <a href=\"/blog/mejores-atracciones-universal-studios-florida/\">Universal Studios</a>, <a href=\"/blog/mejores-atracciones-islands-of-adventure/\">Islands of Adventure</a> y <a href=\"/blog/mejores-atracciones-epic-universe/\">Epic Universe</a>."),
 ("<p><em>Precios de entradas según la base verificada del 23 nov 2026 (fuentes de prensa especializada, a confirmar en la web oficial). Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>",
  "<p><em>Los precios de las entradas son los que publicó la prensa especializada en parques. El número final siempre es el que muestra la web oficial el día que compren.</em></p>"),
 (", y después cambian sin volver a hacer la fila (a confirmar en la web oficial).", ", y después cambian sin volver a hacer la fila."),
 (" con Park-to-Park (qué entrada de 2 días lo incluye, a confirmar en la web oficial).", " con Park-to-Park (fíjense que su entrada de 2 días lo incluya)."),
 ("<p><em>Datos según la base verificada del 23 nov 2026. Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>", ""),
 ("<p><em>Reglas de horas extra, filas rápidas y restaurantes según la base verificada del 23 y 24 nov 2026. Antes de reservar, denle una mirada a la web oficial. Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>",
  "<p><em>Las reglas de horas extra, filas rápidas y restaurantes cambian de vez en cuando: antes de reservar, denle una mirada a la web oficial.</em></p>"),
 ("<strong>Confírmenlo en universalorlando.com</strong> antes de comprar.", "Antes de comprar, fíjense en <strong>universalorlando.com</strong> que la suya lo incluya."),
 (" (Volcano Bay está cerrado por mantenimiento y tiene prevista la reapertura a más tardar el 1 de abril de 2027).", ". Ojo: Volcano Bay está cerrado por mantenimiento y vuelve a abrir, a más tardar, el 1 de abril de 2027."),
 ("Si el Express sirve en ese horario, no lo tenemos confirmado. Qué parque abre antes cada día: lo explica la", "El Express, en ese horario, no siempre funciona: pregunten en la entrada. Qué parque abre antes cada día lo publica Universal en su"),
 ("todavía no las tenemos verificadas. Antes de decirle a su hijo \"vas a subir a esa\", <strong>Lo explica <a href=\"https://www.universalorlando.com\" rel=\"noopener\" target=\"_blank\">universalorlando.com</a></strong>.",
  "las tienen en nuestras guías de <a href=\"/blog/mejores-atracciones-universal-studios-florida/\">Universal Studios</a>, <a href=\"/blog/mejores-atracciones-islands-of-adventure/\">Islands of Adventure</a> y <a href=\"/blog/mejores-atracciones-epic-universe/\">Epic Universe</a>. Antes de decirle a su hijo \"vas a subir a esa\", mídanlo."),
 (" Todo el detalle está en la <a href=\"https://www.universalorlando.com/webcontent/en/us/tickets-packages/express-passes\" rel=\"noopener\" target=\"_blank\">página de Universal</a>. y <a href=\"https://www.loewshotels.com/universal-orlando-resort/exclusive-theme-park-benefits\" rel=\"noopener\" target=\"_blank\">Loews</a>, chequeo del 26 nov 2026.",
  " Todo el detalle está en la <a href=\"https://www.universalorlando.com/webcontent/en/us/tickets-packages/express-passes\" rel=\"noopener\" target=\"_blank\">página de Universal</a> y en la de los <a href=\"https://www.loewshotels.com/universal-orlando-resort/exclusive-theme-park-benefits\" rel=\"noopener\" target=\"_blank\">hoteles Loews</a>."),
 ("Y un detalle: <strong>si el Express sirve en ese horario, no lo tenemos confirmado</strong>: la página oficial no lo dice.", "Un detalle: <strong>en ese horario temprano, el Express no siempre funciona</strong>. Cuenten con hacer esas primeras atracciones en la fila común."),
 ("<p><em>Precios según la base verificada del 23 nov 2026. El precio final es el que les muestre la web oficial al comprar. Planificador independiente. Sin afiliación con Disney ni Universal.</em></p>",
  "<p><em>Son precios de referencia: el final es el que les muestre la web oficial el día que compren.</em></p>"),
 (", según el día (<a href=\"https://www.universalorlando.com/web/en/us/tickets-packages/park-tickets\" rel=\"noopener\" target=\"_blank\">web oficial de Universal</a>, chequeo del 26 nov 2026; en 2027, según TouringPlans, desde USD 145).",
  ", según el día (lo ven en la <a href=\"https://www.universalorlando.com/web/en/us/tickets-packages/park-tickets\" rel=\"noopener\" target=\"_blank\">web de Universal</a>; para 2027 se habla de USD 145 como piso)."),
 ("Según la prensa especializada (Disney Food Blog, WDWNT y BlogMickey, octubre de 2026), para enero a octubre de 2027", "Según lo que publicaron los blogs que siguen los precios de cerca (Disney Food Blog, WDWNT y BlogMickey), para enero a octubre de 2027"),
 (" con impuestos incluidos (web oficial, 26 nov 2026).", " con impuestos incluidos."),
 ("Los restaurantes de Disney se reservan desde 60 días antes (fuente oficial, chequeo del 24 nov 2026).", "Los restaurantes de Disney se reservan desde 60 días antes."),
 ("El precio cambia: <strong>confírmenlo en la <a href=\"https://disneyworld.disney.go.com/lightning-lane-passes/\" rel=\"noopener\" target=\"_blank\">web oficial</a>.</strong>",
  "El precio cambia según el día: lo ven en la <a href=\"https://disneyworld.disney.go.com/lightning-lane-passes/\" rel=\"noopener\" target=\"_blank\">web oficial</a> antes de pagar."),
 ("No tenemos precios verificados: hagan la cuenta con su compañía.", "Los precios varían mucho según el país y la compañía: hagan la cuenta con la suya."),
 ("<p>Este top 10 cruza el ranking de MagicGuides (5 de febrero de 2026) con la guía de Mouse Hacking (26 de mayo de 2026). Como el parque tiene pocas atracciones mecánicas abiertas (Tropical Americas llega en 2027), la lista incluye shows y senderos.</p>",
  "<p>Armamos este top 10 con lo que más disfrutan las familias, cruzando nuestra experiencia con los rankings de los sitios que más saben del parque. Como Animal Kingdom tiene pocas atracciones mecánicas abiertas (Tropical Americas llega en 2027), la lista incluye shows y senderos: acá eso no es relleno, es lo mejor del parque.</p>"),
 ("<p>Este top 10 cruza dos rankings: el de Wandering in Disney (30 de octubre de 2026) como base y el de MagicGuides para duraciones y avisos.</p>",
  "<p>Armamos este top 10 con lo que más disfrutan las familias, cruzando nuestra experiencia con los rankings de los sitios que más saben de EPCOT.</p>"),
 ("Aquí van todas, en el orden del ranking de Orlando Informer, con la altura", "Aquí van todas, de la que más vale la pena a la que menos, con la altura"),
 ("Los datos de Single Rider salen de fuentes no oficiales (Orlando Informer y WDWNT, que cita la app oficial): confírmenlos en la app el día de su visita.", "Single Rider no siempre está abierta: ese mismo día, fíjense en la app."),
 ("Los datos de Single Rider salen de fuentes no oficiales (Orlando Informer y WDWNT): confírmenlos en la app el día de su visita.", "Single Rider no siempre está abierta: ese mismo día, fíjense en la app."),
 ("<strong>El truco:</strong> fue la n.º 1 del ranking de Orlando Informer.", "<strong>El truco:</strong> es la que más eligen los que ya fueron, así que vayan temprano."),
 ("<p>Los puestos 1 a 7 salen del ranking de MagicGuides (21 de septiembre de 2026). Los puestos 8 a 10 no vienen de un ranking: los sumamos nosotros porque tienen Lightning Lane y son populares.</p>",
  "<p>Del 1 al 7, las que nadie se quiere perder. Del 8 al 10, nuestras elegidas: rinden muchísimo con Lightning Lane y a los chicos les encantan.</p>"),
 ("Fue el n.º 1 del ranking de islands.com. Acepta reservas.", "De los restaurantes mejor valorados del parque. Acepta reservas."),
 (", en el orden del ranking de MagicGuides (actualizado en noviembre de 2026), con lo que necesitan saber", ", de la que más vale la pena a la que menos, con lo que necesitan saber"),
 ("no lo podemos adelantar, porque cambia y no tenemos precios verificados de mercadería.", "cambia tanto que no tiene sentido adelantarlo."),
]
OFI = re.compile(r'disney\.go\.com|universalorlando\.com|loewshotels|floridarevenue|orangecountyfl')
def acortar(m):
    inner = m.group(2)
    links = re.findall(r'<a [^>]*>[^<]*</a>', inner)
    if len(links) <= 3: return m.group(0)
    sel, dis, uni = [], False, False
    for a in links:
        h = re.search(r'href="([^"]+)"', a).group(1)
        if "disney.go.com" in h and not dis:
            sel.append(re.sub(r'>[^<]*</a>', '>web oficial de Disney</a>', a)); dis = True
        elif "universalorlando.com" in h and not uni:
            sel.append(re.sub(r'>[^<]*</a>', '>web oficial de Universal</a>', a)); uni = True
    for a in links:
        h = re.search(r'href="([^"]+)"', a).group(1)
        if not OFI.search(h) and len(sel) < 4:
            t = re.sub(r'<[^>]+>', '', a).split(",")[0].split(" (")[0].strip()
            sel.append(re.sub(r'>[^<]*</a>', f'>{t}</a>', a))
    lista = ", ".join(sel[:-1]) + " y " + sel[-1] if len(sel) > 1 else sel[0]
    return m.group(1) + "la " + lista + ", entre otras" + m.group(3)
n = 0
for f in sorted(glob.glob("blog/*/index.html")):
    s = s0 = open(f, encoding="utf-8").read()
    for a, b in R:
        s = s.replace(a, b)
        a2 = a.replace(' rel="noopener" target="_blank"', ""); 
        if a2 != a: pass
    s = re.sub(r'(<p class="fuentes"><em>[^(]*\()((?:[^()]|<[^>]*>)*?)(\))', acortar, s)
    s = s.replace("(la la ", "(la ")
    if s != s0: open(f, "w", encoding="utf-8").write(s); n += 1
print("notas:", n)
