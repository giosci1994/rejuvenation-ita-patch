/* Mostra la versione pubblicata piu' recente, senza doverla aggiornare a mano.
   Se la chiamata non riesce, la pagina resta valida com'e': il link punta
   comunque all'ultima Release. */

(function () {
  'use strict';

  var API = 'https://api.github.com/repos/giosci1994/rejuvenation-ita-patch/releases/latest';

  function scrivi(testo) {
    var elementi = document.querySelectorAll('[data-versione]');
    for (var i = 0; i < elementi.length; i++) {
      elementi[i].textContent = testo;
    }
  }

  function peso(byte) {
    return (byte / 1048576).toFixed(1).replace('.', ',') + ' MB';
  }

  fetch(API, { headers: { Accept: 'application/vnd.github+json' } })
    .then(function (r) {
      if (!r.ok) { throw new Error(r.status); }
      return r.json();
    })
    .then(function (d) {
      if (d && d.tag_name) {
        var testo = d.tag_name;
        if (d.assets && d.assets.length && d.assets[0].size) {
          testo += ' · ' + peso(d.assets[0].size);
        }
        scrivi(testo);
      }
    })
    .catch(function () {
      /* nessun problema: resta il testo scritto nell'HTML */
    });
})();
