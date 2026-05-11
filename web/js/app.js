/**
 * Roobie — AI Coding Assistant
 * Main application JavaScript
 * WebSocket communication, chat UI, file tree, terminal
 */

(function () {
    'use strict';

    // ── State ──────────────────────────────────────────
    const state = {
        ws: null,
        connected: false,
        processing: false,
        messages: [],
        currentModel: 'qwen2.5-coder:3b',
    };

    // ── DOM References ─────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const chatMessages = $('#chatMessages');
    const chatInput = $('#chatInput');
    const sendBtn = $('#sendBtn');
    const welcomeScreen = $('#welcomeScreen');
    const statusDot = $('.status-dot');
    const statusText = $('.status-text');
    const modelSelect = $('#modelSelect');
    const sidebar = $('#sidebar');
    const sidebarToggle = $('#sidebarToggle');
    const fileTree = $('#fileTree');
    const terminalOutput = $('#terminalOutput');
    const terminalInput = $('#terminalInput');
    const previewFrame = $('#previewFrame');
    const previewUrl = $('#previewUrl');
    const clearChatBtn = $('#clearChat');
    const refreshTreeBtn = $('#refreshTree');

    // ── Tool Icons ─────────────────────────────────────
    const TOOL_ICONS = {
        think: '🧠',
        create_file: '📄',
        edit_file: '✏️',
        read_file: '📖',
        delete_file: '🗑️',
        list_directory: '📂',
        create_folder: '📁',
        run_command: '💻',
        web_search: '🔍',
    };

    const TOOL_LABELS = {
        think: 'Thinking',
        create_file: 'Create File',
        edit_file: 'Edit File',
        read_file: 'Read File',
        delete_file: 'Delete File',
        list_directory: 'List Directory',
        create_folder: 'Create Folder',
        run_command: 'Run Command',
        web_search: 'Web Search',
    };

    // ── WebSocket ──────────────────────────────────────
    function connectWS() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${location.host}/ws`;

        try {
            state.ws = new WebSocket(wsUrl);
        } catch (e) {
            setStatus('error', 'WebSocket failed');
            return;
        }

        state.ws.onopen = () => {
            state.connected = true;
            setStatus('connected', 'Connected');
            // Request file tree
            sendWS({ type: 'get_tree' });
        };

        state.ws.onclose = () => {
            state.connected = false;
            setStatus('error', 'Disconnected');
            // Reconnect after 3s
            setTimeout(connectWS, 3000);
        };

        state.ws.onerror = () => {
            setStatus('error', 'Connection error');
        };

        state.ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                handleWSMessage(msg);
            } catch (e) {
                console.error('WS parse error:', e);
            }
        };
    }

    function sendWS(data) {
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
            state.ws.send(JSON.stringify(data));
        }
    }

    function handleWSMessage(msg) {
        switch (msg.type) {
            case 'file_tree':
                renderFileTree(msg.data);
                break;
            case 'file_content':
                showFileContent(msg.data);
                break;
            case 'thinking_start':
                showThinking();
                break;
            case 'thinking_end':
                hideThinking();
                break;
            case 'tool_call':
                addToolCall(msg.data);
                break;
            case 'tool_start':
                addToolCall(msg.data);
                break;
            case 'tool_end':
                updateToolResult(msg.data);
                break;
            case 'tool_result':
                updateToolResult(msg.data);
                break;
            case 'assistant_message':
                if (msg.data.partial) {
                    appendAssistantText(msg.data.content);
                } else {
                    addAssistantMessage(msg.data.content);
                }
                break;
            case 'terminal_output':
                appendTerminal(msg.data.text, 'stdout');
                break;
            case 'error':
                addSystemMessage(msg.data.message, 'error');
                break;
            case 'chat_complete':
                state.processing = false;
                sendBtn.disabled = false;
                hideThinking();
                if (msg.data.response) {
                    addAssistantMessage(msg.data.response);
                }
                // Refresh file tree after chat
                sendWS({ type: 'get_tree' });
                break;
        }
    }

    function setStatus(status, text) {
        statusDot.className = 'status-dot ' + status;
        statusText.textContent = text;
    }

    // ── Chat ───────────────────────────────────────────
    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || state.processing) return;

        // Hide welcome
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }

        // Add user message
        addUserMessage(text);
        chatInput.value = '';
        chatInput.style.height = 'auto';

        state.processing = true;
        sendBtn.disabled = true;

        // Send via WebSocket
        if (state.connected) {
            sendWS({
                type: 'chat',
                message: text,
                model: modelSelect.value,
            });
            showThinking();
        } else {
            // Fallback to REST API
            fetchChat(text);
        }
    }

    async function fetchChat(message) {
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, model: modelSelect.value }),
            });
            const data = await res.json();

            // Process events
            if (data.events) {
                for (const event of data.events) {
                    handleWSMessage(event);
                }
            }

            if (data.response) {
                addAssistantMessage(data.response);
            }
        } catch (e) {
            addSystemMessage('Failed to get response: ' + e.message, 'error');
        } finally {
            state.processing = false;
            sendBtn.disabled = false;
            hideThinking();
            sendWS({ type: 'get_tree' });
        }
    }

    function addUserMessage(text) {
        const div = createMessageEl('user', '👤', 'You', text);
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function addAssistantMessage(text) {
        hideThinking();
        // Check if we already have a partial assistant message
        const existing = chatMessages.querySelector('.message.assistant.partial');
        if (existing) {
            existing.classList.remove('partial');
            const body = existing.querySelector('.message-body');
            body.innerHTML = formatMessage(text);
            scrollToBottom();
            return;
        }

        const div = createMessageEl('assistant', '🤖', 'Roobie', text);
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function appendAssistantText(text) {
        hideThinking();
        let existing = chatMessages.querySelector('.message.assistant.partial');
        if (!existing) {
            existing = createMessageEl('assistant', '🤖', 'Roobie', text);
            existing.classList.add('partial');
            chatMessages.appendChild(existing);
        } else {
            const body = existing.querySelector('.message-body');
            body.innerHTML = formatMessage(text);
        }
        scrollToBottom();
    }

    function addSystemMessage(text, type = 'info') {
        const div = document.createElement('div');
        div.className = `message system ${type}`;
        div.innerHTML = `
            <div class="message-content">
                <div class="message-body" style="color: var(--${type === 'error' ? 'red' : 'yellow'})">${escapeHtml(text)}</div>
            </div>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function createMessageEl(role, avatar, name, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-name">${name}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-body">${formatMessage(text)}</div>
            </div>
        `;
        return div;
    }

    function formatMessage(text) {
        // Basic markdown-like formatting
        let html = escapeHtml(text);

        // Code blocks
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
            return `<pre><code class="lang-${lang}">${code}</code></pre>`;
        });

        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Remove tool_call blocks from display (they're shown separately)
        html = html.replace(/&lt;tool_call&gt;[\s\S]*?&lt;\/tool_call&gt;/g, '');

        // Clean up empty lines
        html = html.replace(/\n{3,}/g, '\n\n');

        return html;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ── Tool Calls ─────────────────────────────────────
    let toolCallCounter = 0;

    function addToolCall(data) {
        hideThinking();
        const id = `tool-${++toolCallCounter}`;
        const name = data.name || data.tool || 'unknown';
        const icon = TOOL_ICONS[name] || '🔧';
        const label = TOOL_LABELS[name] || name;
        const params = data.params || {};

        let paramsDisplay = '';
        if (name === 'create_file' || name === 'edit_file' || name === 'read_file' || name === 'delete_file') {
            paramsDisplay = params.path || '';
        } else if (name === 'run_command') {
            paramsDisplay = params.command || '';
        } else if (name === 'web_search') {
            paramsDisplay = params.query || '';
        } else if (name === 'think') {
            paramsDisplay = (params.thought || '').substring(0, 80) + '...';
        } else if (name === 'create_folder' || name === 'list_directory') {
            paramsDisplay = params.path || '';
        }

        const div = document.createElement('div');
        div.className = 'tool-call';
        div.id = id;
        div.dataset.tool = name;
        div.innerHTML = `
            <div class="tool-call-header" onclick="toggleToolBody('${id}')">
                <span class="tool-call-icon">${icon}</span>
                <span class="tool-call-name">${label}</span>
                <span style="color: var(--text-muted); font-size: 12px; font-family: var(--font-mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px;">${escapeHtml(paramsDisplay)}</span>
                <span class="tool-call-status running">
                    <span class="spinner"></span>
                </span>
            </div>
            <div class="tool-call-body" id="${id}-body">
                <pre>${escapeHtml(JSON.stringify(params, null, 2))}</pre>
            </div>
        `;

        // Insert before any partial message or at end
        const partial = chatMessages.querySelector('.message.partial');
        if (partial) {
            chatMessages.insertBefore(div, partial);
        } else {
            chatMessages.appendChild(div);
        }
        scrollToBottom();

        // Add terminal output for commands
        if (name === 'run_command') {
            appendTerminal(`$ ${params.command}`, 'cmd');
        }
    }

    function updateToolResult(data) {
        const name = data.name || data.tool || '';
        const result = data.result || {};

        // Find the last matching tool call
        const toolCalls = chatMessages.querySelectorAll(`.tool-call[data-tool="${name}"]`);
        const toolEl = toolCalls[toolCalls.length - 1];
        if (!toolEl) return;

        const statusEl = toolEl.querySelector('.tool-call-status');
        const bodyEl = toolEl.querySelector('.tool-call-body');

        if (result.success) {
            statusEl.className = 'tool-call-status success';
            statusEl.textContent = '✓';
        } else {
            statusEl.className = 'tool-call-status error';
            statusEl.textContent = '✗';
        }

        // Update body with result
        let resultText = '';
        if (name === 'run_command') {
            if (result.stdout) {
                resultText += result.stdout;
                appendTerminal(result.stdout, 'stdout');
            }
            if (result.stderr) {
                resultText += '\n' + result.stderr;
                appendTerminal(result.stderr, 'stderr');
            }
        } else if (name === 'read_file') {
            resultText = result.content || result.error || '';
        } else if (name === 'list_directory') {
            const entries = result.entries || [];
            resultText = entries.map(e => `${e.type === 'directory' ? '📁' : '📄'} ${e.name}`).join('\n');
        } else if (name === 'think') {
            resultText = result.thought || '';
        } else if (name === 'web_search') {
            const results = result.results || [];
            resultText = results.map(r => `${r.title}\n  ${r.url}\n  ${r.snippet}`).join('\n\n');
        } else {
            resultText = result.message || result.error || JSON.stringify(result, null, 2);
        }

        if (resultText) {
            bodyEl.innerHTML = `<pre>${escapeHtml(resultText)}</pre>`;
        }

        // Auto-expand think tool results
        if (name === 'think') {
            bodyEl.classList.add('expanded');
        }

        // Refresh file tree for file operations
        if (['create_file', 'edit_file', 'delete_file', 'create_folder'].includes(name)) {
            sendWS({ type: 'get_tree' });
        }

        scrollToBottom();
    }

    // Toggle tool call body
    window.toggleToolBody = function (id) {
        const body = document.getElementById(id + '-body');
        if (body) {
            body.classList.toggle('expanded');
        }
    };

    // ── Thinking Indicator ─────────────────────────────
    function showThinking() {
        if (chatMessages.querySelector('.thinking-indicator')) return;
        const div = document.createElement('div');
        div.className = 'thinking-indicator';
        div.innerHTML = `
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
            <span class="thinking-text">Roobie is thinking...</span>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function hideThinking() {
        const el = chatMessages.querySelector('.thinking-indicator');
        if (el) el.remove();
    }

    // ── File Tree ──────────────────────────────────────
    function renderFileTree(data) {
        if (!data || !data.success) {
            fileTree.innerHTML = '<div class="tree-loading">No files yet</div>';
            return;
        }

        const tree = data.tree || [];
        if (tree.length === 0) {
            fileTree.innerHTML = '<div class="tree-loading">Workspace is empty</div>';
            return;
        }

        fileTree.innerHTML = '';
        renderTreeNodes(tree, fileTree, 0);
    }

    function renderTreeNodes(nodes, container, depth) {
        for (const node of nodes) {
            const item = document.createElement('div');
            item.className = 'tree-item';
            item.style.paddingLeft = (16 + depth * 16) + 'px';

            const icon = node.type === 'directory' ? '📁' : getFileIcon(node.name);

            item.innerHTML = `
                <span class="tree-icon">${icon}</span>
                <span class="tree-name">${escapeHtml(node.name)}</span>
            `;

            if (node.type === 'file') {
                item.addEventListener('click', () => {
                    // Request file content
                    sendWS({ type: 'read_file', path: node.path });
                    // Highlight
                    fileTree.querySelectorAll('.tree-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                });
            }

            container.appendChild(item);

            if (node.children && node.children.length > 0) {
                renderTreeNodes(node.children, container, depth + 1);
            }
        }
    }

    function getFileIcon(name) {
        const ext = name.split('.').pop().toLowerCase();
        const icons = {
            js: '📜', ts: '📘', jsx: '⚛️', tsx: '⚛️',
            py: '🐍', html: '🌐', css: '🎨', json: '📋',
            md: '📝', txt: '📃', yml: '⚙️', yaml: '⚙️',
            sh: '🐚', bash: '🐚', env: '🔐', gitignore: '🔒',
            svg: '🖼️', png: '🖼️', jpg: '🖼️', ico: '🖼️',
        };
        return icons[ext] || '📄';
    }

    function showFileContent(data) {
        if (!data.success) {
            addSystemMessage(`Failed to read file: ${data.error}`, 'error');
            return;
        }
        // Show in a message
        const content = data.content || '';
        const path = data.path || '';
        addAssistantMessage(`📄 **${path}** (${data.lines} lines, ${data.size} bytes)\n\n\`\`\`\n${content}\n\`\`\``);
    }

    // ── Terminal ───────────────────────────────────────
    function appendTerminal(text, type = 'stdout') {
        const line = document.createElement('div');
        line.className = `terminal-${type}`;
        line.textContent = text;
        terminalOutput.appendChild(line);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    async function runTerminalCommand(command) {
        appendTerminal(`$ ${command}`, 'cmd');
        try {
            const res = await fetch('/api/terminal/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command, timeout: 30 }),
            });
            const data = await res.json();
            if (data.stdout) appendTerminal(data.stdout, 'stdout');
            if (data.stderr) appendTerminal(data.stderr, 'stderr');
            if (data.error) appendTerminal(data.error, 'stderr');
        } catch (e) {
            appendTerminal(`Error: ${e.message}`, 'stderr');
        }
    }

    // ── Utilities ──────────────────────────────────────
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }

    function autoResizeTextarea() {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
    }

    // ── Event Listeners ────────────────────────────────
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    chatInput.addEventListener('input', autoResizeTextarea);

    // Sidebar toggle
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // Clear chat
    clearChatBtn.addEventListener('click', async () => {
        chatMessages.innerHTML = '';
        if (welcomeScreen) {
            chatMessages.appendChild(welcomeScreen);
            welcomeScreen.style.display = '';
        }
        try {
            await fetch('/api/chat/history', { method: 'DELETE' });
        } catch (e) { /* ignore */ }
    });

    // Refresh file tree
    refreshTreeBtn.addEventListener('click', () => {
        sendWS({ type: 'get_tree' });
    });

    // Model selector
    modelSelect.addEventListener('change', () => {
        state.currentModel = modelSelect.value;
    });

    // Panel tabs
    $$('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            $$('.panel-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const panel = tab.dataset.panel;
            $$('.panel-content').forEach(p => p.classList.add('hidden'));
            $(`#${panel}Panel`).classList.remove('hidden');
        });
    });

    // Terminal input
    terminalInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const cmd = terminalInput.value.trim();
            if (cmd) {
                runTerminalCommand(cmd);
                terminalInput.value = '';
            }
        }
    });

    // Preview
    $('#previewRefresh')?.addEventListener('click', () => {
        const url = previewUrl.value.trim();
        if (url) {
            previewFrame.src = url;
        }
    });
    previewUrl?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            previewFrame.src = previewUrl.value.trim();
        }
    });

    // ── Check status & load models ─────────────────────
    async function checkStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();

            if (data.ollama?.connected) {
                setStatus('connected', 'Ollama connected');
                // Update model selector with available models
                if (data.ollama.models && data.ollama.models.length > 0) {
                    const currentVal = modelSelect.value;
                    modelSelect.innerHTML = '';
                    for (const model of data.ollama.models) {
                        const opt = document.createElement('option');
                        opt.value = model;
                        opt.textContent = model;
                        if (model === currentVal || model === data.current_model) {
                            opt.selected = true;
                        }
                        modelSelect.appendChild(opt);
                    }
                }
            } else {
                setStatus('error', 'Ollama not connected');
            }
        } catch (e) {
            setStatus('error', 'Server error');
        }
    }

    // ── Initialize ─────────────────────────────────────
    connectWS();
    checkStatus();

    // Periodic status check
    setInterval(checkStatus, 30000);

    // Focus input
    chatInput.focus();

})();
