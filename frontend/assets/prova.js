const code = new URLSearchParams(window.location.search).get("code") || window.location.pathname.split("/").pop();

const els = {
  title: document.querySelector("#examTitle"),
  subtitle: document.querySelector("#examSubtitle"),
  questions: document.querySelector("#examQuestions"),
  form: document.querySelector("#examForm"),
  submit: document.querySelector("#submitButton"),
  result: document.querySelector("#examResult"),
  name: document.querySelector("#participantName"),
};

let currentExam = null;

function renderQuestions(exam) {
  els.title.textContent = exam.title;
  els.subtitle.textContent = `${exam.equipment} · Nota mínima para aprovação: ${exam.passing_score}% · ${exam.questions.length} perguntas`;
  els.questions.innerHTML = exam.questions.map(q => `
    <fieldset class="exam-question">
      <legend>${q.order}. ${q.text}</legend>
      ${q.options.map((opt, idx) => `
        <label class="exam-option">
          <input type="radio" name="q${q.id}" value="${idx}" required>
          <span>${opt}</span>
        </label>
      `).join("")}
    </fieldset>
  `).join("");
}

async function loadExam() {
  try {
    const response = await fetch(`/api/assessments/${encodeURIComponent(code)}/exam`);
    if (!response.ok) throw new Error("not found");
    currentExam = await response.json();
    renderQuestions(currentExam);
  } catch (error) {
    els.title.textContent = "Prova não encontrada";
    els.subtitle.textContent = "Esta avaliação ainda não possui prova interna disponível.";
    els.form.hidden = true;
  }
}

els.form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!currentExam) return;
  els.submit.disabled = true;

  const answers = currentExam.questions.map(q => {
    const checked = els.form.querySelector(`input[name="q${q.id}"]:checked`);
    return { question_id: q.id, selected_index: Number(checked.value) };
  });

  try {
    const response = await fetch(`/api/assessments/${encodeURIComponent(code)}/exam`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        participant_name: els.name.value,
        answers,
      }),
    });
    if (!response.ok) throw new Error("falha ao enviar");
    const result = await response.json();

    els.form.hidden = true;
    els.result.hidden = false;
    els.result.innerHTML = `
      <article class="panel ${result.status === "Aprovado" ? "approved" : "failed"}">
        <h3>${result.status}</h3>
        <p>Você acertou <strong>${result.correct}</strong> de <strong>${result.total}</strong> perguntas.</p>
        <p class="score">${result.score}%</p>
        <a class="button secondary" href="/#painel">Ver painel de indicadores</a>
      </article>
    `;
  } catch (error) {
    alert("Não foi possível enviar a prova. Tente novamente.");
  } finally {
    els.submit.disabled = false;
  }
});

loadExam();
