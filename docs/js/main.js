/* Due cose sole: lo scambio di lingua e la versione pubblicata piu' recente.
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
    try { localStorage.setItem('lingua', lingua); } catch (e) { /* ignorato */ }
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
})();
