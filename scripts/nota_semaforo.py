import re, json, html, os, sys
os.chdir(sys.argv[1])  # web/
B = "https://habiaunavezorlando.com"
SLUG = "cuando-hay-menos-gente-disney"
URL = f"{B}/blog/{SLUG}/"
TIT = "¿Cuándo hay menos gente en Disney? Semáforo de diciembre a marzo"
DESC = "Las semanas con menos gente en Disney World de diciembre 2026 a marzo 2027, en un semáforo simple, más qué día conviene cada parque. Para familias latinoamericanas."
HERO = "main-street-usa-magic-kingdom-walt-disney-world-2024.jpg"
FIG2 = "post-fireworks-crowd-49560220418.jpg"
meta = {v["archivo"]: v for v in json.load(open("../scripts/fotos-commons.json")).values() if not v.get("falta")}
def cap(a):
    m = meta[a]; lic = html.escape(m["licencia"] or "Dominio público")
    l = f'<a href="{html.escape(m["licencia_url"])}" rel="noopener" target="_blank">{lic}</a>' if m["licencia_url"] else lic
    return f'<figcaption>Foto: {html.escape(m["autor"])} · {l} · <a href="{html.escape(m["pagina"])}" rel="noopener" target="_blank">vía Wikimedia Commons</a></figcaption>'
s = open("blog/fechas-mas-baratas-disney-2027/index.html", encoding="utf-8").read()
cuerpo = open("../../scripts/nota_semaforo_cuerpo.html", encoding="utf-8").read() if os.path.exists("../../scripts/nota_semaforo_cuerpo.html") else open("/home/claude/scripts/nota_semaforo_cuerpo.html", encoding="utf-8").read()
# foto dentro: antes de "Si su semana es roja"
cuerpo = cuerpo.replace("<h2>Si su semana es roja", f'<figure class="foto"><img src="/fotos/commons/{FIG2}" alt="Familias saliendo por Main Street al final del día, en una noche con mucha gente" loading="lazy" decoding="async">{cap(FIG2)}</figure><h2>Si su semana es roja', 1)
def slugify(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]
h2s = []
def pid(m):
    i = slugify(html.unescape(m.group(1))); h2s.append((i, m.group(1))); return f'<h2 id="{i}">{m.group(1)}</h2>'
cuerpo = re.sub(r"<h2>(.*?)</h2>", pid, cuerpo)
hero = f'<h1>{TIT}</h1><figure class="foto hero"><img src="/fotos/commons/{HERO}" alt="Main Street U.S.A. del Magic Kingdom con familias paseando y el castillo al fondo" decoding="async">{cap(HERO)}</figure>'
# head
s = re.sub(r"<title>.*?</title>", f"<title>{html.escape(TIT)} | Había una vez Orlando</title>", s, 1)
for a, b in [(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(DESC)}">'),
             (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'),
             (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(TIT)} | Había una vez Orlando">'),
             (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(DESC)}">'),
             (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
             (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{B}/fotos/commons/{HERO}">')]:
    s, n = re.subn(a, b.replace("\\", "\\\\"), s, 1); assert n == 1, a
art = {"@context": "https://schema.org", "@type": "Article", "headline": TIT, "description": DESC, "inLanguage": "es", "mainEntityOfPage": URL,
       "publisher": {"@type": "Organization", "name": "Había una vez Orlando", "url": B}, "author": {"@type": "Organization", "name": "Había una vez Orlando"},
       "datePublished": "2026-11-27", "dateModified": "2026-11-27", "image": f"{B}/fotos/commons/{HERO}", "url": URL}
mig = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": B + "/"}, {"@type": "ListItem", "position": 2, "name": "Guías", "item": B + "/blog/"},
    {"@type": "ListItem", "position": 3, "name": TIT, "item": URL}]}
s = re.sub(r'<script type="application/ld\+json">.*?</script><script type="application/ld\+json">.*?</script>',
           lambda m: '<script type="application/ld+json">' + json.dumps(art, ensure_ascii=False) + '</script><script type="application/ld+json">' + json.dumps(mig, ensure_ascii=False) + "</script>", s, 1, flags=re.S)
# main: cuerpo nuevo + lateral con índice y guías relacionadas
ini = s.index('<div class="cuerpo">') + len('<div class="cuerpo">'); fin = s.index('<aside class="lateral"')
s = s[:ini] + hero + cuerpo + "</div>" + s[fin:]
ind = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in h2s)
s = re.sub(r'(<nav class="lat-caja lat-indice"[^>]*><h2>En esta guía</h2><ol>).*?(</ol>)', lambda m: m.group(1) + ind + m.group(2), s, 1, flags=re.S)
idx = open("blog/index.html", encoding="utf-8").read()
tarj = {u: (img, t) for u, img, t in re.findall(r'<li class="card"><a href="(/blog/[^"]+/)"><img src="([^"]+)"[^>]*><span class="card-t">([^<]+)</span>', idx)}
rel = ["/blog/fechas-mas-baratas-disney-2027/", "/blog/vale-la-pena-lightning-lane/", "/blog/calendario-viaje-disney/"]
guias = "".join(f'<li><a href="{u}"><img src="{tarj[u][0]}" alt="" loading="lazy" decoding="async" width="72" height="54"><span>{tarj[u][1]}</span></a></li>' for u in rel)
s = re.sub(r'(<div class="lat-caja lat-guias"><h2>Sigan leyendo</h2><ul>).*?(</ul>)', lambda m: m.group(1) + guias + m.group(2), s, 1, flags=re.S)
os.makedirs(f"blog/{SLUG}", exist_ok=True)
open(f"blog/{SLUG}/index.html", "w", encoding="utf-8").write(s)
# tarjeta primera en el índice del blog + ItemList
card = f'<li class="card"><a href="/blog/{SLUG}/"><img src="/fotos/commons/{HERO}" alt="" loading="lazy" decoding="async" width="640" height="400"><span class="card-t">{TIT}</span></a><p>Las semanas más tranquilas y las más llenas de diciembre a marzo, en un semáforo simple, y qué día conviene cada parque.</p></li>'
if SLUG not in idx:
    idx = idx.replace('<ul class="lista">', '<ul class="lista">' + card, 1)
    def il(m):
        d = json.loads(m.group(1))
        if d.get("@type") == "CollectionPage":
            l = d["mainEntity"]["itemListElement"]; l.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TIT})
            for k, x in enumerate(l): x["position"] = k + 1
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
    idx = re.sub(r'<script type="application/ld\+json">(.*?)</script>', il, idx, 1, flags=re.S)
    open("blog/index.html", "w", encoding="utf-8").write(idx)
# sitemap
sm = open("sitemap.xml").read()
if SLUG not in sm:
    sm = sm.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-11-27</lastmod></url>\n</urlset>")
    sm = re.sub(r"(<loc>https://habiaunavezorlando.com/blog/</loc><lastmod>)[^<]+", r"\g<1>2026-11-27", sm)
    open("sitemap.xml", "w").write(sm)
# enlaces desde notas relacionadas
for u in rel:
    f = u.strip("/") + "/index.html"; t = open(f, encoding="utf-8").read()
    if SLUG in t: continue
    extra = f'<p><strong>¿Cuándo hay menos gente?</strong> Miren nuestro <a href="/blog/{SLUG}/">semáforo de multitudes de diciembre a marzo</a>, semana por semana.</p>'
    t = t.replace('</div><aside class="lateral"', extra + '</div><aside class="lateral"', 1)
    open(f, "w", encoding="utf-8").write(t)
print("ok", len(h2s), "secciones")
