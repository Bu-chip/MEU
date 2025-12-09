// ============================================
// BILBAO UNDERGROUND - REDESIGN
// ============================================

// Variables globales
let DATA = null;
let currentTab = 'artistas';
let filteredItems = [];
let searchResultsCache = {};
let navigationHistory = []; // Historial de navegación
let currentContext = null; // Contexto actual (para random inteligente)

// ============================================
// INICIALIZACIÓN
// ============================================

window.addEventListener('DOMContentLoaded', function() {
    fetch('data/bandcamp_bilbaotags_clean.json')
        .then(response => response.json())
        .then(data => {
            DATA = data;
            init();
        })
        .catch(err => {
            alert('Error al cargar los datos: ' + err.message);
        });
});

function init() {
    // Ocultar loading screen
    document.getElementById('loadingScreen').classList.add('loaded');
    document.getElementById('mainContainer').classList.add('active');

    // Actualizar estadísticas
    document.getElementById('statAlbums').textContent = DATA.albums.length;
    document.getElementById('statArtists').textContent = DATA.artists.length;
    document.getElementById('statTags').textContent = DATA.tags.length;
    document.getElementById('statYears').textContent = DATA.years.length;

    // Cargar pestaña inicial
    loadTab('artistas');
    document.querySelector('[data-tab="artistas"]').classList.add('active');

    // Setup event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Búsqueda
    document.getElementById('search').addEventListener('input', handleSearch);

    // Random button
    document.getElementById('randomBtn').addEventListener('click', handleRandom);

    // Back button
    document.getElementById('backBtn').addEventListener('click', goBack);

    // Stats cards navigation
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('click', function() {
            const tab = this.dataset.tab;
            if (tab) goToTab(tab);
        });
    });
}

// ============================================
// NAVEGACIÓN ENTRE TABS
// ============================================

function goToTab(tabName) {
    // Limpiar búsqueda
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('searchResults');
    const contentWrapper = document.querySelector('.content-wrapper');

    if (searchInput) searchInput.value = '';
    if (searchResults) {
        searchResults.classList.remove('active');
        searchResults.innerHTML = '';
    }
    if (contentWrapper) contentWrapper.style.display = 'grid';

    // Actualizar estado activo de stats
    document.querySelectorAll('.stat-card').forEach(box => box.classList.remove('active'));
    const activeCard = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeCard) activeCard.classList.add('active');

    // Cargar contenido
    currentTab = tabName;
    loadTab(tabName);
}

function loadTab(tab) {
    const sidebarList = document.getElementById('sidebarList');
    const sidebarTitle = document.getElementById('sidebarTitle');
    const sidebarCount = document.getElementById('sidebarCount');
    document.getElementById('search').value = '';

    if (tab === 'artistas') {
        filteredItems = [...DATA.artists];
        sidebarTitle.textContent = 'ARTISTAS';
        sidebarCount.textContent = `${filteredItems.length} total`;
        renderList(filteredItems, (item) => `${sanitizeForHTML(item)} (${getArtistAlbumCount(item)})`);
    } else if (tab === 'tags') {
        filteredItems = [...DATA.tags];
        sidebarTitle.textContent = 'TAGS';
        sidebarCount.textContent = `${filteredItems.length} total`;
        renderList(filteredItems, (item) => `${sanitizeForHTML(item)} (${getTagCount(item)})`);
    } else if (tab === 'albums') {
        filteredItems = [...DATA.albums];
        sidebarTitle.textContent = 'ÁLBUMES';
        sidebarCount.textContent = `${filteredItems.length} total`;
        sidebarList.innerHTML = filteredItems.map(album =>
            `<div class="list-item" onclick="showAlbum(${album.id})">${sanitizeForHTML(album.artist)} - ${sanitizeForHTML(album.title)}</div>`
        ).join('');
    } else if (tab === 'years') {
        filteredItems = [...DATA.years];
        sidebarTitle.textContent = 'AÑOS';
        sidebarCount.textContent = `${filteredItems.length} total`;
        sidebarList.innerHTML = filteredItems.map(year =>
            `<div class="list-item" onclick="showYearAlbums(${year})">${year} (${getYearCount(year)} álbumes)</div>`
        ).join('');
    }
}

function renderList(items, formatter) {
    const sidebarList = document.getElementById('sidebarList');
    sidebarList.innerHTML = items.map(item =>
        `<div class="list-item" onclick="handleItemClick('${escapeHtml(item)}')">${formatter(item)}</div>`
    ).join('');
}

