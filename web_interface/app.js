// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let chatOpen = false;
let quranMode = false; // تسميع mode - when true, use Quran STT
let chatHistory = []; // Store conversation history

// DOM Elements
const voiceVisualizer = document.getElementById('voiceVisualizer');
const voiceStatus = document.getElementById('voiceStatus');
const outputBox = document.getElementById('outputBox');
const outputContent = document.getElementById('outputContent');
const chatButton = document.getElementById('chatButton');
const chatPanel = document.getElementById('chatPanel');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const chatMessages = document.getElementById('chatMessages');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkServiceHealth();
    setupEventListeners();
    setupVoiceVisualizer();
    verifyBackgroundGif();
    updateQuranModeButton();
});

// Verify background GIF is loading
function verifyBackgroundGif() {
    const img = new Image();
    img.onload = function() {
        console.log('✅ Background GIF loaded successfully');
    };
    img.onerror = function() {
        console.error('❌ Background GIF failed to load');
        console.error('Tried to load: /assets/background.gif');
    };
    // Background GIF verification removed - using CSS gradient background
}

// Toggle Quran Mode (تسميع)
function toggleQuranMode() {
    quranMode = !quranMode;
    updateQuranModeButton();
    
    // Show feedback
    const modeText = quranMode ? 'وضع التسميع مفعّل' : 'وضع التسميع معطّل';
    showOutput('وضع التسميع', modeText, 'info');
}

// Update Quran Mode Button Visual State
function updateQuranModeButton() {
    const button = document.getElementById('quranModeButton');
    if (button) {
        if (quranMode) {
            button.classList.add('active');
            button.title = 'إيقاف وضع التسميع (استخدام STT العادي)';
        } else {
            button.classList.remove('active');
            button.title = 'تفعيل وضع التسميع (استخدام Quran STT)';
        }
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Voice visualizer click
    voiceVisualizer.addEventListener('click', handleVoiceClick);
    
    // Chat input enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

// Setup Voice Visualizer - Generate 288 dots in sphere pattern
function setupVoiceVisualizer() {
    voiceVisualizer.classList.add('active');
    generateSphereDots();
}

// Generate 288 dots arranged in a sphere with three colors
function generateSphereDots() {
    const dotsContainer = document.getElementById('visualizerDots');
    if (!dotsContainer) return;
    
    dotsContainer.innerHTML = ''; // Clear existing dots
    
    const totalDots = 288;
    const radius = 60; // Distance from center (in pixels) - closer together
    
    // Three colors: Blue, White, and Cyan (mixed randomly)
    const colors = [
        '#4A90E2',  // Bright Blue
        '#FFFFFF',  // Pure White
        '#00D4FF'   // Cyan
    ];
    
    // Generate dots using spherical coordinates
    for (let i = 0; i < totalDots; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot sphere-dot';
        
        // Spherical coordinates for even distribution
        // Use golden angle spiral for better distribution
        const goldenAngle = Math.PI * (3 - Math.sqrt(5));
        const theta = i * goldenAngle;
        const y = 1 - (i / (totalDots - 1)) * 2; // -1 to 1
        const radiusAtY = Math.sqrt(1 - y * y);
        const x = Math.cos(theta) * radiusAtY;
        const z = Math.sin(theta) * radiusAtY;
        
        // Convert 3D coordinates to 2D screen position
        const screenX = x * radius;
        const screenY = y * radius;
        const screenZ = z * radius; // For depth effect
        
        // Position dot
        dot.style.left = `calc(50% + ${screenX}px)`;
        dot.style.top = `calc(50% + ${screenY}px)`;
        dot.style.transform = `translate(-50%, -50%) translateZ(${screenZ}px)`;
        
        // Randomly assign color (mixed distribution)
        const colorIndex = Math.floor(Math.random() * colors.length);
        const selectedColor = colors[colorIndex];
        
        dot.style.background = selectedColor;
        dot.dataset.colorIndex = colorIndex;
        
        // Animation delay based on position
        const delay = (i % 20) * 0.1;
        dot.style.animationDelay = `${delay}s`;
        
        dotsContainer.appendChild(dot);
    }
}

// Handle Voice Visualizer Click
async function handleVoiceClick() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

// Start Recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await transcribeAndValidate(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        voiceVisualizer.classList.remove('active');
        voiceVisualizer.classList.add('recording');
        voiceStatus.textContent = 'جاري التسجيل...';
        
    } catch (error) {
        console.error('Error starting recording:', error);
        showOutput('خطأ', 'لا يمكن الوصول إلى الميكروفون. يرجى التحقق من الصلاحيات.', 'error');
        resetVisualizer();
    }
}

// Stop Recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        voiceVisualizer.classList.remove('recording');
        voiceVisualizer.classList.add('processing');
        voiceStatus.textContent = 'جاري المعالجة...';
    }
}

// Reset Visualizer
function resetVisualizer() {
    voiceVisualizer.classList.remove('recording', 'processing');
    voiceVisualizer.classList.add('active');
    voiceStatus.textContent = 'اضغط للتحدث';
    isRecording = false;
}

