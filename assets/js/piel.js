// ============================================
// MEU — PIEL v0 · conmutador de dirección display
// La decisión tipográfica del moodboard está
// abierta: A grotesca condensada / B serif gótica
// / C collage. Este conmutador existe para poder
// comparar las tres en vivo y decidir.
// ============================================

(function () {
    const PIELES = ['piel-a', 'piel-b', 'piel-c'];
    const STORAGE_KEY = 'meu-piel-v0';

    const title = document.querySelector('.site-title');
    const originalTitle = title ? title.textContent : '';

    // Dirección C: el título se corta letra a letra
    // (collage como elemento gráfico, no fuente de sistema)
    function renderCollageTitle() {
        if (!title) return;
        let i = 0;
        title.innerHTML = originalTitle.split(' ').map(function (word) {
            const letters = word.split('').map(function (ch) {
                // variante determinista por posición+carácter, para que
                // el recorte sea siempre el mismo (no aleatorio en cada carga);
                // la 4 (letra quemada en magenta) sale 1 de cada 8
                const v = (i * 3 + ch.charCodeAt(0)) % 8;
                const variant = v < 5 ? v : v - 5;
                i++;
                return '<span class="cut cut-' + variant + '">' + ch + '</span>';
            }).join('');
            // cada palabra es un bloque: el collage no se corta a mitad de palabra
            return '<span class="cut-word">' + letters + '</span>';
        }).join('<span class="cut cut-space"> </span>');
    }

    function restoreTitle() {
        if (!title) return;
        title.textContent = originalTitle;
    }

    function apply(piel) {
        if (PIELES.indexOf(piel) === -1) piel = PIELES[0];
        PIELES.forEach(function (p) { document.body.classList.remove(p); });
        document.body.classList.add(piel);

        if (piel === 'piel-c') renderCollageTitle();
        else restoreTitle();

        document.querySelectorAll('.piel-switch button').forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.piel === piel);
        });

        try { localStorage.setItem(STORAGE_KEY, piel); } catch (e) { /* modo incógnito */ }
    }

    document.querySelectorAll('.piel-switch button').forEach(function (btn) {
        btn.addEventListener('click', function () { apply(btn.dataset.piel); });
    });

    let stored = null;
    try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) { /* modo incógnito */ }
    apply(stored || PIELES[0]);
})();
