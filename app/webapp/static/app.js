const tg = window.Telegram.WebApp;
tg.expand();

// State
let currentNetworkId = null;
let currentSeriesId = null;
const user = tg.initDataUnsafe.user || { id: 12345678 }; // Mock ID for dev if outside TG

// API Helper
async function fetchAPI(endpoint) {
    const res = await fetch(endpoint);
    return res.json();
}

// Navigation
function showSection(id) {
    ['loading', 'network-view', 'series-view', 'episode-view', 'player-view'].forEach(s => {
        document.getElementById(s).classList.add('hidden');
    });
    document.getElementById(id).classList.remove('hidden');
}

// Init
async function init() {
    showSection('loading');

    // In production, you might pass initData for auth
    // For now we use the ID from initDataUnsafe or mock
    const networks = await fetchAPI(`/api/networks/${user.id}`);

    const list = document.getElementById('network-list');
    list.innerHTML = '';

    if (!networks || networks.length === 0) {
        list.innerHTML = '<p class="text-gray-400">No networks found. Create one with /create_network.</p>';
        showSection('network-view');
        return;
    }

    networks.forEach(net => {
        const div = document.createElement('div');
        div.className = 'bg-gray-800 p-4 rounded-lg cursor-pointer hover:bg-gray-700 transition';
        div.innerHTML = `<h3 class="font-bold text-lg">${net.name}</h3><p class="text-sm text-gray-400">Owner ID: ${net.owner_id}</p>`;
        div.onclick = () => loadNetwork(net.id, net.name);
        list.appendChild(div);
    });

    showSection('network-view');
}

async function loadNetwork(id, name) {
    currentNetworkId = id;
    showSection('loading');

    const series = await fetchAPI(`/api/network/${id}/content`);
    document.getElementById('network-title').innerText = name;

    const list = document.getElementById('series-list');
    list.innerHTML = '';

    if (!series || series.length === 0) {
        list.innerHTML = '<p class="text-gray-400">No content yet.</p>';
    }

    series.forEach(s => {
        const div = document.createElement('div');
        div.className = 'bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition';
        const img = s.poster_path ? `https://image.tmdb.org/t/p/w200${s.poster_path}` : 'https://via.placeholder.com/200x300?text=No+Poster';
        div.innerHTML = `
            <img src="${img}" class="w-full h-auto object-cover">
            <div class="p-2">
                <h4 class="font-bold truncate">${s.title}</h4>
                <p class="text-xs text-gray-400">${s.first_air_date || ''}</p>
            </div>
        `;
        div.onclick = () => loadSeries(s._id, s.title); // Beanie uses _id in JSON sometimes, check output
        list.appendChild(div);
    });

    showSection('series-view');
}

async function loadSeries(id, title) {
    currentSeriesId = id;
    showSection('loading');

    const episodes = await fetchAPI(`/api/series/${id}/episodes`);
    document.getElementById('series-title').innerText = title;

    const list = document.getElementById('episode-list');
    list.innerHTML = '';

    episodes.forEach(ep => {
        const div = document.createElement('div');
        div.className = 'bg-gray-800 p-3 rounded flex justify-between items-center cursor-pointer hover:bg-gray-700';
        div.innerHTML = `
            <div>
                <span class="font-bold text-blue-400">S${ep.season_id} E${ep.episode_number}</span>
                <span class="ml-2">${ep.name || 'Episode ' + ep.episode_number}</span>
            </div>
            <button class="bg-blue-600 px-3 py-1 rounded text-sm">Play</button>
        `;
        div.onclick = () => playEpisode(ep.file_id, ep.name);
        list.appendChild(div);
    });

    showSection('episode-view');
}

function playEpisode(fileId, title) {
    showSection('player-view');
    document.getElementById('playing-title').innerText = title || 'Playing...';

    const player = document.getElementById('video-player');
    // Using the proxy stream endpoint
    player.src = `/stream/${fileId}`;
    player.play();
}

function showNetworks() {
    init();
}

function showSeries() {
    // Reload current network
    loadNetwork(currentNetworkId, document.getElementById('network-title').innerText);
}

function showEpisodes() {
    // Reload current series
    loadSeries(currentSeriesId, document.getElementById('series-title').innerText);
}

// Start
init();
