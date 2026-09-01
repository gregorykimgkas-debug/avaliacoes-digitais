const elements = {
  assessmentCards: document.querySelector("#assessmentCards"),
  assessmentFilter: document.querySelector("#assessmentFilter"),
  refreshButton: document.querySelector("#refreshButton"),
  assessmentBars: document.querySelector("#assessmentBars"),
  resultsTable: document.querySelector("#resultsTable"),
};

const formatDate = value => new Intl.DateTimeFormat("pt-BR").format(new Date(value));
const formatPercent = value => `${Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Falha ao carregar ${url}`);
  return response.json();
}

function renderAssessments(items) {
  elements.assessmentCards.innerHTML = items.map(item => `
    <article class="assessment-card">
      <span class="code">${item.code}</span>
      <h3>${item.title}</h3>
      <p>${item.equipment} · Nota mínima ${formatPercent(item.passing_score)}</p>
      ${item.form_url
        ? `<a class="button" href="${item.form_url}" target="_blank" rel="noreferrer">Abrir Microsoft Forms ↗</a>`
        : `<span class="button disabled" aria-disabled="true">Link público em preparação</span>`}
    </article>
  `).join("");

  elements.assessmentFilter.insertAdjacentHTML("beforeend", items.map(item =>
    `<option value="${item.code}">${item.title}</option>`
  ).join(""));
}

function renderDashboard(data) {
  const { summary, by_assessment: grouped, submissions } = data;
  document.querySelector("#responsesKpi").textContent = summary.responses;
  document.querySelector("#averageKpi").textContent = formatPercent(summary.average);
  document.querySelector("#approvalKpi").textContent = formatPercent(summary.approval_rate);
  document.querySelector("#approvedKpi").textContent = summary.approved;
  document.querySelector("#statusDetail").textContent = `aprovados · ${summary.failed} reprovados`;
  document.querySelector("#tableCount").textContent = `${submissions.length} registros`;

  elements.assessmentBars.innerHTML = grouped.length ? grouped.map(item => `
    <div class="bar-row">
      <span>${item.title}</span>
      <span class="track"><i style="width:${Math.min(item.average, 100)}%"></i></span>
      <strong>${formatPercent(item.average)}</strong>
    </div>
  `).join("") : `<p class="loading">Nenhum resultado para este filtro.</p>`;

  const donut = document.querySelector("#approvalDonut");
  donut.style.setProperty("--approval", `${summary.approval_rate}%`);
  donut.querySelector("strong").textContent = formatPercent(summary.approval_rate);

  elements.resultsTable.innerHTML = submissions.map(item => `
    <tr>
      <td>${item.participant}</td><td>${item.assessment}</td><td>${item.client}</td>
      <td>${item.instructor}</td><td><strong>${formatPercent(item.score)}</strong></td>
      <td><span class="badge ${item.status === "Aprovado" ? "approved" : "failed"}">${item.status}</span></td>
      <td>${formatDate(item.submitted_at)}</td>
    </tr>
  `).join("");
}

async function loadDashboard() {
  elements.refreshButton.disabled = true;
  const code = elements.assessmentFilter.value;
  try {
    renderDashboard(await fetchJson(`/api/dashboard${code ? `?assessment=${encodeURIComponent(code)}` : ""}`));
  } catch (error) {
    elements.assessmentBars.innerHTML = `<p class="error">Não foi possível carregar os indicadores.</p>`;
  } finally {
    elements.refreshButton.disabled = false;
  }
}

async function init() {
  try {
    renderAssessments(await fetchJson("/api/assessments"));
    await loadDashboard();
  } catch (error) {
    elements.assessmentCards.innerHTML = `<p class="error">A API não respondeu. Tente novamente em instantes.</p>`;
  }
}

elements.assessmentFilter.addEventListener("change", loadDashboard);
elements.refreshButton.addEventListener("click", loadDashboard);
init();

