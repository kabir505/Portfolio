document.addEventListener("DOMContentLoaded", () => {
    // ✅ Initialize AOS animations
    if (typeof AOS !== "undefined") {
      AOS.init({ duration: 600, once: true });
    }
  
    // ✅ Grab all code lines in the Pygments-rendered table
    const rows = document.querySelectorAll("#code-area table.highlighttable tr");
  
    // ✅ Highlight a line smoothly when button clicked
    document.querySelectorAll(".see-code").forEach(button => {
      button.addEventListener("click", () => {
        const line = parseInt(button.dataset.line);
        const target = rows[line - 1];
  
        if (!target) return;
  
        // ✨ Remove highlight from all
        rows.forEach(row => {
          row.style.backgroundColor = "transparent";
        });
  
        // ✨ Highlight + scroll to the correct line
        setTimeout(() => {
          target.style.backgroundColor = "#5c2b8c88"; // semi-transparent purple
          target.scrollIntoView({ behavior: "smooth", block: "center" });
  
          setTimeout(() => {
            target.style.backgroundColor = "transparent";
          }, 2000);
        }, 100); // let the page layout settle
      });
    });
  });
  