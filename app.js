async function run() {
  const res = await fetch("./data/events.json", { cache: "no-store" });
  const data = await res.json();

  document.getElementById("meta").textContent =
    data.generated_at ? `Sist oppdatert: ${new Date(data.generated_at).toLocaleString("no-NO")}` : "";

  const list = document.getElementById("list");
  list.innerHTML = "";

  for (const e of data.events) {
    const dt = new Date(e.start);
    const line = document.createElement("div");
    line.innerHTML = `
      <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd;">
        <div><strong>${e.title}</strong></div>
        <div>${dt.toLocaleString("no-NO")} · ${e.venue}</div>
        <div><a href="${e.url}" target="_blank" rel="noopener">Åpne</a></div>
      </div>
    `;
    list.appendChild(line);
  }
}

run();
