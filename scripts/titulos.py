import re, glob, html, os, sys, json
os.chdir(sys.argv[1])
T = {
 "blog/abuelos-en-disney": "Abuelos en Disney: viajar en 3 generaciones (guía 2027)",
 "blog/alturas-minimas-disney": "Alturas mínimas en Disney World en cm: tabla 2027",
 "blog/calendario-viaje-disney": "Qué hacer 180, 90, 60 y 30 días antes de ir a Disney",
 "blog/cambio-de-padres-rider-switch": "Rider Switch en Disney: cómo turnarse sin repetir la fila",
 "blog/centro-cuidado-bebes-disney": "Centro de cuidado de bebés en Disney World: cómo usarlo",
 "blog/cuando-hay-menos-gente-disney": "¿Cuándo hay menos gente en Disney? Semáforo dic–mar",
 "blog/cuanto-cuesta-disney-2027": "¿Cuánto cuesta ir a Disney en 2027? Presupuesto real",
 "blog/cuantos-dias-disney-universal": "¿Cuántos días para Disney y Universal? Según sus hijos",
 "blog/disney-con-chicos-de-2-a-6-anos": "Disney con chicos de 2 a 6 años: el plan sin berrinches",
 "blog/disney-sin-hablar-ingles": "¿Hay que hablar inglés para ir a Disney? Guía práctica",
 "blog/disney-world-primera-vez-guia-familias": "Disney World por primera vez: guía completa 2027",
 "blog/disney-y-universal-mismo-viaje": "Disney y Universal en el mismo viaje: planes de 7 a 14 días",
 "blog/dormir-dentro-o-fuera-de-disney": "¿Hotel dentro o fuera de Disney? La cuenta honesta",
 "blog/epic-universe-guia-primera-visita": "Epic Universe: guía para la primera visita (2027)",
 "blog/epic-universe-o-universal-studios": "Epic Universe o Universal Studios: cómo repartir los días",
 "blog/errores-primera-vez-disney": "12 errores de la primera vez en Disney (y cómo evitarlos)",
 "blog/express-pass-universal-hoteles": "Express Pass de Universal: hoteles que lo incluyen (2027)",
 "blog/fechas-mas-baratas-disney-2027": "Las fechas más baratas para ir a Disney en 2027",
 "blog/gastos-ocultos-disney-orlando": "Gastos ocultos de Disney y Universal: la lista completa",
 "blog": "Guías de Disney y Universal Orlando en español",
 "blog/mejores-atracciones-animal-kingdom": "Las 10 mejores atracciones de Animal Kingdom (2027)",
 "blog/mejores-atracciones-epcot": "Las 10 mejores atracciones de EPCOT y dónde comer (2027)",
 "blog/mejores-atracciones-epic-universe": "Las mejores atracciones de Epic Universe (2027)",
 "blog/mejores-atracciones-hollywood-studios": "Las 10 mejores atracciones de Hollywood Studios (2027)",
 "blog/mejores-atracciones-islands-of-adventure": "Mejores atracciones de Islands of Adventure (2027)",
 "blog/mejores-atracciones-magic-kingdom": "Las 10 mejores atracciones de Magic Kingdom (2027)",
 "blog/mejores-atracciones-universal-studios-florida": "Mejores atracciones de Universal Studios Florida (2027)",
 "blog/momentos-que-hacen-llorar-a-los-papas": "15 momentos de Disney que hacen llorar a los papás",
 "blog/test-que-parque-es-tu-familia": "Test: ¿qué parque de Orlando va con su familia?",
 "blog/truco-recuerdos-disney": "Recuerdos de Disney sin berrinches: el truco de la foto",
 "blog/vale-la-pena-lightning-lane": "¿Vale la pena Lightning Lane en Disney? Cuándo sí y no",
 "index.html": "Planificador de viajes a Disney y Universal en español",
}
D = {
 "blog/centro-cuidado-bebes-disney": "Viajar con bebé a Disney: qué ofrecen los centros de cuidado de bebés de cada parque, qué confirmar y cómo armar el día alrededor de siestas y comidas.",
 "blog/cuando-hay-menos-gente-disney": "Las semanas con menos gente en Disney World de diciembre 2026 a marzo 2027, en un semáforo simple, y qué día conviene ir a cada parque.",
 "blog/disney-world-primera-vez-guia-familias": "Primer viaje a Disney y Universal en familia: cuántos días, entradas, filas rápidas, hoteles y un plan día por día. Todo en español, actualizado 2027.",
 "blog/epic-universe-o-universal-studios": "Cómo repartir 1, 2 o 3 días entre Epic Universe, Universal Studios Florida e Islands of Adventure según su familia y su entrada.",
 "blog/express-pass-universal-hoteles": "Qué es el Express de Universal Orlando, los tres hoteles que traen Express Unlimited gratis, por qué no vale en Epic Universe y cuándo conviene pagarlo.",
 "blog/gastos-ocultos-disney-orlando": "Impuestos, estacionamiento, comida, propinas, celular y extras: los gastos que se escapan del presupuesto en Disney y Universal, y cómo anticiparlos.",
 "blog": "Guías en español para planear su viaje a Disney World y Universal Orlando: alturas, días, presupuesto, Lightning Lane, multitudes y más.",
 "creditos": "Autores y licencias de las fotos de Wikimedia Commons que usamos en Había una vez Orlando, con link a cada original. Gracias a quienes las compartieron.",
 "blog/truco-recuerdos-disney": "Una regla simple para que las tiendas de Disney y Universal no terminen en berrinche: sacarle foto a lo que les gusta y elegir uno al final del día.",
 "index.html": "Arme gratis el plan de su viaje a Disney World y Universal Orlando, en español: qué parque cada día, qué reservar y cuándo, y guías con datos oficiales.",
}
for k, v in list(T.items()) + list(D.items()):
    pass
for k in T: assert len(T[k]) <= 62, (k, len(T[k]))
for k in D: assert len(D[k]) <= 158, (k, len(D[k]))
n = 0
for f in glob.glob("**/index.html", recursive=True):
    k = f.replace("/index.html", "") if f != "index.html" else "index.html"
    s = s0 = open(f, encoding="utf-8").read()
    if k in T:
        t = html.escape(T[k], quote=False)
        s = re.sub(r"<title>.*?</title>", lambda m: f"<title>{t}</title>", s, count=1)
        s = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{html.escape(T[k])}">', s, count=1)
    if k in D:
        d = html.escape(D[k])
        s = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{d}">', s, count=1)
        s = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{d}">', s, count=1)
        s = re.sub(r'("@type": "Article".*?"description": ")[^"]*', lambda m: m.group(1) + D[k].replace('"', '\\"'), s, count=1, flags=re.S)
    if s != s0: open(f, "w", encoding="utf-8").write(s); n += 1
# El index tiene un título que la app cambia al navegar: actualizar TITULOS.inicio
s = open("index.html", encoding="utf-8").read()
s = s.replace('inicio:"Había una vez Orlando"', 'inicio:"' + T["index.html"] + ' · Había una vez Orlando"', 1)
open("index.html", "w", encoding="utf-8").write(s)
print("páginas:", n)
