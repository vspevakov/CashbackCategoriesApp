const summaryState = {
  users: {},
  models: [],
};

const summaryUserSelect = document.getElementById("summary-user-select");
const chatUsersSelect = document.getElementById("chat-users-select");
const modelSelect = document.getElementById("model-select");
const summaryOutput = document.getElementById("summary-output");
const chatMessages = document.getElementById("chat-messages");
const chatQuestion = document.getElementById("chat-question");
const chatSendBtn = document.getElementById("chat-send-btn");
const pullModelInput = document.getElementById("pull-model-input");
const pullModelBtn = document.getElementById("pull-model-btn");
const downloadModelSelect = document.getElementById("download-model-select");

const MODEL_PRESETS = [
  { label: "Llama 3.1 8B", value: "llama3.1:8b" },
  { label: "Llama 3.1 70B", value: "llama3.1:70b" },
  { label: "Llama 3.2 1B", value: "llama3.2:1b" },
  { label: "Llama 3.2 3B", value: "llama3.2:3b" },
  { label: "Mistral 7B", value: "mistral:7b" },
  { label: "Qwen 2.5 3B", value: "qwen2.5:3b" },
  { label: "Qwen 2.5 7B", value: "qwen2.5:7b" },
  { label: "Qwen 2.5 14B", value: "qwen2.5:14b" },
  { label: "Gemma 2 2B", value: "gemma2:2b" },
  { label: "Gemma 2 9B", value: "gemma2:9b" },
  { label: "Gemma 2 27B", value: "gemma2:27b" },
  { label: "DeepSeek R1 7B", value: "deepseek-r1:7b" },
  { label: "DeepSeek R1 8B", value: "deepseek-r1:8b" },
  { label: "DeepSeek R1 14B", value: "deepseek-r1:14b" },
];

function formatPercent(value) {
  const numericValue = Number(value) || 0;
  return Number.isInteger(numericValue)
    ? String(numericValue)
    : numericValue.toFixed(1);
}

function fillSummaryUsers() {
  const current = summaryUserSelect.value;
  summaryUserSelect.innerHTML = '<option value="">Выберите пользователя</option>';
  chatUsersSelect.innerHTML = "";

  Object.keys(summaryState.users)
    .sort((a, b) => a.localeCompare(b, "ru"))
    .forEach((user) => {
      const option = document.createElement("option");
      option.value = user;
      option.textContent = user;
      if (user === current) {
        option.selected = true;
      }
      summaryUserSelect.append(option);

      const chatOption = document.createElement("option");
      chatOption.value = user;
      chatOption.textContent = user;
      chatUsersSelect.append(chatOption);
    });
}

function fillModels() {
  const current = modelSelect.value;
  modelSelect.innerHTML = "";

  if (summaryState.models.length === 0) {
    modelSelect.innerHTML = '<option value="">Нет доступных моделей</option>';
    return;
  }

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Выберите модель";
  modelSelect.append(placeholder);

  summaryState.models.forEach((model) => {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    if (model === current) {
      option.selected = true;
    }
    modelSelect.append(option);
  });
}

function fillDownloadModelOptions() {
  downloadModelSelect.innerHTML = '<option value="">Выберите готовую модель</option>';
  MODEL_PRESETS.forEach((preset) => {
    const option = document.createElement("option");
    option.value = preset.value;
    option.textContent = `${preset.label} (${preset.value})`;
    downloadModelSelect.append(option);
  });
}

function syncPullModelInput() {
  const model = downloadModelSelect.value;
  if (model) {
    pullModelInput.value = model;
  } else if (!pullModelInput.value.trim()) {
    pullModelInput.value = "";
  }
}

function renderSummary() {
  const user = summaryUserSelect.value;
  summaryOutput.innerHTML = "";

  if (!user) {
    summaryOutput.innerHTML = '<p class="summary__empty">Выберите пользователя.</p>';
    return;
  }

  const cards = summaryState.users[user] || {};
  const cardNames = Object.keys(cards).sort((a, b) => a.localeCompare(b, "ru"));

  if (cardNames.length === 0) {
    summaryOutput.innerHTML = '<p class="summary__empty">У пользователя пока нет карт.</p>';
    return;
  }

  cardNames.forEach((cardName) => {
    const cardData = cards[cardName] || {};
    const activeCategories = Object.entries(cardData)
      .filter(([, categoryState]) => Boolean(categoryState?.enabled))
      .sort(([left], [right]) => left.localeCompare(right, "ru"));

    const row = document.createElement("p");
    row.className = "summary-line";

    if (activeCategories.length === 0) {
      row.textContent = `${cardName}: нет активных категорий`;
      summaryOutput.append(row);
      return;
    }

    const categoriesText = activeCategories
      .map(([categoryName, categoryState]) => {
        return `${categoryName} - ${formatPercent(categoryState.percent)}%`;
      })
      .join(", ");

    row.textContent = `${cardName}: ${categoriesText}`;
    summaryOutput.append(row);
  });
}

