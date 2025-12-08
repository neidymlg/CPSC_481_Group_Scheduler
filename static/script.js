// Use same origin as your Flask app (Codespaces-safe)
const API_URL = window.location.origin + "/schedule";

const userInput = document.getElementById("user-input");
const choreInput = document.getElementById("chore-input");
const addUserBtn = document.getElementById("add-user-btn");
const addChoreBtn = document.getElementById("add-chore-btn");
const usersListEl = document.getElementById("users-list");
const choresListEl = document.getElementById("chores-list");
const generateBtn = document.getElementById("generate-btn");
const errorMessage = document.getElementById("error-message");

const inputView = document.getElementById("input-view");
const scheduleView = document.getElementById("schedule-view");
const scheduleOutput = document.getElementById("schedule-output");
const backBtn = document.getElementById("back-btn");
const qualityOutput = document.getElementById("quality-output");

const difficultyGrid = document.getElementById("difficulty-grid");
const preferencesCard = document.getElementById("preferences-card");
const prefUserSelect = document.getElementById("pref-user-select");
const lovedChips = document.getElementById("loved-chips");
const hatedChips = document.getElementById("hated-chips");
const lovedSelect = document.getElementById("loved-select");
const hatedSelect = document.getElementById("hated-select");

//allow pressing 'Enter' to add a user/chore
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();      //prevent form submit/page reload
    addUserBtn.click();
  }
});

choreInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    addChoreBtn.click();
  }
});

// Stored data
let users = [];
let chores = [];
let difficulties = {};
let loved = {};
let hated = {};

function showError(msg) {
  errorMessage.textContent = msg;
  errorMessage.style.display = "block";
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.style.display = "none";
}

function ensureDifficultyDefaults() {
  users.forEach((u) => {
    if (!difficulties[u.name]) {
      difficulties[u.name] = {};
    }
    chores.forEach((c) => {
      if (difficulties[u.name][c.name] === undefined) {
        difficulties[u.name][c.name] = 0; // default difficulty
      }
    });
  });
}

function syncPreferencesWithUsersAndChores() {
  const userNames = users.map((u) => u.name);
  const choreNames = chores.map((c) => c.name);

  //make sure each existing user has entries
  userNames.forEach((name) => {
    if (!loved[name]) loved[name] = [];
    if (!hated[name]) hated[name] = [];
  });

  //remove from deleted users
  Object.keys(loved).forEach((name) => {
    if (!userNames.includes(name)) delete loved[name];
  });
  Object.keys(hated).forEach((name) => {
    if (!userNames.includes(name)) delete hated[name];
  });

  //remove deleted chores
  const cleanList = (arr) => arr.filter((chore) => choreNames.includes(chore));
  Object.keys(loved).forEach((name) => {
    loved[name] = cleanList(loved[name]);
  });
  Object.keys(hated).forEach((name) => {
    hated[name] = cleanList(hated[name]);
  });
}

function createPrefChip(choreName, type, userName) {
  const chip = document.createElement("span");
  chip.className = `chip ${type}-chip`;
  chip.textContent = choreName;

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "chip-remove";
  btn.textContent = "×";
  btn.addEventListener("click", () => {
    if (type === "loved") {
      loved[userName] = loved[userName].filter((c) => c !== choreName);
    } else {
      hated[userName] = hated[userName].filter((c) => c !== choreName);
    }
    renderPreferences();
  });

  chip.appendChild(btn);
  return chip;
}

function renderUsers() {
  usersListEl.innerHTML = "";
  users.forEach((u, idx) => {
    const li = document.createElement("li");
    li.textContent = `${u.name} (max: ${u.max_chores})`;
    li.title = "Click to remove";

    li.addEventListener("click", () => {
      const removed = users.splice(idx, 1)[0];
      if (removed && difficulties[removed.name]) {
        delete difficulties[removed.name];
      }
      renderUsers();
      renderDifficultyMatrix();
      renderPreferences();
    });

    usersListEl.appendChild(li);
  });
}

function renderChores() {
  choresListEl.innerHTML = "";
  chores.forEach((c, idx) => {
    const li = document.createElement("li");
    li.textContent = `${c.name} (amount: ${c.amount})`;
    li.title = "Click to remove";

    li.addEventListener("click", () => {
      const removed = chores.splice(idx, 1)[0];
      if (removed) {
        // remove this chore's difficulty entry from every user
        Object.keys(difficulties).forEach((userName) => {
          if (difficulties[userName] && difficulties[userName][removed.name] !== undefined) {
            delete difficulties[userName][removed.name];
          }
        });
      }
      renderChores();
      renderDifficultyMatrix();
      renderPreferences();
    });

    choresListEl.appendChild(li);
  });
}

