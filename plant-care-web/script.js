const API_BASE_URL = 'http://localhost:8000';

let selectedImage = null;
let selectedImageBlob = null;

// Handle image selection
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Store the file
    selectedImageBlob = file;

    // Create preview
    const reader = new FileReader();
    reader.onload = function (e) {
        selectedImage = e.target.result;
        showAnalysisSection();
    };
    reader.readAsDataURL(file);
}

// Show analysis section
function showAnalysisSection() {
    document.getElementById('home-section').classList.remove('active');
    document.getElementById('analysis-section').classList.add('active');
    document.getElementById('preview-image').src = selectedImage;
    document.getElementById('input-section').classList.remove('hidden');
    document.getElementById('loading-section').classList.add('hidden');
    document.getElementById('results-section').classList.add('hidden');
}

// Go back to home
function goBack() {
    document.getElementById('analysis-section').classList.remove('active');
    document.getElementById('home-section').classList.add('active');
    document.getElementById('user-actions').value = '';
    selectedImage = null;
    selectedImageBlob = null;
}

// Analyze plant
async function analyzePlant() {
    const userActions = document.getElementById('user-actions').value.trim();

    if (!userActions) {
        alert('Por favor describe qué has hecho con tu planta');
        return;
    }

    if (!selectedImageBlob) {
        alert('Por favor selecciona una imagen primero');
        return;
    }

    // Show loading
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('loading-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('image', selectedImageBlob);
        formData.append('user_actions', userActions);

        // Make API call
        const response = await fetch(`${API_BASE_URL}/api/analyze-plant`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const result = await response.json();

        // Debug: ver qué llegó del backend
        console.log('Respuesta del backend:', result);

        if (result.success) {
            displayResults(result);
        } else {
            throw new Error(result.error || 'Error en el análisis');
        }

    } catch (error) {
        console.error('Error completo:', error);
        console.error('Stack trace:', error.stack);
        alert('Error al analizar la planta. Verifica que el backend esté corriendo en http://localhost:8000');
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('input-section').classList.remove('hidden');
    }
}

// Display results
function displayResults(data) {
    // Hide loading
    document.getElementById('loading-section').classList.add('hidden');

    // Species
    document.getElementById('species-name').textContent = data.plant_info.species;

    const commonNames = data.plant_info.common_names.length > 0
        ? data.plant_info.common_names.join(', ')
        : '';
    document.getElementById('common-names').textContent = commonNames;

    const confidence = Math.round(data.plant_info.confidence * 100);
    document.getElementById('confidence').textContent = `Confianza: ${confidence}%`;

    // Health
    const score = data.health_assessment.score;
    const healthColor = getHealthColor(score);
    const healthEmoji = getHealthEmoji(score);

    document.getElementById('health-score-container').innerHTML = `
        <span class="health-emoji">${healthEmoji}</span>
        <span style="color: ${healthColor}; font-weight: 700;">${score}/10</span>
    `;
    document.getElementById('health-status').textContent = data.health_assessment.status;

    // Diagnosis
    document.getElementById('diagnosis-summary').textContent = data.diagnosis.summary;

    // Visual problems
    const problemsList = document.getElementById('problems-list');
    if (data.diagnosis.visual_problems.length > 0) {
        problemsList.innerHTML = `
            <div class="problems-list">
                <h4 style="color: var(--text-dark); margin-bottom: 1rem;">Problemas detectados:</h4>
                ${data.diagnosis.visual_problems.map(problem => `
                    <div class="problem-item">${problem}</div>
                `).join('')}
            </div>
        `;
    } else {
        problemsList.innerHTML = '';
    }

    // Recommendations
    const recsList = document.getElementById('recommendations-list');
    recsList.innerHTML = data.recommendations.map((rec, index) => `
        <div class="recommendation-item">
            <div class="rec-number">${index + 1}</div>
            <div class="rec-text">${rec}</div>
        </div>
    `).join('');

    // Show results
    document.getElementById('results-section').classList.remove('hidden');

    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Helper functions
function getHealthColor(score) {
    if (score >= 8) return '#4caf50';
    if (score >= 6) return '#8bc34a';
    if (score >= 4) return '#ff9800';
    return '#f44336';
}

function getHealthEmoji(score) {
    if (score >= 8) return '😃';
    if (score >= 6) return '🙂';
    if (score >= 4) return '😐';
    return '😞';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('PlantCare AI Web iniciado');
    console.log('Conectando a:', API_BASE_URL);
});
