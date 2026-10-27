<script>
/* «Cómo trabajamos», ya en amarillo (idea de buttermax.net, hecha a mano):
   - las tarjetas siguen al ratón, cada una a su profundidad, como el título de buttermax al entrar;
   - el ratón arrastra una mancha de tinta negra, ancha y líquida (círculos fundidos con un filtro «goo»); las letras que
     quedan debajo se ven amarillas por contraste y, solo en el borde de la mancha, de colores irisados que van cambiando
     de tono (rosa y violeta, luego cian y verde), como en buttermax;
   - la tarjeta que tiene el ratón encima (si va despacio) se acerca con un movimiento de cámara; las demás siguen normales.
   Solo con ratón y si no se pide reducir el movimiento */
(function(){
  var banda=document.querySelector('.metodo'),cv=banda&&banda.querySelector('.metodo-tinta');
  if(!cv||!matchMedia('(hover: hover) and (pointer: fine)').matches||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var cx=cv.getContext('2d'),aux=document.createElement('canvas'),ax=aux.getContext('2d');
  var nucleo=document.createElement('canvas'),nx_=nucleo.getContext('2d'),capa=document.createElement('canvas'),kx=capa.getContext('2d');
  if(!cx||!ax||!nx_||!kx)return;
  var fin=banda.querySelector('.metodo-fin'),camara=fin.querySelector('.metodo-camara'),goo=document.querySelector('#tinta-goo feGaussianBlur');
  var W=0,H=0,dpr=1,gotas=[],raf=0,palabras=[],activa=null,raton=null,cabeza=null,listo=false;
  // la tarjeta bajo el ratón solo se activa cuando el ratón va despacio: una pasada rápida deja solo la tinta
  var sobre=null,velocidad=0,tMov=0,previo=null,LENTO=.32;
  var VIDA=1500,R_MIN=28,R_MAX=72,PASO=5,AMARILLO='#F6C81E',BORDE=17;   // BORDE: ancho de la franja de colores
  var conFiltro='filter' in cx;
  var ESTIRA={'100%':'normal','112.5%':'semi-expanded','125%':'expanded','150%':'extra-expanded'};
  // cada tarjeta sigue al ratón con su propia profundidad (unas se mueven más que otras)
  var capas=[].slice.call(fin.querySelectorAll('.metodo-lista li')).map(function(li,i){
    return {li:li,x:0,y:0,ox:0,oy:0,kx:[24,14,30,18,26][i%5],ky:[14,24,12,20,16][i%5],rx:0,ry:0,orx:0,ory:0};
  });

  function medir(){
    var r=fin.getBoundingClientRect();dpr=Math.min(window.devicePixelRatio||1,2);W=r.width;H=r.height;
    cv.width=aux.width=nucleo.width=capa.width=Math.round(W*dpr);cv.height=aux.height=nucleo.height=capa.height=Math.round(H*dpr);
    if(goo)goo.setAttribute('stdDeviation',String(11*dpr));
  }
  // dónde está cada palabra con las tarjetas en reposo, para repintarla en amarillo encima de la tinta
  function mapear(){
    capas.forEach(function(c){c.x=c.y=0;c.li.style.setProperty('--mx','0px');c.li.style.setProperty('--my','0px')});
    medir();
    var base=fin.getBoundingClientRect(),rango=document.createRange();palabras=[];
    fin.querySelectorAll('.metodo-lista .paso-num,.metodo-lista h4,.metodo-lista p').forEach(function(el){
      var cs=getComputedStyle(el),li=el.closest('li'),fuente=cs.fontStyle+' '+cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily,estira=ESTIRA[cs.fontStretch]||'normal';
      var capa=capas.filter(function(c){return c.li===li})[0];
      cx.font=fuente;if('fontStretch' in cx)cx.fontStretch=estira;
      var sube=cx.measureText('Hg').fontBoundingBoxAscent||parseFloat(cs.fontSize)*.9;
      var marcha=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),nodo;
      while((nodo=marcha.nextNode())){
        var re=/\S+/g,m;
        while((m=re.exec(nodo.textContent))){
          rango.setStart(nodo,m.index);rango.setEnd(nodo,m.index+m[0].length);
          var r=rango.getClientRects()[0];if(!r)continue;
          palabras.push({t:m[0],x:r.left-base.left,y:r.top-base.top+sube,w:r.width,h:r.height,top:r.top-base.top,f:fuente,e:estira,ls:cs.letterSpacing,c:parseFloat(cs.fontSize),capa:capa,
            nodo:nodo,a:m.index,b:m.index+m[0].length});
        }
      }
    });
    if('fontStretch' in cx)cx.fontStretch='normal';
  }
  function pedir(){if(!raf)raf=requestAnimationFrame(pintar)}
  // la cabeza de la mancha persigue al ratón con suavidad: el trazo sale fluido aunque el ratón dé tirones
  function avanzar(ahora){
    if(!raton)return;
    if(!cabeza)cabeza={x:raton.x,y:raton.y};
    var nx=cabeza.x+(raton.x-cabeza.x)*.3,ny=cabeza.y+(raton.y-cabeza.y)*.3,paso=Math.hypot(nx-cabeza.x,ny-cabeza.y);
    if(paso<.4)return;
    var r0=Math.min(R_MAX,R_MIN+paso*1.7),n=Math.max(1,Math.ceil(paso/PASO));
    for(var k=1;k<=n;k++)gotas.push({x:cabeza.x+(nx-cabeza.x)*k/n,y:cabeza.y+(ny-cabeza.y)*k/n,r:r0*(.9+Math.random()*.2),t:ahora,v:VIDA});
    if(paso>9&&Math.random()<.35){
      var px=-(ny-cabeza.y)/paso,py=(nx-cabeza.x)/paso,lado=Math.random()<.5?-1:1,lejos=r0*(1.1+Math.random()*.9);
      gotas.push({x:nx+px*lado*lejos,y:ny+py*lado*lejos,r:4+Math.random()*9,t:ahora,v:VIDA*1.3});
    }
    cabeza.x=nx;cabeza.y=ny;
  }
  // las tarjetas se deslizan hacia su objetivo (y la activa se inclina hacia el ratón), siempre con suavidad
  function mover(){
    var quietas=true;
    capas.forEach(function(c){
      c.x+=(c.ox-c.x)*.08;c.y+=(c.oy-c.y)*.08;c.rx+=(c.orx-c.rx)*.14;c.ry+=(c.ory-c.ry)*.14;
      if(Math.abs(c.ox-c.x)+Math.abs(c.oy-c.y)+Math.abs(c.orx-c.rx)+Math.abs(c.ory-c.ry)>.05)quietas=false;
      c.li.style.setProperty('--mx',c.x.toFixed(2)+'px');c.li.style.setProperty('--my',c.y.toFixed(2)+'px');
      c.li.style.setProperty('--rx',c.rx.toFixed(2)+'deg');c.li.style.setProperty('--ry',c.ry.toFixed(2)+'deg');
    });
    return quietas;
  }
  // una palabra en su sitio actual (la tarjeta inclinada se encaja con su escala)
  function letra(c,p,x,top,sx,sy,relleno){
    c.font=p.f;if('fontStretch' in c)c.fontStretch=p.e;if('letterSpacing' in c)c.letterSpacing=p.ls==='normal'?'0px':p.ls;
    c.fillStyle=relleno;
    // sin mover el lienzo cuando se puede: así los colores irisados siguen seguidos de una palabra a otra
    if(sx===1&&sy===1){c.fillText(p.t,x,top+p.y-p.top);return}
    c.save();c.translate(x,top);c.scale(sx,sy);c.fillText(p.t,0,p.y-p.top);c.restore();
  }
  // los colores del borde, irisados como en buttermax: bandas diagonales rosa, blanco, violeta, azul, cian, verde…
  // que desfilan despacio, así cada trozo de borde va cambiando de color
  var tesela=document.createElement('canvas'),tx=tesela.getContext('2d'),PERIODO=230,patron=null;
  tesela.width=PERIODO;tesela.height=8;
  (function(){
    var g=tx.createLinearGradient(0,0,PERIODO,0),tonos=['#FF3ECF','#FFF6FF','#A65BFF','#5470FF','#3FE6E4','#F2FFF8','#58F07A','#D8FF5E','#FF3ECF'];
    tonos.forEach(function(t,i){g.addColorStop(i/(tonos.length-1),t)});
    tx.fillStyle=g;tx.fillRect(0,0,PERIODO,8);
  })();
  function irisado(ahora){
    if(!patron)patron=cx.createPattern(tesela,'repeat');
    if(patron.setTransform&&window.DOMMatrix)patron.setTransform(new DOMMatrix().rotateSelf(-32).translateSelf(-(ahora*.06)%PERIODO,0));
    return patron;
  }
  function apartada(c){return c&&(c.li.classList.contains('activa')||c.li.classList.contains('soltando'))}
  function activar(c){
    if(activa&&activa!==c)soltar(activa);
    activa=c;c.li.classList.remove('soltando');c.li.classList.add('activa');
  }
  function pintar(){
    raf=0;var ahora=performance.now(),quietas=mover();
    if(ahora-tMov>60)velocidad*=.85;
    if(sobre&&activa!==sobre&&velocidad<LENTO)activar(sobre);
    var esperaActivar=sobre&&activa!==sobre;
    avanzar(ahora);
    gotas=gotas.filter(function(g){return ahora-g.t<g.v});
    cx.setTransform(1,0,0,1,0,0);cx.clearRect(0,0,cv.width,cv.height);
    if(!gotas.length){if(raton||!quietas||esperaActivar)pedir();return}
    // 1. la tinta: círculos que encogen con el tiempo, fundidos por el filtro en una sola mancha líquida
    // (y el «núcleo»: la misma mancha encogida BORDE px, para saber dónde acaba la franja del borde)
    ax.setTransform(dpr,0,0,dpr,0,0);ax.clearRect(0,0,W,H);ax.fillStyle='#111';
    nx_.setTransform(dpr,0,0,dpr,0,0);nx_.clearRect(0,0,W,H);nx_.fillStyle='#111';
    var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    gotas.forEach(function(g){
      var r=g.r*Math.pow(1-(ahora-g.t)/g.v,.65);if(r<.5)return;
      ax.beginPath();ax.arc(g.x,g.y,r,0,7);ax.fill();
      if(r>BORDE){nx_.beginPath();nx_.arc(g.x,g.y,r-BORDE,0,7);nx_.fill()}
      x0=Math.min(x0,g.x-r);y0=Math.min(y0,g.y-r);x1=Math.max(x1,g.x+r);y1=Math.max(y1,g.y+r);
    });
    if(conFiltro)cx.filter='url(#tinta-goo)';
    cx.drawImage(aux,0,0);cx.filter='none';
    cx.setTransform(dpr,0,0,dpr,0,0);
    // 2. las palabras que pisa la tinta, allí donde está ahora su tarjeta (la inclinada se mide en vivo)
    var b=fin.getBoundingClientRect(),vivo=document.createRange(),visibles=[];
    palabras.forEach(function(p){
      var x,top,sx=1,sy=1;
      if(apartada(p.capa)){
        vivo.setStart(p.nodo,p.a);vivo.setEnd(p.nodo,p.b);var r=vivo.getClientRects()[0];if(!r)return;
        x=r.left-b.left;top=r.top-b.top;sx=r.width/p.w;sy=r.height/p.h;
      }else{x=p.x+(p.capa?p.capa.x:0);top=p.top+(p.capa?p.capa.y:0)}
      if(x>x1||x+p.w*sx<x0||top>y1||top+p.h*sy<y0)return;
      visibles.push([p,x,top,sx,sy]);
    });
    if(visibles.length){
      // 2a. todas, de colores irisados (lo que quede a la vista será solo la franja del borde)
      cx.globalCompositeOperation='source-atop';cx.textBaseline='alphabetic';cx.textAlign='start';
      var iris=irisado(ahora);
      visibles.forEach(function(v){letra(cx,v[0],v[1],v[2],v[3],v[4],iris)});
      // 2b. encima, en amarillo, pero solo dentro del núcleo: el amarillo por contraste del interior de la mancha
      kx.setTransform(dpr,0,0,dpr,0,0);kx.clearRect(0,0,W,H);kx.textBaseline='alphabetic';kx.textAlign='start';
      visibles.forEach(function(v){letra(kx,v[0],v[1],v[2],v[3],v[4],AMARILLO)});
      kx.setTransform(1,0,0,1,0,0);kx.globalCompositeOperation='destination-in';
      if(conFiltro)kx.filter='url(#tinta-goo)';
      kx.drawImage(nucleo,0,0);kx.filter='none';kx.globalCompositeOperation='source-over';
      cx.setTransform(1,0,0,1,0,0);cx.drawImage(capa,0,0);
    }
    cx.globalCompositeOperation='source-over';
    pedir();
  }
  fin.addEventListener('pointermove',function(e){
    if(!listo)return;
    var b=fin.getBoundingClientRect(),x=e.clientX-b.left,y=e.clientY-b.top,nx=(x-b.width/2)/(b.width/2),ny=(y-b.height/2)/(b.height/2);
    var t=performance.now();
    if(previo){var dt=Math.max(4,t-previo.t),v=Math.hypot(x-previo.x,y-previo.y)/dt;velocidad=velocidad*.6+v*.4}
    previo={x:x,y:y,t:t};tMov=t;
    raton={x:x,y:y};
    capas.forEach(function(c){c.ox=nx*c.kx;c.oy=ny*c.ky});
    pedir();
  },{passive:true});
  fin.addEventListener('pointerleave',function(){
    raton=null;cabeza=null;previo=null;sobre=null;capas.forEach(function(c){c.ox=c.oy=0});pedir();
  });

  // los efectos se encienden cuando la cámara de entrada y la llegada de las tarjetas han terminado del todo
  function cuandoQuieto(){
    var moviendo=getComputedStyle(camara).transform!=='none'||(fin.getAnimations&&fin.getAnimations({subtree:true}).some(function(a){return a.playState==='running'}));
    if(moviendo){setTimeout(cuandoQuieto,150);return}
    banda.classList.add('pasos-listos');mapear();listo=true;
  }
  var esperando=false;
  new MutationObserver(function(){
    if(!banda.classList.contains('fin')||esperando)return;
    esperando=true;setTimeout(cuandoQuieto,1800);
  }).observe(banda,{attributes:true,attributeFilter:['class']});
  addEventListener('resize',function(){
    if(!listo)return;
    capas.forEach(function(c){c.li.classList.remove('activa','soltando');c.orx=c.ory=c.rx=c.ry=0});activa=null;
    requestAnimationFrame(mapear);
  });

  // la tarjeta con el ratón encima: se acerca a cámara, se inclina hacia el ratón y se entinta;
  // al pasar a otra, el efecto se va con el ratón
  function soltar(c){
    if(!c)return;
    c.li.classList.remove('activa');c.li.classList.add('soltando');c.orx=c.ory=0;
    setTimeout(function(){c.li.classList.remove('soltando')},360);
    if(activa===c)activa=null;
  }
  capas.forEach(function(c){
    c.li.addEventListener('pointerenter',function(){if(!listo)return;sobre=c;pedir()});
    c.li.addEventListener('pointermove',function(e){
      if(activa!==c)return;
      var r=c.li.getBoundingClientRect();
      c.ory=((e.clientX-r.left)/r.width-.5)*14;c.orx=-((e.clientY-r.top)/r.height-.5)*12;pedir();
    },{passive:true});
    c.li.addEventListener('pointerleave',function(){if(sobre===c)sobre=null;if(activa===c)soltar(c);pedir()});
  });
})();
</script>