// Add user: "Name, maxChores"
addUserBtn.addEventListener("click", () => {
  clearError();
  const text = userInput.value.trim();
  if (!text) return;

  const parts = text.split(",");
  if (parts.length < 2) {
    showError("User format must be: Name, maxChores (example: User_1, 5)");
    return;
  }

  const name = parts[0].trim();
  const maxStr = parts[1].trim();
  const max = Number(maxStr);

  if (!name || Number.isNaN(max)) {
    showError("User format must be: Name, maxChores (example: User_1, 5)");
    return;
  }

  users.push({ name, max_chores: max });

  // Clear and refocus the text box
  userInput.value = "";
  userInput.focus();

  renderUsers();
  renderDifficultyMatrix();
  renderPreferences();
});

// Add chore: "Name, amount"
addChoreBtn.addEventListener("click", () => {
  clearError();
  const text = choreInput.value.trim();
  if (!text) return;

  const parts = text.split(",");
  if (parts.length < 2) {
    showError("Chore format must be: Name, amount (example: dishes, 3)");
    return;
  }

  const name = parts[0].trim();
  const amtStr = parts[1].trim();
  const amt = Number(amtStr);

  if (!name || Number.isNaN(amt)) {
    showError("Chore format must be: Name, amount (example: dishes, 3)");
    return;
  }

  chores.push({ name, amount: amt });

  // Clear and refocus the text box
  choreInput.value = "";
  choreInput.focus();

  renderChores();
  renderDifficultyMatrix();
  renderPreferences();
});

// Generate schedule -> call backend, then show schedule view
generateBtn.addEventListener("click", async () => {
  clearError();

  if (users.length === 0 || chores.length === 0) {
    showError("Please add at least one user and one chore.");
    return;
  }

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ users, chores, difficulties, loved,hated }),
    });

    if (!res.ok) {
      throw new Error(`Server responded with status ${res.status}`);
    }

    const data = await res.json();
    renderSchedule(data.schedule || {}, data.quality);

    // Switch "page"
    inputView.style.display = "none";
    scheduleView.style.display = "block";
  } catch (err) {
    showError("Error contacting server: " + err.message);
  }
});

prefUserSelect.addEventListener("change", () => {
  renderPreferences();
});

lovedSelect.addEventListener("change", () => {
  const userName = prefUserSelect.value;
  const choreName = lovedSelect.value;
  if (!userName || !choreName) return;

  if (!loved[userName]) loved[userName] = [];
  if (!loved[userName].includes(choreName)) {
    loved[userName].push(choreName);
  }
  lovedSelect.value = "";
  renderPreferences();
});

hatedSelect.addEventListener("change", () => {
  const userName = prefUserSelect.value;
  const choreName = hatedSelect.value;
  if (!userName || !choreName) return;

  if (!hated[userName]) hated[userName] = [];
  if (!hated[userName].includes(choreName)) {
    hated[userName].push(choreName);
  }
  hatedSelect.value = "";
  renderPreferences();
});


