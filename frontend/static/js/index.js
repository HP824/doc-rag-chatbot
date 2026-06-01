const API = "";
let deleteChatId = null;

async function loadChats() {
  const res = await fetch(`${API}/api/chats`);
  const chats = await res.json();
  const list = document.getElementById("chat-list");
  const empty = document.getElementById("empty-state");

  if (chats.length === 0) {
    empty.classList.remove("d-none");
    return;
  }

  empty.classList.add("d-none");
  list.innerHTML = chats.map(chat => `
    <div class="col-md-4 col-sm-6">
      <div class="card shadow-sm chat-card-index h-100" onclick="window.location='/chat/${chat.id}'">
        <div class="card-body d-flex flex-column justify-content-between">
          <div>
            <h5 class="card-title fw-bold mb-1">
              <i class="bi bi-chat-square-text me-2 text-primary"></i>${chat.name}
            </h5>
            <p class="card-text text-muted small">${chat.description || "No description"}</p>
          </div>
          <div class="d-flex justify-content-between align-items-center mt-3">
            <small class="text-muted">${chat.created_at.slice(0, 10)}</small>
            <button
              class="btn btn-sm btn-outline-danger"
              onclick="event.stopPropagation(); confirmDelete('${chat.id}', '${chat.name.replace(/'/g, "\\'")}')">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join("");
}

function confirmDelete(id, name) {
  deleteChatId = id;
  document.getElementById("delete-chat-name").textContent = name;
  new bootstrap.Modal(document.getElementById("deleteModal")).show();
}

document.getElementById("confirm-delete-btn").addEventListener("click", async () => {
  if (!deleteChatId) return;
  await fetch(`${API}/api/chats/${deleteChatId}`, { method: "DELETE" });
  bootstrap.Modal.getInstance(document.getElementById("deleteModal")).hide();
  deleteChatId = null;
  loadChats();
});

document.getElementById("create-chat-btn").addEventListener("click", async () => {
  const name = document.getElementById("chat-name").value.trim();
  const desc = document.getElementById("chat-desc").value.trim();
  const err = document.getElementById("new-chat-error");

  if (!name) {
    err.textContent = "Chat name is required.";
    err.classList.remove("d-none");
    return;
  }

  err.classList.add("d-none");

  const res = await fetch(`${API}/api/chats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description: desc || null })
  });

  const chat = await res.json();
  bootstrap.Modal.getInstance(document.getElementById("newChatModal")).hide();
  document.getElementById("chat-name").value = "";
  document.getElementById("chat-desc").value = "";
  window.location = `/chat/${chat.id}`;
});

loadChats();
