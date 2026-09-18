const form = document.getElementById("trouble-form");
const formMessage = document.getElementById("form-message");
const analyzeBtn = document.getElementById("analyze-btn");
const resultCard = document.getElementById("result-card");
const resultContent = document.getElementById("result-content");
const loading = document.getElementById("loading");
const retryBtn = document.getElementById("retry-btn");

let lastPayload = null;

function showMessage(message, status = "error") {
  formMessage.textContent = message;
  formMessage.className = `message status-${status}`;
}

function getErrorMessage(status, data) {
  if (status === 400 || status === 422) {
    return data.detail || data.error || "입력 내용을 확인해주세요.";
  }
  if (status === 429) {
    return "요청이 많습니다. 잠시 후 다시 시도해주세요.";
  }
  if (status >= 500) {
    return "AI 서버에 일시적인 문제가 있습니다. 다시 시도해주세요.";
  }
  return data.detail || data.error || "AI 서버 연결 중 오류가 발생했습니다.";
}

async function requestAnalysis(payload) {
  const maxRetries = 2;

  for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        if (data.success !== true || typeof data.result !== "string" || !data.result.trim()) {
          throw new Error("서버 응답 형식이 올바르지 않습니다.");
        }
        return data.result.trim();
      }

      const retryable = response.status === 408 || response.status === 429 || response.status >= 500;
      if (!retryable || attempt === maxRetries) {
        throw new Error(getErrorMessage(response.status, data));
      }
    } catch (error) {
      const retryable = error.name === "AbortError" || error instanceof TypeError;
      if (!retryable || attempt === maxRetries) {
        throw error;
      }
    } finally {
      clearTimeout(timeoutId);
    }

    await new Promise((resolve) => setTimeout(resolve, 700 * 2 ** attempt));
  }

  throw new Error("AI 서버 연결 중 오류가 발생했습니다.");
}

async function analyze(payload) {
  analyzeBtn.disabled = true;
  retryBtn.classList.add("hidden");
  resultCard.classList.remove("empty");
  resultCard.setAttribute("aria-busy", "true");
  resultCard.classList.remove("status-success", "status-error");
  resultContent.innerHTML = "";
  loading.classList.remove("hidden");
  showMessage("분석 요청을 처리하고 있습니다.", "loading");

  try {
    const result = await requestAnalysis(payload);
    const pre = document.createElement("pre");
    pre.className = "result-text";
    pre.textContent = result;
    resultContent.appendChild(pre);
    resultCard.classList.add("status-success");
    showMessage("분석이 완료되었습니다.", "success");
    document.getElementById("result").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    const message =
      error.name === "AbortError"
        ? "AI 응답이 지연되고 있습니다. 다시 시도해주세요."
        : error.message || "AI 서버 연결 중 오류가 발생했습니다. 다시 시도해주세요.";
    const p = document.createElement("p");
    p.className = "message";
    p.textContent = message;
    resultContent.appendChild(p);
    resultCard.classList.add("status-error");
    retryBtn.classList.remove("hidden");
    showMessage(message);
  } finally {
    loading.classList.add("hidden");
    resultCard.setAttribute("aria-busy", "false");
    analyzeBtn.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("");

  const payload = {
    equipmentName: document.getElementById("equipmentName").value.trim(),
    equipmentType: document.getElementById("equipmentType").value.trim(),
    alarmCode: document.getElementById("alarmCode").value.trim(),
    symptom: document.getElementById("symptom").value.trim(),
    context: document.getElementById("context").value.trim(),
  };

  if (!payload.symptom) {
    showMessage("문제 증상을 입력해주세요.");
    document.getElementById("symptom").focus();
    return;
  }

  lastPayload = payload;
  await analyze(payload);
});

retryBtn.addEventListener("click", async () => {
  if (lastPayload) {
    await analyze(lastPayload);
  }
});

form.addEventListener("reset", () => {
  lastPayload = null;
  showMessage("");
  resultCard.classList.add("empty");
  resultCard.classList.remove("status-success", "status-error");
  retryBtn.classList.add("hidden");
  resultContent.innerHTML = '<p class="placeholder">아직 분석 결과가 없습니다.</p>';
});
