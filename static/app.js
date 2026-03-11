const state = {
  users: {},
  availableCategories: [],
};

const userSelect = document.getElementById("user-select");
const cardSelect = document.getElementById("card-select");
const newUserInput = document.getElementById("new-user-input");
const addUserBtn = document.getElementById("add-user-btn");
const newCardInput = document.getElementById("new-card-input");
const addCardBtn = document.getElementById("add-card-btn");
const newCategoryInput = document.getElementById("new-category-input");
const addCategoryBtn = document.getElementById("add-category-btn");
const saveBtn = document.getElementById("save-btn");
const statusNode = document.getElementById("status");
const categoriesList = document.getElementById("categories-list");

function setStatus(message, type = "") {
  statusNode.textContent = message;
  statusNode.className = `status ${type}`.trim();
}

function getSelectedUser() {
  return userSelect.value;
}

function getSelectedCard() {
  return cardSelect.value;
}

function getCategoryInputs() {
  return Array.from(
    categoriesList.querySelectorAll('input[type="checkbox"]'),
  );
}

function getCategoryRows() {
  return Array.from(categoriesList.querySelectorAll("[data-category]"));
}

function renderCategoryList() {
  categoriesList.innerHTML = "";

  state.availableCategories.forEach((category) => {
    const row = document.createElement("div");
    row.className = "category-row";
    row.dataset.category = category;

    const label = document.createElement("label");
    label.className = "checkbox";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = category;
    input.disabled = true;

    const span = document.createElement("span");
    span.textContent = category;

    const percentInput = document.createElement("input");
    percentInput.type = "number";
    percentInput.min = "0";
    percentInput.max = "100";
    percentInput.step = "0.1";
    percentInput.placeholder = "0";
    percentInput.className = "percent-input";
    percentInput.disabled = true;

    input.addEventListener("change", () => {
      percentInput.disabled = !input.checked;
      if (!input.checked) {
        percentInput.value = "0";
      }
    });

    percentInput.addEventListener("input", () => {
      const value = Number(percentInput.value);
      if (Number.isFinite(value) && value > 0) {
        input.checked = true;
        percentInput.disabled = false;
      }
    });

    const suffix = document.createElement("span");
    suffix.className = "percent-suffix";
    suffix.textContent = "%";

    const percentWrap = document.createElement("div");
    percentWrap.className = "percent-wrap";
    percentWrap.append(percentInput, suffix);

    label.append(input, span);
    row.append(label, percentWrap);
    categoriesList.append(row);
  });
}

function fillUserOptions() {
  const current = getSelectedUser();
  userSelect.innerHTML = '<option value="">Выберите пользователя</option>';

  Object.keys(state.users)
    .sort((a, b) => a.localeCompare(b, "ru"))
    .forEach((user) => {
      const option = document.createElement("option");
      option.value = user;
      option.textContent = user;
      if (user === current) {
        option.selected = true;
      }
      userSelect.append(option);
    });
}

function fillCardOptions() {
  const user = getSelectedUser();
  const current = getSelectedCard();
  cardSelect.innerHTML = "";

  if (!user) {
    cardSelect.disabled = true;
    cardSelect.innerHTML = '<option value="">Сначала выберите пользователя</option>';
    syncCategoryInputs();
    return;
  }

  const cards = Object.keys(state.users[user] || {});
  cardSelect.disabled = false;

  if (cards.length === 0) {
    cardSelect.innerHTML = '<option value="">У пользователя пока нет карт</option>';
    syncCategoryInputs();
    return;
  }

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Выберите карту";
  cardSelect.append(placeholder);

  cards.sort((a, b) => a.localeCompare(b, "ru")).forEach((card) => {
    const option = document.createElement("option");
    option.value = card;
    option.textContent = card;
    if (card === current) {
      option.selected = true;
    }
    cardSelect.append(option);
  });

  syncCategoryInputs();
}

