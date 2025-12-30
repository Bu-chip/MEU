// ============================================
// BILBAO UNDERGROUND - REDESIGN
// ============================================

// Variables globales
let DATA = null;
let currentTab = 'artistas';
let filteredItems = [];
let searchResultsCache = {};

// ============================================
// INICIALIZACIÓN
// ============================================

window.addEventListener('DOMContentLoaded', function () {
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

    // Stats cards navigation
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('click', function () {
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
        renderList(filteredItems, (item) => `${item} (${getArtistAlbumCount(item)})`);
    } else if (tab === 'tags') {
        filteredItems = [...DATA.tags];
        sidebarTitle.textContent = 'TAGS';
        sidebarCount.textContent = `${filteredItems.length} total`;
        renderList(filteredItems, (item) => `${item} (${getTagCount(item)})`);
    } else if (tab === 'albums') {
        filteredItems = [...DATA.albums];
        sidebarTitle.textContent = 'ÁLBUMES';
        sidebarCount.textContent = `${filteredItems.length} total`;
        sidebarList.innerHTML = filteredItems.map(album =>
            `<div class="list-item" onclick="navigateToAlbum(${album.id})">${album.artist} - ${album.title}</div>`
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
            `${artist} <span style="color:var(--text-secondary)">(${getArtistAlbumCount(artist)} álbumes)</span>`,
            (artist) => `searchShowArtist('${escapeHtml(artist)}')`
        );
    }

    // Álbumes
    if (albumResults.length > 0) {
        searchResultsCache.albums = albumResults;
        html += buildSearchCategory('ÁLBUMES', albumResults, 'albums', (album) =>
            `<div style="font-weight:600">${album.title}</div>
             <div style="font-size:14px;color:var(--text-secondary)">${album.artist} • ${album.year || '?'}</div>`,
            (album) => `navigateToAlbum(${album.id})`
        );
    }

    // Tags
    if (tagResults.length > 0) {
        searchResultsCache.tags = tagResults;
        html += buildSearchCategory('TAGS', tagResults, 'tags', (tag) =>
            `${tag} <span style="color:var(--text-secondary)">(${getTagCount(tag)} álbumes)</span>`,
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
                ${title}
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
                ${artist} <span style="color:var(--text-secondary)">(${getArtistAlbumCount(artist)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'tags') {
        container.innerHTML = items.map(tag => `
            <div class="search-result-item" onclick="searchShowTag('${escapeHtml(tag)}')">
                ${tag} <span style="color:var(--text-secondary)">(${getTagCount(tag)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'albums') {
        container.innerHTML = items.map(album => `
            <div class="search-result-item" onclick="navigateToAlbum(${album.id})">
                <div style="font-weight:600">${album.title}</div>
                <div style="font-size:14px;color:var(--text-secondary)">${album.artist} • ${album.year || '?'}</div>
            </div>
        `).join('');
    }

    window.event.target.style.display = 'none';
}

// ============================================
// RANDOM
// ============================================

function handleRandom() {
    const randomAlbum = DATA.albums[Math.floor(Math.random() * DATA.albums.length)];
    navigateToAlbum(randomAlbum.id);
}

// ============================================
// MOSTRAR ÁLBUM
// ============================================

function showAlbum(albumId) {
    const album = DATA.albums.find(a => a.id === albumId);
    if (!album) return;

    const detail = document.getElementById('detailArea');

    let html = `
    <div class="album-detail">
        <div class="album-title">${album.title}</div>
        <div class="album-artist">${album.artist}</div>

        <div class="album-meta">
            <div class="meta-item">
                <div class="meta-label">GÉNERO</div>
                <div class="meta-value">${album.genre}</div>
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
            `<span class="tag" onclick="showTagAlbums('${escapeHtml(tag)}')">${tag}</span>`
        ).join('')}
            </div>
        `;
    }

    // Enlace a Bandcamp
    if (album.url) {
        html += `<a href="${album.url}" target="_blank" class="bandcamp-btn">ABRIR EN BANDCAMP ↗</a>`;
    }

    // Más del mismo artista
    const sameArtist = DATA.albums.filter(a => a.artist === album.artist && a.id !== album.id).slice(0, 6);
    if (sameArtist.length > 0) {
        html += `
            <div class="related-section">
                <div class="section-title mint-accent">MÁS DE ${album.artist}</div>
                <div class="related-grid">
                    ${sameArtist.map(a => `
                        <div class="related-album" onclick="navigateToAlbum(${a.id})">
                            <div class="related-album-title">${a.title}</div>
                            <div class="related-album-artist">${a.year || '?'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Álbumes similares
    if (album.tags.length > 0) {
        const sameTags = DATA.albums.filter(a =>
            a.id !== album.id && a.tags.some(t => album.tags.includes(t))
        ).slice(0, 6);

        if (sameTags.length > 0) {
            html += `
                <div class="related-section">
                    <div class="section-title coral-accent">ÁLBUMES SIMILARES</div>
                    <div class="related-grid">
                        ${sameTags.map(a => `
                            <div class="related-album" onclick="navigateToAlbum(${a.id})">
                                <div class="related-album-title">${a.title}</div>
                                <div class="related-album-artist">${a.artist}</div>
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

function showArtistAlbums(artist) {
    const albums = DATA.albums.filter(a => a.artist === artist);
    const detail = document.getElementById('detailArea');

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
        <div class="album-title">${artist}</div>

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
            `<span class="tag" onclick="searchShowGenre('${escapeHtml(genre)}')">${genre}</span>`
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
            `<span class="tag" onclick="searchShowTag('${escapeHtml(tag)}')">${tag} <span style="color:var(--text-secondary)">(${count})</span></span>`
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
                <div class="related-album" onclick="navigateToAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.year || '?'} • ${a.genre}</div>
                </div>
            `).join('')}
    </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR TAG
// ============================================

function showTagAlbums(tag) {
    const albums = DATA.albums.filter(a => a.tags.includes(tag));
    const detail = document.getElementById('detailArea');

    let html = `
    <div class="section-title mint-accent">TAG: ${tag}</div>
    <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
    <div class="related-grid">
        ${albums.slice(0, 40).map(a => `
                <div class="related-album" onclick="navigateToAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
                </div>
            `).join('')}
    </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR AÑO
// ============================================

function showYearAlbums(year) {
    const albums = DATA.albums.filter(a => a.year === year);
    const detail = document.getElementById('detailArea');

    let html = `
    <div class="section-title coral-accent">AÑO: ${year}</div>
    <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
    <div class="related-grid">
        ${albums.map(a => `
                <div class="related-album" onclick="navigateToAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
                </div>
            `).join('')}
    </div>
    `;

    detail.innerHTML = html;
}

// ============================================
// MOSTRAR GÉNERO
// ============================================

function searchShowGenre(genre) {
    const albums = DATA.albums.filter(a => a.genre === genre);
    const detail = document.getElementById('detailArea');

    let html = `
    <div class="section-title mint-accent">GÉNERO: ${genre}</div>
    <p style="color:var(--text-secondary);margin-bottom:var(--space-lg);font-size:18px">${albums.length} álbumes</p>
    <div class="related-grid">
        ${albums.slice(0, 40).map(a => `
                <div class="related-album" onclick="navigateToAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
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

function navigateToAlbum(albumId) {
    closeSearch();
    showAlbum(albumId);
}



// ============================================
// UTILIDADES
// ============================================

function escapeHtml(text) {
    return text.replace(/'/g, "\\'");
}
