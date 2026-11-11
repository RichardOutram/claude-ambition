// Tabs, Markdown rendering and the file viewer for the results site. No build step.
(function () {
  const loaded = new WeakSet();

  function renderMarkdown(el, text) {
    const html = window.marked ? window.marked.parse(text) : null;
    if (html && window.DOMPurify) el.innerHTML = window.DOMPurify.sanitize(html);
    else { const pre = document.createElement("pre"); pre.textContent = text; el.replaceChildren(pre); }
  }

  async function loadMd(el) {
    if (loaded.has(el)) return;
    loaded.add(el);
    el.textContent = "Loading…";
    try {
      const res = await fetch(el.dataset.md);
      if (!res.ok) throw new Error(res.status);
      renderMarkdown(el, await res.text());
    } catch (err) {
      el.textContent = "Couldn't load this file.";
    }
  }

  // Markdown blocks: load visible ones now, ones inside closed <details> when opened.
  document.querySelectorAll("[data-md]").forEach((el) => {
    const closed = el.closest("details:not([open])");
    if (!closed) loadMd(el);
  });
  document.querySelectorAll("details").forEach((d) =>
    d.addEventListener("toggle", () => {
      if (d.open) d.querySelectorAll(":scope > [data-md], :scope > * [data-md]").forEach((el) => {
        if (!el.closest("details:not([open])")) loadMd(el);
      });
    })
  );

  // Tabs
  document.querySelectorAll(".tabs").forEach((bar) => {
    const buttons = bar.querySelectorAll("[data-tab]");
    buttons.forEach((btn) =>
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.setAttribute("aria-selected", String(b === btn)));
        let panel = bar.nextElementSibling;
        while (panel && panel.matches("[data-panel]")) {
          panel.hidden = panel.dataset.panel !== btn.dataset.tab;
          panel = panel.nextElementSibling;
        }
      })
    );
  });

  // File viewer
  document.querySelectorAll(".files").forEach((box) => {
    const viewer = box.querySelector(".viewer");
    const name = viewer.querySelector(".viewer-head code");
    const raw = viewer.querySelector(".viewer-head a");
    const body = viewer.querySelector(".viewer-body");
    box.querySelectorAll("a[data-file]").forEach((link) =>
      link.addEventListener("click", async (ev) => {
        const kind = link.dataset.kind;
        if (kind === "download") return;
        ev.preventDefault();
        box.querySelectorAll("a[aria-current]").forEach((a) => a.removeAttribute("aria-current"));
        link.setAttribute("aria-current", "true");
        viewer.hidden = false;
        name.textContent = link.textContent;
        raw.href = link.dataset.file;
        body.replaceChildren();
        if (kind === "html") {
          const frame = document.createElement("iframe");
          frame.setAttribute("sandbox", "allow-scripts allow-forms");
          frame.src = link.dataset.file;
          frame.title = link.textContent;
          body.append(frame);
        } else if (kind === "img") {
          const img = document.createElement("img");
          img.src = link.dataset.file;
          img.alt = link.textContent;
          body.append(img);
        } else {
          try {
            const text = await (await fetch(link.dataset.file)).text();
            if (kind === "md") {
              const div = document.createElement("div");
              div.className = "md";
              renderMarkdown(div, text);
              body.append(div);
            } else {
              const pre = document.createElement("pre");
              pre.textContent = text;
              body.append(pre);
            }
          } catch (err) {
            body.textContent = "Couldn't load this file.";
          }
        }
        if (window.matchMedia("(max-width: 760px)").matches) viewer.scrollIntoView({ behavior: "smooth", block: "start" });
      })
    );
  });
})();
