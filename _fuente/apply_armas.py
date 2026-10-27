"""Web de propuesta para Reformas Antonio Armas (Las Palmas de Gran Canaria), a partir de la de ESYSS: marca propia
(amarillo de cinta de obra y negro, como su cartel), sin la entrada de ladrillos (abre directo en la portada), sus
servicios (de su Instagram y su cartel), sus reseñas reales de Google y sus datos de contacto públicos.
Uso: python apply_armas.py <index de ESYSS ya construido> <carpeta de destino>"""
import io, sys, os, re, shutil

origen, destino = sys.argv[1], sys.argv[2]
esyss = os.path.dirname(os.path.abspath(origen)) if len(sys.argv) < 4 else sys.argv[3]
s = io.open(origen, encoding='utf-8').read()
MAPS = 'https://www.google.com/maps/search/?api=1&amp;query=Reformas+Antonio+Armas+Las+Palmas+de+Gran+Canaria'


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), n, old[:120])
    s = s.replace(old, new)


def tramo(inicio, fin, nuevo, desde=None):
    global s
    i = s.index(inicio) if desde is None else s.index(inicio, s.index(desde))
    j = s.index(fin, i) + len(fin)
    s = s[:i] + nuevo + s[j:]


MARCA = ('<rect width="56" height="56" rx="9" fill="#F6C81E"/>'
         '<path d="M14 31L28 16.5L42 31" fill="none" stroke="#141414" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M14 40.5H42" fill="none" stroke="#141414" stroke-width="6.5" stroke-linecap="round"/>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 56 56%22%3E"
           "%3Crect width=%2256%22 height=%2256%22 rx=%229%22 fill=%22%23F6C81E%22/%3E"
           "%3Cpath d=%22M14 31L28 16.5L42 31%22 fill=%22none%22 stroke=%22%23141414%22 stroke-width=%226.5%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22/%3E"
           "%3Cpath d=%22M14 40.5H42%22 stroke=%22%23141414%22 stroke-width=%226.5%22 stroke-linecap=%22round%22/%3E%3C/svg%3E")

# ===== cabecera del documento =====
s = re.sub(r'<title>.*?</title>', '<title>Reformas en Las Palmas de Gran Canaria | Reformas Antonio Armas</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]*">',
           '<meta name="description" content="Reformas integrales, baños, alicatados y humedades en Las Palmas de Gran Canaria. '
           '4,9 en Google con 31 reseñas. Llama al 654 83 70 40.">', s, count=1)
s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Reformas Antonio Armas · Las Palmas de Gran Canaria">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">',
           '<meta property="og:description" content="Reformas integrales, baños y humedades, con tu casa cuidada y la obra limpia.">', s, count=1)
