import re, glob, os, sys, html, unicodedata
os.chdir(sys.argv[1])  # carpeta web
ACTION = re.search(r'const NEWSLETTER_ACTION = "([^"]+)"', open("index.html", encoding="utf-8").read()).group(1)
def slugify(t):
    t = unicodedata.normalize("NFKD", html.unescape(re.sub("<[^>]+>", "", t))).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]

# ---------- Portada: pantalla Próximamente en dos columnas ----------
s = open("index.html", encoding="utf-8").read()
if "/* ancho-escritorio */" not in s:
    css = """
/* ancho-escritorio */
@media (min-width:960px){
  #vista-empezar .paso{ width:min(100% - 48px, 1120px); }
  #vista-empezar .paso main{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); column-gap:56px; align-items:start; padding-bottom:40px; }
  #vista-empezar .paso main > picture{ grid-column:1; grid-row:1 / span 30; position:sticky; top:24px; }
  #vista-empezar .paso main > picture img.cover{ width:100%; height:auto; aspect-ratio:4/5; object-fit:cover; border-radius:var(--radius-card); }
  #vista-empezar .paso main > *:not(picture){ grid-column:2; }
  #vista-empezar .paso main h1{ font-size:clamp(2.6rem,3.6vw,3.6rem); }
}
"""
    s = s.replace("</style>", css + "</style>", 1)
    open("index.html", "w", encoding="utf-8").write(s)

# ---------- Blog ----------
CSS_BLOG = """<style>/* ancho-escritorio */
.top{max-width:1180px}
@media (min-width:900px){ main.indice-blog{max-width:1180px} main.indice-blog .lista{grid-template-columns:repeat(3,minmax(0,1fr));gap:22px} }
.lateral{display:grid;gap:18px;margin-top:36px}
.lat-caja{background:var(--paper,#FFFCFA);border:1px solid #e3def7;border-radius:18px;padding:18px 20px}
.lat-caja h2{font-family:Georgia,serif;font-weight:400;font-size:1.15rem;margin:0 0 10px;color:var(--indigo,#27205F)}
.lat-caja p{font-size:.95rem;margin:0 0 10px;line-height:1.5}
.lat-indice{display:none}
.lat-indice ol{margin:0;padding-left:1.1em;font-size:.95rem;line-height:1.55}
.lat-indice li{margin:0 0 6px}
.lat-mail{background:var(--indigo,#27205F);color:var(--cream,#FFF8EA);border:0}
.lat-mail h2{color:var(--cream,#FFF8EA)}
.lat-mail form{display:grid;gap:8px}
.lat-mail input{min-height:44px;padding:8px 14px;border:0;border-radius:999px;font:16px Arial,Helvetica,sans-serif}
.lat-mail button{min-height:44px;border:0;border-radius:999px;background:var(--mint,#85E8D7);color:var(--indigo,#27205F);font:700 15px Arial,Helvetica,sans-serif;cursor:pointer}
.lat-mail .estado{min-height:1.2em;font-size:.9rem;font-weight:700;margin:4px 0 0}
.lat-guias ul{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.lat-guias a{display:grid;grid-template-columns:72px 1fr;gap:10px;align-items:center;font-size:.92rem;line-height:1.35;text-decoration:none;color:inherit}
.lat-guias img{width:72px;height:54px;object-fit:cover;border-radius:10px}
@media (min-width:1100px){
  main.con-lateral{max-width:1180px;display:grid;grid-template-columns:minmax(0,1fr) 320px;column-gap:56px;align-items:start}
  main.con-lateral .cuerpo{max-width:760px}
  .lateral{position:sticky;top:20px;margin-top:8px;max-height:calc(100vh - 40px);overflow:auto}
  .lat-indice{display:block}
}
</style>"""
JS_MAIL = """<script>(function(){var A=%s;document.querySelectorAll('form.form-aviso').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var m=f.querySelector('input'),es=f.querySelector('.estado'),v=m.value.trim();if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(v)){es.textContent='Revisen el mail: parece que le falta algo.';m.focus();return;}var d=new FormData();d.append('EMAIL',v);d.append('email_address_check','');d.append('locale','es');fetch(A,{method:'POST',body:d,mode:'no-cors'}).then(function(){es.textContent='¡Listo! Les mandamos un mail para confirmar ✨';f.reset();}).catch(function(){es.textContent='No pudimos anotarlos. Prueben de nuevo en un rato.';});});});})();</script>""" % ('"' + ACTION + '"')

idx = open("blog/index.html", encoding="utf-8").read()
tarjetas = re.findall(r'<li class="card"><a href="(/blog/[^"]+/)"><img src="([^"]+)"[^>]*><span class="card-t">([^<]+)</span>', idx)
if "/* ancho-escritorio */" not in idx:
    idx = idx.replace("</head>", CSS_BLOG + "</head>", 1).replace("<main>", '<main class="indice-blog">', 1)
    open("blog/index.html", "w", encoding="utf-8").write(idx)

hechas = 0
for f in sorted(glob.glob("blog/*/index.html")):
    s = open(f, encoding="utf-8").read()
    if "/* ancho-escritorio */" in s: continue
    url = "/" + f[:-len("index.html")]
    # ids en los subtítulos
    usados = set()
    def poner_id(m):
        attrs, txt = m.group(1), m.group(2)
        if "id=" in attrs: return m.group(0)
        i = slugify(txt) or "seccion"
        while i in usados: i += "-2"
        usados.add(i)
        return f'<h2{attrs} id="{i}">{txt}</h2>'
    ini, fin = s.index("<main>"), s.index("</main>")
    cuerpo = re.sub(r"<h2([^>]*)>(.*?)</h2>", poner_id, s[ini + 6:fin], flags=re.S)
    h2s = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', cuerpo, re.S)
    indice = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t)}</a></li>' for i, t in h2s)
    pos = [k for k, t in enumerate(tarjetas) if t[0] == url]
    k = pos[0] if pos else -1
    otras = [tarjetas[(k + j) % len(tarjetas)] for j in range(1, 4)]
    guias = "".join(f'<li><a href="{u}"><img src="{img}" alt="" loading="lazy" decoding="async" width="72" height="54"><span>{t}</span></a></li>' for u, img, t in otras)
    lateral = (
        '<aside class="lateral" aria-label="Más de esta guía">'
        + (f'<nav class="lat-caja lat-indice" aria-label="En esta guía"><h2>En esta guía</h2><ol>{indice}</ol></nav>' if h2s else "")
        + '<div class="lat-caja lat-mail"><h2>Su plan gratis, muy pronto ✨</h2><p>Estamos terminando el planificador que arma el viaje de su familia solo. Les avisamos apenas abra.</p>'
          '<form class="form-aviso" novalidate><label class="sr" for="aviso-mail" style="position:absolute;left:-9999px">Su mail</label>'
          '<input id="aviso-mail" type="email" name="EMAIL" autocomplete="email" placeholder="su@mail.com" required>'
          '<button type="submit">Avísenme</button><p class="estado" role="status" aria-live="polite"></p></form></div>'
        + f'<div class="lat-caja lat-guias"><h2>Sigan leyendo</h2><ul>{guias}</ul></div>'
        + "</aside>")
    s = s[:ini] + '<main class="con-lateral"><div class="cuerpo">' + cuerpo + "</div>" + lateral + s[fin:]
    s = s.replace("</head>", CSS_BLOG + "</head>", 1).replace("</body>", JS_MAIL + "</body>", 1)
    open(f, "w", encoding="utf-8").write(s); hechas += 1
print("notas:", hechas, "tarjetas:", len(tarjetas))
