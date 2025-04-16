document.addEventListener("DOMContentLoaded", () => {
  // Toggle sticky header styling on checkbox change
  const toggleSticky = document.getElementById("toggle-sticky");
  const wrapper = document.querySelector(".sticky-wrapper");
  toggleSticky?.addEventListener("change", () => {
    wrapper.classList.toggle("sticky-enabled", toggleSticky.checked);
  });

  // Scroll to code line and apply highlight glow when "See in Code" is clicked
  document.querySelectorAll(".see-code").forEach(btn => {
    btn.addEventListener("click", () => {
      const line = btn.dataset.line;
      const row = document.getElementById(`line-${line}`);
      if (!row) return;
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      const span = row.querySelector("td.linenos span");
      if (span) {
        span.classList.add("highlight-glow");
        setTimeout(() => span.classList.remove("highlight-glow"), 2000);
      }
    });
  });

  // Copy suggestion code snippets to clipboard
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const code = btn.closest(".suggestion-box").querySelector("code").innerText;
      navigator.clipboard.writeText(code);
      btn.innerText = "✅ Copied!";
      setTimeout(() => (btn.innerText = "📋 Copy"), 1500);
    });
  });

  // Expand/collapse suggestion boxes
  document.querySelectorAll(".toggle-code").forEach(toggle => {
    const box = toggle.closest(".suggestion-box");
    const body = box.querySelector(".suggestion-body");
    toggle.addEventListener("click", () => {
      if (box.classList.contains("collapsed")) {
        body.style.maxHeight = body.scrollHeight + "px";
        toggle.innerText = "▼";
      } else {
        body.style.maxHeight = 0;
        toggle.innerText = "▶";
      }
      box.classList.toggle("collapsed");
    });
  });

  // Chart.js configuration base (shared between charts)
  const chartBaseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 1000 },
    plugins: {
      legend: { labels: { color: "#fff" } },
      title: { display: true, color: "#fff", font: { size: 18 } }
    },
    layout: { padding: 20 }
  };

  // Structure Efficiency Bar Chart
  if (typeof structureChartData !== "undefined") {
    new Chart(document.getElementById("structureChart"), {
      type: "bar",
      data: {
        labels: structureChartData.map(d => d.type),
        datasets: [{
          label: "Efficiency (%)",
          data: structureChartData.map(d => d.efficiency),
          backgroundColor: "#bb86fc"
        }]
      },
      options: {
        ...chartBaseOptions,
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { color: "#fff" } },
          x: { ticks: { color: "#fff" } }
        },
        plugins: {
          ...chartBaseOptions.plugins,
          title: {
            ...chartBaseOptions.plugins.title,
            text: "Efficiency Score by Structure Type"
          }
        }
      }
    });

    // Structure Usage Pie Chart
    new Chart(document.getElementById("usageChart"), {
      type: "doughnut",
      data: {
        labels: structureChartData.map(d => d.type),
        datasets: [{
          data: structureChartData.map(d => d.count),
          backgroundColor: ["#bb86fc", "#ff9800", "#4caf50", "#f44336", "#03a9f4"]
        }]
      },
      options: {
        ...chartBaseOptions,
        plugins: {
          ...chartBaseOptions.plugins,
          title: {
            ...chartBaseOptions.plugins.title,
            text: "Structure Usage Distribution"
          }
        }
      }
    });
  }

  // Suggestion Category Breakdown Chart
  if (typeof suggestionCategoryData !== "undefined") {
    new Chart(document.getElementById("categoryChart"), {
      type: "bar",
      data: {
        labels: Object.keys(suggestionCategoryData),
        datasets: [{
          label: "Suggestions",
          data: Object.values(suggestionCategoryData),
          backgroundColor: "#4caf50"
        }]
      },
      options: {
        ...chartBaseOptions,
        indexAxis: "y",
        scales: {
          y: { ticks: { color: "#fff" } },
          x: { beginAtZero: true, ticks: { color: "#fff" } }
        },
        plugins: {
          ...chartBaseOptions.plugins,
          title: {
            ...chartBaseOptions.plugins.title,
            text: "Suggestion Category Breakdown"
          }
        }
      }
    });
  }

  // Initialise the Ace editor for code editing
  const editor = ace.edit("editor", {
    mode: "ace/mode/python",
    theme: "ace/theme/dracula",
    fontSize: "14px",
    showPrintMargin: false,
    useSoftTabs: true
  });

  // Handle theme switching from dropdown
  const themeSelect = document.getElementById("theme-selector");
  if (themeSelect) {
    const themeMap = {
      "dracula": "ace/theme/dracula",
      "monokai": "ace/theme/monokai",
    };

    const saved = localStorage.getItem("preferredTheme");
    if (saved && themeMap[saved]) themeSelect.value = saved;

    const applyTheme = theme => editor.setTheme(themeMap[theme] || themeMap["dracula"]);
    applyTheme(themeSelect.value);

    themeSelect.addEventListener("change", () => {
      const selected = themeSelect.value;
      localStorage.setItem("preferredTheme", selected);
      applyTheme(selected);
    });
  }

  // Submit button for editor content
  document.getElementById("run-editor-btn")?.addEventListener("click", () => {
    return handleEditorSubmit();
  });

  // Expand all suggestion boxes
  window.expandAll = () => {
    document.querySelectorAll(".suggestion-box").forEach(box => {
      const body = box.querySelector(".suggestion-body");
      const toggle = box.querySelector(".toggle-code");
      box.classList.remove("collapsed");
      body.style.maxHeight = body.scrollHeight + "px";
      toggle.innerText = "▼";
    });
  };

  // Collapse all suggestion boxes
  window.collapseAll = () => {
    document.querySelectorAll(".suggestion-box").forEach(box => {
      const body = box.querySelector(".suggestion-body");
      const toggle = box.querySelector(".toggle-code");
      box.classList.add("collapsed");
      body.style.maxHeight = 0;
      toggle.innerText = "▶";
    });
  };

  // Download all fix snippets as a single file
