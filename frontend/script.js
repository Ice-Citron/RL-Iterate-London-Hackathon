// Configuration
const CONFIG = {
    AGENT_API: 'http://localhost:4000',
    JUDGE_API: 'http://localhost:8080',
    FRONTEND_PORT: 8000
};

// State
let challenges = [];
let selectedChallenge = null;
let agentResponse = null;

// DOM Elements
const challengeList = document.getElementById('challengeList');
const selectedChallengeTitle = document.getElementById('selectedChallengeTitle');
const selectedChallengeDesc = document.getElementById('selectedChallengeDesc');
const runAgentBtn = document.getElementById('runAgentBtn');
const evaluateBtn = document.getElementById('evaluateBtn');
const agentOutput = document.getElementById('agentOutput');
const judgeOutput = document.getElementById('judgeOutput');
const loadingModal = document.getElementById('loadingModal');
const loadingText = document.getElementById('loadingText');

// Initialize
async function init() {
    try {
        await loadChallenges();
        renderChallenges();
        setupEventListeners();
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to load challenges. Please refresh the page.');
    }
}

// Load challenges from JSON
async function loadChallenges() {
    const response = await fetch('challenges.json');
    challenges = await response.json();
}

// Render challenge list
function renderChallenges() {
    challengeList.innerHTML = '';
    
    challenges.forEach(challenge => {
        const card = createChallengeCard(challenge);
        challengeList.appendChild(card);
    });
}

// Create challenge card element
function createChallengeCard(challenge) {
    const card = document.createElement('div');
    card.className = 'challenge-card';
    card.dataset.id = challenge.id;
    
    const difficultyClass = challenge.difficulty.toLowerCase();
    
    card.innerHTML = `
        <h3>${challenge.title}</h3>
        <p>${challenge.description}</p>
        <div class="challenge-meta">
            <span class="badge badge-${difficultyClass}">${challenge.difficulty}</span>
            <span class="badge badge-category">${challenge.category}</span>
        </div>
    `;
    
    card.addEventListener('click', () => selectChallenge(challenge));
    
    return card;
}

// Select a challenge
function selectChallenge(challenge) {
    selectedChallenge = challenge;
    agentResponse = null;
    
    // Update UI
    document.querySelectorAll('.challenge-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-id="${challenge.id}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    selectedChallengeTitle.textContent = challenge.title;
    selectedChallengeDesc.textContent = challenge.description;
    
    runAgentBtn.disabled = false;
    evaluateBtn.disabled = true;
    
    // Clear outputs
    agentOutput.innerHTML = '<div class="output-placeholder">Click "Run Agent" to start the challenge</div>';
    judgeOutput.innerHTML = '<div class="output-placeholder">Run the agent first, then evaluate the response</div>';
}

// Setup event listeners
function setupEventListeners() {
    runAgentBtn.addEventListener('click', runAgent);
    evaluateBtn.addEventListener('click', evaluateResponse);
}

// Run the trainee agent
async function runAgent() {
    if (!selectedChallenge) return;
    
    showLoading('Running trainee agent...');
    runAgentBtn.disabled = true;
    
    try {
        const response = await fetch(`${CONFIG.AGENT_API}/complete_task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_description: selectedChallenge.description
            })
        });
        
        if (!response.ok) {
            throw new Error(`Agent API error: ${response.status}`);
        }
        
        const data = await response.json();
        agentResponse = data.summary;
        
        displayAgentResponse(agentResponse);
        evaluateBtn.disabled = false;
        
    } catch (error) {
        console.error('Agent error:', error);
        displayAgentError(error.message);
        runAgentBtn.disabled = false;
    } finally {
        hideLoading();
    }
}

// Evaluate the agent's response
async function evaluateResponse() {
    if (!selectedChallenge || !agentResponse) return;
    
    showLoading('Evaluating with LLM judge...');
    evaluateBtn.disabled = true;
    
    try {
        const response = await fetch(`${CONFIG.JUDGE_API}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_description: selectedChallenge.description,
                agent_response: agentResponse
            })
        });
        
        if (!response.ok) {
            throw new Error(`Judge API error: ${response.status}`);
        }
        
        const data = await response.json();
        displayJudgeEvaluation(data);
        
    } catch (error) {
        console.error('Judge error:', error);
        displayJudgeError(error.message);
    } finally {
        hideLoading();
        evaluateBtn.disabled = false;
        runAgentBtn.disabled = false;
    }
}

// Display agent response
function displayAgentResponse(summary) {
    agentOutput.innerHTML = `
        <div class="output-content">
            <div class="output-header">
                <span class="status-icon">🤖</span>
                <h4>Agent Response</h4>
            </div>
            <div class="output-body">${escapeHtml(summary)}</div>
        </div>
    `;
}

// Display agent error
function displayAgentError(errorMessage) {
    agentOutput.innerHTML = `
        <div class="output-content">
            <div class="output-header">
                <span class="status-icon">❌</span>
                <h4>Error</h4>
            </div>
            <div class="error-message">
                Failed to run agent: ${escapeHtml(errorMessage)}
                <br><br>
                Make sure the trainee agent is running on ${CONFIG.AGENT_API}
            </div>
        </div>
    `;
}

// Display judge evaluation
function displayJudgeEvaluation(evaluation) {
    const score = evaluation.score;
    const scoreClass = score >= 0.7 ? 'score-high' : score >= 0.4 ? 'score-medium' : 'score-low';
    const scoreIcon = score >= 0.7 ? '✅' : score >= 0.4 ? '⚠️' : '❌';
    
    judgeOutput.innerHTML = `
        <div class="output-content">
            <div class="output-header">
                <span class="status-icon">⚖️</span>
                <h4>Judge Evaluation</h4>
            </div>
            <div class="score-display ${scoreClass}">
                <span>${scoreIcon}</span>
                <span>Score: ${(score * 100).toFixed(1)}%</span>
            </div>
            <div class="output-body">${escapeHtml(evaluation.summary)}</div>
        </div>
    `;
}

// Display judge error
function displayJudgeError(errorMessage) {
    judgeOutput.innerHTML = `
        <div class="output-content">
            <div class="output-header">
                <span class="status-icon">❌</span>
                <h4>Error</h4>
            </div>
            <div class="error-message">
                Failed to evaluate: ${escapeHtml(errorMessage)}
                <br><br>
                Make sure the judge server is running on ${CONFIG.JUDGE_API}
            </div>
        </div>
    `;
}

// Show loading modal
function showLoading(message) {
    loadingText.textContent = message;
    loadingModal.classList.add('active');
}

// Hide loading modal
function hideLoading() {
    loadingModal.classList.remove('active');
}

// Show error notification
function showError(message) {
    alert(message); // Simple error handling, could be improved with toast notifications
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Start the application
init();
