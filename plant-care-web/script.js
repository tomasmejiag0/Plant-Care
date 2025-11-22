const API_BASE_URL = 'http://localhost:8000';

// State Management
let selectedImage = null;
let selectedImageBlob = null;
let selectedCategory = 'General';
let chatHistory = []; // Array de {role: 'user'|'assistant', content: string, image?: string}
let capabilities = {
    image_analysis_available: true,
    chat_available: true
};

// Category Tips Data (can be fetched from backend later)
const categoryTips = {
    'General': [
        {
            icon: 'fa-droplet',
            title: 'Riego Inteligente',
            description: 'La mayoría de plantas mueren por exceso de agua. Revisa siempre los primeros 2cm de tierra antes de regar.'
        },
        {
            icon: 'fa-sun',
            title: 'Luz Indirecta',
            description: 'El sol directo a través de ventanas puede quemar las hojas. Usa cortinas difusoras o mueve la planta.'
        },
        {
            icon: 'fa-scissors',
            title: 'Poda Regular',
            description: 'Retira hojas amarillas y muertas para redirigir energía al nuevo crecimiento.'
        },
        {
            icon: 'fa-thermometer-half',
            title: 'Temperatura',
            description: 'La mayoría de plantas de interior prefieren temperaturas entre 18-24°C.'
        }
    ],
    'Tropical': [
        {
            icon: 'fa-droplet',
            title: 'Alta Humedad',
            description: 'Las plantas tropicales necesitan humedad alta. Usa un humidificador o bandeja con agua.'
        },
        {
            icon: 'fa-sun',
            title: 'Luz Brillante Indirecta',
            description: 'Colócalas cerca de ventanas con luz filtrada, nunca bajo sol directo.'
        },
        {
            icon: 'fa-leaf',
            title: 'Riego Consistente',
            description: 'Mantén la tierra húmeda pero no empapada. Riega cuando la superficie esté seca.'
        },
        {
            icon: 'fa-wind',
            title: 'Buen Drenaje',
            description: 'Asegúrate de que la maceta tenga agujeros de drenaje para evitar raíces podridas.'
        }
    ],
    'Succulents': [
        {
            icon: 'fa-droplet',
            title: 'Riego Mínimo',
            description: 'Las suculentas almacenan agua. Riega solo cuando la tierra esté completamente seca.'
        },
        {
            icon: 'fa-sun',
            title: 'Luz Directa',
            description: 'Necesitan al menos 6 horas de luz solar directa al día para prosperar.'
        },
        {
            icon: 'fa-flask',
            title: 'Suelo Bien Drenado',
            description: 'Usa mezcla de tierra para cactus o agrega arena/perlita para mejor drenaje.'
        },
        {
            icon: 'fa-snowflake',
            title: 'Temperaturas Moderadas',
            description: 'Evita temperaturas bajo 10°C. La mayoría prefiere 15-25°C.'
        }
    ],
    'Bonsai': [
        {
            icon: 'fa-scissors',
            title: 'Poda Regular',
            description: 'Poda las ramas nuevas para mantener la forma deseada. Usa tijeras afiladas y limpias.'
        },
        {
            icon: 'fa-droplet',
            title: 'Riego Cuidadoso',
            description: 'Riega cuando la superficie del suelo esté seca. Evita el encharcamiento.'
        },
        {
            icon: 'fa-sun',
            title: 'Luz Adecuada',
            description: 'La mayoría necesita luz brillante indirecta. Algunas especies prefieren sol directo.'
        },
        {
            icon: 'fa-seedling',
            title: 'Trasplante Periódico',
            description: 'Trasplanta cada 2-3 años para renovar el suelo y podar raíces.'
        }
    ],
    'Pests': [
        {
            icon: 'fa-bug',
            title: 'Inspección Regular',
            description: 'Revisa las hojas semanalmente, especialmente el envés, para detectar plagas temprano.'
        },
        {
            icon: 'fa-spray-can',
            title: 'Tratamiento Natural',
            description: 'Usa agua jabonosa o aceite de neem. Aplica en las hojas afectadas cada 3-5 días.'
        },
        {
            icon: 'fa-wind',
            title: 'Buen Flujo de Aire',
            description: 'Mantén buena ventilación para prevenir plagas. Evita el hacinamiento de plantas.'
        },
        {
            icon: 'fa-ban',
            title: 'Aislamiento',
            description: 'Si detectas plagas, aísla la planta afectada inmediatamente para evitar propagación.'
        }
    ],
    'Indoor': [
        {
            icon: 'fa-lightbulb',
            title: 'Iluminación Artificial',
            description: 'Si no hay suficiente luz natural, usa luces LED de crecimiento durante 12-14 horas.'
        },
        {
            icon: 'fa-droplet',
            title: 'Riego Moderado',
            description: 'Las plantas de interior generalmente necesitan menos agua. Revisa la humedad del suelo.'
        },
        {
            icon: 'fa-wind',
            title: 'Ventilación',
            description: 'Abre ventanas regularmente para renovar el aire, pero evita corrientes fuertes.'
        },
        {
            icon: 'fa-broom',
            title: 'Limpieza de Hojas',
            description: 'Limpia las hojas con un paño húmedo para mejorar la absorción de luz.'
        }
    ],
    'Outdoor': [
        {
            icon: 'fa-cloud-sun',
            title: 'Aclimatación',
            description: 'Acostumbra gradualmente las plantas al exterior, empezando con sombra parcial.'
        },
        {
            icon: 'fa-thermometer-half',
            title: 'Protección del Clima',
            description: 'Protege de heladas, vientos fuertes y lluvias excesivas según la especie.'
        },
        {
            icon: 'fa-droplet',
            title: 'Riego Según Clima',
            description: 'Ajusta el riego según la estación y las condiciones climáticas locales.'
        },
        {
            icon: 'fa-seedling',
            title: 'Espaciado Adecuado',
            description: 'Deja espacio suficiente entre plantas para permitir crecimiento y circulación de aire.'
        }
    ]
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    console.log('PlantCare AI iniciado');
    console.log('Conectando a:', API_BASE_URL);
    
    // Setup image input
    const imageInput = document.getElementById('imageInput');
    imageInput.addEventListener('change', handleImageSelect);
    
    // Setup drag and drop
    setupDragAndDrop();
    
    // Verificar capacidades del sistema al cargar
    checkBackendConnection();
    
    // Setup message input (Enter to send, Shift+Enter for new line)
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Load default tips
    loadTips('General');
    
    // Check backend connection
    checkBackendConnection();
});