// Downloads all suggestion snippets currently shown (the old behavior)
window.downloadFixSnippets = () => {
  const code = Array.from(document.querySelectorAll(".suggestion-box code"))
    .map(el => el.innerText)
    .join("\n\n");

  const blob = new Blob([code], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "fix_snippets.py";
  a.click();
};

window.downloadAutoFixed = async () => {
  // Get the most recently submitted code (from a hidden input field)
  const code = document.getElementById("submitted_code").value;

  // Prevent empty or placeholder code from being sent
  if (!code.trim() || code.trim().startsWith("# Paste your Python code here")) {
    alert("No valid analysed code found. Please run an analysis first.");
    return;
  }

  // Send code to backend to apply auto-fixes
  const response = await fetch("/autofix", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code })
  });

  const result = await response.text();

  // Trigger file download with fixed code
  const blob = new Blob([result], { type: "text/x-python" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "auto_fixed_code.py";
  a.click();
};



  // Filter suggestion boxes by keyword
  document.getElementById("filter-input")?.addEventListener("input", e => {
    const val = e.target.value.toLowerCase();
    document.querySelectorAll(".suggestion-box").forEach(box => {
      box.style.display = box.innerText.toLowerCase().includes(val) ? "block" : "none";
    });
  });

  // Animate sections as they scroll into view
  const fadeInOnScroll = () => {
    const elements = document.querySelectorAll(
      "h3, h2, .sticky-wrapper, .upload-box, #editor, #code-area, .structure-table, .suggestion-box, .controls-row, ul"
    );

    elements.forEach(el => el.classList.add("fade-in"));

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("visible");
        obs.unobserve(entry.target);
      });
    }, {
      threshold: 0.1,
      rootMargin: "0px 0px -40px 0px"
    });

    elements.forEach(el => observer.observe(el));
  };

  fadeInOnScroll();
});

// Show selected file name in the upload label
function showFileName(input) {
  const name = input.files[0]?.name || "No file selected";
  document.getElementById("file-name").innerText = `📁 ${name}`;
}

// Begin loading bar animation
function startLoadingBar() {
  const bar = document.getElementById("loading-bar");
  bar.style.width = "0%";
  bar.style.display = "block";

  let width = 0;
  const interval = setInterval(() => {
    if (width >= 90) {
      clearInterval(interval);
    } else {
      width += 2;
      bar.style.width = width + "%";
    }
  }, 20);
  return interval;
}

// Stop and hide the loading bar
function stopLoadingBar() {
  const bar = document.getElementById("loading-bar");
  bar.style.width = "100%";
  setTimeout(() => {
    bar.style.display = "none";
    bar.style.width = "0%";
  }, 400);
}

// Submit the file upload form with loading animation
function handleUploadSubmit() {
  const interval = startLoadingBar();

  const uploadInput = document.getElementById("codefile");
  if (uploadInput.files[0]) {
    const reader = new FileReader();
    reader.onload = () => {
      document.getElementById("submitted_code").value = reader.result;
      clearInterval(interval);
      stopLoadingBar();
      document.querySelector(".upload-box form").submit();
    };
    reader.readAsText(uploadInput.files[0]);
    return false;
  }

  // fallback if something goes wrong
  setTimeout(() => {
    clearInterval(interval);
    stopLoadingBar();
    document.querySelector("form").submit();
  }, 1000);

  return false;
}

// Submit the live editor form with loading animation
function handleEditorSubmit() {
  const interval = startLoadingBar();
  const code = ace.edit("editor").getValue();
  document.getElementById("editor_code").value = code;
  document.getElementById("submitted_code").value = code; // ✅ New line
  setTimeout(() => {
    clearInterval(interval);
    stopLoadingBar();
    document.getElementById("editor-form").submit();
  }, 1000);
  return false;
}