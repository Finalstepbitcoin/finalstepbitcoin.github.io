/* ══════════════════════════════════════════════════════════════════
   STATISTICHE DEL SITO — Counter.dev

   Questa e' una copia FEDELE del file che Counter.dev distribuisce su
   https://cdn.counter.dev/script.js (versione del 29 aprile 2026).
   Sta qui, sul nostro sito, invece che sul loro CDN: cosi' il browser di
   chi visita non deve contattare Cloudflare per scaricarlo. L'unica cosa
   che esce verso l'esterno e' la richiesta di conteggio a t.counter.dev.

   Progetto: https://github.com/ihucos/counter.dev — licenza AGPL-3.0.
   NON MODIFICARE il codice qui sotto: se un domani vuoi aggiornarlo,
   riscarica il file originale e sostituisci tutto quello che segue.

   COSA MANDA, e nient'altro:
     - da dove sei arrivato (il referrer) e la dimensione dello schermo,
       una volta sola per visita, dopo 4,5 secondi
     - l'indirizzo della pagina che stai guardando (es. /risorse.html)
   Nessun cookie. Scrive solo un segnalino "_swa" nella memoria della
   scheda del browser, che sparisce quando la scheda si chiude, e serve a
   non contare due volte la stessa visita.

   COME NON FARSI CONTARE (utile a te, per non falsare i numeri): apri il
   sito, premi ⌥⌘I per la console del browser e incolla
       localStorage.setItem("doNotTrack", "1")
   Da quel momento quel browser viene ignorato per sempre.
   ══════════════════════════════════════════════════════════════════ */

(function () {
    if (sessionStorage.getItem("doNotTrack") || localStorage.getItem("doNotTrack")) {
        return;
    }
    var id = document.currentScript.getAttribute("data-id");
    var utcoffset = document.currentScript.getAttribute("data-utcoffset");
    var server = document.currentScript.getAttribute("data-server") || "https://t.counter.dev";

    if (!sessionStorage.getItem("_swa") && !document.referrer.startsWith(location.protocol + "//" + location.host)) {
        setTimeout(function () {
            sessionStorage.setItem("_swa", "1");
            fetch(
                server +
                    "/track?" +
                    new URLSearchParams({
                        referrer: document.referrer,
                        screen: screen.width + "x" + screen.height,
                        id: id,
                        utcoffset: utcoffset,
                    }),
            );
        }, 4500);
    }
    navigator.sendBeacon(
        server + "/trackpage",
        new URLSearchParams({
            id: id,
            page: window.location.pathname,
        }),
    );
})();
