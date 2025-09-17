class BrewStats {
    constructor() {
        this.allPlayers = [];
        this.filteredPlayers = [];
        this.init();
    }

    async init() {
        await this.loadPlayers();
        this.renderPlayers();
        this.setupSearch();
        document.getElementById('loading').style.display = 'none';
    }

    async loadPlayers() {
        try {
            // Try to load real data first
            const response = await fetch('data/players.json');
            if (response.ok) {
                this.allPlayers = await response.json();
            } else {
                // Fallback sample data
                this.allPlayers = this.getSamplePlayers();
            }
            this.filteredPlayers = [...this.allPlayers];
        } catch (error) {
            console.error('Error loading players:', error);
            this.allPlayers = this.getSamplePlayers();
            this.filteredPlayers = [...this.allPlayers];
        }
    }

    getSamplePlayers() {
        return [
            {
                id: 'jackson-chourio',
                name: 'Jackson Chourio',
                position: 'OF',
                age: 20,
                level: 'Milwaukee Brewers',
                currentStats: { avg: '.267', hr: 18, rbi: 65, ops: '.847' }
            },
            {
                id: 'tyler-black',
                name: 'Tyler Black',
                position: 'SS',
                age: 24,
                level: 'Nashville Sounds',
                currentStats: { avg: '.285', hr: 16, rbi: 71, ops: '.823' }
            },
            {
                id: 'brock-wilken',
                name: 'Brock Wilken',
                position: '3B',
                age: 22,
                level: 'Biloxi Shuckers',
                currentStats: { avg: '.289', hr: 24, rbi: 78, ops: '.891' }
            },
            {
                id: 'carlos-rodriguez',
                name: 'Carlos Rodriguez',
                position: 'SS',
                age: 19,
                level: 'Wisconsin Timber Rattlers',
                currentStats: { avg: '.245', hr: 8, rbi: 42, ops: '.734' }
            },
            {
                id: 'jeferson-quero',
                name: 'Jeferson Quero',
                position: 'C',
                age: 21,
                level: 'Biloxi Shuckers',
                currentStats: { avg: '.272', hr: 13, rbi: 57, ops: '.798' }
            },
            {
                id: 'cooper-pratt',
                name: 'Cooper Pratt',
                position: '2B',
                age: 23,
                level: 'Nashville Sounds',
                currentStats: { avg: '.268', hr: 11, rbi: 52, ops: '.789' }
            },
            {
                id: 'eduarqui-fernandez',
                name: 'Eduarqui Fernandez',
                position: 'OF',
                age: 18,
                level: 'Carolina Mudcats',
                currentStats: { avg: '.241', hr: 5, rbi: 34, ops: '.712' }
            },
            {
                id: 'garrett-mitchell',
                name: 'Garrett Mitchell',
                position: 'CF',
                age: 26,
                level: 'Milwaukee Brewers',
                currentStats: { avg: '.255', hr: 12, rbi: 45, ops: '.795' }
            }
        ];
    }

    renderPlayers() {
        const container = document.getElementById('players-list');
        
        if (this.filteredPlayers.length === 0) {
            container.innerHTML = '<p>No players found</p>';
            return;
        }

        const html = this.filteredPlayers.map(player => `
            <div class="player-card" onclick="viewPlayer('${player.id}')">
                <div class="player-name">${player.name}</div>
                <div class="player-details">
                    <span class="position-tag">${player.position}</span>
                    <span class="age-tag">Age ${player.age}</span>
                </div>
                <div class="level-tag">${player.level}</div>
                <div class="quick-stats">
                    <span>AVG: ${player.currentStats.avg}</span>
                    <span>HR: ${player.currentStats.hr}</span>
                    <span>RBI: ${player.currentStats.rbi}</span>
                    <span>OPS: ${player.currentStats.ops}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    setupSearch() {
        const searchInput = document.getElementById('player-search');
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            if (query === '') {
                this.filteredPlayers = [...this.allPlayers];
            } else {
                this.filteredPlayers = this.allPlayers.filter(player =>
                    player.name.toLowerCase().includes(query) ||
                    player.position.toLowerCase().includes(query) ||
                    player.level.toLowerCase().includes(query)
                );
            }
            
            this.renderPlayers();
        });
    }
}

function viewPlayer(playerId) {
    window.location.href = `player.html?id=${playerId}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new BrewStats();
});
