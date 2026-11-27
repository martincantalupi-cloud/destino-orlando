import re, json, glob, os, sys, html
os.chdir(sys.argv[1])
BASE = "https://habiaunavezorlando.com"
FIX = {"/blog/08-alturas-minimas-disney":"/blog/alturas-minimas-disney/",
       "/blog/09-cambio-de-padres-rider-switch":"/blog/cambio-de-padres-rider-switch/",
       "/blog/11-truco-recuerdos-disney":"/blog/truco-recuerdos-disney/",
       "/blog/17-epic-universe-primera-visita":"/blog/epic-universe-guia-primera-visita/",
       "/blog/18-epic-universe-o-universal-studios":"/blog/epic-universe-o-universal-studios/",
       "/blog/19-express-pass-universal-hoteles":"/blog/express-pass-universal-hoteles/"}
TW = '<meta name="twitter:card" content="summary_large_image">'
cambios = 0
for f in glob.glob("**/index.html", recursive=True):
    s0 = s = open(f, encoding="utf-8").read()
    for a, b in FIX.items():
        s = s.replace(f'href="{a}"', f'href="{b}"')
    if 'name="twitter:card"' not in s:
        s = s.replace("</title>", "</title>" + TW, 1)
    # Artículos: imagen, fecha de publicación y migas
    if f.startswith("blog/") and f != "blog/index.html":
        m = re.search(r'<script type="application/ld\+json">(\{.*?\})</script>', s, re.S)
        if m:
            d = json.loads(m.group(1))
            if d.get("@type") == "Article":
                if "image" not in d:
                    og = re.search(r'<meta property="og:image" content="([^"]+)"', s)
                    im = re.search(r'<figure class="foto"><img src="([^"]+)"', s)
                    src = og.group(1) if og else (im.group(1) if im else None)
                    if src:
                        d["image"] = src if src.startswith("http") else BASE + src
                d.setdefault("datePublished", d.get("dateModified", "2026-11-25"))
                d["url"] = d.get("mainEntityOfPage")
                migas = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
                    {"@type":"ListItem","position":1,"name":"Inicio","item":BASE + "/"},
                    {"@type":"ListItem","position":2,"name":"Guías","item":BASE + "/blog/"},
                    {"@type":"ListItem","position":3,"name":d.get("headline",""),"item":d.get("mainEntityOfPage")}]}
                nuevo = '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
                if '"BreadcrumbList"' not in s:
                    nuevo += '<script type="application/ld+json">' + json.dumps(migas, ensure_ascii=False) + '</script>'
                s = s.replace(m.group(0), nuevo, 1)
    if f == "index.html" and "application/ld+json" not in s:
        d = [{"@context":"https://schema.org","@type":"Organization","name":"Había una vez Orlando","url":BASE + "/",
              "logo":BASE + "/marca/icono-512.png","description":"Planificador independiente de viajes a Disney World y Universal Orlando, en español."},
             {"@context":"https://schema.org","@type":"WebSite","name":"Había una vez Orlando","url":BASE + "/","inLanguage":"es"}]
        s = s.replace("</head>", "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>" for x in d) + "\n</head>", 1)
    if f == "blog/index.html" and "application/ld+json" not in s:
        items = re.findall(r'<a href="(/blog/[^"]+/)"><img[^>]*><span class="card-t">([^<]+)</span>', s)
        d = {"@context":"https://schema.org","@type":"CollectionPage","name":"Guías para viajar a Disney y Universal Orlando","url":BASE + "/blog/","inLanguage":"es",
             "mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":BASE + u,"name":html.unescape(t)} for i,(u,t) in enumerate(items)]}}
        s = s.replace("</title>", "</title>" + '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>", 1)
    if s != s0:
        open(f, "w", encoding="utf-8").write(s); cambios += 1
# Redirecciones de las direcciones viejas con número
red = ["# Direcciones viejas (con número) → las actuales"] + [f"{a} {b} 301" for a, b in FIX.items()] + [f"{a}/ {b} 301" for a, b in FIX.items()]
open("_redirects", "w").write("\n".join(red) + "\n")
# Las copias en *.pages.dev no se indexan (la buena es habiaunavezorlando.com)
open("_headers", "w").write("https://:project.pages.dev/*\n  X-Robots-Tag: noindex\n")
print("archivos tocados:", cambios)