// Transcribe and Validate
async function transcribeAndValidate(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');
        // Add mode parameter: 'quran' for تسميع mode, 'normal' for default
        formData.append('mode', quranMode ? 'quran' : 'normal');

        const response = await fetch(`${API_BASE_URL}/voice_query`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        // Add to chat history if it's a recitation validation
        if (data.intent === 'recitation_validation' || quranMode) {
            chatHistory.push({
                role: 'user',
                content: data.transcript || ''
            });
            chatHistory.push({
                role: 'assistant',
                content: data.response || ''
            });
        }
        
        displayResult(data);
        resetVisualizer();
        
    } catch (error) {
        console.error('Transcription error:', error);
        showOutput('خطأ', 'حدث خطأ أثناء معالجة الصوت. يرجى المحاولة مرة أخرى.', 'error');
        resetVisualizer();
    }
}

// Display Result
function displayResult(data) {
    // Handle mode switch
    if (data.intent === 'mode_switch' || data.mode_switched) {
        quranMode = true;
        updateQuranModeButton();
        const response = data.response || data.response_arabic || 'تم تفعيل وضع التسميع';
        showOutput('وضع التسميع', response, 'correct');
        return;
    }
    
    const result = data.result || data;
    const response = data.response || result.feedback || result.response_arabic || 'لا توجد استجابة';
    const isCorrect = result.is_correct !== undefined ? result.is_correct : data.is_correct;
    const corrections = result.corrections || [];
    const matchedVerse = result.matched_verse || '';
    
    // Determine result type
    let resultType = 'info';
    if (isCorrect === true) {
        resultType = 'correct';
    } else if (isCorrect === false) {
        resultType = 'incorrect';
    }
    
    // Build HTML
    let html = `<div class="result-main">${response}</div>`;
    
    if (matchedVerse) {
        html += `<div class="result-verse"><strong>الآية المطابقة:</strong><br>${matchedVerse}</div>`;
    }
    
    if (corrections && corrections.length > 0) {
        html += `<div class="result-corrections"><strong>التصحيحات:</strong><ul>`;
        corrections.forEach(correction => {
            const correctionText = typeof correction === 'string' ? correction : JSON.stringify(correction);
            html += `<li>${correctionText}</li>`;
        });
        html += `</ul></div>`;
    }
    
    showOutput('النتيجة', html, resultType);
}

// Show Output
function showOutput(title, content, type = 'info') {
    outputContent.className = 'output-content ' + type;
    outputContent.innerHTML = content;
    outputBox.classList.remove('hidden');
    
    // Auto scroll
    outputContent.scrollTop = outputContent.scrollHeight;
}

// Close Output
function closeOutput() {
    outputBox.classList.add('hidden');
}

// Toggle Chat
function toggleChat() {
    chatOpen = !chatOpen;
    if (chatOpen) {
        chatPanel.classList.remove('hidden');
        chatInput.focus();
    } else {
        chatPanel.classList.add('hidden');
    }
}

// Send Chat Message
async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to history and display
    chatHistory.push({ role: 'user', content: message });
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Show loading
    const loadingId = addChatMessage('assistant', 'جاري المعالجة...', true);

    try {
        // Check if message contains "تسميع" keyword
        const isQuranMode = message.includes('تسميع') || quranMode;
        
        const response = await fetch(`${API_BASE_URL}/text_query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: message,
                context: {
                    chat_history: chatHistory.slice(-10), // Last 10 messages for context
                    mode: isQuranMode ? 'quran' : 'normal'
                }
            })
        });

        const data = await response.json();
        
        // Handle mode switch in chat
        if (data.intent === 'mode_switch' || data.mode_switched) {
            quranMode = true;
            updateQuranModeButton();
            const assistantResponse = data.response || data.response_arabic || 'تم تفعيل وضع التسميع';
            chatHistory.push({ role: 'assistant', content: assistantResponse });
            updateChatMessage(loadingId, 'assistant', assistantResponse);
            return;
        }
        
        const assistantResponse = data.response || data.result?.response || 'عذراً، لم أتمكن من الإجابة';
        
        // Add assistant response to history
        chatHistory.push({ role: 'assistant', content: assistantResponse });
        
        // Update loading message
        updateChatMessage(loadingId, 'assistant', assistantResponse);
        
    } catch (error) {
        console.error('Chat error:', error);
        updateChatMessage(loadingId, 'assistant', 'حدث خطأ أثناء المعالجة. يرجى المحاولة مرة أخرى.');
    }
}

// Add Chat Message
function addChatMessage(role, text, isLoading = false) {
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now() + '-' + Math.random();
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${role}`;
    
    if (isLoading) {
        messageDiv.innerHTML = '<span class="loading-dots">...</span>';
    } else {
        messageDiv.textContent = text;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Update Chat Message
function updateChatMessage(messageId, role, text) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        messageDiv.textContent = text;
    }
}

// Check Service Health
async function checkServiceHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy' || data.status === 'degraded') {
            // Services are ready
            console.log('Services are ready');
        } else {
            showOutput('تحذير', 'بعض الخدمات غير متاحة. قد لا تعمل جميع الميزات بشكل صحيح.', 'error');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        showOutput('خطأ', 'لا يمكن الاتصال بالخادم. يرجى التأكد من أن جميع الخدمات تعمل.', 'error');
    }
}

// Make functions globally available
window.closeOutput = closeOutput;
window.toggleChat = toggleChat;
window.sendChatMessage = sendChatMessage;
window.toggleQuranMode = toggleQuranMode;
