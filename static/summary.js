const summaryState = {
  users: {},
};

const summaryUserSelect = document.getElementById("summary-user-select");
const summaryOutput = document.getElementById("summary-output");

function formatPercent(value) {
  const numericValue = Number(value) || 0;
  return Number.isInteger(numericValue)
    ? String(numericValue)
    : numericValue.toFixed(1);
}

function fillSummaryUsers() {
  const current = summaryUserSelect.value;
  summaryUserSelect.innerHTML = '<option value="">Выберите пользователя</option>';

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
    });
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

summaryUserSelect.addEventListener("change", renderSummary);

loadSummaryState().catch((error) => {
  console.error(error);
  summaryOutput.innerHTML = '<p class="summary__empty">Ошибка загрузки данных.</p>';
});
