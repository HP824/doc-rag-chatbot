const API = "";
const chatId = window.location.pathname.split("/").pop();
let hasDocuments = false;

// ── Load chat info ─────────────────────────────────────────────────────────
async function loadChat() {
  const res = await fetch(`${API}/api/chats/${chatId}`);
  const chat = await res.json();
  document.title = `${chat.name} — Document RAG`;
  document.getElementById("nav-chat-name").textContent = chat.name;
  document.getElementById("edit-name").value = chat.name;
  document.getElementById("edit-desc").value = chat.description || "";
}

// ── Load documents ─────────────────────────────────────────────────────────
async function loadDocuments() {
  const res = await fetch(`${API}/api/chats/${chatId}/documents`);
  const docs = await res.json();
  const list = document.getElementById("doc-list");
  const count = document.getElementById("doc-count");

  count.textContent = docs.length;
  hasDocuments = docs.length > 0;
  updateChatInput();

  if (docs.length === 0) {
    list.innerHTML = `<p class="text-muted small text-center">No documents yet.</p>`;
    return;
  }

  list.innerHTML = docs.map(doc => `
    <div class="doc-item" id="doc-${doc.id}">
      <span class="doc-name" title="${doc.name}">
        <i class="bi bi-file-earmark-text me-1 text-primary"></i>${doc.name}
      </span>
      <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="removeDocument('${doc.id}')">
        <i class="bi bi-x"></i>
      </button>
    </div>
  `).join("");
}

async function removeDocument(docId) {
  await fetch(`${API}/api/documents/${docId}`, { method: "DELETE" });
  loadDocuments();
}

// ── File upload ────────────────────────────────────────────────────────────
document.getElementById("file-input").addEventListener("change", async (e) => {
  const files = Array.from(e.target.files);
  if (!files.length) return;

  const progress = document.getElementById("upload-progress");
  const status = document.getElementById("upload-status");
  progress.classList.remove("d-none");

  for (const file of files) {
    status.textContent = `Uploading ${file.name}...`;
    const formData = new FormData();
    formData.append("file", file);
    await fetch(`${API}/api/chats/${chatId}/documents`, {
      method: "POST",
      body: formData
    });
  }

  progress.classList.add("d-none");
  e.target.value = "";
  loadDocuments();
});

// ── Chat input state ───────────────────────────────────────────────────────
function updateChatInput() {
  const input = document.getElementById("question-input");
  const btn = document.getElementById("ask-btn");
  const empty = document.getElementById("chat-empty");

  input.disabled = !hasDocuments;
  btn.disabled = !hasDocuments;

  if (hasDocuments) {
    empty.classList.add("d-none");
  } else {
    empty.classList.remove("d-none");
  }
}

// ── Chat messages ──────────────────────────────────────────────────────────
function appendMessage(role, content, sources = []) {
  const messages = document.getElementById("chat-messages");
  const empty = document.getElementById("chat-empty");
  empty.classList.add("d-none");

  const bubble = document.createElement("div");
  bubble.className = `message-bubble message-${role}`;
  bubble.textContent = content;
  messages.appendChild(bubble);

  if (role === "assistant" && sources.length > 0) {
    const src = document.createElement("div");
    src.className = "message-sources";
    src.innerHTML = `<i class="bi bi-paperclip me-1"></i>Sources: ${sources.join(", ")}`;
    messages.appendChild(src);
  }

  messages.scrollTop = messages.scrollHeight;
}

function appendThinking() {
  const messages = document.getElementById("chat-messages");
  const el = document.createElement("div");
  el.className = "thinking";
  el.id = "thinking-indicator";
  el.textContent = "Thinking...";
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

function removeThinking() {
  const el = document.getElementById("thinking-indicator");
  if (el) el.remove();
}

// ── Ask question ───────────────────────────────────────────────────────────
async function askQuestion() {
  const input = document.getElementById("question-input");
  const question = input.value.trim();
  if (!question) return;

  input.value = "";
  appendMessage("user", question);
  appendThinking();

  const res = await fetch(`${API}/api/chats/${chatId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const result = await res.json();
  removeThinking();
  appendMessage("assistant", result.answer, result.sources || []);
}

document.getElementById("ask-btn").addEventListener("click", askQuestion);
document.getElementById("question-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") askQuestion();
});

// ── Edit chat ──────────────────────────────────────────────────────────────
document.getElementById("save-edit-btn").addEventListener("click", async () => {
  const name = document.getElementById("edit-name").value.trim();
  const desc = document.getElementById("edit-desc").value.trim();
  if (!name) return;

  await fetch(`${API}/api/chats/${chatId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description: desc || null })
  });

  bootstrap.Modal.getInstance(document.getElementById("editChatModal")).hide();
  loadChat();
});

// ── Delete chat ────────────────────────────────────────────────────────────
document.getElementById("confirm-delete-btn").addEventListener("click", async () => {
  await fetch(`${API}/api/chats/${chatId}`, { method: "DELETE" });
  window.location = "/";
});

// ── Init ───────────────────────────────────────────────────────────────────
loadChat();
loadDocuments();