// Setup Drag and Drop
function setupDragAndDrop() {
    const uploadZone = document.getElementById('uploadZone');
    
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--primary-green)';
        uploadZone.style.background = 'rgba(34, 197, 94, 0.1)';
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = 'var(--glass-border)';
        uploadZone.style.background = 'var(--glass-bg)';
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--glass-border)';
        uploadZone.style.background = 'var(--glass-bg)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleImageFile(files[0]);
        }
    });
}

// Handle Image Selection
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleImageFile(file);
    }
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Por favor selecciona una imagen válida', 'warning');
        return;
    }
    
    selectedImageBlob = file;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        selectedImage = e.target.result;
        showImagePreview(selectedImage);
        // Don't add message here, wait for user to send
    };
    reader.readAsDataURL(file);
}

function showImagePreview(imageSrc) {
    const uploadZone = document.getElementById('uploadZone');
    const previewContainer = document.getElementById('imagePreviewContainer');
    const preview = document.getElementById('imagePreview');
    
    if (uploadZone) uploadZone.classList.add('hidden');
    if (preview) preview.src = imageSrc;
    if (previewContainer) previewContainer.classList.remove('hidden');
}

function removeImage() {
    selectedImage = null;
    selectedImageBlob = null;
    
    const uploadZone = document.getElementById('uploadZone');
    const previewContainer = document.getElementById('imagePreviewContainer');
    const imageInput = document.getElementById('imageInput');
    
    if (uploadZone) uploadZone.classList.remove('hidden');
    if (previewContainer) previewContainer.classList.add('hidden');
    if (imageInput) imageInput.value = '';
}

