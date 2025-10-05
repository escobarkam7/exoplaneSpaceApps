const API_BASE = 'http://127.0.0.1:8000';  // FastAPI usa el mismo puerto

async function loadPlanets() {
    const datasetSelect = document.getElementById('datasetSelect');
    const limitInput = document.getElementById('limitInput');
    const selectedDataset = datasetSelect.value;
    const limit = parseInt(limitInput.value) || 50;
    
    if (!selectedDataset) {
        showError('Por favor selecciona un dataset');
        return;
    }

    showLoading();
    hideError();

    try {
        // Asumiendo que tu endpoint API es /planets/{dataset}
        const response = await fetch(`${API_BASE}/planets/${selectedDataset}?limit=${limit}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }

        displayPlanets(result.data, selectedDataset, result.total);
        
    } catch (error) {
        showError('Error cargando datos: ' + error.message);
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// El resto de tu código permanece igual...

function displayPlanets(planets, dataset, total) {
    const container = document.getElementById('planetsContainer');
    const stats = document.getElementById('stats');
    
    stats.textContent = `${total} exoplanetas encontrados`;
    
    if (planets.length === 0) {
        container.innerHTML = '<div class="planet-card"><p>No se encontraron exoplanetas</p></div>';
        return;
    }

    container.innerHTML = planets.map(planet => `
        <div class="planet-card">
            <h3>${getPlanetName(planet, dataset)}</h3>
            ${renderPlanetDetails(planet, dataset)}
        </div>
    `).join('');
}

function getPlanetName(planet, dataset) {
    switch(dataset) {
        case 'kepler': return planet.kepler_name || planet.kepoi_name || `KEPLER-${planet.kepid}`;
        case 'k2planets': return planet.pl_name || 'K2 Exoplanet';
        case 'tess': return planet.toi ? `TOI-${planet.toi}` : 'TESS Exoplanet';
        default: return 'Exoplanet';
    }
}

function renderPlanetDetails(planet, dataset) {
    const details = [];
    
    // Estado/disposición
    if (planet.koi_disposition || planet.disposition || planet.tfopwg_disp) {
        details.push(`<p><strong>Estado:</strong> ${planet.koi_disposition || planet.disposition || planet.tfopwg_disp}</p>`);
    }
    
    // Periodo orbital
    if (planet.koi_period || planet.pl_orber || planet.pl_orbper) {
        details.push(`<p><strong>Periodo orbital:</strong> ${planet.koi_period || planet.k2_period || planet.pl_orbper} días</p>`);
    }
    
    // Radio planetario
    if (planet.koi_prad || planet.k2_prad || planet.pl_rade) {
        details.push(`<p><strong>Radio planetario:</strong> ${planet.koi_prad || planet.k2_prad || planet.pl_rade} radios terrestres</p>`);
    }
    
    // Temperatura
    if (planet.koi_teq || planet.pl_eqt || planet.pl_eqt) {
        details.push(`<p><strong>Temperatura equilibrio:</strong> ${planet.koi_teq || planet.k2_teq || planet.pl_eqt} K</p>`);
    }
    
    // Temperatura estelar
    if (planet.koi_steff || planet.st_steff || planet.st_teff) {
        details.push(`<p><strong>Temperatura estelar:</strong> ${planet.koi_steff || planet.k2_steff || planet.st_teff} K</p>`);
    }
    
    // ID adicional
    if (planet.kepid || planet.tid || planet.hostname) {
        details.push(`<p><strong>ID:</strong> ${planet.kepid || planet.tid || planet.hostname}</p>`);
    }
    
    return details.join('');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('planetsContainer').innerHTML = '';
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}

// Cargar datos cuando se cambie el select
document.getElementById('datasetSelect').addEventListener('change', loadPlanets);