function handleItemClick(item) {
    if (currentTab === 'artistas') showArtistAlbums(item);
    else if (currentTab === 'tags') showTagAlbums(item);
    else if (currentTab === 'years') showYearAlbums(parseInt(item));
}

// ============================================
// CONTADORES
// ============================================

function getArtistAlbumCount(artist) {
    return DATA.albums.filter(a => a.artist === artist).length;
}

function getTagCount(tag) {
    return DATA.albums.filter(a => a.tags.includes(tag)).length;
}

function getYearCount(year) {
    return DATA.albums.filter(a => a.year === year).length;
}

// ============================================
// BÚSQUEDA GLOBAL
// ============================================

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    const searchResults = document.getElementById('searchResults');
    const contentWrapper = document.querySelector('.content-wrapper');

    if (query === '') {
        searchResults.classList.remove('active');
        searchResults.innerHTML = '';
        contentWrapper.style.display = 'grid';
        return;
    }

    contentWrapper.style.display = 'none';
    searchResults.classList.add('active');

    // Buscar en todas las categorías
    const artistResults = DATA.artists.filter(artist =>
        artist.toLowerCase().includes(query)
    );

    const albumResults = DATA.albums.filter(album =>
        album.title.toLowerCase().includes(query) ||
        album.artist.toLowerCase().includes(query)
    );

    const tagResults = DATA.tags.filter(tag =>
        tag.toLowerCase().includes(query)
    );

    const yearResults = DATA.years.filter(year =>
        year.toString().includes(query)
    );

    // Construir HTML
    let html = '';

    // Artistas
    if (artistResults.length > 0) {
        searchResultsCache.artists = artistResults;
        html += buildSearchCategory('ARTISTAS', artistResults, 'artists', (artist) =>
            `${sanitizeForHTML(artist)} <span style="color:var(--text-secondary)">(${getArtistAlbumCount(artist)} álbumes)</span>`,
            (artist) => `searchShowArtist('${escapeHtml(artist)}')`
        );
    }

    // Álbumes
    if (albumResults.length > 0) {
        searchResultsCache.albums = albumResults;
        html += buildSearchCategory('ÁLBUMES', albumResults, 'albums', (album) =>
            `<div style="font-weight:600">${sanitizeForHTML(album.title)}</div>
             <div style="font-size:14px;color:var(--text-secondary)">${sanitizeForHTML(album.artist)} • ${album.year || '?'}</div>`,
            (album) => `showAlbum(${album.id})`
        );
    }

    // Tags
    if (tagResults.length > 0) {
        searchResultsCache.tags = tagResults;
        html += buildSearchCategory('TAGS', tagResults, 'tags', (tag) =>
            `${sanitizeForHTML(tag)} <span style="color:var(--text-secondary)">(${getTagCount(tag)} álbumes)</span>`,
            (tag) => `searchShowTag('${escapeHtml(tag)}')`
        );
    }

    // Años
    if (yearResults.length > 0) {
        html += buildSearchCategory('AÑOS', yearResults, 'years', (year) =>
            `${year} <span style="color:var(--text-secondary)">(${getYearCount(year)} álbumes)</span>`,
            (year) => `searchShowYear(${year})`
        );
    }

    if (html === '') {
        html = `<div class="search-no-results">No se encontraron resultados para "${query}"</div>`;
    }

    searchResults.innerHTML = html;
}

function buildSearchCategory(title, results, type, formatter, clickHandler) {
    const displayResults = results.slice(0, 10);
    const hasMore = results.length > 10;

    return `
        <div class="search-category">
            <div class="search-category-title">
                ${sanitizeForHTML(title)}
                <span class="search-category-count">(${results.length})</span>
            </div>
            <div id="${type}-results">
                ${displayResults.map(item => `
                    <div class="search-result-item" onclick="${clickHandler(item)}">
                        ${formatter(item)}
                    </div>
                `).join('')}
            </div>
            ${hasMore ? `
                <button class="show-more-btn" onclick="showMoreResults('${type}')">
                    Ver todos (${results.length})
                </button>
            ` : ''}
        </div>
    `;
}

