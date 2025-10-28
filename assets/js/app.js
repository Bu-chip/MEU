// Variables globales
let DATA = null;
let currentTab = 'artistas';
let filteredItems = [];

// Inicialización del cargador de archivos
document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            DATA = JSON.parse(event.target.result);
            init();
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };
    reader.readAsText(file);
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
        filteredItems = [...DATA.years].reverse();
        renderList(filteredItems, (item) => `${item} (${getYearCount(item)})`);
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

// Búsqueda
document.getElementById('search').addEventListener('input', function(e) {
    const q = e.target.value.toLowerCase();

    if (currentTab === 'artistas') {
        filteredItems = DATA.artists.filter(a => a.toLowerCase().includes(q));
        renderList(filteredItems, (item) => `${item} (${getArtistAlbumCount(item)})`);
    } else if (currentTab === 'tags') {
        filteredItems = DATA.tags.filter(t => t.toLowerCase().includes(q));
        renderList(filteredItems, (item) => `${item} (${getTagCount(item)})`);
    } else if (currentTab === 'albums') {
        filteredItems = DATA.albums.filter(a =>
            a.title.toLowerCase().includes(q) || a.artist.toLowerCase().includes(q)
        );
        const sidebar = document.getElementById('sidebar');
        sidebar.innerHTML = filteredItems.map(album =>
            `<div class="list-item" onclick="showAlbum(${album.id})">${album.artist} - ${album.title}</div>`
        ).join('');
    } else if (currentTab === 'years') {
        filteredItems = DATA.years.filter(y => y.toString().includes(q));
        renderList(filteredItems, (item) => `${item} (${getYearCount(item)})`);
    }
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

// Mostrar álbumes de un artista
function showArtistAlbums(artist) {
    const albums = DATA.albums.filter(a => a.artist === artist);
    const detail = document.getElementById('detailArea');

    let html = `
        <div class="section-title">▶ ${artist}</div>
        <p style="color:#0a0;margin-bottom:30px">${albums.length} álbumes</p>
        <div class="related-grid">
            ${albums.map(a => `
                <div class="related-album" onclick="showAlbum(${a.id})">
                    <div class="related-album-title">${a.title}</div>
                    <div class="related-album-artist">${a.year || '?'} • ${a.genre}</div>
                </div>
            `).join('')}
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
