/* Lo scambio di lingua, la versione pubblicata piu' recente, il menu sul
   telefono e un'entrata leggera con Motion (facoltativa).
   Se qualcosa non riesce la pagina resta valida com'e'. */

(function () {
  'use strict';

  var html = document.documentElement;
  var rilascio = null;          // dati dell'ultima Release, quando arrivano

  /* --- lingua ------------------------------------------------------------
     Il testo esiste due volte nell'HTML, marcato con lang="it" o lang="en";
     e' il CSS a mostrarne uno solo. Qui si cambia l'attributo e si ricorda
     la scelta. La lingua iniziale e' gia' stata decisa da uno script nel
     <head>, per non far comparire i due testi insieme al caricamento. */

  var TITOLI = {
    it: 'Rejuvenation ITA Patch — Pokémon Rejuvenation in italiano',
    en: 'Rejuvenation ITA Patch — Pokémon Rejuvenation in Italian'
  };

  var bottoni = document.querySelectorAll('[data-imposta]');

  function peso(byte, lingua) {
    var mb = (byte / 1048576).toFixed(1);
    // l'italiano scrive 8,1 MB e l'inglese 8.1 MB
    return (lingua === 'it' ? mb.replace('.', ',') : mb) + ' MB';
  }

  function scriviVersione(lingua) {
    if (!rilascio || !rilascio.tag_name) { return; }
    var testo = rilascio.tag_name;
    if (rilascio.assets && rilascio.assets.length && rilascio.assets[0].size) {
      testo += ' · ' + peso(rilascio.assets[0].size, lingua);
    }
    var campi = document.querySelectorAll('[data-versione]');
    for (var i = 0; i < campi.length; i++) {
      campi[i].textContent = testo;
    }
  }

  function applica(lingua) {
    if (lingua !== 'it' && lingua !== 'en') { lingua = 'it'; }
    html.setAttribute('data-lang', lingua);
    html.setAttribute('lang', lingua);
    document.title = TITOLI[lingua];

    for (var i = 0; i < bottoni.length; i++) {
      var suo = bottoni[i].getAttribute('data-imposta');
      bottoni[i].setAttribute('aria-pressed', suo === lingua ? 'true' : 'false');
    }
    scriviVersione(lingua);
    impostaMenu(menuAperto);
    try { localStorage.setItem('lingua', lingua); } catch (e) { /* ignorato */ }
  }

  /* --- menu sul telefono --------------------------------------------------
     Il pulsante esiste solo quando questo script gira: senza, i link restano
     nella barra, su una seconda riga. */

  var menuBtn = document.getElementById('menu-pulsante');
  var menu = document.getElementById('menu-principale');
  var menuAperto = false;
  var ETICHETTE_MENU = {
    it: { apri: 'Apri il menu', chiudi: 'Chiudi il menu' },
    en: { apri: 'Open menu', chiudi: 'Close menu' }
  };

  function impostaMenu(aperto) {
    menuAperto = aperto;
    if (!menuBtn || !menu) { return; }
    var e = ETICHETTE_MENU[html.getAttribute('data-lang') === 'en' ? 'en' : 'it'];
    menuBtn.setAttribute('aria-expanded', aperto ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', aperto ? e.chiudi : e.apri);
    html.classList.toggle('menu-open', aperto);
  }

  if (menuBtn && menu) {
    menuBtn.hidden = false;
    html.classList.add('menu-ready');
    menuBtn.addEventListener('click', function () { impostaMenu(!menuAperto); });
    menu.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) { impostaMenu(false); }
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && menuAperto) { impostaMenu(false); menuBtn.focus(); }
    });
    if (window.matchMedia) {
      var largo = window.matchMedia('(min-width: 721px)');
      var chiudiSeLargo = function (m) { if (m.matches) { impostaMenu(false); } };
      if (largo.addEventListener) { largo.addEventListener('change', chiudiSeLargo); }
    }
  }

  for (var i = 0; i < bottoni.length; i++) {
    bottoni[i].addEventListener('click', function () {
      applica(this.getAttribute('data-imposta'));
    });
  }

  // allinea i bottoni alla lingua gia' decisa nel <head>
  applica(html.getAttribute('data-lang') || 'it');

  /* --- versione pubblicata ----------------------------------------------- */

  var API = 'https://api.github.com/repos/giosci1994/rejuvenation-ita-patch/releases/latest';

  fetch(API, { headers: { Accept: 'application/vnd.github+json' } })
    .then(function (r) {
      if (!r.ok) { throw new Error(r.status); }
      return r.json();
    })
    .then(function (d) {
      rilascio = d;
      scriviVersione(html.getAttribute('data-lang') || 'it');
    })
    .catch(function () {
      /* nessun problema: resta il testo scritto nell'HTML */
    });

  /* --- entrata con Motion -------------------------------------------------
     Gli elementi [data-reveal] sono nascosti solo finche' Motion e' atteso
     (classe motion-ready, tolta comunque dopo 1,5 s). Qui ognuno sale di
     pochi pixel quando entra nello schermo. Con prefers-reduced-motion o
     senza Motion non si muove niente. */

  (function () {
    var M = window.Motion;
    var ridotto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    clearTimeout(window.__rejuvReveal);
    if (!M || ridotto || !M.animate || !M.inView) {
      html.classList.remove('motion-ready');
      return;
    }
    var curva = [0.22, 1, 0.36, 1];
    var voci = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
    var mostraTutto = function () {
      voci.forEach(function (el) { el.style.opacity = ''; el.style.transform = ''; });
    };
    voci.forEach(function (el) { el.style.opacity = '0'; });
    html.classList.remove('motion-ready');

    var gruppo = 0;
    var timerGruppo = null;
    try {
      voci.forEach(function (el) {
        M.inView(el, function () {
          var ritardo = Math.min(gruppo, 5) * 0.06;
          gruppo += 1;
          clearTimeout(timerGruppo);
          timerGruppo = setTimeout(function () { gruppo = 0; }, 120);
          M.animate(el, { opacity: [0, 1], transform: ['translateY(8px)', 'translateY(0px)'] },
            { duration: 0.45, delay: ritardo, ease: curva });
        }, { amount: 0.15 });
      });
    } catch (e) {
      mostraTutto();
    }
  })();
})();
