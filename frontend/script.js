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

// Run the trainee agent with streaming
async function runAgent() {
    if (!selectedChallenge) return;

    runAgentBtn.disabled = true;
    evaluateBtn.disabled = true;

    // Initialize the output display for streaming
    // Use flex layout to fill available space
    agentOutput.style.cssText = 'display: flex; flex-direction: column; height: 100%;';
    agentOutput.innerHTML = `
        <div class="output-header" style="flex-shrink: 0; margin-bottom: 8px;">
            <span class="status-icon">🤖</span>
            <h4 style="margin: 0;">Agent Working...</h4>
            <span class="loading-spinner"></span>
        </div>
        <div id="streamingOutput" style="flex: 1; min-height: 0; overflow-y: scroll; overflow-x: hidden; background: #f0f9ff; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 0.85rem; color: #1e293b;"></div>
        <div id="finalSummary" style="display: none;"></div>
    `;

    const streamingOutput = document.getElementById('streamingOutput');
    const finalSummary = document.getElementById('finalSummary');
    let toolCallCount = 0;
    let currentTextBuffer = '';  // Buffer for accumulating text deltas
    let currentTextElement = null;  // Current text element being built

    try {
        const response = await fetch(`${CONFIG.AGENT_API}/complete_task_stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_description: selectedChallenge.description,
                max_turns: 50
            })
        });

        if (!response.ok) {
            throw new Error(`Agent API error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const eventData = JSON.parse(line.slice(6));
                        const result = handleStreamEvent(eventData, streamingOutput, finalSummary, ++toolCallCount, currentTextBuffer, currentTextElement);
                        if (result) {
                            currentTextBuffer = result.buffer;
                            currentTextElement = result.element;
                        }
                    } catch (e) {
                        console.warn('Failed to parse SSE event:', e);
                    }
                }
            }
        }

        // Update header to show completion
        const header = agentOutput.querySelector('.output-header');
        if (header) {
            header.innerHTML = `
                <span class="status-icon">✅</span>
                <h4>Agent Complete</h4>
            `;
        }

        evaluateBtn.disabled = false;

    } catch (error) {
        console.error('Agent error:', error);
        displayAgentError(error.message);
    } finally {
        runAgentBtn.disabled = false;
    }
}

