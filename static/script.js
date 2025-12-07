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

function showError(msg) {
  errorMessage.textContent = msg;
  errorMessage.style.display = "block";
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.style.display = "none";
}

function renderUsers() {
  usersListEl.innerHTML = "";
  users.forEach((u, idx) => {
    const li = document.createElement("li");
    li.textContent = `${u.name} (max: ${u.max_chores})`;
    li.title = "Click to remove";

    li.addEventListener("click", () => {
      users.splice(idx, 1);
      renderUsers();
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
      chores.splice(idx, 1);
      renderChores();
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
      body: JSON.stringify({ users, chores }),
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
