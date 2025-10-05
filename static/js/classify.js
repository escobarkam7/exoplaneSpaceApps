// Documentación toggle
document.addEventListener('DOMContentLoaded', function() {
    const docsToggle = document.getElementById('docsToggle');
    const docsContent = document.getElementById('docsContent');
    
    if (docsToggle && docsContent) {
        docsToggle.addEventListener('click', function() {
            const isVisible = docsContent.style.display === 'block';
            docsContent.style.display = isVisible ? 'none' : 'block';
            docsToggle.textContent = isVisible ? '▼ Mostrar Documentación' : '▲ Ocultar Documentación';
        });
    }
    
    // El resto de tu código existente...
    new ExoplanetClassifier();
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado - JavaScript funcionando');
    
    const menuIcon = document.querySelector('.menu-icon');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const closeBtn = document.getElementById('closeSidebar');

    // Función para abrir menú
    menuIcon.addEventListener('click', function() {
        console.log('Abriendo menú');
        sidebar.classList.add('active');
        overlay.classList.add('active');
    });

    // Función para cerrar menú
    function closeMenu() {
        console.log('Cerrando menú');
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }

    closeBtn.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);

    // Manejar enlaces del menú - SOLUCIÓN SIMPLE
    document.querySelectorAll('.sidebar-menu a').forEach(function(link) {
        link.addEventListener('click', function(e) {
            console.log('Clic en enlace:', this.getAttribute('href'));
            // Solo cerrar el menú, la navegación ocurre naturalmente
            closeMenu();
        });
    });

    // Cerrar menú con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
});

