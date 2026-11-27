#!/usr/bin/env python3
"""Baja a la web las fotos de Wikimedia Commons que hoy se cargan desde afuera.

- Busca en web/ todos los links a thumb.wikimedia.org / upload.wikimedia.org.
- Pide autor y licencia de cada archivo a la API de Commons.
- Baja una versión de 960 px a web/fotos/commons/ (de a una, despacio,
  respetando el Retry-After si Wikimedia pide esperar).
- Reemplaza los links por la copia local.
- Arma web/creditos/index.html con autor, licencia y link al original.
- Agrega un link a "Créditos de fotos" en el pie de cada página.

Se puede correr varias veces: lo ya bajado no se vuelve a pedir.
"""
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
DESTINO = WEB / "fotos" / "commons"
CACHE_META = RAIZ / "scripts" / "fotos-commons.json"
UA = "HabiaUnaVezOrlando/1.0 (https://habiaunavezorlando.com; github.com/martincantalupi-cloud/destino-orlando)"
ANCHO = 960
PAUSA = 3            # segundos entre pedidos
ESPERA_MAX = 1800    # si piden esperar más que esto, cortamos y se reintenta otro día
LIMITE_TOTAL = 4.5 * 3600

URL_RE = re.compile(r"https://(?:thumb|upload)\.wikimedia\.org/[^\"'\s)<>]+")
EXT_TEXTO = {".html", ".js", ".css", ".json", ".webmanifest", ".xml"}
inicio = time.time()


def pedir(url, binario=False):
    intentos = 0
    while True:
        intentos += 1
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                datos = r.read()
            time.sleep(PAUSA)
            return datos if binario else json.loads(datos)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and intentos <= 6:
                espera = int(e.headers.get("Retry-After") or 60 * intentos)
                if espera > ESPERA_MAX or time.time() - inicio + espera > LIMITE_TOTAL:
                    raise
                print(f"  Wikimedia pide esperar {espera}s ({e.code})", flush=True)
                time.sleep(espera + 5)
                continue
            raise


def nombre_archivo(url):
    p = urllib.parse.urlparse(url).path
    m = re.match(r"/wikipedia/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/([^/]+)", p)
    return urllib.parse.unquote(m.group(1)) if m else None


def slug(nombre):
    base, _, ext = nombre.rpartition(".")
    s = base.lower()
    for a, b in zip("áéíóúüñ", "aeiouun"):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80]
    ext = ext.lower()
    if ext in ("jpeg", "jpg"):
        ext = "jpg"
    elif ext not in ("png", "webp", "gif"):
        ext = "jpg"  # svg/tif: Commons entrega la miniatura en jpg/png
    return f"{s}.{ext}"


