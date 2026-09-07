const form = document.getElementById("trouble-form");
const formMessage = document.getElementById("form-message");
const analyzeBtn = document.getElementById("analyze-btn");
const resultCard = document.getElementById("result-card");
const resultContent = document.getElementById("result-content");
const loading = document.getElementById("loading");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "";

  const payload = {
    equipmentName: document.getElementById("equipmentName").value.trim(),
    equipmentType: document.getElementById("equipmentType").value.trim(),
    alarmCode: document.getElementById("alarmCode").value.trim(),
    symptom: document.getElementById("symptom").value.trim(),
    context: document.getElementById("context").value.trim(),
  };

  if (!payload.symptom) {
    formMessage.textContent = "문제 증상을 입력해주세요.";
    document.getElementById("symptom").focus();
    return;
  }

  analyzeBtn.disabled = true;
  resultCard.classList.remove("empty");
  resultContent.innerHTML = "";
  loading.classList.remove("hidden");

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch("/api/ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "AI 서버 연결 중 오류가 발생했습니다.");
    }

    resultContent.innerHTML = "";
    const pre = document.createElement("pre");
    pre.className = "result-text";
    pre.textContent = data.result || "분석 결과를 생성하지 못했습니다.";
    resultContent.appendChild(pre);

    document.getElementById("result").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    const message =
      error.name === "AbortError"
        ? "AI 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
        : error.message || "AI 서버 연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";

    resultContent.innerHTML = "";
    const p = document.createElement("p");
    p.className = "message";
    p.textContent = message;
    resultContent.appendChild(p);
  } finally {
    loading.classList.add("hidden");
    analyzeBtn.disabled = false;
  }
});

form.addEventListener("reset", () => {
  formMessage.textContent = "";
  resultCard.classList.add("empty");
  resultContent.innerHTML = '<p class="placeholder">아직 분석 결과가 없습니다.</p>';
});