s = re.sub(r'<link rel="icon" href="[^"]*">', f'<link rel="icon" href="{FAVICON}">', s, count=1)
s = re.sub(r'<script type="importmap">.*?</script>\n', '', s, count=1)
s = re.sub(r'<script type="application/ld\+json">.*?</script>', '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "GeneralContractor",
  "name": "Reformas Antonio Armas",
  "telephone": "+34 654 83 70 40",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "C. Calzada Lateral del Norte",
    "postalCode": "35014",
    "addressLocality": "Las Palmas de Gran Canaria",
    "addressRegion": "Las Palmas",
    "addressCountry": "ES"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 28.1060077, "longitude": -15.4293026 },
  "areaServed": "Las Palmas de Gran Canaria",
  "sameAs": ["https://www.instagram.com/anntonioarmass/"]
}
</script>''', s, count=1, flags=re.S)

# ===== sin entrada: la web abre directamente en la portada =====
tramo('<div class="entrada" id="intro" hidden>', '</div>\n<script>document.documentElement.classList.add(\'js\');', '<script>document.documentElement.classList.add(\'js\');')
s = re.sub(r"<script>document\.documentElement\.classList\.add\('js'\);\(function\(\)\{var q=matchMedia[^\n]*</script>",
           "<script>document.documentElement.classList.add('js')</script>", s, count=1)
i = s.index('/* Entrada, toda con el scroll:')
j = s.index('\n})();\n', i) + len('\n})();\n')
bloque = s[i:j]
assert 'function fin(saltando)' in bloque and 'listo3d' in bloque, 'el bloque de la entrada no es el esperado'
s = s[:i] + "/* La portada se anima nada más cargar */\n(function(){var html=document.documentElement;requestAnimationFrame(function(){html.classList.add('portada-lista')})})();\n" + s[j:]
s = re.sub(r'<script type="text/plain" id="codigo-muro3d">.*?</script>\n', '', s, count=1, flags=re.S)
tramo('/* ESYSS de ladrillos en 3D para la entrada', "document.body.appendChild(modulo3d);\n}\n", '')
assert 'id="intro"' not in s and 'codigo-muro3d' not in s

# ===== logotipo =====
tramo('<a class="brand" href="#inicio"', '</a>',
      '<a class="brand" href="#inicio" aria-label="Reformas Antonio Armas. Inicio"><svg class="logo logo-armas" viewBox="0 0 332 56" aria-hidden="true">'
      + MARCA + '<text class="armas-nombre" x="70" y="27" font-size="25.5" textLength="262" lengthAdjust="spacingAndGlyphs" translate="no">ANTONIO ARMAS</text>'
      '<text class="armas-lema" x="70.5" y="50.5" font-size="16.5" textLength="261" lengthAdjust="spacing">REFORMAS INTEGRALES</text></svg></a>')

# ===== portada =====
s = re.sub(r'<h1>.*?</h1>', '<h1><span class="l"><span style="--i:0">Tú pones</span></span> <span class="l"><span style="--i:1">la idea,</span></span> '
           '<span class="l"><span style="--i:2">nosotros</span></span> <span class="l"><span style="--i:3"><em>el casco.</em></span></span></h1>', s, count=1, flags=re.S)
rep('<a class="btn btn-solid" href="#contacto">Pide tu visita<svg', '<a class="btn btn-solid" href="#contacto">Pide presupuesto<svg')
s = re.sub(r'<ul class="datos"[^>]*>.*?</ul>', f'''<ul class="datos" aria-label="Reformas Antonio Armas en cuatro datos">
      <li class="dato"><a href="{MAPS}" target="_blank" rel="noopener"><span class="dato-estrellas" aria-hidden="true">★★★★★</span> 4,9 · 31 reseñas</a></li>
      <li class="dato">Trato directo con Antonio</li>
      <li class="dato">Obra limpia y sin ruido</li>
      <li class="dato">Las Palmas de G.C.</li>
    </ul>''', s, count=1, flags=re.S)

# ===== servicios (de su Instagram y su cartel) y reseñas reales de Google =====
rep('<h2 class="h2-grande">Empresa experta en proyectos de albañilería</h2>', '<h2 class="h2-grande">Reformas integrales en Las Palmas</h2>')
SERVICIOS = [('Reformas integrales', 'Reforma integral'), ('Baños', 'Baño'), ('Alicatados', 'Alicatado'), ('Tarima flotante', 'Tarima flotante'),
             ('Pintura y fachadas', 'Pintura o fachada'), ('Humedades', 'Humedades'), ('Locales comerciales', 'Local comercial'),
             ('Comunidades y viviendas vacacionales', 'Comunidad o vivienda vacacional')]
fila = '\n'.join(f'      <li><a href="#contacto" data-servicio="{p}">{n}</a></li>' for n, p in SERVICIOS)
s = re.sub(r'(<ul class="servicios-fila" aria-label="Lo que reformamos">\n).*?(\n    </ul>)', lambda m: m.group(1) + fila + m.group(2), s, count=1, flags=re.S)
rep('<div class="nota-google"><b>4,7</b></div>', '<div class="nota-google"><b>4,9</b></div>')
rep('<stop offset=".7" stop-color="#D9A21B"/><stop offset=".7" stop-color="#E4DBC6"/>', '<stop offset=".9" stop-color="#E3A800"/><stop offset=".9" stop-color="#E4DBC6"/>')
rep('target="_blank" rel="noopener">en Google · 56 reseñas</a>', 'target="_blank" rel="noopener">en Google · 31 reseñas</a>')
RESENAS = [('Terminamos la reforma completa de nuestro piso, en una cuarta planta sin ascensor, y no podríamos estar más contentos. '
            'Muy profesionales, súper limpios y sorprendentemente silenciosos.', 'Matic C.'),
           ('Fueron la solución a nuestros problemas con las humedades: rápidos, con resultados impecables y atención al detalle. '
            'Cuidaron muchísimo la casa y los muebles.', 'Leslie V.'),
           ('Contacté con Antonio para reparar el baño y la experiencia ha sido excelente: profesional, rápido y con una gran '
            'atención al detalle. 100% recomendable.', 'Marina P.')]
bloques = '\n'.join(f'        <blockquote>\n          <p>“{t}”</p>\n          <footer>{a}, reseña en Google</footer>\n        </blockquote>' for t, a in RESENAS)
s = re.sub(r'(<div class="resenas">\n).*?(\n      </div>\n    </div>)', lambda m: m.group(1) + bloques + m.group(2), s, count=1, flags=re.S)

# ===== por qué: frase y cuatro compromisos sacados de lo que dicen sus clientes =====
s = re.sub(r'<h2 class="declaracion" id="declaracion">.*?</h2>',
           '<h2 class="declaracion" id="declaracion">Reformamos tu casa como si fuera la nuestra: la protegemos, trabajamos '
           '<em>limpio y sin ruido</em> y te la devolvemos <em>impecable.</em></h2>', s, count=1, flags=re.S)
for viejo, nuevo in [('El mismo equipo de principio a fin', 'Trato directo con Antonio'), ('Garantía por escrito en cada trabajo', 'Cuidamos tu casa y tus muebles'),
                     ('Presupuesto por partidas, sin sorpresas', 'Atención al detalle en cada acabado'), ('Fecha de entrega acordada antes de empezar', 'Rápidos, sin alargar la obra')]:
    rep(f'<h3>{viejo}</h3>', f'<h3>{nuevo}</h3>')

# ===== cómo trabajamos =====
PASOS = [('Visita y medición', 'Vamos a tu casa, tomamos medidas y escuchamos lo que quieres conseguir.'),
         ('Presupuesto claro', 'Te explicamos qué vamos a hacer y cuánto cuesta antes de empezar.'),
         ('Tu casa, protegida', 'Cubrimos suelos y muebles para que todo quede como estaba.'),
         ('Obra limpia y en silencio', 'Trabajamos ordenados y sin ruido, aunque sea un cuarto piso sin ascensor.'),
         ('Entrega impecable', 'Repasamos cada detalle contigo y te dejamos la casa limpia y lista para vivir.')]
viejos_h3 = re.findall(r'<li class="paso"><h3>(.*?)</h3><p>(.*?)</p></li>', s)
assert len(viejos_h3) == 5
for (h, p), (nh, np_) in zip(viejos_h3, PASOS):
    rep(f'<li class="paso"><h3>{h}</h3><p>{p}</p></li>', f'<li class="paso"><h3>{nh}</h3><p>{np_}</p></li>')
viejos_h4 = re.findall(r'<li style="--i:\d"><h4>(.*?)</h4><p>(.*?)</p></li>', s)
assert len(viejos_h4) == 5
for (h, p), (nh, np_) in zip(viejos_h4, PASOS):
    rep(f'<h4>{h}</h4><p>{p}</p>', f'<h4>{nh}</h4><p>{np_}</p>')

# ===== obras =====
rep('<span>Albañilería</span><b>·</b><span>Baños</span><b>·</b><span>Cocinas</span><b>·</b><span>Reformas integrales</span><b>·</b><span>Gran Canaria</span>',
    '<span>Reformas integrales</span><b>·</b><span>Baños</span><b>·</b><span>Alicatados</span><b>·</b><span>Humedades</span><b>·</b><span>Las Palmas</span>', 3)
rep('src="img/pared-esyss.webp"', 'src="img/pared-armas.webp"')

# ===== contacto: teléfono de su cartel, dirección y mapa de su ficha de Google =====
s = re.sub(r'https://www\.google\.com/maps/search/\?api=1(&amp;|&)query=ESYSS\+Construcciones\+y\+reformas(&amp;|&)query_place_id=ChIJrfx77NuVQAwRNCVSApFx7JU',
           lambda m: MAPS.replace('&amp;', m.group(1)), s)
# menú del móvil: solo el botón de WhatsApp (sin «Llamar» ni la línea de debajo)
for viejo, nuevo in [('    <a class="btn btn-solid" href="tel:+34673368790">Llamar al 673&nbsp;36&nbsp;87&nbsp;90</a>\n', ''),
                     ('\n    <p class="menu-horario">Lunes a viernes, de 8:00 a 16:00</p>', ''),
                     ('673&nbsp;36&nbsp;87&nbsp;90', '654&nbsp;83&nbsp;70&nbsp;40'), ('673 36 87 90', '654 83 70 40'), ('34673368790', '34654837040'),
                     ('Hola%20ESYSS%2C%20quiero%20pedir%20una%20visita', 'Hola%20Antonio%2C%20quiero%20pedir%20presupuesto'),
                     ("'Hola ESYSS, soy '", "'Hola Antonio, soy '"), ("Quiero pedir una visita.'", "Quiero pedir presupuesto.'"),
                     ('<span>Lunes a viernes, de 8:00 a 16:00</span>', '<span>Llamadas y WhatsApp</span>'),
                     ('<b>C. José Franchy Roca, 5</b><span>35007 Las Palmas de Gran Canaria. Ver en el mapa</span>',
                      '<b>C. Calzada Lateral del Norte</b><span>35014 Las Palmas de Gran Canaria. Ver en el mapa</span>'),
                     ('q=28.1386228,-15.4316587', 'q=28.1060077,-15.4293026'),
                     ('title="Mapa: ESYSS en C. José Franchy Roca, 5, Las Palmas de Gran Canaria"', 'title="Mapa: Reformas Antonio Armas, C. Calzada Lateral del Norte, Las Palmas de Gran Canaria"')]:
    assert viejo in s, viejo
    s = s.replace(viejo, nuevo)

# ===== pie =====
tramo('<a class="marca-pie" href="#inicio"', '</a>',
      f'<a class="marca-pie" href="#inicio" aria-label="Reformas Antonio Armas, volver arriba"><svg viewBox="0 0 56 56" aria-hidden="true">{MARCA}</svg><b>Antonio Armas</b></a>')
rep('<span>ESYSS S.L. Construcciones y reformas en Canarias. C. José Franchy Roca, 5, 35007 Las Palmas de Gran Canaria.</span>',
    '<span>Reformas Antonio Armas. Reformas integrales en Las Palmas de Gran Canaria. C. Calzada Lateral del Norte, 35014 Las Palmas de Gran Canaria.</span>')
rep('Maqueta de propuesta para ESYSS S.L. No es su web oficial.', 'Maqueta de propuesta para Reformas Antonio Armas. No es su web oficial.')
# ARMAS del pie: de lado a lado con las proporciones de la letra (208 px de cuerpo ocupan los 1000 de ancho)
s = re.sub(r'<svg class="pie-marca"[^>]*>.*?</svg>',
           '<svg class="pie-marca" viewBox="0 0 1000 150" aria-hidden="true" focusable="false">'
           '<text x="0" y="146" textLength="1000" lengthAdjust="spacingAndGlyphs">ARMAS</text></svg>', s, count=1, flags=re.S)

# ===== editor de la maqueta y fondo de cuadros =====
rep("'Notas para Claude sobre la web de ESYSS ('", "'Notas para Claude sobre la web de Reformas Antonio Armas ('")
rep("'esyss-notas'", "'armas-notas'", 2)
rep("var COLORES=['#1660D6','#D9A21B','#F6C81E'];", "var COLORES=['#1C1C1C','#F6C81E','#E3A800'];")

CSS = r'''
/* ===== Reformas Antonio Armas: amarillo de cinta de obra y negro, como su cartel ===== */
:root{--balcon:#1C1C1C;--balcon-ink:#FFFFFF;--cobalto:#1C1C1C;--barra:#1C1C1C;--piedra:#1A1A1A;--piedra-2:#5E5A54;
  --amarillo:#F6C81E;--ocre:#E3A800;--carbon:#121212;--ocre-claro:#FCEFC2}
.logo-armas .armas-nombre{font-family:var(--f-display);font-weight:800;font-stretch:125%;fill:var(--piedra)}
.logo-armas .armas-lema{font-family:var(--f-body);font-weight:600;fill:var(--piedra-2)}
@media (max-width:420px){.brand .logo{height:38px}}
#servicios::before,#confianza::before,#trabajos::before,#opiniones::before,.cierre::before{opacity:.07}
.btn-solid{box-shadow:0 12px 24px -16px rgba(0,0,0,.7)}
@media (hover:hover){.btn-solid:hover{background:var(--amarillo);border-color:var(--amarillo);color:#141414}}
.top .btn-solid{background:var(--amarillo);border-color:var(--amarillo);color:#141414;box-shadow:0 10px 22px -14px rgba(120,90,0,.8)}
.top .tel-num{color:#141414}
.top .tel-num::before{background:rgba(0,0,0,.25)}
.nav a:hover{color:#000}
.nav a[aria-current="true"]{color:#000;text-decoration:underline;text-decoration-color:var(--amarillo);text-decoration-thickness:3px;text-underline-offset:7px}
.hero h1 em{color:inherit;background:linear-gradient(transparent 58%,var(--amarillo) 58%,var(--amarillo) 90%,transparent 90%);padding-inline:.04em}
.metodo-lista li::before{background:var(--amarillo);color:#141414;box-shadow:0 0 0 7px rgba(246,200,30,.25)}
.obra-etq i+i,.visor figure+figure figcaption{background:var(--amarillo);color:#141414}
.resenas blockquote:first-child{grid-column:1/-1}
@media (max-width:1240px){.datos{grid-template-columns:repeat(4,minmax(0,1fr))}.dato{white-space:normal;padding-right:16px}.dato+.dato{padding-left:16px}}
@media (max-width:900px){.datos{grid-template-columns:repeat(2,minmax(0,1fr))}.dato:nth-child(odd){padding-left:0}}
.pie{background:#0E0E0E}
.pie-marca text{fill:var(--amarillo)}
.pie .marca-pie svg{width:52px}
.pie .marca-pie b{text-transform:uppercase}
/* «¿Hablamos de tu reforma?» pintado en amarillo a rodillo, con el borde algo irregular de la pintura */
.cierre h2{color:#F6C81E;background:url(img/pintura-amarilla.webp) 0 0/auto 100% repeat-x;-webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;filter:url(#borde-pintura)}
/* «Cómo trabajamos» sobre el mismo fondo de cal que el resto, con los cuadros que se encienden al pasar */
#como-trabajamos,.con-metodo .metodo,.metodo-fin{background:transparent}
.metodo-lista li::after{border-top-color:rgba(26,26,26,.28)}
/* Títulos en Archivo Expanded (gratuita, OFL, ya alojada en la web): ancha y gruesa, la elegida en lugar de Agrandir Grand */
:root{--f-titulos:var(--f-display)}
.hero h1,.bloque h2,#servicios .h2-grande,#confianza .declaracion,.cierre h2,.metodo-titulo,.metodo-fin-tit,.menu-panel li a,.nota-google b,.cinta span,.visor-titulo,.pie-marca text{
  font-family:var(--f-titulos);font-stretch:125%;font-weight:800}
.hero h1{font-size:clamp(52px,7.4vw,108px);line-height:.92;letter-spacing:-.03em}
.hero h1 .l{padding-bottom:.08em;margin-bottom:-.08em}
.bloque h2{font-size:clamp(36px,4.6vw,64px);line-height:1;letter-spacing:-.025em;max-width:none}
#servicios .h2-grande{font-size:clamp(40px,5.4vw,82px);line-height:.98;max-width:none}
#confianza .declaracion{font-size:clamp(30px,3.9vw,60px);line-height:1.16;letter-spacing:-.02em;max-width:none}
.cierre h2{font-size:clamp(46px,7.6vw,124px);line-height:.94;letter-spacing:-.03em;max-width:none}
.metodo-titulo{font-size:clamp(30px,9.4vw,170px);line-height:.86;letter-spacing:-.015em}
.metodo-fin-tit{font-size:clamp(38px,5.6vw,80px);letter-spacing:-.025em}
.nota-google b{font-size:clamp(96px,10.5vw,168px);line-height:.82;letter-spacing:-.02em}
.menu-panel li a{font-size:clamp(30px,7.5vw,54px);letter-spacing:-.02em}
.cinta span{font-size:clamp(28px,4vw,52px);letter-spacing:.01em}
/* ARMAS del pie: con 208 px de cuerpo ocupa justo los 1000 de ancho, así que no se deforma */
svg.pie-marca{height:auto;aspect-ratio:1000/150}
.pie-marca text{font-size:208px}
@media (max-width:900px){.hero h1{font-size:clamp(44px,16vw,96px)}}
'''
rep('</style>\n</head>', CSS + '</style>\n</head>')
rep('<h2 id="cierre-titulo">',
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><filter id="borde-pintura" x="-2%" y="-5%" width="104%" height="110%">'
    '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" result="n"/>'
    '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G"/></filter></svg>'
    '<h2 id="cierre-titulo">')

# ===== por qué nosotros: el mini texto «Como invitados», sin los cuatro compromisos de debajo =====
s = re.sub(r'<h2 class="declaracion" id="declaracion">.*?</h2>',
           '<h2 class="declaracion" id="declaracion">Sabemos lo que es abrirle la puerta de casa a una obra. Por eso entramos como invitados: '
           'tapamos suelos y muebles, trabajamos sin ruido y lo dejamos todo recogido. Lo único que se queda es <em>la reforma.</em> '
           'Bueno, y <em>las ganas de enseñarla.</em></h2>', s, count=1, flags=re.S)
s, n = re.subn(r'\n    <div class="confianza">.*?\n    </div>\n', '\n', s, count=1, flags=re.S)
assert n == 1 and 'class="conf"' not in s

# ===== «Cómo trabajamos»: los cinco pasos en negro sobre amarillo, al estilo de buttermax.net =====
rep('<div class="metodo-fin" id="metodo-pasos" hidden>\n      <h3 class="metodo-fin-tit"',
    '<svg class="filtros-tinta" width="0" height="0" aria-hidden="true" focusable="false"><filter id="tinta-goo" x="-20%" y="-20%" width="140%" height="140%" '
    'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="11"/><feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10"/></filter></svg>\n'
    '    <div class="metodo-fin" id="metodo-pasos" hidden>\n      <canvas class="metodo-tinta" aria-hidden="true"></canvas>\n'
    '      <div class="metodo-camara">\n      <h3 class="metodo-fin-tit"')
i = s.index('<ol class="metodo-lista">')
j = s.index('</ol>', i) + len('</ol>')
s = s[:j] + '\n      </div>' + s[j:]
# cada paso con su número grande, para las tarjetas
for k in range(5):
    rep(f'<li style="--i:{k}"><h4>', f'<li style="--i:{k}"><span class="paso-num" aria-hidden="true">0{k + 1}</span><h4>')
# el punto amarillo nace donde está el ratón (o el dedo); con teclado, en el centro
rep("  var ESPERA=2000,cuenta=0;\n  function mostrar(conFoco){\n    if(banda.classList.contains('fin'))return;\n    clearTimeout(cuenta);\n",
    "  var ESPERA=2000,cuenta=0,px=null,py=null;\n"
    "  function apuntar(e){var r=banda.getBoundingClientRect();px=e.clientX-r.left;py=e.clientY-r.top}\n"
    "  banda.addEventListener('pointermove',apuntar,{passive:true});banda.addEventListener('pointerdown',apuntar,{passive:true});\n"
    "  function mostrar(conFoco){\n    if(banda.classList.contains('fin'))return;\n    clearTimeout(cuenta);\n"
    "    fin.style.setProperty('--px',conFoco||px===null?'50%':px+'px');fin.style.setProperty('--py',conFoco||py===null?'50%':py+'px');\n")
TINTA = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tinta_buttermax.js'), encoding='utf-8').read()
rep('</body>\n</html>', TINTA + '</body>\n</html>')

# ===== pie: más limpio y útil, sin el ARMAS gigante =====
tramo('<footer class="pie">', '</footer>', f'''<footer class="pie pie-armas">
  <div class="wrap">
    <div class="pie-arriba">
      <a class="marca-pie" href="#inicio" aria-label="Reformas Antonio Armas, volver arriba"><svg viewBox="0 0 56 56" aria-hidden="true">{MARCA}</svg><span><b>Antonio Armas</b><i>Reformas integrales en Las Palmas de Gran Canaria</i></span></a>
    </div>
    <div class="pie-columnas">
      <div><p class="pie-tit">Llámanos</p><a href="tel:+34654837040">654&nbsp;83&nbsp;70&nbsp;40</a></div>
      <div><p class="pie-tit">Escríbenos</p><a href="https://wa.me/34654837040" target="_blank" rel="noopener">WhatsApp</a></div>
      <div><p class="pie-tit">Dónde estamos</p><a href="{MAPS}" target="_blank" rel="noopener">C. Calzada Lateral del Norte<br>35014 Las Palmas de G.C.</a></div>
      <div><p class="pie-tit">Síguenos</p><a href="https://www.instagram.com/anntonioarmass/" target="_blank" rel="noopener">Instagram</a></div>
    </div>
    <div class="pie-abajo">
      <span>© 2026 Reformas Antonio Armas</span>
      <span class="pie-legal"><a href="aviso-legal.html">Aviso legal</a><a href="privacidad.html">Privacidad y cookies</a></span>
      <span class="aviso-maqueta" role="note">Maqueta de propuesta. No es su web oficial.</span>
    </div>
  </div>
</footer>''')

CSS2 = r'''
/* ===== «Por qué nosotros»: un mini texto ===== */
#confianza .declaracion{font-size:clamp(24px,2.7vw,42px);line-height:1.28;letter-spacing:-.015em;max-width:30em}
/* ===== «Cómo trabajamos» al estilo buttermax: el amarillo se abre desde un punto y los pasos llegan como vistos
   por una cámara que se endereza. El bloque se funde por «diferencia»: amarillo sobre amarillo se ve negro y,
   donde pasa la tinta, las letras se vuelven amarillas ===== */
.metodo-fin{background:var(--amarillo);opacity:1;perspective:1100px;clip-path:circle(0 at var(--px,50%) var(--py,50%));transition:clip-path 1.15s cubic-bezier(.7,0,.2,1)}
.metodo.fin .metodo-fin{clip-path:circle(150vmax at var(--px,50%) var(--py,50%))}
.metodo-tinta{position:absolute;inset:0;width:100%;height:100%;z-index:2;pointer-events:none}
.filtros-tinta{position:absolute;width:0;height:0;overflow:hidden}
.metodo-camara{position:relative;z-index:1;color:#141414;transform-origin:50% 65%;
  transform:translate3d(0,9vh,-420px) rotateX(34deg) rotateZ(-7deg) scale(.9);filter:blur(14px);opacity:0;
  transition:transform 1.6s cubic-bezier(.16,1,.3,1) .45s,filter 1.2s ease .45s,opacity .6s ease .45s}
.metodo.fin .metodo-camara{transform:none;filter:none;opacity:1}
/* sin el título encima de los pasos (sigue para lectores de pantalla y para el foco del teclado) */
.metodo-camara .metodo-fin-tit{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
/* los cinco pasos, cada uno en su tarjeta: tres arriba y dos abajo, más grandes y anchas */
.metodo-fin{padding:clamp(28px,6vh,64px) max(20px,calc(50% - 640px))}
.metodo-camara .metodo-lista{margin:0;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:clamp(14px,1.6vw,22px);perspective:1100px}
.metodo-camara .metodo-lista li{grid-column:span 2;display:flex;flex-direction:column;min-height:clamp(200px,24vh,250px);padding:clamp(22px,2vw,30px) clamp(22px,2.2vw,32px) clamp(24px,2.2vw,32px);
  border:2px solid #141414;border-radius:26px;isolation:isolate}
.metodo-camara .metodo-lista li:nth-child(4){grid-column:2/span 2}
.metodo-camara .metodo-lista li:nth-child(5){grid-column:4/span 2}
.metodo-camara .metodo-lista li::before,.metodo-camara .metodo-lista li::after{content:none;display:none}
.paso-num{display:block;margin-bottom:auto;padding-bottom:18px;font:800 clamp(38px,3.6vw,56px)/1 var(--f-display);font-stretch:125%;letter-spacing:-.03em;color:#141414}
.metodo-camara .metodo-lista h4{margin:0 0 10px;font:800 clamp(22px,1.9vw,30px)/1.08 var(--f-display);font-stretch:125%;letter-spacing:-.02em;color:#141414}
.metodo-camara .metodo-lista p{margin:0;font-size:clamp(16px,1.2vw,18px);line-height:1.45;color:rgba(20,20,20,.8)}
.metodo-lista li{transition-delay:calc(1.05s + var(--i) * .12s)}
/* ya quietas: siguen al ratón (lo mueve el script) y la que tiene el ratón encima se acerca a cámara, sin rellenarse de negro */
.metodo.pasos-listos .metodo-camara .metodo-lista li{transition:none;transform:translate3d(var(--mx,0px),var(--my,0px),0)}
.metodo.pasos-listos .metodo-camara .metodo-lista li.soltando{transition:transform .35s cubic-bezier(.2,.9,.25,1.1),border-color .3s}
.metodo.pasos-listos .metodo-camara .metodo-lista li.soltando{z-index:1}
.metodo-camara .metodo-lista li .paso-num,.metodo-camara .metodo-lista li h4,.metodo-camara .metodo-lista li p{transition:color .2s ease .08s,text-shadow .2s ease .12s}
.metodo.pasos-listos .metodo-camara .metodo-lista li.activa{transition:box-shadow .25s ease}
.metodo.pasos-listos .metodo-camara .metodo-lista li.activa{z-index:1;box-shadow:0 36px 60px -34px rgba(20,20,20,.55);
  transform:translate3d(var(--mx,0px),var(--my,0px),40px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) scale(1.02);animation:camara-paso .6s cubic-bezier(.16,1,.3,1)}
@keyframes camara-paso{from{transform:translate3d(var(--mx,0px),var(--my,0px),-60px) rotateX(26deg) rotateZ(-4deg) scale(.94);filter:blur(5px)}
  to{transform:translate3d(var(--mx,0px),var(--my,0px),40px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) scale(1.02);filter:none}}
@media (max-width:1000px){
  .metodo-camara .metodo-lista{grid-template-columns:repeat(2,minmax(0,1fr))}
  .metodo-camara .metodo-lista li,.metodo-camara .metodo-lista li:nth-child(4),.metodo-camara .metodo-lista li:nth-child(5){grid-column:auto}
}
@media (max-width:760px){
  .con-metodo .metodo.fin{height:auto;min-height:clamp(560px,88svh,780px)}
  .metodo.fin .metodo-fin{position:relative;inset:auto;overflow:visible}
  .metodo-camara .metodo-lista{grid-template-columns:minmax(0,1fr);gap:14px}
  .metodo-camara .metodo-lista li{display:flex;min-height:0}
  .paso-num{margin-bottom:14px;padding-bottom:0}
}
@media (prefers-reduced-motion:reduce){.metodo-fin,.metodo-camara{transition:none}.metodo-camara{transform:none;filter:none}}
/* ===== Pie ===== */
.pie.pie-armas{padding:clamp(56px,8vh,88px) 0 28px;background:#0E0E0E;color:rgba(255,255,255,.62);font-size:15px}
.pie-armas .wrap{display:block}
.pie-armas a{color:#fff;text-decoration:none;transition:color .2s}
.pie-armas a:hover{color:var(--amarillo)}
.pie-arriba{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:24px;padding-bottom:clamp(32px,5vh,48px);border-bottom:1px solid rgba(255,255,255,.12)}
.pie-armas .marca-pie{display:flex;align-items:center;gap:16px;margin:0;flex-basis:auto}
.pie-armas .marca-pie svg{width:56px;height:56px;flex:none}
.pie-armas .marca-pie span{display:grid;gap:4px}
.pie-armas .marca-pie b{font:800 clamp(22px,2.4vw,32px)/1 var(--f-display);font-stretch:125%;text-transform:uppercase;color:#fff;letter-spacing:.01em}
.pie-armas .marca-pie i{font-style:normal;font-size:14px;color:rgba(255,255,255,.55)}
.pie-boton{background:var(--amarillo);border-color:var(--amarillo);color:#141414!important;padding:14px 22px}
.pie-boton:hover{background:#fff;border-color:#fff}
.pie-columnas{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px;padding:clamp(32px,5vh,48px) 0}
.pie-tit{margin:0 0 10px;font:600 12px/1 var(--f-body);letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.45)}
.pie-columnas a{font:600 clamp(17px,1.4vw,20px)/1.35 var(--f-body)}
.pie-abajo{display:flex;flex-wrap:wrap;align-items:center;gap:10px 28px;padding-top:22px;border-top:1px solid rgba(255,255,255,.12);font-size:13.5px}
.pie-legal{display:flex;gap:20px}
.pie-legal a{color:rgba(255,255,255,.75);text-decoration:underline;text-underline-offset:3px}
.pie-armas .aviso-maqueta{margin-left:auto;color:rgba(255,255,255,.4)}
@media (max-width:860px){.pie-columnas{grid-template-columns:repeat(2,minmax(0,1fr))}.pie-armas .aviso-maqueta{margin-left:0}}
@media (max-width:480px){.pie-columnas{grid-template-columns:minmax(0,1fr)}.pie-boton{width:100%}}
'''
rep('</style>\n</head>', CSS2 + '</style>\n</head>')

# el cargador del mapa con botón ya no se usa (el mapa va cargado); y los comentarios del código, sin el nombre de ESYSS
s = s.replace("mapa.title='Mapa: ESYSS en C. José Franchy Roca, 5, Las Palmas de Gran Canaria'",
              "mapa.title='Mapa: Reformas Antonio Armas, C. Calzada Lateral del Norte, Las Palmas de Gran Canaria'")
s = s.replace('azul ESYSS', 'color de la marca').replace('Por qué ESYSS', 'Por qué nosotros').replace('ESYSS', 'la marca')
assert 'ESYSS' not in s and 'Franchy' not in s
resto = re.sub(r'<style>.*?</style>|<script>.*?</script>', '', s, flags=re.S)
assert 'ESYSS' not in resto and 'Franchy' not in resto and '673' not in resto, [m for m in ('ESYSS', 'Franchy', '673') if m in resto]

# ===== archivos =====
os.makedirs(os.path.join(destino, 'img'), exist_ok=True)
for f in ('portada-balcon.webp', 'raya-carretera.webp', 'pared-limpia.webp'):
    shutil.copyfile(os.path.join(esyss, 'img', f), os.path.join(destino, 'img', f))
shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pintura_dir', 'pintura-amarilla.webp'),
                os.path.join(destino, 'img', 'pintura-amarilla.webp'))
if os.path.isdir(os.path.join(destino, 'fuentes')):
    shutil.rmtree(os.path.join(destino, 'fuentes'))
shutil.copytree(os.path.join(esyss, 'fuentes'), os.path.join(destino, 'fuentes'))
io.open(os.path.join(destino, 'index.html'), 'w', encoding='utf-8', newline='').write(s)

# páginas legales: borradores con los datos de Antonio Armas
for nombre in ('aviso-legal.html', 'privacidad.html'):
    t = io.open(os.path.join(esyss, nombre), encoding='utf-8').read()
    for viejo, nuevo in [('| ESYSS Construcciones y Reformas</title>', '| Reformas Antonio Armas</title>'),
                         ('<a class="marca" href="index.html">ESYSS</a>', '<a class="marca" href="index.html">Antonio Armas</a>'),
                         ('Borrador para revisar con ESYSS y su asesor.', 'Borrador para revisar con Reformas Antonio Armas y su asesor.'),
                         ('<li>Titular: ESYSS S.L.</li>', '<li>Titular: <mark>nombre o razón social pendiente</mark> (Reformas Antonio Armas)</li>'),
                         ('<li>CIF: <mark>pendiente</mark></li>', '<li>NIF o CIF: <mark>pendiente</mark></li>'),
                         ('Registro Mercantil de Las Palmas, <mark>tomo, folio, hoja e inscripción pendientes</mark>', '<mark>solo si es una sociedad: Registro Mercantil, tomo, folio, hoja e inscripción</mark>'),
                         ('ESYSS S.L., CIF <mark>pendiente</mark>,', '<mark>Titular pendiente</mark> (Reformas Antonio Armas), NIF o CIF <mark>pendiente</mark>,'),
                         ('C. José Franchy Roca, 5, 35007 Las Palmas de Gran Canaria', 'C. Calzada Lateral del Norte, 35014 Las Palmas de Gran Canaria'),
                         ('tel:+34673368790', 'tel:+34654837040'), ('673 36 87 90', '654 83 70 40'),
                         ('ESYSS S.L.', 'Reformas Antonio Armas'), ('ESYSS', 'Reformas Antonio Armas'),
                         (':root{--cal:#F2F7FB;--piedra:#1D3445;--piedra-2:#4E6577;--balcon:#1660D6;--ocre:#D9A21B;--linea:#C9DAE6}',
                          ':root{--cal:#F5F2EC;--piedra:#1A1A1A;--piedra-2:#5E5A54;--balcon:#1C1C1C;--ocre:#E3A800;--linea:rgba(29,29,29,.14)}\n'
                          'header{box-shadow:inset 0 -4px 0 #F6C81E}')]:
        t = t.replace(viejo, nuevo)
    t = re.sub(r'<link rel="icon" href="[^"]*">', f'<link rel="icon" href="{FAVICON}">', t, count=1)
    assert 'ESYSS' not in t and 'Franchy' not in t
    io.open(os.path.join(destino, nombre), 'w', encoding='utf-8', newline='').write(t)
print('web de Antonio Armas', len(s))
