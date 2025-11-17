const imageInput = document.getElementById("imageInput");
const checkButton = document.getElementById("checkButton");
const previewContainer = document.getElementById("preview");
const resultContainer = document.getElementById("result");

let selectedFile = null;

function resetResult() {
  resultContainer.className = "result";
  resultContainer.classList.remove("visible", "safe", "unsafe", "error");
  resultContainer.textContent = "";
}

function showPreview(file) {
  previewContainer.innerHTML = "";
  if (!file) {
    previewContainer.innerHTML = "<p>No image selected.</p>";
    return;
  }

  const reader = new FileReader();
  reader.onload = (event) => {
    const img = document.createElement("img");
    img.src = event.target.result;
    img.alt = "Selected preview";
    previewContainer.innerHTML = "";
    previewContainer.appendChild(img);
  };
  reader.readAsDataURL(file);
}

function setLoading(isLoading) {
  checkButton.disabled = isLoading;
  checkButton.textContent = isLoading ? "Checking..." : "Check Image";
}

function formatResult(result) {
  const { status, reason, confidence, categories, category_scores } = result;
  const statusClass =
    status === "Safe" ? "safe" : status === "Error" ? "error" : "unsafe";
  resultContainer.className = `result visible ${statusClass}`;

  const details = document.createElement("div");
  details.innerHTML = `
    <strong>Status:</strong> ${status}<br />
    <strong>Reason:</strong> ${reason}<br />
    <strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%
  `;

  const meta = document.createElement("pre");
  meta.textContent = JSON.stringify(
    { categories, category_scores },
    null,
    2
  );

  resultContainer.innerHTML = "";
  resultContainer.appendChild(details);
  resultContainer.appendChild(meta);
}

async function submitImage(file) {
  if (!file) {
    resultContainer.className = "result visible error";
    resultContainer.textContent = "Please select an image before checking.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    setLoading(true);
    resetResult();

    const response = await fetch("/check-image", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || "Unexpected server error.";
      resultContainer.className = "result visible error";
      resultContainer.textContent = message;
      return;
    }

    const result = await response.json();
    formatResult(result);
  } catch (error) {
    resultContainer.className = "result visible error";
    resultContainer.textContent = error.message || "Network error";
  } finally {
    setLoading(false);
  }
}

imageInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  selectedFile = file ?? null;
  showPreview(selectedFile);
  resetResult();
});

checkButton.addEventListener("click", () => submitImage(selectedFile));

showPreview(null);
