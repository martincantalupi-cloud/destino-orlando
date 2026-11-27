import json, re, html, sys, os
os.chdir(sys.argv[1])
meta = {v["archivo"]: v for v in json.load(open("scripts/fotos-commons.json")).values() if not v.get("falta")}
ALT = {
 "main-street-usa-magic-kingdom-walt-disney-world-2024.jpg": "Main Street U.S.A. del Magic Kingdom con el castillo al fondo y familias paseando",
 "big-thunder-mountain-lightning-lane.jpg": "Cartel de entrada Lightning Lane en Big Thunder Mountain Railroad del Magic Kingdom",
 "disney-s-port-orleans-resort-riverside-entrance-2024.jpg": "Entrada del hotel Port Orleans Riverside de Disney, de estilo sureño con jardines",
 "its-a-small-world-at-magic-kingdom-florida.jpg": "Fachada colorida de it's a small world en el Magic Kingdom, una atracción tranquila para todas las edades",
 "space-mountain-in-the-magic-kingdom-in-2021.jpg": "La montaña blanca de Space Mountain en Tomorrowland, Magic Kingdom",
 "mission-space-epcot.jpg": "Edificio de Mission: SPACE en EPCOT, una atracción con altura mínima",
 "slinky-dog-dash-sunset.jpg": "Montaña rusa Slinky Dog Dash al atardecer en Toy Story Land, Hollywood Studios",
 "wishes-14076813120.jpg": "Fuegos artificiales sobre el castillo del Magic Kingdom",
 "seven-dwarfs-mine-train-magic-kingdom-1.jpg": "Montaña rusa Seven Dwarfs Mine Train en Fantasyland, Magic Kingdom",
 "peter-pan-s-flight-at-magic-kingdom.jpg": "Entrada de Peter Pan's Flight en Fantasyland, una atracción para los más chicos",
 "wdw-peoplemover.jpg": "El PeopleMover recorriendo Tomorrowland, un paseo tranquilo para hacer con bebé",
 "ueu-entrance.jpg": "Entrada principal de Epic Universe, el parque más nuevo de Universal Orlando",
 "spaceship-earth-at-night.jpg": "La gran esfera plateada de Spaceship Earth iluminada de noche en la entrada de EPCOT",
 "universal-islands-of-adventure-harry-potter-castle-9127i.jpg": "Castillo de Hogwarts en The Wizarding World of Harry Potter, Islands of Adventure",
 "toy-story-mania-disney-s-hollywood-studios-1.jpg": "Entrada de Toy Story Mania! en Hollywood Studios",
 "mexico-pavilion-at-night-26891542476.jpg": "Pirámide del pabellón de México iluminada de noche en World Showcase de EPCOT",
 "the-american-adventure-23860708488.jpg": "Edificio de The American Adventure en World Showcase de EPCOT",
 "anaheim-produce-and-toluca-legs-turkey-co-at-disney-s-hollywood-studios.jpg": "Puestos de comida que venden patas de pavo y fruta en Sunset Boulevard, Hollywood Studios",
 "disney-s-all-star-movies-swimming-pool-5130249790.jpg": "Piscina temática del hotel económico All-Star Movies de Disney con reposeras alrededor",
 "super-nintendo-world-epic-universe-orlando-florida.jpg": "Super Nintendo World en Epic Universe, Universal Orlando",
 "portofino-bay-hotel-universal.jpg": "Hotel Portofino Bay de Universal Orlando, uno de los que incluyen Express Unlimited",
 "velocicoaster-2.jpg": "Montaña rusa Jurassic World VelociCoaster en Islands of Adventure",
 "cinderella-castle-january-2021.jpg": "Castillo de Cenicienta visto desde Main Street U.S.A. en un día soleado, Magic Kingdom",
 "nighttime-main-street-crowd-cinderella-castle-lights-in-distance-magic-kingdom-j.jpg": "Main Street U.S.A. de noche, con las tiendas iluminadas y el castillo al fondo",
 "post-fireworks-crowd-49560220418.jpg": "Familias saliendo por Main Street al final del día, después de los fuegos",
 "main-street-rain-jtpi-5137-15454967755.jpg": "Main Street U.S.A. en un día de lluvia en el Magic Kingdom",
}
# nota: [fotos internas en orden (None = dejar)], tarjeta (None = dejar)
PLAN = {
 "abuelos-en-disney": (["main-street-usa-magic-kingdom-walt-disney-world-2024.jpg", "big-thunder-mountain-lightning-lane.jpg", "disney-s-port-orleans-resort-riverside-entrance-2024.jpg"], "its-a-small-world-at-magic-kingdom-florida.jpg"),
 "alturas-minimas-disney": (["space-mountain-in-the-magic-kingdom-in-2021.jpg", "mission-space-epcot.jpg", "slinky-dog-dash-sunset.jpg"], None),
 "calendario-viaje-disney": ([None, None, "big-thunder-mountain-lightning-lane.jpg"], "wishes-14076813120.jpg"),
 "cambio-de-padres-rider-switch": ([None, "seven-dwarfs-mine-train-magic-kingdom-1.jpg", "slinky-dog-dash-sunset.jpg"], None),
 "centro-cuidado-bebes-disney": (["peter-pan-s-flight-at-magic-kingdom.jpg", "wdw-peoplemover.jpg", "its-a-small-world-at-magic-kingdom-florida.jpg"], None),
 "cuanto-cuesta-disney-2027": ([None, "ueu-entrance.jpg", None], None),
 "cuantos-dias-disney-universal": (["spaceship-earth-at-night.jpg", "universal-islands-of-adventure-harry-potter-castle-9127i.jpg", None], None),
 "disney-con-chicos-de-2-a-6-anos": (["main-street-usa-magic-kingdom-walt-disney-world-2024.jpg", "peter-pan-s-flight-at-magic-kingdom.jpg", "toy-story-mania-disney-s-hollywood-studios-1.jpg"], None),
 "disney-sin-hablar-ingles": (["mexico-pavilion-at-night-26891542476.jpg", "the-american-adventure-23860708488.jpg", "anaheim-produce-and-toluca-legs-turkey-co-at-disney-s-hollywood-studios.jpg"], None),
 "disney-world-primera-vez-guia-familias": (["spaceship-earth-at-night.jpg", None, "big-thunder-mountain-lightning-lane.jpg"], None),
 "dormir-dentro-o-fuera-de-disney": ([None, "disney-s-all-star-movies-swimming-pool-5130249790.jpg", None], None),
 "epic-universe-guia-primera-visita": ([None, "ueu-entrance.jpg", "super-nintendo-world-epic-universe-orlando-florida.jpg"], "skylineof-wizarding-world-ministry-of-magic-at-night.jpg"),
 "epic-universe-o-universal-studios": ([None, None, "portofino-bay-hotel-universal.jpg"], None),
 "express-pass-universal-hoteles": (["velocicoaster-2.jpg", "portofino-bay-hotel-universal.jpg", None], "hogsmeade-station-islands-of-adventure-hogwarts-express-sept2018.jpg"),
 "test-que-parque-es-tu-familia": ([None, None, "cinderella-castle-january-2021.jpg"], "spaceship-earth-at-night.jpg"),
 "truco-recuerdos-disney": (["main-street-usa-magic-kingdom-walt-disney-world-2024.jpg", "nighttime-main-street-crowd-cinderella-castle-lights-in-distance-magic-kingdom-j.jpg", "post-fireworks-crowd-49560220418.jpg"], None),
 "vale-la-pena-lightning-lane": ([None, "slinky-dog-dash-sunset.jpg", "main-street-rain-jtpi-5137-15454967755.jpg"], None),
 "momentos-que-hacen-llorar-a-los-papas": ([None, None, None], "harmonious1.jpg"),
}
def caption(a):
    m = meta[a]
    lic = html.escape(m["licencia"] or "Dominio público")
    lic_html = f'<a href="{html.escape(m["licencia_url"])}" rel="noopener" target="_blank">{lic}</a>' if m["licencia_url"] else lic
    return f'<figcaption>Foto: {html.escape(m["autor"])} · {lic_html} · <a href="{html.escape(m["pagina"])}" rel="noopener" target="_blank">vía Wikimedia Commons</a></figcaption>'