function appendChatMessage(role, text) {
  const message = document.createElement("div");
  message.className = `chat-message ${role}`;
  message.textContent = text;
  chatMessages.append(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return message;
}

async function loadSummaryState() {
  const response = await fetch("/api/state");
  if (!response.ok) {
    throw new Error("Не удалось загрузить данные");
  }

  const payload = await response.json();
  summaryState.users = payload.users;
  fillSummaryUsers();
  renderSummary();
}

async function loadModels() {
  const response = await fetch("/api/ollama/models");
  const payload = await response.json();

  if (!response.ok) {
    summaryState.models = [];
    fillModels();
    appendChatMessage("assistant", payload.detail || "Не удалось загрузить модели Ollama.");
    return;
  }

  summaryState.models = payload.models;
  fillModels();
}

async function askOllama() {
  const selectedUsers = Array.from(chatUsersSelect.selectedOptions).map((option) => option.value);
  const model = modelSelect.value;
  const question = chatQuestion.value.trim();

  if (selectedUsers.length === 0) {
    appendChatMessage("assistant", "Сначала выберите одного или нескольких пользователей для сравнения.");
    return;
  }
  if (!model) {
    appendChatMessage("assistant", "Сначала выберите модель Ollama.");
    return;
  }
  if (!question) {
    appendChatMessage("assistant", "Введите вопрос.");
    return;
  }

  appendChatMessage("user", question);
  chatQuestion.value = "";
  chatSendBtn.disabled = true;

  const response = await fetch("/api/ollama/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_names: selectedUsers,
      model,
      question,
    }),
  });
  const payload = await response.json();
  chatSendBtn.disabled = false;

  if (!response.ok) {
    appendChatMessage("assistant", payload.detail || "Ошибка при обращении к Ollama.");
    return;
  }

  appendChatMessage("assistant", payload.answer);
}

async function pullModel() {
  const model = pullModelInput.value.trim();
  if (!model) {
    appendChatMessage("assistant", "Введите имя модели для загрузки.");
    return;
  }

  pullModelBtn.disabled = true;
  const progressMessage = appendChatMessage("assistant", `Загружаю модель ${model}...`);

  const response = await fetch(`/api/ollama/pull-stream?model=${encodeURIComponent(model)}`);
  if (!response.ok || !response.body) {
    let detail = "Не удалось загрузить модель.";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (error) {
      console.error(error);
    }
    progressMessage.textContent = detail;
    pullModelBtn.disabled = false;
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let lastStatus = `Загружаю модель ${model}...`;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    lines.forEach((line) => {
      if (!line.trim()) {
        return;
      }

      try {
        const event = JSON.parse(line);
        const status = event.status || lastStatus;
        const completed = event.completed;
        const total = event.total;

        if (typeof completed === "number" && typeof total === "number" && total > 0) {
          const percent = Math.min(100, Math.round((completed / total) * 100));
          lastStatus = `${status} (${percent}%)`;
        } else {
          lastStatus = status;
        }
        progressMessage.textContent = lastStatus;
      } catch (error) {
        console.error(error);
      }
    });
  }

  await loadModels();
  modelSelect.value = model;
  pullModelInput.value = "";
  progressMessage.textContent = lastStatus.includes("100%")
    ? lastStatus
    : `Модель ${model} загружена`;
  pullModelBtn.disabled = false;
}

summaryUserSelect.addEventListener("change", renderSummary);
downloadModelSelect.addEventListener("change", syncPullModelInput);
chatSendBtn.addEventListener("click", () => {
  askOllama().catch((error) => {
    console.error(error);
    chatSendBtn.disabled = false;
    appendChatMessage("assistant", "Ошибка при обращении к Ollama.");
  });
});
pullModelBtn.addEventListener("click", () => {
  pullModel().catch((error) => {
    console.error(error);
    pullModelBtn.disabled = false;
    appendChatMessage("assistant", "Ошибка при загрузке модели.");
  });
});

loadSummaryState().catch((error) => {
  console.error(error);
  summaryOutput.innerHTML = '<p class="summary__empty">Ошибка загрузки данных.</p>';
});

loadModels().catch((error) => {
  console.error(error);
  summaryState.models = [];
  fillModels();
  appendChatMessage("assistant", "Не удалось подключиться к Ollama.");
});

fillDownloadModelOptions();
