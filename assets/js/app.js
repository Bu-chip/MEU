// Variables globales
let DATA = null;
let currentTab = 'artistas';
let filteredItems = [];
let searchResultsCache = {}; // NUEVA LÍNEA

// Cargar JSON automáticamente al iniciar
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

// Inicialización de la aplicación
function init() {
    document.getElementById('uploadArea').classList.add('loaded');
    document.getElementById('mainContent').classList.add('active');
    document.getElementById('statAlbums').textContent = DATA.albums.length;
    document.getElementById('statArtists').textContent = DATA.artists.length;
    document.getElementById('statTags').textContent = DATA.tags.length;
    document.getElementById('statYears').textContent = DATA.years.length;
    loadTab('artistas');
    document.querySelectorAll('.stat-box')[0].classList.add('active');
}

// Manejo de pestañas
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        currentTab = this.dataset.tab;
        loadTab(currentTab);
    });
});

// Función para ir a una pestaña desde las estadísticas
function goToTab(tabName) {
    // Limpiar búsqueda (con verificación)
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('searchResults');
    const contentArea = document.querySelector('.content-area');
    
    if (searchInput) searchInput.value = '';
    if (searchResults) {
        searchResults.classList.remove('active');
        searchResults.innerHTML = '';
    }
    if (contentArea) contentArea.style.display = 'grid';
    
    // Quitar "active" de todas las estadísticas
    document.querySelectorAll('.stat-box').forEach(box => box.classList.remove('active'));
    
    // Marcar como activa la estadística correspondiente
    const statBoxes = document.querySelectorAll('.stat-box');
    const tabIndex = {
        'artistas': 0,
        'tags': 1,
        'albums': 2,
        'years': 3
    };
    
    if (statBoxes[tabIndex[tabName]]) {
        statBoxes[tabIndex[tabName]].classList.add('active');
    }
    
    // Cargar contenido
    currentTab = tabName;
    loadTab(tabName);
}

// Carga de contenido de pestañas
function loadTab(tab) {
    const sidebar = document.getElementById('sidebar');
    document.getElementById('search').value = '';

    if (tab === 'artistas') {
        filteredItems = [...DATA.artists];
        renderList(filteredItems, (item) => `${item} (${getArtistAlbumCount(item)})`);
    } else if (tab === 'tags') {
        filteredItems = [...DATA.tags];
        renderList(filteredItems, (item) => `${item} (${getTagCount(item)})`);
    } else if (tab === 'albums') {
        filteredItems = [...DATA.albums];
        sidebar.innerHTML = filteredItems.map(album =>
            `<div class="list-item" onclick="showAlbum(${album.id})">${album.artist} - ${album.title}</div>`
        ).join('');
    } else if (tab === 'years') {
    filteredItems = [...DATA.years];
    const sidebar = document.getElementById('sidebar');
    sidebar.innerHTML = filteredItems.map(year =>
        `<div class="list-item" onclick="showYearAlbums(${year})">${year} (${getYearCount(year)} álbumes)</div>`
    ).join('');
}
}

// Renderizado de listas
function renderList(items, formatter) {
    const sidebar = document.getElementById('sidebar');
    sidebar.innerHTML = items.map(item =>
        `<div class="list-item" onclick="handleItemClick('${escapeHtml(item)}')">${formatter(item)}</div>`
    ).join('');
}

// Manejo de clicks en items
function handleItemClick(item) {
    if (currentTab === 'artistas') showArtistAlbums(item);
    else if (currentTab === 'tags') showTagAlbums(item);
    else if (currentTab === 'years') showYearAlbums(parseInt(item));
}

// Funciones de conteo
function getArtistAlbumCount(artist) {
    return DATA.albums.filter(a => a.artist === artist).length;
}

function getTagCount(tag) {
    return DATA.albums.filter(a => a.tags.includes(tag)).length;
}

function getYearCount(year) {
    return DATA.albums.filter(a => a.year === year).length;
}