def limpiar(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def archivos_texto():
    for f in WEB.rglob("*"):
        if f.is_file() and f.suffix.lower() in EXT_TEXTO:
            yield f


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    meta = json.loads(CACHE_META.read_text()) if CACHE_META.exists() else {}

    # 1. Juntar links
    usos = {}
    for f in archivos_texto():
        for u in set(URL_RE.findall(f.read_text(encoding="utf-8"))):
            n = nombre_archivo(u)
            if n:
                usos.setdefault(n, set()).add(u)
    print(f"{len(usos)} fotos de Commons enlazadas desde afuera", flush=True)

    # 2. Autor y licencia
    faltan = [n for n in usos if n not in meta]
    for i in range(0, len(faltan), 40):
        tanda = faltan[i:i + 40]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": 2,
            "titles": "|".join("File:" + n for n in tanda),
            "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": ANCHO,
        })
        d = pedir("https://commons.wikimedia.org/w/api.php?" + q)
        norm = {x["to"]: x["from"] for x in d["query"].get("normalized", [])}
        for p in d["query"]["pages"]:
            clave = norm.get(p["title"], p["title"])[len("File:"):]
            if "imageinfo" not in p:
                meta[clave] = {"falta": True}
                continue
            ii = p["imageinfo"][0]
            em = ii.get("extmetadata", {})
            g = lambda k: limpiar(em.get(k, {}).get("value"))
            meta[clave] = {
                "original": ii["url"], "miniatura": ii.get("thumburl"),
                "pagina": ii["descriptionurl"], "ancho": ii.get("width"),
                "autor": g("Artist") or "Autor desconocido",
                "licencia": g("LicenseShortName"), "licencia_url": g("LicenseUrl"),
                "archivo": slug(clave),
            }
        CACHE_META.write_text(json.dumps(meta, ensure_ascii=False, indent=1))

    # 3. Bajar
    bajadas, fallas = 0, []
    for n in usos:
        m = meta.get(n, {})
        if m.get("falta"):
            fallas.append((n, "no existe en Commons"))
            continue
        dest = DESTINO / m["archivo"]
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        if time.time() - inicio > LIMITE_TOTAL:
            fallas.append((n, "sin tiempo, queda para la próxima corrida"))
            continue
        candidatos = []
        if m.get("miniatura"):
            candidatos.append(m["miniatura"].split("?")[0])
            candidatos.append(candidatos[-1].replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/"))
        if (m.get("ancho") or 0) <= 2400:
            candidatos.append(m["original"])
        ok = False
        for url in dict.fromkeys(candidatos):
            try:
                datos = pedir(url, binario=True)
                if len(datos) > 1000:
                    dest.write_bytes(datos)
                    ok = True
                    bajadas += 1
                    print(f"  ok {m['archivo']} ({len(datos)//1024} KB)", flush=True)
                    break
            except Exception as e:  # probamos el siguiente candidato
                print(f"  no salió {url[:90]}: {e}", flush=True)
        if not ok:
            fallas.append((n, "no se pudo bajar"))

    # 4. Reemplazar links por la copia local
    locales = {n: "/fotos/commons/" + meta[n]["archivo"] for n in usos
               if not meta.get(n, {}).get("falta") and (DESTINO / meta[n]["archivo"]).exists()}
    cambiados = 0
    for f in archivos_texto():
        t = f.read_text(encoding="utf-8")
        nuevo = URL_RE.sub(lambda mo: locales.get(nombre_archivo(mo.group(0)), mo.group(0)), t)
        if nuevo != t:
            f.write_text(nuevo, encoding="utf-8")
            cambiados += 1

    # 5. Página de créditos (todas las fotos de Commons guardadas en la web)
    todas = sorted((v for v in meta.values() if not v.get("falta") and (DESTINO / v["archivo"]).exists()),
                   key=lambda v: v["archivo"])
    filas = []
    for v in todas:
        lic = html.escape(v["licencia"] or "ver licencia")
        lic_html = f'<a href="{html.escape(v["licencia_url"])}" rel="noopener" target="_blank">{lic}</a>' if v["licencia_url"] else lic
        filas.append(
            f'<li><img src="/fotos/commons/{v["archivo"]}" alt="" loading="lazy" decoding="async" width="120" height="80">'
            f'<span>Foto: {html.escape(v["autor"])} · {lic_html} · '
            f'<a href="{html.escape(v["pagina"])}" rel="noopener" target="_blank">original en Wikimedia Commons</a></span></li>'
        )
    plantilla = (WEB / "blog" / "index.html").read_text(encoding="utf-8")
    cabeza = plantilla.split("<main>")[0]
    cola = plantilla.split("</main>", 1)[1]
    cabeza = re.sub(r"<title>.*?</title>", "<title>Créditos de fotos | Había una vez Orlando</title>", cabeza, flags=re.S)
    cabeza = re.sub(r'<meta name="description" content="[^"]*">',
                    '<meta name="description" content="Autores y licencias de las fotos de Wikimedia Commons usadas en Había una vez Orlando.">', cabeza)
    cabeza = re.sub(r'<link rel="canonical" href="[^"]*">',
                    '<link rel="canonical" href="https://habiaunavezorlando.com/creditos/">', cabeza)
    estilo = ("<style>.creditos{list-style:none;padding:0;display:grid;gap:12px}"
              ".creditos li{display:flex;gap:12px;align-items:center;font-size:.9rem}"
              ".creditos img{width:120px;height:80px;object-fit:cover;border-radius:8px;flex:none}</style>")
    cuerpo = (f"<main>{estilo}<h1>Créditos de fotos</h1>"
              "<p class=\"meta\">Estas fotos son de Wikimedia Commons, con licencias libres. "
              "Gracias a sus autores. Las guardamos en nuestro sitio y citamos autor, licencia y original.</p>"
              f"<ul class=\"creditos\">{''.join(filas)}</ul></main>")
    (WEB / "creditos").mkdir(exist_ok=True)
    (WEB / "creditos" / "index.html").write_text(cabeza + cuerpo + cola, encoding="utf-8")

    # 6. Link a créditos en el pie
    for f in WEB.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if "/creditos/" in t or "<footer" not in t:
            continue
        t2 = re.sub(r"(<footer[^>]*>.*?)(</footer>)",
                    r'\1 · <a href="/creditos/">Créditos de fotos</a>\2', t, count=1, flags=re.S)
        if t2 != t:
            f.write_text(t2, encoding="utf-8")

    # 7. Sitemap
    sm = WEB / "sitemap.xml"
    if sm.exists() and "/creditos/" not in sm.read_text():
        s = sm.read_text().replace(
            "</urlset>",
            f"  <url><loc>https://habiaunavezorlando.com/creditos/</loc><lastmod>{time.strftime('%Y-%m-%d')}</lastmod></url>\n</urlset>")
        sm.write_text(s)

    print(f"\nBajadas ahora: {bajadas}. Archivos de la web actualizados: {cambiados}. "
          f"Fotos en créditos: {len(todas)}.")
    if fallas:
        print(f"Quedaron {len(fallas)} pendientes (se reintentan en la próxima corrida):")
        for n, motivo in fallas:
            print(f"  - {n}: {motivo}")
    restantes = sum(1 for f in archivos_texto() if URL_RE.search(f.read_text(encoding="utf-8")))
    print(f"Archivos que todavía enlazan a Wikimedia: {restantes}")


if __name__ == "__main__":
    sys.exit(main())
