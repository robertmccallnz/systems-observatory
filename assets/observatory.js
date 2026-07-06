/* Te Pā Systems Observatory — client
 * Loads data/indicators.json, renders 12 panels, wires the annotation form.
 * Zero dependencies. Sparklines drawn as inline SVG.
 */
(function () {
  const DATA_URL = "data/indicators.json";
  // Gradio Space endpoint (POST /api/annotate). Configured post-deploy.
  const ANNOTATE_URL = window.OBS_ANNOTATE_URL ||
    "https://te-pa-systems-observatory-anomaly.hf.space/gradio_api/call/submit_annotation";

  const grid = document.getElementById("grid");
  const updated = document.getElementById("obs-updated");
  const kaupapa = document.getElementById("obs-kaupapa");
  const select = document.querySelector("#annotate-form select[name='leverage_point']");
  const form = document.getElementById("annotate-form");
  const status = document.getElementById("form-status");
  const dsLink = document.getElementById("ds-link");

  function sparkline(series, anomalyAt) {
    if (!series || series.length < 2) return '<div class="obs-empty">Series pending live-fetch.</div>';
    const vals = series.map(s => s.value);
    const min = Math.min(...vals), max = Math.max(...vals);
    const range = max - min || 1;
    const w = 240, h = 40, pad = 2;
    const pts = vals.map((v, i) => {
      const x = pad + (i / (vals.length - 1)) * (w - pad * 2);
      const y = h - pad - ((v - min) / range) * (h - pad * 2);
      return [x, y];
    });
    const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
    const last = pts[pts.length - 1];
    const anomalyDot = anomalyAt
      ? `<circle cx="${last[0]}" cy="${last[1]}" r="4" fill="#d7261e" stroke="#f4ecd8" stroke-width="1"/>`
      : `<circle cx="${last[0]}" cy="${last[1]}" r="3" fill="#e8a83a"/>`;
    return `<svg class="obs-spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">
      <path d="${path}" fill="none" stroke="#f4ecd8" stroke-width="1.4" opacity="0.85"/>
      ${anomalyDot}
    </svg>`;
  }

  function card(lp) {
    const hasAnomaly = !!lp.anomaly;
    const latest = lp.latest !== null && lp.latest !== undefined
      ? `<div class="obs-latest">${Number(lp.latest).toLocaleString(undefined, { maximumFractionDigits: 2 })}<small>${lp.unit || ""}</small></div>`
      : `<div class="obs-empty">Awaiting first live fetch.</div>`;
    const anomalyLine = hasAnomaly
      ? `<div><span class="obs-flag">◆ anomaly</span> <span style="color:#d7261e;font-size:12px;">${lp.anomaly.message}</span></div>`
      : "";
    return `<article class="obs-card${hasAnomaly ? " has-anomaly" : ""}" data-lp="${lp.id}">
      <div class="obs-card-tier"><span>${lp.tier}</span><span class="lp-number">${lp.id}</span></div>
      <h3>${lp.name}</h3>
      <p class="obs-question">${lp.paradigm_question}</p>
      ${latest}
      ${sparkline(lp.series, lp.anomaly && lp.anomaly.at)}
      ${anomalyLine}
      <div class="obs-source">Source: <a href="${lp.source_url}" target="_blank" rel="noopener">${lp.source_name}</a></div>
    </article>`;
  }

  function fillSelect(points) {
    select.innerHTML = points.map(p =>
      `<option value="${p.id}">${p.id}. ${p.tier} — ${p.name}</option>`
    ).join("");
  }

  async function submitAnnotation(payload) {
    // Two-step Gradio API: POST to get event_id, then GET results.
    const post = await fetch(ANNOTATE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: [payload.handle, Number(payload.leverage_point), payload.intervention,
               Number(payload.rank), payload.whakapapa, payload.reasoning],
      }),
    });
    if (!post.ok) throw new Error("submission rejected (" + post.status + ")");
    const j = await post.json();
    return j;
  }

  fetch(DATA_URL)
    .then(r => r.json())
    .then(doc => {
      updated.textContent = "Refreshed " + (doc.meta.generated_at || "").slice(0, 10);
      kaupapa.textContent = doc.meta.kaupapa || "";
      if (dsLink && doc.meta.annotations_dataset) {
        dsLink.href = "https://huggingface.co/datasets/" + doc.meta.annotations_dataset;
        dsLink.textContent = doc.meta.annotations_dataset;
      }
      grid.innerHTML = doc.leverage_points.map(card).join("");
      fillSelect(doc.leverage_points);
    })
    .catch(err => {
      grid.innerHTML = `<div class="obs-empty">Could not load indicators.json — ${err.message}</div>`;
    });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.textContent = "Writing to archive…";
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    try {
      await submitAnnotation(payload);
      status.textContent = "Kia ora — added to the public archive.";
      form.reset();
    } catch (err) {
      status.textContent = "Could not submit: " + err.message + " · Please try again shortly.";
    }
  });
})();