function syncCategoryInputs() {
  const user = getSelectedUser();
  const card = getSelectedCard();
  const categories = state.users[user]?.[card] || {};
  const enabled = Boolean(user && card);

  getCategoryRows().forEach((row) => {
    const checkbox = row.querySelector('input[type="checkbox"]');
    const percentInput = row.querySelector(".percent-input");
    const categoryName = row.dataset.category;
    const categoryState = categories[categoryName] || { enabled: false, percent: 0 };

    checkbox.disabled = !enabled;
    checkbox.checked = enabled ? Boolean(categoryState.enabled) : false;
    percentInput.disabled = !enabled || !checkbox.checked;
    percentInput.value = enabled ? String(categoryState.percent ?? 0) : "";
  });

  getCategoryInputs().forEach((input) => {
    input.disabled = !enabled;
  });

  saveBtn.disabled = !enabled;
}

async function loadState() {
  const response = await fetch("/api/state");
  if (!response.ok) {
    throw new Error("Не удалось загрузить данные");
  }

  const payload = await response.json();
  state.users = payload.users;
  state.availableCategories = payload.available_categories;

  renderCategoryList();
  fillUserOptions();
  fillCardOptions();
  syncCategoryInputs();
}

async function addUser() {
  const name = newUserInput.value.trim();
  if (!name) {
    setStatus("Введите имя пользователя", "error");
    return;
  }

  const response = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const payload = await response.json();

  if (!response.ok) {
    setStatus(payload.detail || "Не удалось добавить пользователя", "error");
    return;
  }

  state.users = payload.users;
  newUserInput.value = "";
  fillUserOptions();
  userSelect.value = name;
  fillCardOptions();
  setStatus("Пользователь добавлен", "success");
}

async function addCard() {
  const userName = getSelectedUser();
  const cardName = newCardInput.value.trim();

  if (!userName) {
    setStatus("Сначала выберите пользователя", "error");
    return;
  }
  if (!cardName) {
    setStatus("Введите название карты", "error");
    return;
  }

  const response = await fetch("/api/cards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: userName, card_name: cardName }),
  });
  const payload = await response.json();

  if (!response.ok) {
    setStatus(payload.detail || "Не удалось добавить карту", "error");
    return;
  }

  state.users = payload.users;
  newCardInput.value = "";
  fillCardOptions();
  cardSelect.value = cardName;
  syncCategoryInputs();
  setStatus("Карта добавлена", "success");
}

async function saveCashback() {
  const userName = getSelectedUser();
  const cardName = getSelectedCard();

  if (!userName || !cardName) {
    setStatus("Выберите пользователя и карту", "error");
    return;
  }

  const categories = Object.fromEntries(
    getCategoryRows().map((row) => {
      const categoryName = row.dataset.category;
      const checkbox = row.querySelector('input[type="checkbox"]');
      const percentInput = row.querySelector(".percent-input");
      const rawPercent = percentInput.value.trim();
      const percent = rawPercent === "" ? 0 : Number(rawPercent);

      return [categoryName, {
        enabled: checkbox.checked,
        percent: Number.isFinite(percent) ? percent : 0,
      }];
    }),
  );

  const response = await fetch("/api/cashback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_name: userName,
      card_name: cardName,
      categories,
    }),
  });
  const payload = await response.json();

  if (!response.ok) {
    setStatus(payload.detail || "Не удалось сохранить данные", "error");
    return;
  }

  state.users = payload.users;
  syncCategoryInputs();
  setStatus("Категории сохранены в JSON", "success");
}

async function addCategory() {
  const name = newCategoryInput.value.trim();
  if (!name) {
    setStatus("Введите название категории", "error");
    return;
  }

  const response = await fetch("/api/categories", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const payload = await response.json();

  if (!response.ok) {
    setStatus(payload.detail || "Не удалось добавить категорию", "error");
    return;
  }

  state.users = payload.users;
  state.availableCategories = payload.available_categories;
  newCategoryInput.value = "";
  renderCategoryList();
  syncCategoryInputs();
  setStatus("Категория добавлена", "success");
}

userSelect.addEventListener("change", () => {
  fillCardOptions();
  syncCategoryInputs();
  setStatus("");
});

cardSelect.addEventListener("change", () => {
  syncCategoryInputs();
  setStatus("");
});

addUserBtn.addEventListener("click", addUser);
addCardBtn.addEventListener("click", addCard);
addCategoryBtn.addEventListener("click", addCategory);
saveBtn.addEventListener("click", saveCashback);

loadState().catch((error) => {
  console.error(error);
  setStatus("Ошибка загрузки данных", "error");
});
