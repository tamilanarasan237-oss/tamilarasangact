const task = document.getElementById("task");
const inputText = document.getElementById("inputText");
const options = document.getElementById("options");
const submitBtn = document.getElementById("submitBtn");
const result = document.getElementById("result");
const statusEl = document.getElementById("status");
const copyBtn = document.getElementById("copyBtn");

let lastResultText = "";

function optionMarkup() {
  const type = task.value;

  if (type === "explain" || type === "learn") {
    return `
      <div class="option-group">
        <label for="level">Level</label>
        <select id="level">
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
      ${type === "learn" ? `
      <div class="option-group">
        <label for="duration">Weeks</label>
        <input id="duration" type="number" min="1" max="52" value="8">
      </div>` : ""}
    `;
  }

  if (type === "quiz") {
    return `
      <div class="option-group">
        <label for="numQuestions">Questions</label>
        <select id="numQuestions">
          <option value="3">3</option>
          <option value="5">5</option>
          <option value="10">10</option>
        </select>
      </div>
    `;
  }

  if (type === "summarize") {
    return `
      <div class="option-group">
        <label for="maxWords">Max words</label>
        <input id="maxWords" type="number" min="30" max="1000" value="150">
      </div>
    `;
  }

  return "";
}

function updatePlaceholder() {
  const placeholders = {
    qa: "Example: Which is the largest ocean?",
    explain: "Example: Pythagoras theorem",
    quiz: "Paste a passage or notes to turn into MCQs...",
    summarize: "Paste the educational passage you want summarized...",
    learn: "Example: SQL"
  };
  inputText.placeholder = placeholders[task.value];
  options.innerHTML = optionMarkup();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResponse(data) {
  if (data.error) {
    result.classList.add("error");
    result.innerHTML = `<pre>${escapeHtml(data.error)}</pre>`;
    lastResultText = data.error;
    copyBtn.disabled = false;
    return;
  }

  result.classList.remove("error");

  if (task.value === "quiz" && Array.isArray(data.questions)) {
    let html = `<h2>${escapeHtml(data.title)}</h2>`;
    data.questions.forEach((q, i) => {
      html += `
        <div class="quiz-question">
          <h3>${i + 1}. ${escapeHtml(q.question)}</h3>
          ${q.options.map((opt, idx) => `
            <div class="quiz-option">
              <strong>${String.fromCharCode(65 + idx)}.</strong>
              ${escapeHtml(opt)}
            </div>
          `).join("")}
          <details>
            <summary>Show answer</summary>
            <p><strong>Correct:</strong> ${escapeHtml(q.correct_answer)}</p>
            <p>${escapeHtml(q.explanation || "")}</p>
          </details>
        </div>
      `;
    });
    result.innerHTML = html;
    lastResultText = JSON.stringify(data, null, 2);
  } else {
    const text =
      data.answer ??
      data.summary ??
      data.learning_path ??
      JSON.stringify(data, null, 2);

    result.innerHTML = `<pre>${escapeHtml(text)}</pre>`;
    lastResultText = text;
  }

  copyBtn.disabled = false;
}

async function runTask() {
  const value = inputText.value.trim();

  if (!value) {
    statusEl.textContent = "Please enter some text first.";
    return;
  }

  submitBtn.disabled = true;
  copyBtn.disabled = true;
  statusEl.textContent = "EduGenie is thinking...";
  result.classList.remove("error");
  result.innerHTML = `<div class="empty-state"><span>⏳</span><p>Generating your result...</p></div>`;

  let endpoint = "";
  let body = {};

  switch (task.value) {
    case "qa":
      endpoint = "/qa";
      body = { question: value };
      break;
    case "explain":
      endpoint = "/explain";
      body = {
        topic: value,
        level: document.getElementById("level").value
      };
      break;
    case "quiz":
      endpoint = "/quiz";
      body = {
        text: value,
        num_questions: Number(document.getElementById("numQuestions").value)
      };
      break;
    case "summarize":
      endpoint = "/summarize";
      body = {
        text: value,
        max_words: Number(document.getElementById("maxWords").value)
      };
      break;
    case "learn":
      endpoint = "/learn/recommendations";
      body = {
        topic: value,
        level: document.getElementById("level").value,
        duration_weeks: Number(document.getElementById("duration").value)
      };
      break;
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await response.json();

    if (!response.ok && !data.error) {
      data.error = `Request failed with HTTP ${response.status}.`;
    }

    renderResponse(data);
    statusEl.textContent = data.error ? "Request completed with an error." : "Done.";
  } catch (error) {
    renderResponse({ error: `Could not reach the backend: ${error.message}` });
    statusEl.textContent = "Connection error.";
  } finally {
    submitBtn.disabled = false;
  }
}

task.addEventListener("change", updatePlaceholder);
submitBtn.addEventListener("click", runTask);

copyBtn.addEventListener("click", async () => {
  if (!lastResultText) return;
  await navigator.clipboard.writeText(lastResultText);
  statusEl.textContent = "Result copied.";
});

updatePlaceholder();
