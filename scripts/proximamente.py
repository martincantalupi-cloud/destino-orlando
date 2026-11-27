import re, sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:70], c)
    s = s.replace(a, b)

# 1) Vista #empezar: Próximamente + mail
ini = s.index('<form id="form-viaje"'); fin = s.index('</form>', ini) + len('</form>')
form_viejo = s[ini:fin]
rep('<p class="eyebrow">Mi viaje</p>\n      <h1 id="paso-titulo">El viaje empieza en casa</h1>\n      <p class="intro">Anoten cuántas personas viajan. Si todavía no eligieron las fechas, pueden empezar igual.</p>\n      ' + form_viejo,
'''<p class="eyebrow"><span class="sello-pronto">✨ Próximamente</span></p>
      <h1 id="paso-titulo">Su plan se está terminando de hornear</h1>
      <p class="intro">Estamos dejando el planificador impecable para que arme el viaje de su familia solo: qué parque cada día, qué reservar y cuándo, y a qué pueden subir los chicos. Gratis, en español.</p>
      <p class="intro"><strong>Déjennos su mail y les avisamos apenas abra.</strong> Un solo aviso, sin spam.</p>
      <form id="form-proximo" class="form-mail" novalidate>
        <label for="proximo-mail">Su mail</label>
        <input id="proximo-mail" name="EMAIL" type="email" autocomplete="email" inputmode="email" placeholder="su@mail.com" required>
        <button class="btn" type="submit">Avísenme cuando abra ✨</button>
        <p id="proximo-estado" class="estado-mail" role="status" aria-live="polite"></p>
        <p class="ayuda-campo">Les llega un mail para confirmar. Se pueden dar de baja cuando quieran.</p>
      </form>
      <div class="pronto-mientras">
        <h2>Mientras tanto</h2>
        <ul>
          <li><a href="/blog/disney-world-primera-vez-guia-familias/">Disney World por primera vez: la guía completa</a></li>
          <li><a href="/blog/calendario-viaje-disney/">Qué hacer 180, 90, 60, 30… días antes</a></li>
          <li><a href="/blog/cuanto-cuesta-disney-2027/">¿Cuánto cuesta Disney en 2027?</a></li>
          <li><a href="/blog/">Ver todas las guías →</a></li>
        </ul>
      </div>
      <div hidden aria-hidden="true">''' + form_viejo + '</div>')

# 2) Router: todo lo del planificador va a la pantalla de Próximamente
rep('''  else if (h === "empezar") vista = "empezar";
  else if (h === "familia") vista = "familia";
  else if (VISTAS_APP.includes(h)) vista = "app";
  else if (h === "mis-planes") vista = "misplanes";''',
'''  else if (h === "empezar" || h === "familia" || h === "mis-planes" || VISTAS_APP.includes(h)) vista = "empezar"; /* Próximamente */''')
rep('empezar:"Primer paso · Había una vez Orlando"', 'empezar:"Próximamente: su plan gratis · Había una vez Orlando"')

# 3) Landing: CTAs y planes
rep('<a href="#mis-planes">Mis planes</a>\n      <a href="#empezar" class="ld-nav-cta">Empezar gratis</a>',
    '<a href="#empezar" class="ld-nav-cta">Avísenme ✨</a>')
rep('Empezar mi plan gratis <span aria-hidden="true">↗</span></a>', 'Quiero mi plan gratis <span aria-hidden="true">↗</span></a>', 2)
rep('<a class="ld-link-claro" href="#como-funciona">Ver cómo funciona</a>', '<a class="ld-link-claro" href="#como-funciona">Ver cómo funciona</a>\n          <span class="sello-pronto">Próximamente</span>')
rep('<span class="ld-sello ld-sello-gratis">GRATIS</span>', '<span class="ld-sello ld-sello-gratis">GRATIS · PRÓXIMAMENTE</span>')
rep('<a class="btn" href="#empezar">Empezar gratis</a>', '<a class="btn" href="#empezar">Avísenme cuando abra</a>')
rep('<span class="ld-sello">OFERTA</span>', '<span class="ld-sello">OFERTA · PRÓXIMAMENTE</span>')
rep('<li>✓ Sin crear cuenta</li>', '<li>✓ Abre muy pronto</li>')
for a, b in [('data-evento="cta-como">Empezar mi plan gratis', 'data-evento="cta-como">Quiero mi plan gratis'),
             ('data-evento="cta-producto">Probarlo gratis', 'data-evento="cta-producto">Avísenme cuando abra')]:
    rep(a, b)

# 4) Estilos
rep('.ld-news-form{', '''.sello-pronto{ display:inline-block; background:var(--mint); color:var(--indigo); border-radius:999px; padding:4px 12px; font-size:.8rem; font-weight:700; letter-spacing:.02em; vertical-align:middle; }
.form-mail{ display:grid; gap:10px; margin:18px 0 8px; }
.form-mail input{ min-height:48px; padding:10px 16px; border:1px solid #cfc8f2; border-radius:999px; font:16px var(--font-body); color:var(--ink); }
.estado-mail{ min-height:1.4em; font-weight:700; margin:0; }
.pronto-mientras{ margin-top:22px; padding-top:16px; border-top:1px solid #e3def7; }
.pronto-mientras h2{ font-size:1.1rem; margin:0 0 8px; }
.pronto-mientras ul{ margin:0; padding-left:1.1em; line-height:1.9; }
.ld-news-form{''')

# 5) Formularios de mail: uno solo para todos
ini = s.index('/* Newsletter (Valen + Tomás).'); fin = s.index('</script>', ini)
s = s[:ini] + '''/* Lista de avisos por mail (Valen + Tomás). La dirección es el link del formulario de Brevo
   (Marketing > Forms > Share > link para compartir). Mientras esté vacía, avisa que la lista abre en días. */
const NEWSLETTER_ACTION = "";
function conectarFormMail(idForm, idMail, idEstado){
  const f = document.getElementById(idForm); if (!f) return;
  const est = document.getElementById(idEstado), mail = document.getElementById(idMail);
  f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const v = mail.value.trim();
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(v)){ est.textContent = "Revisen el mail: parece que le falta algo."; mail.focus(); return; }
    if (!NEWSLETTER_ACTION){ est.textContent = "Estamos terminando de abrir la lista: vuelvan en unos días. ¡Gracias por la paciencia! ✨"; return; }
    const btn = f.querySelector("button"); if (btn) btn.disabled = true;
    try {
      const datos = new FormData(); datos.append("EMAIL", v); datos.append("email_address_check", ""); datos.append("locale", "es");
      await fetch(NEWSLETTER_ACTION, { method:"POST", body:datos, mode:"no-cors" });
      est.textContent = "¡Listo! Les mandamos un mail: confirmen ahí y quedan anotados ✨"; f.reset();
    } catch(err){ est.textContent = "No pudimos anotarlos. Prueben de nuevo en un rato."; }
    if (btn) btn.disabled = false;
  });
}
conectarFormMail("form-news", "news-mail", "news-estado");
conectarFormMail("form-proximo", "proximo-mail", "proximo-estado");
''' + s[fin:]
p.write_text(s, encoding="utf-8")
print("ok")
