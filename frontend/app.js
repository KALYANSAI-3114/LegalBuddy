/* ═══════════════════════════════════════════════════════════
   LegalBuddy — Legal Assistant  |  Frontend Application Logic
   ═══════════════════════════════════════════════════════════ */

(() => {
    "use strict";

    // ─── Configuration ───
    const API_BASE = window.location.origin;
    const ENDPOINTS = {
        chat: `${API_BASE}/chat`,
        health: `${API_BASE}/health`,
    };

    // ─── DOM References ───
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const dom = {
        chatForm: $("#chatForm"),
        queryInput: $("#queryInput"),
        btnSend: $("#btnSend"),
        btnNewChat: $("#btnNewChat"),
        messages: $("#messages"),
        chatContainer: $("#chatContainer"),
        welcomeScreen: $("#welcomeScreen"),
        starterChips: $("#starterChips"),
        statusDot: $("#statusDot"),
        statusLabel: $("#statusLabel"),
        statusDetail: $("#statusDetail"),
        inputWrapper: $(".input-wrapper"),
        sidebar: $("#sidebar"),
        mobileMenuToggle: $("#mobileMenuToggle"),
        sidebarOverlay: $("#sidebarOverlay"),
    };

    // ─── State ───
    let isLoading = false;
    let messageCount = 0;

    // ═══════════════════════════════════════════════════════
    // HEALTH CHECK
    // ═══════════════════════════════════════════════════════
    async function checkHealth() {
        dom.statusDot.className = "status-dot";
        dom.statusLabel.textContent = "Checking…";
        dom.statusDetail.textContent = "";

        try {
            const res = await fetch(ENDPOINTS.health, { signal: AbortSignal.timeout(5000) });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (data.status === "ok") {
                dom.statusDot.className = "status-dot connected";
                dom.statusLabel.textContent = "All systems online";
                dom.statusDetail.textContent = `Model: ${data.model || "tinyllama"}`;
            } else {
                dom.statusDot.className = "status-dot degraded";
                dom.statusLabel.textContent = "Partially available";
                const parts = [];
                if (data.rag_engine !== "ready") parts.push("RAG loading");
                if (data.ollama !== "connected") parts.push("Ollama offline");
                dom.statusDetail.textContent = parts.join(" · ") || "Check server logs";
            }
        } catch (err) {
            dom.statusDot.className = "status-dot disconnected";
            dom.statusLabel.textContent = "Backend offline";
            dom.statusDetail.textContent = "Start the server and refresh";
        }
    }

    // ═══════════════════════════════════════════════════════
    // CHAT LOGIC
    // ═══════════════════════════════════════════════════════
    async function fetchAnswer(query) {
        if (isLoading) return;
        isLoading = true;
        setInputDisabled(true);

        // Hide welcome, show user message
        hideWelcome();
        renderMessage("user", query);

        // Show typing indicator
        const typingEl = showTypingIndicator();

        try {
            const res = await fetch(ENDPOINTS.chat, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            });

            // Remove typing indicator
            typingEl.remove();

            if (!res.ok) {
                const errData = await res.json().catch(() => null);
                const errMsg =
                    errData?.detail ||
                    `Server responded with status ${res.status}. Please try again.`;
                renderError(errMsg);
                return;
            }

            const data = await res.json();
            renderMessage("ai", data.answer, data.sources);
        } catch (err) {
            typingEl.remove();
            if (err.name === "TypeError" && err.message.includes("fetch")) {
                renderError("Cannot reach the backend server. Please make sure it is running.");
            } else {
                renderError(`Something went wrong: ${err.message}`);
            }
        } finally {
            isLoading = false;
            setInputDisabled(false);
            dom.queryInput.focus();
        }
    }

    // ═══════════════════════════════════════════════════════
    // RENDER HELPERS
    // ═══════════════════════════════════════════════════════

    function renderMessage(role, content, sources) {
        messageCount++;
        const msg = document.createElement("div");
        msg.className = `message ${role}`;
        msg.id = `msg-${messageCount}`;

        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.textContent = role === "user" ? "U" : "L";

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";

        // Format content — convert newlines to paragraphs for AI
        if (role === "ai") {
            bubble.innerHTML = formatAIContent(content);
        } else {
            bubble.textContent = content;
        }

        // Sources
        if (role === "ai" && sources && sources.length > 0) {
            const sourcesSection = buildSourcesSection(sources);
            bubble.appendChild(sourcesSection);
        }

        msg.appendChild(avatar);
        msg.appendChild(bubble);
        dom.messages.appendChild(msg);
        scrollToBottom();
    }

    function formatAIContent(text) {
        // Simple markdown-like formatting
        let html = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Bold **text**
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        // Italic *text*
        html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
        // Line breaks
        html = html.replace(/\n\n/g, "</p><p>");
        html = html.replace(/\n/g, "<br/>");

        return `<p>${html}</p>`;
    }

    function buildSourcesSection(sources) {
        const wrapper = document.createElement("div");

        const toggle = document.createElement("button");
        toggle.className = "sources-toggle";
        toggle.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
            ${sources.length} source${sources.length > 1 ? "s" : ""}
        `;

        const list = document.createElement("div");
        list.className = "sources-list";
        const ul = document.createElement("ul");
        sources.forEach((src) => {
            const li = document.createElement("li");
            li.textContent = src;
            ul.appendChild(li);
        });
        list.appendChild(ul);

        toggle.addEventListener("click", () => {
            toggle.classList.toggle("open");
            list.classList.toggle("visible");
        });

        wrapper.appendChild(toggle);
        wrapper.appendChild(list);
        return wrapper;
    }

    function showTypingIndicator() {
        const el = document.createElement("div");
        el.className = "typing-indicator";
        el.id = "typingIndicator";

        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.style.background = "linear-gradient(135deg, var(--gold-500), var(--gold-600))";
        avatar.style.color = "var(--navy-900)";
        avatar.textContent = "L";

        const dots = document.createElement("div");
        dots.className = "typing-dots";
        dots.innerHTML = "<span></span><span></span><span></span>";

        el.appendChild(avatar);
        el.appendChild(dots);
        dom.messages.appendChild(el);
        scrollToBottom();
        return el;
    }

    function renderError(message) {
        const el = document.createElement("div");
        el.className = "msg-error";
        el.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <span>${escapeHtml(message)}</span>
        `;
        dom.messages.appendChild(el);
        scrollToBottom();
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // ═══════════════════════════════════════════════════════
    // UI HELPERS
    // ═══════════════════════════════════════════════════════

    function hideWelcome() {
        if (dom.welcomeScreen && !dom.welcomeScreen.classList.contains("hidden")) {
            dom.welcomeScreen.classList.add("hidden");
        }
    }

    function showWelcome() {
        dom.welcomeScreen.classList.remove("hidden");
    }

    function scrollToBottom() {
        requestAnimationFrame(() => {
            dom.chatContainer.scrollTop = dom.chatContainer.scrollHeight;
        });
    }

    function setInputDisabled(disabled) {
        dom.queryInput.disabled = disabled;
        dom.btnSend.disabled = disabled;
        dom.inputWrapper.classList.toggle("disabled", disabled);
    }

    function updateSendButton() {
        const hasContent = dom.queryInput.value.trim().length > 0;
        dom.btnSend.disabled = !hasContent || isLoading;
    }

    function autoResizeTextarea() {
        dom.queryInput.style.height = "auto";
        dom.queryInput.style.height =
            Math.min(dom.queryInput.scrollHeight, parseInt(getComputedStyle(document.documentElement).getPropertyValue("--input-max-height"))) + "px";
    }

    // ═══════════════════════════════════════════════════════
    // EVENT HANDLERS
    // ═══════════════════════════════════════════════════════

    // Form submission
    dom.chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = dom.queryInput.value.trim();
        if (!query || isLoading) return;
        dom.queryInput.value = "";
        dom.queryInput.style.height = "auto";
        updateSendButton();
        fetchAnswer(query);
    });

    // Input events
    dom.queryInput.addEventListener("input", () => {
        updateSendButton();
        autoResizeTextarea();
    });

    // Enter to send, Shift+Enter for newline
    dom.queryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            dom.chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // New Chat
    dom.btnNewChat.addEventListener("click", () => {
        dom.messages.innerHTML = "";
        messageCount = 0;
        showWelcome();
        dom.queryInput.value = "";
        dom.queryInput.style.height = "auto";
        updateSendButton();
        closeMobileSidebar();
        dom.queryInput.focus();
    });

    // Starter chips
    dom.starterChips.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip");
        if (!chip) return;
        const query = chip.dataset.query;
        if (query) fetchAnswer(query);
    });

    // Mobile sidebar
    dom.mobileMenuToggle.addEventListener("click", () => {
        dom.sidebar.classList.toggle("open");
        dom.sidebarOverlay.classList.toggle("active");
    });

    dom.sidebarOverlay.addEventListener("click", closeMobileSidebar);

    function closeMobileSidebar() {
        dom.sidebar.classList.remove("open");
        dom.sidebarOverlay.classList.remove("active");
    }

    // ═══════════════════════════════════════════════════════
    // INITIALISATION
    // ═══════════════════════════════════════════════════════
    checkHealth();
    // Re-check health every 30 seconds
    setInterval(checkHealth, 30000);

    // Focus input on load
    dom.queryInput.focus();
})();