// Category Selection
function selectCategory(category) {
    selectedCategory = category;
    
    // Update UI
    document.querySelectorAll('.category-card').forEach(card => {
        card.classList.remove('active');
    });
    
    const selectedCard = document.querySelector(`[data-category="${category}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }
    
    // Update badge
    document.getElementById('selectedCategoryBadge').textContent = category;
    
    // Load tips
    loadTips(category);
    
    // Add message to chat
    addUserMessage(`Categoría seleccionada: ${category}`);
}

function loadTips(category) {
    const tipsContainer = document.getElementById('tipsContainer');
    const tips = categoryTips[category] || categoryTips['General'];
    
    tipsContainer.innerHTML = tips.map(tip => `
        <div class="tip-card">
            <div class="tip-header">
                <div class="tip-icon">
                    <i class="fa-solid ${tip.icon}"></i>
                </div>
                <div class="tip-title">${tip.title}</div>
            </div>
            <div class="tip-description">${tip.description}</div>
        </div>
    `).join('');
}

// Chat Functions
function addUserMessage(text, imageSrc = null) {
    // Add to history
    chatHistory.push({
        role: 'user',
        content: text,
        image: imageSrc || null
    });
    
    const chatContainer = document.getElementById('chatContainer');
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-user';
    
    let imageHtml = '';
    if (imageSrc) {
        imageHtml = `
            <div class="message-image-container">
                <img src="${imageSrc}" class="message-image-large" alt="Imagen de la planta">
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        ${imageHtml}
        <div class="message-bubble">${escapeHtml(text)}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollChatToBottom();
}

function addAssistantMessage(text, imageSrc = null) {
    // Add to history
    chatHistory.push({
        role: 'assistant',
        content: text,
        image: imageSrc || null
    });
    
    const chatContainer = document.getElementById('chatContainer');
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-assistant';
    
    let imageHtml = '';
    if (imageSrc) {
        imageHtml = `
            <div class="message-image-container">
                <img src="${imageSrc}" class="message-image-large" alt="Análisis de la planta">
            </div>
        `;
    }
    
    // Detectar si el texto ya contiene HTML (como de displayAnalysisResults)
    // Verificar si comienza con un tag HTML y contiene tags HTML válidos
    const trimmedText = text.trim();
    const isHtml = trimmedText.startsWith('<') && /<\s*(div|h[1-6]|p|ul|ol|li|strong|em|span|br|hr)[\s>]/i.test(trimmedText);
    
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    
    if (isHtml) {
        // Si ya es HTML, insertarlo directamente usando innerHTML
        messageBubble.innerHTML = text;
    } else {
        // Si es texto plano, procesarlo con formatMessage
        messageBubble.innerHTML = formatMessage(text);
    }
    
    // Construir el mensaje completo
    if (imageSrc) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'message-image-container';
        const img = document.createElement('img');
        img.src = imageSrc;
        img.className = 'message-image-large';
        img.alt = 'Análisis de la planta';
        imageContainer.appendChild(img);
        messageDiv.appendChild(imageContainer);
    }
    
    messageDiv.appendChild(messageBubble);
    chatContainer.appendChild(messageDiv);
    scrollChatToBottom();
}