// Handle individual stream events
function handleStreamEvent(event, streamingOutput, finalSummary, count, textBuffer, textElement) {
    const displayType = event.display_type || event.type;
    let newBuffer = textBuffer || '';
    let newElement = textElement;

    // Helper to flush text buffer into a message element
    const flushTextBuffer = () => {
        if (newBuffer.trim() && newElement) {
            const contentDiv = newElement.querySelector('.event-content');
            if (contentDiv) {
                contentDiv.textContent = newBuffer.trim();
            }
        }
        // Reset for next message
        newBuffer = '';
        newElement = null;
    };

    switch (displayType) {
        case 'text_delta':
            // Accumulate text deltas into buffer
            if (event.content) {
                newBuffer += event.content;

                // Create or update text element
                if (!newElement) {
                    newElement = document.createElement('div');
                    newElement.className = 'message-event streaming-text';
                    newElement.innerHTML = `
                        <div class="event-header message">
                            <span class="event-icon">💬</span>
                            <strong>Agent Thinking</strong>
                        </div>
                        <div class="event-content"></div>
                    `;
                    streamingOutput.appendChild(newElement);
                }

                // Update content in real-time
                const contentDiv = newElement.querySelector('.event-content');
                if (contentDiv) {
                    contentDiv.textContent = newBuffer;
                }
                streamingOutput.scrollTop = streamingOutput.scrollHeight;
            }
            break;

        case 'tool_call':
            flushTextBuffer();  // Flush any pending text
            const toolDiv = document.createElement('div');
            toolDiv.className = 'tool-call-event';

            // Parse tool args and extract code if present
            let toolArgsDisplay = event.tool_args || '';
            let argsContent = '';

            try {
                let parsedArgs = toolArgsDisplay;
                if (typeof toolArgsDisplay === 'string' && (toolArgsDisplay.startsWith('{') || toolArgsDisplay.startsWith('['))) {
                    parsedArgs = JSON.parse(toolArgsDisplay);
                }

                if (typeof parsedArgs === 'object' && parsedArgs !== null) {
                    // Check if this is execute_code with a "code" field
                    if (parsedArgs.code) {
                        const codeContent = parsedArgs.code;
                        const codeLang = detectLanguage(codeContent) || 'python';
                        argsContent = createCodeBlock(codeContent, codeLang);
                    }
                    // Check for command field (bash/shell commands)
                    else if (parsedArgs.command) {
                        argsContent = createCodeBlock(parsedArgs.command, 'bash');
                    }
                    // Check for query field (SQL)
                    else if (parsedArgs.query) {
                        argsContent = createCodeBlock(parsedArgs.query, 'sql');
                    }
                    // Check for url field
                    else if (parsedArgs.url) {
                        argsContent = `<div class="event-args"><strong>URL:</strong> ${escapeHtml(parsedArgs.url)}</div>`;
                    }
                    // Default: show as formatted JSON but compact
                    else {
                        const jsonStr = JSON.stringify(parsedArgs, null, 2);
                        argsContent = createCodeBlock(truncateText(jsonStr, 400), 'json');
                    }
                } else {
                    argsContent = `<div class="event-args">${escapeHtml(truncateText(String(toolArgsDisplay), 200))}</div>`;
                }
            } catch (e) {
                // Fallback for non-JSON args
                argsContent = `<div class="event-args">${escapeHtml(truncateText(String(toolArgsDisplay), 200))}</div>`;
            }

            toolDiv.innerHTML = `
                <div class="event-header tool-call">
                    <span class="event-icon">🔧</span>
                    <strong>${escapeHtml(event.tool_name || 'Tool')}</strong>
                </div>
                ${argsContent}
            `;
            streamingOutput.appendChild(toolDiv);
            highlightCodeBlocks(toolDiv);
            streamingOutput.scrollTop = streamingOutput.scrollHeight;
            break;

        case 'tool_output':
            flushTextBuffer();  // Flush any pending text
            const outputDiv = document.createElement('div');
            outputDiv.className = 'tool-output-event';

            const outputText = event.output || '';
            const outputLang = detectLanguage(outputText);
            let formattedOutput;

            if (outputLang) {
                // Code output - use syntax highlighting
                formattedOutput = createCodeBlock(truncateText(outputText, 800), outputLang);
            } else if (outputText.includes('\n') && outputText.length > 50) {
                // Multi-line output - use terminal style
                formattedOutput = createTerminalOutput(truncateText(outputText, 800));
            } else {
                // Simple output
                formattedOutput = `<pre class="event-output">${escapeHtml(truncateText(outputText, 500))}</pre>`;
            }

            outputDiv.innerHTML = `
                <div class="event-header tool-output">
                    <span class="event-icon">📤</span>
                    <strong>Output</strong>
                </div>
                ${formattedOutput}
            `;
            streamingOutput.appendChild(outputDiv);
            highlightCodeBlocks(outputDiv);
            streamingOutput.scrollTop = streamingOutput.scrollHeight;
            break;

        case 'message':
            flushTextBuffer();  // Flush any pending text
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message-event';
            const msgContent = event.content || '';
            const formattedMsg = formatWithCodeHighlighting(truncateText(msgContent, 500));
            msgDiv.innerHTML = `
                <div class="event-header message">
                    <span class="event-icon">💬</span>
                    <strong>Agent Thinking</strong>
                </div>
                <div class="event-content">${formattedMsg}</div>
            `;
            streamingOutput.appendChild(msgDiv);
            highlightCodeBlocks(msgDiv);
            streamingOutput.scrollTop = streamingOutput.scrollHeight;
            break;

        case 'final':
            flushTextBuffer();  // Flush any pending text
            agentResponse = event.summary;

            // Hide the streaming output and show final response in its place
            streamingOutput.style.display = 'none';

            // Make final summary take the full space using flex
            finalSummary.style.cssText = 'display: flex; flex-direction: column; flex: 1; min-height: 0; overflow-y: auto; background: linear-gradient(135deg, rgba(16,185,129,0.05), rgba(59,130,246,0.05)); border: 2px solid #10b981; border-radius: 8px; padding: 16px;';

            // Display as plain text - no code formatting
            const summaryText = escapeHtml(event.summary || 'Task completed');
            finalSummary.innerHTML = `
                <div class="final-header" style="flex-shrink: 0; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(16,185,129,0.3); color: #10b981; font-size: 1.1rem;">
                    <span class="event-icon">🎯</span>
                    <strong>Final Response</strong>
                </div>
                <div class="final-content" style="flex: 1; overflow-y: auto; color: #1e293b; line-height: 1.7; white-space: pre-wrap; word-wrap: break-word; font-size: 0.95rem;">${summaryText}</div>
            `;
            break;

        case 'error':
            flushTextBuffer();  // Flush any pending text
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-event';
            errorDiv.innerHTML = `
                <div class="event-header error">
                    <span class="event-icon">❌</span>
                    <strong>Error</strong>
                </div>
                <div class="event-content">${escapeHtml(event.error || 'Unknown error')}</div>
            `;
            streamingOutput.appendChild(errorDiv);
            break;

        case 'info':
            // Skip generic info events - they're noise
            break;

        default:
            // Skip unknown events to reduce noise
            break;
    }

    return { buffer: newBuffer, element: newElement };
}