class ExoplanetClassifier {
    constructor() {
        this.API_URL = '/api';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const predictBtn = document.getElementById('predictBtn');

        // Upload area events
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));

        // File input change
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Predict button
        predictBtn.addEventListener('click', this.handlePrediction.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFileSelect(e) {
        if (e.target.files.length > 0) {
            this.handleFile(e.target.files[0]);
        }
    }

    handleFile(file) {
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            this.selectedFile = file;
            this.updateUploadArea(file.name);
            this.enablePredictButton();
            this.hideAlert();
        } else {
            this.showAlert('Por favor, selecciona un archivo CSV válido', 'error');
        }
    }

    updateUploadArea(fileName) {
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <h3>Archivo listo: ${fileName}</h3>
            <p>Haz clic en "Clasificar Exoplanetas" para procesar</p>
        `;
    }

    enablePredictButton() {
        const predictBtn = document.getElementById('predictBtn');
        predictBtn.disabled = false;
    }

    disablePredictButton() {
        const predictBtn = document.getElementById('predictBtn');
        predictBtn.disabled = true;
    }

    showLoading() {
        const loading = document.getElementById('loadingClassify');
        loading.style.display = 'block';
    }

    hideLoading() {
        const loading = document.getElementById('loadingClassify');
        loading.style.display = 'none';
    }

    async handlePrediction() {
        if (!this.selectedFile) {
            this.showAlert('Por favor, selecciona un archivo CSV primero', 'error');
            return;
        }

        this.showLoading();
        this.disablePredictButton();
        this.hideAlert();

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        try {
            const response = await fetch(`${this.API_URL}/classify`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error del servidor');
            }

            if (data.success) {
                this.displayResults(data);
                this.showAlert('Clasificación completada exitosamente', 'success');
            } else {
                throw new Error(data.message || 'Error en la predicción');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showAlert(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
            this.enablePredictButton();
        }
    }

    // NUEVA FUNCIÓN: Convertir probabilidades a 3 categorías
    getDispositionFromProbabilities(probExoplanet, probFalsePositive) {
        const planetPercent = probExoplanet * 100;
        
        // UMBRALES PARA 3 CATEGORÍAS
        if (planetPercent >= 80) {
            return "CONFIRMED";        // Alta probabilidad (>80%)
        } else if (planetPercent >= 50) {
            return "CANDIDATE";        // Probabilidad media (50-79%)
        } else {
            return "FALSE POSITIVE";   // Baja probabilidad (<50%)
        }
    }

    // NUEVA FUNCIÓN: Obtener clase CSS para cada categoría
    getDispositionClass(disposition) {
        switch(disposition) {
            case "CONFIRMED":
                return "confirmed-badge";
            case "CANDIDATE":
                return "candidate-badge";
            case "FALSE POSITIVE":
                return "false-positive-badge";
            default:
                return "candidate-badge";
        }
    }

    // NUEVA FUNCIÓN: Obtener descripción detallada
    getDispositionDescription(disposition, probExoplanet) {
        const percent = (probExoplanet * 100).toFixed(1);
        
        switch(disposition) {
            case "CONFIRMED":
                return `Alta confianza (${percent}%) - Muy probable exoplaneta real`;
            case "CANDIDATE":
                return `Señal prometedora (${percent}%) - Necesita más estudio`;
            case "FALSE POSITIVE":
                return `Baja probabilidad (${percent}%) - Posible artefacto o estrella binaria`;
            default:
                return "Clasificación en proceso";
        }
    }

    displayResults(data) {
        this.showResultsSection();
        this.displayStatistics(data.statistics, data.predictions);
        this.displayPredictions(data.predictions);
    }

    // FUNCIÓN MODIFICADA: Ahora usa las 3 categorías
    displayStatistics(stats, predictions) {
        const statsGrid = document.getElementById('statsGrid');
        
        // Calcular distribución de las 3 categorías
        let confirmedCount = 0;
        let candidateCount = 0;
        let falsePositiveCount = 0;
        
        predictions.forEach(pred => {
            const disposition = this.getDispositionFromProbabilities(
                pred.probability_exoplanet, 
                pred.probability_false_positive
            );
            
            if (disposition === "CONFIRMED") confirmedCount++;
            else if (disposition === "CANDIDATE") candidateCount++;
            else if (disposition === "FALSE POSITIVE") falsePositiveCount++;
        });
        
        const total = predictions.length;
        
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${total}</div>
                <div>Total Analizado</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${confirmedCount}</div>
                <div>Confirmados<br><small>${((confirmedCount/total)*100).toFixed(1)}%</small></div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${candidateCount}</div>
                <div>Candidatos<br><small>${((candidateCount/total)*100).toFixed(1)}%</small></div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${falsePositiveCount}</div>
                <div>Falsos Positivos<br><small>${((falsePositiveCount/total)*100).toFixed(1)}%</small></div>
            </div>
        `;
    }

    // FUNCIÓN COMPLETAMENTE MODIFICADA: Ahora muestra las 3 categorías
    displayPredictions(predictions) {
        const predictionsBody = document.getElementById('predictionsBody');
        predictionsBody.innerHTML = predictions.map(pred => {
            // Convertir probabilidades a categoría
            const disposition = this.getDispositionFromProbabilities(
                pred.probability_exoplanet, 
                pred.probability_false_positive
            );
            const dispositionClass = this.getDispositionClass(disposition);
            const dispositionDesc = this.getDispositionDescription(disposition, pred.probability_exoplanet);
            
            return `
            <tr>
                <td><strong>${pred.id}</strong></td>
                <td>
                    <span class="disposition-badge ${dispositionClass}" title="${dispositionDesc}">
                        ${disposition}
                    </span>
                    <div class="disposition-desc">${dispositionDesc}</div>
                </td>
                <td>
                    <strong>${(pred.confidence * 100).toFixed(1)}%</strong>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${pred.confidence * 100}%"></div>
                    </div>
                </td>
                <td>${(pred.probability_exoplanet * 100).toFixed(1)}%</td>
                <td>${(pred.probability_false_positive * 100).toFixed(1)}%</td>
            </tr>
            `;
        }).join('');
    }

    showResultsSection() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
    }

    hideAlert() {
        const alertContainer = document.getElementById('alertContainer');
        alertContainer.innerHTML = '';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ExoplanetClassifier();
    console.log('Clasificador de Exoplanetas inicializado - 3 Categorías');
});