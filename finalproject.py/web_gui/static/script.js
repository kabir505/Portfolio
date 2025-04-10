document.addEventListener("DOMContentLoaded", () => {
    const toggleSticky = document.getElementById("toggle-sticky");
    const wrapper = document.querySelector(".sticky-wrapper");
  
    toggleSticky?.addEventListener("change", () => {
      wrapper.classList.toggle("sticky-enabled", toggleSticky.checked);
    });
  
    // Scroll Glow Effect
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
  
    // Copy Snippets
    document.querySelectorAll(".copy-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const code = btn.closest(".suggestion-box").querySelector("code").innerText;
        navigator.clipboard.writeText(code);
        btn.innerText = "✅ Copied!";
        setTimeout(() => (btn.innerText = "📋 Copy"), 1500);
      });
    });
  
    // Expand/Collapse Suggestions
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
  
    // Chart Configuration
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
  
    // Ace Editor Setup
    const editor = ace.edit("editor", {
      mode: "ace/mode/python",
      theme: "ace/theme/dracula",
      fontSize: "14px",
      showPrintMargin: false,
      useSoftTabs: true
    });
  
    // Theme Selection
    const themeSelect = document.getElementById("theme-selector");
    if (themeSelect) {
      const themeMap = {
        "dracula": "ace/theme/dracula",
        "monokai": "ace/theme/monokai",
        "solarized_dark": "ace/theme/solarized_dark",
        "tomorrow_night": "ace/theme/tomorrow_night",
        "github_dark": "ace/theme/github_dark"
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
  
    // Editor Submit
    document.getElementById("run-editor-btn")?.addEventListener("click", () => {
      return handleEditorSubmit();
    });
  
    // Expand/Collapse All
    window.expandAll = () => {
      document.querySelectorAll(".suggestion-box").forEach(box => {
        const body = box.querySelector(".suggestion-body");
        const toggle = box.querySelector(".toggle-code");
        box.classList.remove("collapsed");
        body.style.maxHeight = body.scrollHeight + "px";
        toggle.innerText = "▼";
      });
    };
  
    window.collapseAll = () => {
      document.querySelectorAll(".suggestion-box").forEach(box => {
        const body = box.querySelector(".suggestion-body");
        const toggle = box.querySelector(".toggle-code");
        box.classList.add("collapsed");
        body.style.maxHeight = 0;
        toggle.innerText = "▶";
      });
    };
  
    // Auto Fix Download
    window.autoFix = () => {
      const code = Array.from(document.querySelectorAll(".suggestion-box code"))
        .map(el => el.innerText)
        .join("\n\n");
      const blob = new Blob([code], { type: "text/plain" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "auto_fixed_code.py";
      a.click();
    };
  
    // Filter Suggestions
    document.getElementById("filter-input")?.addEventListener("input", e => {
      const val = e.target.value.toLowerCase();
      document.querySelectorAll(".suggestion-box").forEach(box => {
        box.style.display = box.innerText.toLowerCase().includes(val) ? "block" : "none";
      });
    });
  
    // Scroll-triggered fade-in animation
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
  
  // 📁 File Upload Label
  function showFileName(input) {
    const name = input.files[0]?.name || "No file selected";
    document.getElementById("file-name").innerText = `📁 ${name}`;
  }
  
  // === Loading Overlay Logic ===
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
  
  function stopLoadingBar() {
    const bar = document.getElementById("loading-bar");
    bar.style.width = "100%";
    setTimeout(() => {
      bar.style.display = "none";
      bar.style.width = "0%";
    }, 400);
  }
  
  // Submit Handlers
  function handleUploadSubmit() {
    const interval = startLoadingBar();
    setTimeout(() => {
      clearInterval(interval);
      stopLoadingBar();
      document.querySelector("form").submit();
    }, 1000);
    return false;
  }
  
  function handleEditorSubmit() {
    const interval = startLoadingBar();
    const code = ace.edit("editor").getValue();
    document.getElementById("editor_code").value = code;
    setTimeout(() => {
      clearInterval(interval);
      stopLoadingBar();
      document.getElementById("editor-form").submit();
    }, 1000);
    return false;
  }
  