// Truncate text helper
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Evaluate the agent's response
async function evaluateResponse() {
    if (!selectedChallenge || !agentResponse) return;
    
    showLoading('Evaluating with LLM judge...');
    evaluateBtn.disabled = true;
    
    try {
        const requestBody = {
            task_description: selectedChallenge.description,
            agent_response: agentResponse
        };
        
        // Include model_answer if available
        if (selectedChallenge.model_answer) {
            requestBody.model_answer = selectedChallenge.model_answer;
        }
        
        const response = await fetch(`${CONFIG.JUDGE_API}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
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

// Detect code language from content or filename
function detectLanguage(text) {
    if (!text || typeof text !== 'string') return null;

    // Check for common code patterns
    if (/^\s*(def |class |import |from .* import |print\(|if __name__|async def )/.test(text)) return 'python';
    if (/^\s*(function |const |let |var |=>|console\.|export |import \{)/.test(text)) return 'javascript';
    if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s/i.test(text)) return 'sql';
    if (/^\s*[\$#]/.test(text) || /^\s*(cd |ls |cat |grep |curl |wget |npm |pip |git |echo |mkdir |rm )/.test(text)) return 'bash';
    if (/^\s*\{[\s\S]*"[\w]+"\s*:/.test(text) || /^\s*\[[\s\S]*\{/.test(text)) return 'json';
    if (/^\s*<(!DOCTYPE|html|head|body|div|span|p|a |script|style)/i.test(text)) return 'html';
    if (/^\s*(body|div|\.[\w-]+|#[\w-]+)\s*\{/.test(text)) return 'css';
    return null;
}

// Format text with code block detection and syntax highlighting
function formatWithCodeHighlighting(text) {
    if (!text) return '';

    // Check if the entire content looks like code
    const detectedLang = detectLanguage(text);
    if (detectedLang) {
        return createCodeBlock(text, detectedLang);
    }

    // Look for markdown-style code blocks ```lang ... ```
    const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
    let result = text;
    let hasCodeBlocks = false;

    result = result.replace(codeBlockRegex, (match, lang, code) => {
        hasCodeBlocks = true;
        const language = lang || detectLanguage(code) || 'plaintext';
        return createCodeBlock(code.trim(), language);
    });

    // Also check for indented code blocks (4+ spaces at start of lines)
    if (!hasCodeBlocks) {
        const indentedCodeRegex = /^((?:    |\t).+\n?)+/gm;
        const indentedMatch = text.match(indentedCodeRegex);
        if (indentedMatch && indentedMatch[0].length > 50) {
            const code = indentedMatch[0].replace(/^(    |\t)/gm, '');
            const lang = detectLanguage(code) || 'plaintext';
            result = result.replace(indentedMatch[0], createCodeBlock(code.trim(), lang));
        }
    }

    // Format inline code with backticks
    result = result.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    return result;
}

// Create a styled code block with syntax highlighting
function createCodeBlock(code, language) {
    const langDisplay = language.charAt(0).toUpperCase() + language.slice(1);
    const escapedCode = escapeHtml(code);
    const uniqueId = 'code-' + Math.random().toString(36).substr(2, 9);

    return `
        <div class="code-block" id="${uniqueId}">
            <div class="code-block-header">
                <div class="code-lang-label">
                    <span class="code-lang-icon ${language}"></span>
                    ${langDisplay}
                </div>
                <button class="copy-btn" onclick="copyCode('${uniqueId}')">Copy</button>
            </div>
            <pre class="language-${language}"><code class="language-${language}">${escapedCode}</code></pre>
        </div>
    `;
}

// Copy code to clipboard
function copyCode(blockId) {
    const block = document.getElementById(blockId);
    if (!block) return;

    const code = block.querySelector('code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        const btn = block.querySelector('.copy-btn');
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
        }, 2000);
    });
}

// Create terminal-style output
function createTerminalOutput(output, title = 'Output') {
    const escapedOutput = escapeHtml(output);
    return `
        <div class="terminal-output">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <span class="terminal-dot red"></span>
                    <span class="terminal-dot yellow"></span>
                    <span class="terminal-dot green"></span>
                </div>
                <span class="terminal-title">${escapeHtml(title)}</span>
            </div>
            <div class="terminal-body">${escapedOutput}</div>
        </div>
    `;
}

// Apply Prism highlighting to new code blocks
function highlightCodeBlocks(container) {
    if (typeof Prism !== 'undefined') {
        const codeBlocks = container.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            Prism.highlightElement(block);
        });
    }
}

// Start the application
init();