FIG = re.compile(r'<figure class="foto"><img src="([^"]+)" alt="[^"]*"([^>]*)>(<figcaption>.*?</figcaption>)</figure>', re.S)
B = "https://habiaunavezorlando.com"
idx = open("web/blog/index.html", encoding="utf-8").read(); home = open("web/index.html", encoding="utf-8").read()
for slug, (figs, card) in PLAN.items():
    f = f"web/blog/{slug}/index.html"; s = open(f, encoding="utf-8").read()
    found = list(FIG.finditer(s)); assert len(found) >= len(figs), (slug, len(found))
    out, last = [], 0
    for mobj, nuevo in zip(found, figs + [None] * (len(found) - len(figs))):
        out.append(s[last:mobj.start()])
        if nuevo:
            assert nuevo in meta and nuevo in ALT, nuevo
            out.append(f'<figure class="foto"><img src="/fotos/commons/{nuevo}" alt="{html.escape(ALT[nuevo])}"{mobj.group(2)}>{caption(nuevo)}</figure>')
        else:
            out.append(mobj.group(0))
        last = mobj.end()
    out.append(s[last:]); s = "".join(out)
    if card:
        assert card in meta, card
        url = f"/fotos/commons/{card}"
        idx = re.sub(rf'(<a href="/blog/{slug}/"><img src=")[^"]+', rf'\g<1>{url}', idx)
        home = re.sub(rf'(<a href="/blog/{slug}/"><img class="ld-guia-foto" src=")[^"]+', rf'\g<1>{url}', home)
        s = re.sub(r'(property="og:image" content=")[^"]+', rf'\g<1>{B}{url}', s, count=1)
        s = re.sub(r'("@type": "Article".*?"image": ")[^"]+', rf'\g<1>{B}{url}', s, count=1, flags=re.S)
    open(f, "w", encoding="utf-8").write(s)
open("web/blog/index.html", "w", encoding="utf-8").write(idx); open("web/index.html", "w", encoding="utf-8").write(home)
print("ok", len(PLAN))