function addLoadingMessage() {
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message message-assistant';
    loadingDiv.id = 'loadingMessage';
    loadingDiv.innerHTML = `
        <div class="message-bubble">
            <div class="loading-indicator">
                <span>Analizando...</span>
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(loadingDiv);
    scrollChatToBottom();
}

function removeLoadingMessage() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

function scrollChatToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Send Message
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message && !selectedImageBlob) {
        showToast('Por favor escribe un mensaje o sube una imagen', 'warning');
        return;
    }
    
    // Add user message with image if available
    if (selectedImageBlob && selectedImage) {
        const fullMessage = message || 'Analiza esta planta';
        addUserMessage(fullMessage, selectedImage);
        messageInput.value = '';
        await analyzePlant(fullMessage);  // Pasar el mensaje completo incluyendo la pregunta
    } else if (message) {
        addUserMessage(message);
        messageInput.value = '';
        await chatWithAgent(message);
    }
}

// Analyze Plant
async function analyzePlant(userContext = '') {
    if (!selectedImageBlob) {
        showToast('Por favor sube una imagen primero', 'warning');
        return;
    }
    
    // Verificar si el análisis de imágenes está disponible
    if (!capabilities.image_analysis_available) {
        showToast('El análisis de imágenes no está disponible en este momento. Por favor, usa el chat de texto.', 'warning');
        removeImage();
        return;
    }
    
    addLoadingMessage();
    
    try {
        const formData = new FormData();
        formData.append('image', selectedImageBlob);
        formData.append('user_actions', userContext || '');
        
        const response = await fetch(`${API_BASE_URL}/api/analyze-plant`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            // Manejar error 503 (servicio no disponible)
            if (response.status === 503) {
                const errorData = await response.json();
                throw new Error(errorData.detail?.message || 'El análisis de imágenes no está disponible');
            }
            throw new Error(`Error: ${response.status}`);
        }
        
        const result = await response.json();
        
        removeLoadingMessage();
        
        // Verificar si hay error de servicio no disponible
        if (response.status === 503 || result.detail?.error === 'image_analysis_unavailable') {
            const errorMsg = result.detail?.message || 'El análisis de imágenes no está disponible en este momento. Por favor, usa el chat de texto para hacer preguntas sobre cuidado de plantas.';
            addAssistantMessage(errorMsg);
            removeImage();
            showToast('Análisis de imágenes no disponible', 'warning');
            // Actualizar capacidades
            capabilities.image_analysis_available = false;
            updateUIForCapabilities();
            return;
        }
        
        if (result.success) {
            displayAnalysisResults(result);
        } else {
            throw new Error(result.error || 'Error en el análisis');
        }
        
    } catch (error) {
        const errorMessage = error.message || error.toString();
        
        // Manejar error 503 o servicio no disponible
        if (errorMessage.includes('no está disponible') || errorMessage.includes('503')) {
            addAssistantMessage('⚠️ El análisis de imágenes no está disponible en este momento. Por favor, usa el chat de texto para hacer preguntas sobre cuidado de plantas.');
            removeImage();
            showToast('Análisis de imágenes no disponible', 'warning');
            capabilities.image_analysis_available = false;
            updateUIForCapabilities();
            return;
        }
        console.error('Error:', error);
        removeLoadingMessage();
        addAssistantMessage('Lo siento, hubo un error al analizar la planta. Por favor verifica que el backend esté corriendo en http://localhost:8000');
        showToast('Error al conectar con el backend', 'danger');
    }
}

// Display Analysis Results
function displayAnalysisResults(data) {
    const plantInfo = data.plant_info || {};
    const healthAssessment = data.health_assessment || {};
    const diagnosis = data.diagnosis || {};
    const recommendations = data.recommendations || [];
    
    // Build response message with better formatting
    let responseText = `<div style="line-height: 1.7;"><h4 style="margin: 1rem 0 0.75rem 0; color: var(--primary-green); font-size: 1.1rem;">🌿 Análisis de tu Planta</h4>`;
    
    // Plant Identification
    if (plantInfo.species) {
        responseText += `<p style="margin: 0.5rem 0;"><strong>Especie identificada:</strong> <span style="color: var(--accent-green);">${escapeHtml(plantInfo.species)}</span></p>`;
        if (plantInfo.common_names && plantInfo.common_names.length > 0) {
            responseText += `<p style="margin: 0.5rem 0;"><strong>Nombres comunes:</strong> ${escapeHtml(plantInfo.common_names.join(', '))}</p>`;
        }
        if (plantInfo.confidence) {
            const confidence = Math.round(plantInfo.confidence * 100);
            const confidenceColor = confidence >= 70 ? 'var(--success)' : confidence >= 40 ? 'var(--warning)' : 'var(--text-muted)';
            responseText += `<p style="margin: 0.5rem 0;"><strong>Confianza:</strong> <span style="color: ${confidenceColor};">${confidence}%</span></p>`;
        }
    }
    
    // Health Assessment
    if (healthAssessment.score !== undefined) {
        const score = healthAssessment.score;
        const emoji = getHealthEmoji(score);
        const status = healthAssessment.status || '';
        const healthColor = score >= 8 ? 'var(--success)' : score >= 6 ? 'var(--accent-green)' : score >= 4 ? 'var(--warning)' : 'var(--danger)';
        responseText += `<p style="margin: 0.5rem 0;"><strong>Estado de salud:</strong> <span style="color: ${healthColor};">${emoji} ${score}/10 - ${escapeHtml(status)}</span></p>`;
    }
    
    // Diagnosis
    if (diagnosis.summary) {
        responseText += `<h4 style="margin: 1rem 0 0.75rem 0; color: var(--info); font-size: 1rem;">🔍 Diagnóstico</h4><p style="margin: 0.5rem 0; line-height: 1.6;">${escapeHtml(diagnosis.summary)}</p>`;
    }
    
    if (diagnosis.visual_problems && diagnosis.visual_problems.length > 0) {
        responseText += `<h4 style="margin: 1rem 0 0.75rem 0; color: var(--warning); font-size: 1rem;">⚠️ Problemas detectados</h4><ul style="margin: 0.5rem 0; padding-left: 1.5rem; list-style-type: disc;">`;
        diagnosis.visual_problems.forEach(problem => {
            responseText += `<li style="margin: 0.5rem 0; line-height: 1.6;">${escapeHtml(problem)}</li>`;
        });
        responseText += `</ul>`;
    }
    
    // Recommendations
    if (recommendations.length > 0) {
        responseText += `<h4 style="margin: 1rem 0 0.75rem 0; color: var(--primary-green); font-size: 1rem;">💡 Recomendaciones</h4><ol style="margin: 0.5rem 0; padding-left: 1.5rem; list-style-type: decimal;">`;
        recommendations.forEach((rec) => {
            responseText += `<li style="margin: 0.75rem 0; line-height: 1.7;">${escapeHtml(rec)}</li>`;
        });
        responseText += `</ol>`;
    }
    
    responseText += `</div>`;
    
    // Pasar el HTML directamente sin procesar
    addAssistantMessage(responseText, selectedImage);
    
    // Show success toast
    showToast('Análisis completado exitosamente', 'success');
}

// Helper Functions
function getHealthEmoji(score) {
    if (score >= 8) return '😃';
    if (score >= 6) return '🙂';
    if (score >= 4) return '😐';
    return '😞';
}

function formatMessage(text) {
    // Limpieza agresiva de markdown y texto truncado
    let cleaned = text;
    
    // Eliminar TODOS los headers de markdown (# ## ### #### ##### ######)
    cleaned = cleaned.replace(/^#{1,6}\s+/gm, '');
    cleaned = cleaned.replace(/#{1,6}\s+/g, ''); // También en medio de líneas
    
    // Eliminar puntos suspensivos (indicadores de truncado)
    cleaned = cleaned.replace(/\.\.\.+/g, '');
    cleaned = cleaned.replace(/\.\.\.\s*$/gm, '');
    
    // Eliminar frases genéricas comunes
    const phrases = [
        /Basándome en la información disponible[:\s]*/gi,
        /Según los documentos[:\s]*/gi,
        /Según la información[:\s]*/gi,
        /De acuerdo a[:\s]*/gi,
        /Basándome en[:\s]*/gi,
        /De acuerdo con[:\s]*/gi,
        /Con base en[:\s]*/gi
    ];
    phrases.forEach(phrase => {
        cleaned = cleaned.replace(phrase, '');
    });
    
    // Eliminar líneas que son solo números o viñetas sin contenido real
    let lines = cleaned.split('\n');
    cleaned = lines.filter(line => {
        const stripped = line.trim();
        // Mantener líneas con contenido real (más de 3 caracteres y no solo números/viñetas)
        return stripped && !/^[\d\.\-\•\*]+$/.test(stripped) && stripped.length > 3;
    }).join('\n');
    
    // Split into lines for processing
    lines = cleaned.split('\n');
    let result = [];
    let inList = false;
    let listItems = [];
    let currentParagraph = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        
        if (!line) {
            // Empty line - close list if open, flush paragraph
            if (inList && listItems.length > 0) {
                result.push(`<ul style="margin: 0.75rem 0; padding-left: 1.5rem; list-style-type: disc;">${listItems.join('')}</ul>`);
                listItems = [];
                inList = false;
            }
            if (currentParagraph.length > 0) {
                const paraText = currentParagraph.join(' ');
                let processedText = escapeHtml(paraText);
                processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
                processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
                result.push(`<p style="margin: 0.75rem 0; line-height: 1.7;">${processedText}</p>`);
                currentParagraph = [];
            }
            continue;
        }
        
        // Check for list items
        if (line.match(/^[-•*]\s+/) || line.match(/^\d+\.\s+/)) {
            // Flush current paragraph if exists
            if (currentParagraph.length > 0) {
                const paraText = currentParagraph.join(' ');
                let processedText = escapeHtml(paraText);
                processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
                processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
                result.push(`<p style="margin: 0.75rem 0; line-height: 1.7;">${processedText}</p>`);
                currentParagraph = [];
            }
            
            if (!inList) {
                inList = true;
                listItems = [];
            }
            const itemText = line.replace(/^[-•*]\s+/, '').replace(/^\d+\.\s+/, '');
            // Process bold and italic in list items
            let processedText = escapeHtml(itemText);
            processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
            processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
            listItems.push(`<li style="margin-bottom: 0.5rem; line-height: 1.6;">${processedText}</li>`);
            continue;
        }
        
        // Regular text - add to current paragraph
        if (inList && listItems.length > 0) {
            result.push(`<ul style="margin: 0.75rem 0; padding-left: 1.5rem; list-style-type: disc;">${listItems.join('')}</ul>`);
            listItems = [];
            inList = false;
        }
        
        currentParagraph.push(line);
    }
    
    // Flush remaining paragraph
    if (currentParagraph.length > 0) {
        const paraText = currentParagraph.join(' ');
        let processedText = escapeHtml(paraText);
        processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
        processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        result.push(`<p style="margin: 0.75rem 0; line-height: 1.7;">${processedText}</p>`);
    }
    
    // Close any remaining list
    if (inList && listItems.length > 0) {
        result.push(`<ul style="margin: 0.75rem 0; padding-left: 1.5rem; list-style-type: disc;">${listItems.join('')}</ul>`);
    }
    
    return result.join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toast Notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');
    
    toastMsg.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}

// Chat with Agent (Text-based RAG)
async function chatWithAgent(message) {
    addLoadingMessage();
    
    try {
        // Prepare chat history for context (last 10 messages)
        const recentHistory = chatHistory.slice(-10).map(msg => ({
            role: msg.role,
            content: msg.content
        }));
        
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: recentHistory
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        
        const result = await response.json();
        removeLoadingMessage();
        
        if (result.success) {
            addAssistantMessage(result.response);
        } else {
            throw new Error(result.error || 'Error en la respuesta');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage();
        
        // Verificar si es error de quota o servicio no disponible
        const errorMessage = error.message || error.toString();
        if (errorMessage.includes('quota') || errorMessage.includes('exceeded') || errorMessage.includes('429')) {
            addAssistantMessage('⚠️ Se ha agotado la cuota del servicio de IA. El sistema ahora funciona usando solo la base de conocimiento. Puedes seguir haciendo preguntas sobre cuidado de plantas y recibirás respuestas basadas en los documentos disponibles.');
            // Actualizar capacidades
            capabilities.gemini_llm_available = false;
        } else if (error.message.includes('404') || error.message.includes('Error: 404')) {
            addAssistantMessage('El endpoint de chat aún no está disponible en el backend. Por favor sube una imagen de tu planta para analizarla, o contacta al administrador para habilitar el chat con RAG.');
        } else {
            addAssistantMessage('Lo siento, hubo un error al procesar tu pregunta. El sistema intentará usar solo la base de conocimiento. Por favor verifica que el backend esté corriendo en http://localhost:8000');
        }
        showToast('Error al conectar con el backend', 'danger');
    }
}

// Check Backend Connection
function updateUIForCapabilities() {
    const imageUploadSection = document.getElementById('imageUploadSection');
    const uploadZone = document.getElementById('uploadZone');
    const imageUploadWarning = document.getElementById('imageUploadWarning');
    
    if (!capabilities.image_analysis_available) {
        if (uploadZone) {
            uploadZone.style.opacity = '0.5';
            uploadZone.style.pointerEvents = 'none';
        }
        if (imageUploadSection && !imageUploadWarning) {
            const warning = document.createElement('div');
            warning.id = 'imageUploadWarning';
            warning.className = 'upload-warning';
            warning.style.cssText = 'padding: 0.5rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem;';
            warning.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Análisis de imágenes no disponible';
            imageUploadSection.appendChild(warning);
        }
    } else {
        if (uploadZone) {
            uploadZone.style.opacity = '1';
            uploadZone.style.pointerEvents = 'auto';
        }
        if (imageUploadWarning) {
            imageUploadWarning.remove();
        }
    }
}

async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        
        // Verificar capacidades del sistema
        try {
            const capabilitiesResponse = await fetch(`${API_BASE_URL}/api/capabilities`);
            if (capabilitiesResponse.ok) {
                capabilities = await capabilitiesResponse.json();
                updateUIForCapabilities();
            }
        } catch (e) {
            console.warn('No se pudieron verificar capacidades:', e);
        }
        if (response.ok) {
            console.log('✅ Backend conectado');
        }
    } catch (error) {
        console.warn('⚠️ Backend no disponible:', error);
    }
}