function renderDifficultyMatrix() {
  difficultyGrid.innerHTML = "";

  if (users.length === 0 || chores.length === 0) {
    difficultyGrid.innerHTML =
      "<p class='hint'>Add at least one user and one chore to set difficulties.</p>";
    return;
  }

  ensureDifficultyDefaults();

  const table = document.createElement("table");
  table.classList.add("difficulty-table");

  //header row: corner+chore names
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");

  const corner = document.createElement("th");
  corner.textContent = "User / Chore";
  headRow.appendChild(corner);

  chores.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = c.name;
    headRow.appendChild(th);
  });

  thead.appendChild(headRow);
  table.appendChild(thead);

  //body - one row per user
  const tbody = document.createElement("tbody");

  users.forEach((u) => {
    const row = document.createElement("tr");

    const userCell = document.createElement("th");
    userCell.textContent = u.name;
    row.appendChild(userCell);

    chores.forEach((c) => {
      const cell = document.createElement("td");

      const input = document.createElement("input");
      input.type = "number";
      input.min = "-10";
      input.max = "10";
      input.classList.add("difficulty-input");

      const currentVal =
        difficulties[u.name] && difficulties[u.name][c.name] !== undefined
          ? difficulties[u.name][c.name]
          : 0;
      input.value = currentVal;

      input.addEventListener("change", () => {
        let val = parseInt(input.value, 10);
        if (Number.isNaN(val)) val = 0;
        if (val < -10) val = -10;
        if (val > 10) val = 10;
        input.value = val;

        if (!difficulties[u.name]) difficulties[u.name] = {};
        difficulties[u.name][c.name] = val;
      });

      cell.appendChild(input);
      row.appendChild(cell);
    });

    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  difficultyGrid.appendChild(table);
}

function renderPreferences() {
  preferencesCard.style.display = "block";

  syncPreferencesWithUsersAndChores();

  let selectedName = prefUserSelect.value;
  
  //populate user dropdown
  prefUserSelect.innerHTML = "";
  if (users.length === 0 || chores.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = users.length === 0
      ? "Add a user to edit preferences"
      : "Add a chore to edit preferences";
    prefUserSelect.appendChild(opt);
    lovedChips.innerHTML = "";
    hatedChips.innerHTML = "";
    lovedSelect.innerHTML = '<option value="">+ Add loved chore…</option>';
    hatedSelect.innerHTML = '<option value="">+ Add hated chore…</option>';
    return;
  }

  if (!users.some((u) => u.name === selectedName)) {
    selectedName = users[0].name;
  }

  users.forEach((u) => {
    const opt = document.createElement("option");
    opt.value = u.name;
    opt.textContent = u.name;
    if (u.name === selectedName) opt.selected = true;
    prefUserSelect.appendChild(opt);
  });

  const currentUser = selectedName;
  const userLoved = loved[currentUser] || [];
  const userHated = hated[currentUser] || [];

  //render chips
  lovedChips.innerHTML = "";
  userLoved.forEach((choreName) => {
    const chip = createPrefChip(choreName, "loved", currentUser);
    lovedChips.appendChild(chip);
  });

  hatedChips.innerHTML = "";
  userHated.forEach((choreName) => {
    const chip = createPrefChip(choreName, "hated", currentUser);
    hatedChips.appendChild(chip);
  });

  //populate dropdowns for chores not already in list
  const availableForLoved = chores
    .map((c) => c.name)
    .filter((name) => !userLoved.includes(name));

  const availableForHated = chores
    .map((c) => c.name)
    .filter((name) => !userHated.includes(name));

  lovedSelect.innerHTML = '<option value="">+ Add loved chore…</option>';
  availableForLoved.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    lovedSelect.appendChild(opt);
  });

  hatedSelect.innerHTML = '<option value="">+ Add hated chore…</option>';
  availableForHated.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    hatedSelect.appendChild(opt);
  });
}

// Render schedule table
function renderSchedule(schedule, quality) {
  //added quality summary
  qualityOutput.innerHTML = "";

  if (quality) {
    const scoreText = `${quality.score}/100 ${quality.score_results}`;

    qualityOutput.innerHTML = `
      <h2>Schedule Quality</h2>
      <p><strong>Quality Score:</strong> ${scoreText}</p>
      <p><strong>Situation:</strong> ${quality.situation}</p>
      <p><strong>Capacity Ratio:</strong> ${quality.capacity_ratio}x</p>
    `;
  }

  //workload
  if (quality && quality.user_loads) {
  const loads = quality.user_loads;

  qualityOutput.innerHTML += `<hr class="workload-divider">`;

  let workloadsHtml = `<h3>Individual Workloads</h3><div class="workload-section">`;

  Object.entries(loads).forEach(([name, info], index, arr) => {
    workloadsHtml += `
      <div class="workload-entry">
        <p class="workload-line">
          <strong>${name}:</strong>
          ${info.assigned}/${info.capacity} chores
          (${info.percentage}% capacity, ratio=${info.ratio})
        </p>
      </div>
    `;

    //add separator except after the last user
    if (index < arr.length - 1) {
        workloadsHtml += `<hr class="workload-separator">`;
    }
});

  workloadsHtml += `</div>`;

  qualityOutput.innerHTML += workloadsHtml;
}


  const table = document.createElement("table");

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  const thUser = document.createElement("th");
  thUser.textContent = "User";
  const thChores = document.createElement("th");
  thChores.textContent = "Chores";

  headRow.appendChild(thUser);
  headRow.appendChild(thChores);
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  Object.entries(schedule).forEach(([user, choresArr]) => {
    const row = document.createElement("tr");
    const userCell = document.createElement("td");
    userCell.textContent = user;

    const choresCell = document.createElement("td");
    choresCell.textContent = (choresArr || []).join(", ");

    row.appendChild(userCell);
    row.appendChild(choresCell);
    tbody.appendChild(row);
  });

  table.appendChild(tbody);

  scheduleOutput.innerHTML = "";

  //add title for schedule for clear separation
  const scheduleTitle = document.createElement("h2");
  scheduleTitle.textContent = "Schedule";
  scheduleOutput.appendChild(scheduleTitle);

  scheduleOutput.appendChild(table);
}

// Back button -> return to input view
backBtn.addEventListener("click", () => {
  scheduleView.style.display = "none";
  inputView.style.display = "block";
});

renderDifficultyMatrix();
renderPreferences();