// Búsqueda global
document.getElementById('search').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase().trim();
    const searchResults = document.getElementById('searchResults');
    const contentArea = document.querySelector('.content-area');
    
    // Si no hay búsqueda, ocultar resultados y mostrar contenido normal
    if (query === '') {
        searchResults.classList.remove('active');
        searchResults.innerHTML = '';
        contentArea.style.display = 'grid';
        return;
    }
    
    // Ocultar contenido normal y mostrar resultados
    contentArea.style.display = 'none';
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
    
    // Construir HTML de resultados
    let html = '';
    
    // Artistas
    if (artistResults.length > 0) {
        searchResultsCache.artists = artistResults; // Guardar en caché
        
        html += `
            <div class="search-category">
                <div class="search-category-title">
                    ▶ ARTISTAS
                    <span class="search-category-count">(${artistResults.length})</span>
                </div>
                <div id="artists-results">
                    ${artistResults.slice(0, 10).map(artist => `
                        <div class="search-result-item" onclick="searchShowArtist('${escapeHtml(artist)}')">
                            ${artist} <span style="color:#0a0">(${getArtistAlbumCount(artist)} álbumes)</span>
                        </div>
                    `).join('')}
                </div>
                ${artistResults.length > 10 ? `
                    <button class="show-more-btn" onclick="showMoreResults('artists')">
                        ▶ Ver todos (${artistResults.length})
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    // Álbumes
    if (albumResults.length > 0) {
        searchResultsCache.albums = albumResults; // Guardar en caché
        
        html += `
            <div class="search-category">
                <div class="search-category-title">
                    ▶ ÁLBUMES
                    <span class="search-category-count">(${albumResults.length})</span>
                </div>
                <div id="albums-results">
                    ${albumResults.slice(0, 10).map(album => `
                        <div class="search-result-item" onclick="showAlbum(${album.id})">
                            <div style="color:#0ff">${album.title}</div>
                            <div style="color:#0a0;font-size:0.9em">${album.artist} • ${album.year || '?'}</div>
                        </div>
                    `).join('')}
                </div>
                ${albumResults.length > 10 ? `
                    <button class="show-more-btn" onclick="showMoreResults('albums')">
                        ▶ Ver todos (${albumResults.length})
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    // Tags
    if (tagResults.length > 0) {
        searchResultsCache.tags = tagResults; // Guardar en caché
        
        html += `
            <div class="search-category">
                <div class="search-category-title">
                    ▶ TAGS
                    <span class="search-category-count">(${tagResults.length})</span>
                </div>
                <div id="tags-results">
                    ${tagResults.slice(0, 10).map(tag => `
                        <div class="search-result-item" onclick="searchShowTag('${escapeHtml(tag)}')">
                            ${tag} <span style="color:#0a0">(${getTagCount(tag)} álbumes)</span>
                        </div>
                    `).join('')}
                </div>
                ${tagResults.length > 10 ? `
                    <button class="show-more-btn" onclick="showMoreResults('tags')">
                        ▶ Ver todos (${tagResults.length})
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    // Años
    if (yearResults.length > 0) {
        html += `
            <div class="search-category">
                <div class="search-category-title">
                    ▶ AÑOS
                    <span class="search-category-count">(${yearResults.length})</span>
                </div>
                ${yearResults.map(year => `
                    <div class="search-result-item" onclick="searchShowYear(${year})">
                        ${year} <span style="color:#0a0">(${getYearCount(year)} álbumes)</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Sin resultados
    if (html === '') {
        html = `<div class="search-no-results">◀ No se encontraron resultados para "${query}"</div>`;
    }
    
    searchResults.innerHTML = html;
});

// Botón random
document.getElementById('randomBtn').addEventListener('click', function() {
    const randomAlbum = DATA.albums[Math.floor(Math.random() * DATA.albums.length)];
    showAlbum(randomAlbum.id);
});

// Mostrar detalles de álbum
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
            <div class="tags-section">
                <div class="section-title">▶ TAGS</div>
                <div class="tag-cloud">
                    ${album.tags.map(tag =>
                        `<span class="tag" onclick="showTagAlbums('${escapeHtml(tag)}')">${tag}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    // Enlace a Bandcamp
    if (album.url) {
        html += `<a href="${album.url}" target="_blank" class="bandcamp-btn">▶ ABRIR EN BANDCAMP</a>`;
    }

    // Más del mismo artista
    const sameArtist = DATA.albums.filter(a => a.artist === album.artist && a.id !== album.id).slice(0, 6);
    if (sameArtist.length > 0) {
        html += `
            <div class="related-section">
                <div class="section-title">▶ MÁS DE ${album.artist}</div>
                <div class="related-grid">
                    ${sameArtist.map(a => `
                        <div class="related-album" onclick="showAlbum(${a.id})">
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
                    <div class="section-title">▶ ÁLBUMES SIMILARES</div>
                    <div class="related-grid">
                        ${sameTags.map(a => `
                            <div class="related-album" onclick="showAlbum(${a.id})">
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

function showArtistAlbums(artist) {
    const albums = DATA.albums.filter(a => a.artist === artist);
    const detail = document.getElementById('detailArea');
    
    // Calcular estadísticas del artista
    const years = albums.map(a => a.year).filter(y => y).sort((a, b) => a - b);
    const firstYear = years[0];
    const lastYear = years[years.length - 1];
    
    // Géneros únicos
    const genres = [...new Set(albums.map(a => a.genre))];
    
    // Tags más frecuentes
    const tagCount = {};
    albums.forEach(album => {
        album.tags.forEach(tag => {
            tagCount[tag] = (tagCount[tag] || 0) + 1;
        });
    });
    
    // Ordenar tags por frecuencia y tomar los top 10
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
            <div style="margin-top:30px">
                <div class="section-title">▶ GÉNEROS</div>
                <div class="tag-cloud">
                    ${genres.map(genre => 
                        `<span class="tag" onclick="searchShowGenre('${escapeHtml(genre)}')">${genre}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    // Tags más frecuentes
    if (topTags.length > 0) {
        html += `
            <div style="margin-top:30px">
                <div class="section-title">▶ TAGS MÁS FRECUENTES</div>
                <div class="tag-cloud">
                    ${topTags.map(([tag, count]) => 
                        `<span class="tag" onclick="searchShowTag('${escapeHtml(tag)}')">${tag} <span style="color:#0a0">(${count})</span></span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    // Álbumes ordenados por año
    const sortedAlbums = albums.sort((a, b) => (b.year || 0) - (a.year || 0));
    
    html += `
        <div style="margin-top:30px">
            <div class="section-title">▶ DISCOGRAFÍA</div>
            <div class="related-grid">
                ${sortedAlbums.map(a => `
                    <div class="related-album" onclick="showAlbum(${a.id})">
                        <div class="related-album-title">${a.title}</div>
                        <div class="related-album-artist">${a.year || '?'} • ${a.genre}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    detail.innerHTML = html;
}

// Mostrar álbumes de un tag
function showTagAlbums(tag) {
    const albums = DATA.albums.filter(a => a.tags.includes(tag));
    const detail = document.getElementById('detailArea');

    let html = `
        <div class="section-title">▶ TAG: ${tag}</div>
        <p style="color:#0a0;margin-bottom:30px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${albums.slice(0, 20).map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// Mostrar álbumes de un año
function showYearAlbums(year) {
    const albums = DATA.albums.filter(a => a.year === year);
    const detail = document.getElementById('detailArea');

    let html = `
        <div class="section-title">▶ AÑO: ${year}</div>
        <p style="color:#0a0;margin-bottom:30px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${albums.map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}

// Función helper para escapar HTML
function escapeHtml(text) {
    return text.replace(/'/g, "\\'");
}

// Funciones para búsqueda global
function searchShowArtist(artist) {
    document.getElementById('search').value = '';
    document.getElementById('searchResults').classList.remove('active');
    document.getElementById('searchResults').innerHTML = '';
    document.querySelector('.content-area').style.display = 'grid';
    
    // Cambiar a pestaña artistas
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="artistas"]').classList.add('active');
    currentTab = 'artistas';
    
    showArtistAlbums(artist);
}

function searchShowTag(tag) {
    document.getElementById('search').value = '';
    document.getElementById('searchResults').classList.remove('active');
    document.getElementById('searchResults').innerHTML = '';
    document.querySelector('.content-area').style.display = 'grid';
    
    // Cambiar a pestaña tags
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="tags"]').classList.add('active');
    currentTab = 'tags';
    
    showTagAlbums(tag);
}

function searchShowYear(year) {
    document.getElementById('search').value = '';
    document.getElementById('searchResults').classList.remove('active');
    document.getElementById('searchResults').innerHTML = '';
    document.querySelector('.content-area').style.display = 'grid';
    
    // Cambiar a pestaña años
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="years"]').classList.add('active');
    currentTab = 'years';
    
    showYearAlbums(year);
}

// Función para mostrar más resultados
function showMoreResults(type) {
    const container = document.getElementById(`${type}-results`);
    const items = searchResultsCache[type];
    
    if (!items) return;
    
    if (type === 'artists') {
        container.innerHTML = items.map(artist => `
            <div class="search-result-item" onclick="searchShowArtist('${escapeHtml(artist)}')">
                ${artist} <span style="color:#0a0">(${getArtistAlbumCount(artist)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'tags') {
        container.innerHTML = items.map(tag => `
            <div class="search-result-item" onclick="searchShowTag('${escapeHtml(tag)}')">
                ${tag} <span style="color:#0a0">(${getTagCount(tag)} álbumes)</span>
            </div>
        `).join('');
    } else if (type === 'albums') {
        container.innerHTML = items.map(album => `
            <div class="search-result-item" onclick="showAlbum(${album.id})">
                <div style="color:#0ff">${album.title}</div>
                <div style="color:#0a0;font-size:0.9em">${album.artist} • ${album.year || '?'}</div>
            </div>
        `).join('');
    }
    
    // Ocultar el botón
    window.event.target.style.display = 'none';
}

function searchShowGenre(genre) {
    const albums = DATA.albums.filter(a => a.genre === genre);
    const detail = document.getElementById('detailArea');

    let html = `
        <div class="section-title">▶ GÉNERO: ${genre}</div>
        <p style="color:#0a0;margin-bottom:30px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${albums.slice(0, 20).map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.artist}</div>
                </div>
            `).join('')}
        </div>
    `;

    detail.innerHTML = html;
}