function showMoreResults(type) {
    const container = document.getElementById(`${type}-results`);
    const items = searchResultsCache[type];

    if (!items) return;

    if (type === 'artists') {
        container.innerHTML = items.map(artist => `
            <div class="search-result-item" onclick="searchShowArtist('${escapeHtml(artist)}')">
                ${sanitizeForHTML(artist)} <span style="color:var(--text-secondary)">(${getArtistAlbumCount(artist)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'tags') {
        container.innerHTML = items.map(tag => `
            <div class="search-result-item" onclick="searchShowTag('${escapeHtml(tag)}')">
                ${sanitizeForHTML(tag)} <span style="color:var(--text-secondary)">(${getTagCount(tag)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'albums') {
        container.innerHTML = items.map(album => `
            <div class="search-result-item" onclick="showAlbum(${album.id})">
                <div style="font-weight:600">${sanitizeForHTML(album.title)}</div>
                <div style="font-size:14px;color:var(--text-secondary)">${sanitizeForHTML(album.artist)} • ${album.year || '?'}</div>
            </div>
        `).join('');
    }

    window.event.target.style.display = 'none';
}

// ============================================
// RANDOM
// ============================================

function handleRandom() {
    let randomAlbum;

    // Random inteligente según contexto
    if (currentContext) {
        let filteredAlbums = [];

        if (currentContext.type === 'tag') {
            filteredAlbums = DATA.albums.filter(a => a.tags.includes(currentContext.name));
        } else if (currentContext.type === 'year') {
            filteredAlbums = DATA.albums.filter(a => a.year === currentContext.year);
        } else if (currentContext.type === 'artist') {
            filteredAlbums = DATA.albums.filter(a => a.artist === currentContext.name);
        } else if (currentContext.type === 'genre') {
            filteredAlbums = DATA.albums.filter(a => a.genre === currentContext.name);
        }

        if (filteredAlbums.length > 0) {
            randomAlbum = filteredAlbums[Math.floor(Math.random() * filteredAlbums.length)];
        } else {
            randomAlbum = DATA.albums[Math.floor(Math.random() * DATA.albums.length)];
        }
    } else {
        randomAlbum = DATA.albums[Math.floor(Math.random() * DATA.albums.length)];
    }

    showAlbum(randomAlbum.id);

    // Cerrar búsqueda si está abierta
    document.getElementById('search').value = '';
    document.getElementById('searchResults').classList.remove('active');
    document.querySelector('.content-wrapper').style.display = 'grid';
}

// ============================================
// MOSTRAR ÁLBUM
// ============================================

function showAlbum(albumId, addHistory = true) {
    const album = DATA.albums.find(a => a.id === albumId);
    if (!album) return;

    // Agregar al historial
    if (addHistory && navigationHistory.length === 0 ||
        (navigationHistory.length > 0 && navigationHistory[navigationHistory.length - 1].id !== albumId)) {
        addToHistory({ type: 'album', id: albumId });
    }

    // Actualizar contexto (el álbum no cambia el contexto de random)
    updateRandomButton();

    const detail = document.getElementById('detailArea');

    let html = `
        <div class="album-detail">
            <div class="album-title">${sanitizeForHTML(album.title)}</div>
            <div class="album-artist">${sanitizeForHTML(album.artist)}</div>

            <div class="album-meta">
                <div class="meta-item">
                    <div class="meta-label">GÉNERO</div>
                    <div class="meta-value">${sanitizeForHTML(album.genre)}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">AÑO</div>
                    <div class="meta-value">${album.year || '?'}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">TAGS</div>
                    <div class="meta-value">${album.tags.length}</div>
                </div>
            </div>
    `;

    // Tags
    if (album.tags.length > 0) {
        html += `
            <div class="section-title coral-accent">TAGS</div>
            <div class="tag-cloud">
                ${album.tags.map(tag =>
                    `<span class="tag" onclick="showTagAlbums('${escapeHtml(tag)}')">${sanitizeForHTML(tag)}</span>`
                ).join('')}
            </div>
        `;
    }

    // Enlace a Bandcamp
    if (album.url) {
        html += `<a href="${album.url}" target="_blank" class="bandcamp-btn">ABRIR EN BANDCAMP ↗</a>`;
    }

    // Más del mismo artista (shuffled)
    const sameArtist = shuffleArray(
        DATA.albums.filter(a => a.artist === album.artist && a.id !== album.id)
    ).slice(0, 6);
    if (sameArtist.length > 0) {
        html += `
            <div class="related-section">
                <div class="section-title mint-accent">MÁS DE ${sanitizeForHTML(album.artist)}</div>
                <div class="related-grid">
                    ${sameArtist.map(a => `
                        <div class="related-album" onclick="showAlbum(${a.id})">
                            <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                            <div class="related-album-artist">${a.year || '?'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Álbumes similares (shuffled)
    if (album.tags.length > 0) {
        const sameTags = shuffleArray(
            DATA.albums.filter(a => a.id !== album.id && a.tags.some(t => album.tags.includes(t)))
        ).slice(0, 6);

        if (sameTags.length > 0) {
            html += `
                <div class="related-section">
                    <div class="section-title coral-accent">ÁLBUMES SIMILARES</div>
                    <div class="related-grid">
                        ${sameTags.map(a => `
                            <div class="related-album" onclick="showAlbum(${a.id})">
                                <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                                <div class="related-album-artist">${sanitizeForHTML(a.artist)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    html += '</div>';
    detail.innerHTML = html;
}

// ============================================
// MOSTRAR ARTISTA
// ============================================

function showArtistAlbums(artist, addHistory = true) {
    const albums = DATA.albums.filter(a => a.artist === artist);
    const detail = document.getElementById('detailArea');

    // Agregar al historial
    if (addHistory) {
        addToHistory({ type: 'artist', name: artist });
    }

    // Actualizar contexto
    currentContext = { type: 'artist', name: artist };
    updateRandomButton();

    // Calcular estadísticas
    const years = albums.map(a => a.year).filter(y => y).sort((a, b) => a - b);
    const firstYear = years[0];
    const lastYear = years[years.length - 1];
    const genres = [...new Set(albums.map(a => a.genre))];

    // Tags más frecuentes
    const tagCount = {};
    albums.forEach(album => {
        album.tags.forEach(tag => {
            tagCount[tag] = (tagCount[tag] || 0) + 1;
        });
    });

    const topTags = Object.entries(tagCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    // Construir HTML
    let html = `
        <div class="artist-header">
            <div class="album-title">${sanitizeForHTML(artist)}</div>

            <div class="artist-meta-grid">
                <div class="meta-item">
                    <div class="meta-label">ÁLBUMES</div>
                    <div class="meta-value">${albums.length}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">AÑOS ACTIVO</div>
                    <div class="meta-value">${firstYear}${lastYear !== firstYear ? ' - ' + lastYear : ''}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">GÉNEROS</div>
                    <div class="meta-value">${genres.length}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">TAGS ÚNICOS</div>
                    <div class="meta-value">${Object.keys(tagCount).length}</div>
                </div>
            </div>
        </div>
    `;

    // Géneros
    if (genres.length > 0) {
        html += `
            <div class="section-title coral-accent">GÉNEROS</div>
            <div class="tag-cloud">
                ${genres.map(genre =>
                    `<span class="tag" onclick="searchShowGenre('${escapeHtml(genre)}')">${sanitizeForHTML(genre)}</span>`
                ).join('')}
            </div>
        `;
    }

    // Tags más frecuentes
    if (topTags.length > 0) {
        html += `
            <div class="section-title mint-accent">TAGS MÁS FRECUENTES</div>
            <div class="tag-cloud">
                ${topTags.map(([tag, count]) =>
                    `<span class="tag" onclick="searchShowTag('${escapeHtml(tag)}')">${sanitizeForHTML(tag)} <span style="color:var(--text-secondary)">(${count})</span></span>`
                ).join('')}
            </div>
        `;
    }

    // Discografía
    const sortedAlbums = albums.sort((a, b) => (b.year || 0) - (a.year || 0));

    html += `
        <div class="section-title coral-accent">DISCOGRAFÍA</div>
        <div class="related-grid">
            ${sortedAlbums.map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                    <div class="related-album-artist">${a.year || '?'} • ${sanitizeForHTML(a.genre)}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR TAG
// ============================================

function showTagAlbums(tag, addHistory = true) {
    const albums = DATA.albums.filter(a => a.tags.includes(tag));
    const detail = document.getElementById('detailArea');

    // Agregar al historial
    if (addHistory) {
        addToHistory({ type: 'tag', name: tag });
    }

    // Actualizar contexto
    currentContext = { type: 'tag', name: tag };
    updateRandomButton();

    // Shuffle albums
    const shuffledAlbums = shuffleArray(albums);

    let html = `
        <div class="section-title mint-accent">TAG: ${sanitizeForHTML(tag)}</div>
        <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${shuffledAlbums.slice(0, 40).map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                    <div class="related-album-artist">${sanitizeForHTML(a.artist)}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR AÑO
// ============================================

function showYearAlbums(year, addHistory = true) {
    const albums = DATA.albums.filter(a => a.year === year);
    const detail = document.getElementById('detailArea');

    // Agregar al historial
    if (addHistory) {
        addToHistory({ type: 'year', year: year });
    }

    // Actualizar contexto
    currentContext = { type: 'year', year: year };
    updateRandomButton();

    // Shuffle albums
    const shuffledAlbums = shuffleArray(albums);

    let html = `
        <div class="section-title coral-accent">AÑO: ${year}</div>
        <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${shuffledAlbums.map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                    <div class="related-album-artist">${sanitizeForHTML(a.artist)}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR GÉNERO
// ============================================

function searchShowGenre(genre, addHistory = true) {
    const albums = DATA.albums.filter(a => a.genre === genre);
    const detail = document.getElementById('detailArea');

    // Agregar al historial
    if (addHistory) {
        addToHistory({ type: 'genre', name: genre });
    }

    // Actualizar contexto
    currentContext = { type: 'genre', name: genre };
    updateRandomButton();

    // Shuffle albums
    const shuffledAlbums = shuffleArray(albums);

    let html = `
        <div class="section-title mint-accent">GÉNERO: ${sanitizeForHTML(genre)}</div>
        <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${shuffledAlbums.slice(0, 40).map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${sanitizeForHTML(a.title)}</div>
                    <div class="related-album-artist">${sanitizeForHTML(a.artist)}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// FUNCIONES DE BÚSQUEDA (DESDE RESULTADOS)
// ============================================

function searchShowArtist(artist) {
    closeSearch();
    showArtistAlbums(artist);
}

function searchShowTag(tag) {
    closeSearch();
    showTagAlbums(tag);
}

function searchShowYear(year) {
    closeSearch();
    showYearAlbums(year);
}

function closeSearch() {
    document.getElementById('search').value = '';
    document.getElementById('searchResults').classList.remove('active');
    document.getElementById('searchResults').innerHTML = '';
    document.querySelector('.content-wrapper').style.display = 'grid';
}

// ============================================
// UTILIDADES
// ============================================

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/\\/g, '\\\\')  // Escape backslashes first
        .replace(/'/g, "\\'")     // Escape single quotes
        .replace(/"/g, '\\"')     // Escape double quotes
        .replace(/\n/g, '\\n')    // Escape newlines
        .replace(/\r/g, '\\r');   // Escape carriage returns
}

function sanitizeForHTML(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Shuffle array (Fisher-Yates)
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// ============================================
// HISTORIAL DE NAVEGACIÓN
// ============================================

function addToHistory(state) {
    navigationHistory.push(state);
    updateBackButton();
}

function goBack() {
    if (navigationHistory.length > 0) {
        const previousState = navigationHistory.pop();

        // Restaurar estado sin agregar al historial
        if (previousState.type === 'album') {
            showAlbum(previousState.id, false);
        } else if (previousState.type === 'artist') {
            showArtistAlbums(previousState.name, false);
        } else if (previousState.type === 'tag') {
            showTagAlbums(previousState.name, false);
        } else if (previousState.type === 'year') {
            showYearAlbums(previousState.year, false);
        } else if (previousState.type === 'genre') {
            searchShowGenre(previousState.name, false);
        }

        updateBackButton();
    }
}

function updateBackButton() {
    const backBtn = document.getElementById('backBtn');
    if (navigationHistory.length > 0) {
        backBtn.style.display = 'block';
    } else {
        backBtn.style.display = 'none';
    }
}

// ============================================
// RANDOM INTELIGENTE
// ============================================

function updateRandomButton() {
    const randomText = document.getElementById('randomText');

    if (currentContext) {
        if (currentContext.type === 'tag') {
            randomText.textContent = `RANDOM: ${currentContext.name}`;
        } else if (currentContext.type === 'year') {
            randomText.textContent = `RANDOM: ${currentContext.year}`;
        } else if (currentContext.type === 'artist') {
            randomText.textContent = `RANDOM: ${currentContext.name}`;
        } else if (currentContext.type === 'genre') {
            randomText.textContent = `RANDOM: ${currentContext.name}`;
        }
    } else {
        randomText.textContent = 'RANDOM';
    }
}
