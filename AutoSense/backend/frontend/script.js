const cpuEl = document.getElementById("cpu");
const ramEl = document.getElementById("ram");
const diskEl = document.getElementById("disk");
const healthEl = document.getElementById("health");
const fixesEl = document.getElementById("fixes");
const alertBox = document.getElementById("alertBox");
const uptimeEl = document.getElementById("uptime");
const tableBody = document.getElementById("recordsTable");
const downloadBtn = document.getElementById("downloadBtn");
const themeBtn = document.getElementById("themeToggle");

/* 🌗 THEME */
themeBtn.onclick = () => {
  document.documentElement.classList.toggle("light");
  localStorage.setItem(
    "theme",
    document.documentElement.classList.contains("light") ? "light" : "dark"
  );
  updateChartTheme();
};

if (localStorage.getItem("theme") === "light") {
  document.documentElement.classList.add("light");
}

/* 📊 CHART */
const labels = [], cpuData = [], ramData = [], diskData = [];
const ctx = document.getElementById("chart").getContext("2d");

const chart = new Chart(ctx, {
  type: "line",
  data: {
    labels,
    datasets: [
      { label: "CPU", data: cpuData, borderColor: "#38bdf8" },
      { label: "RAM", data: ramData, borderColor: "#22c55e" },
      { label: "Disk", data: diskData, borderColor: "#facc15" }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
});

function updateChartTheme() {
  const light = document.documentElement.classList.contains("light");
  chart.options.scales.x.ticks.color = light ? "#000" : "#fff";
  chart.options.scales.y.ticks.color = light ? "#000" : "#fff";
  chart.update();
}

updateChartTheme();

/* 🔄 FETCH HEALTH */
async function fetchHealth() {
  const res = await fetch("/api/health");
  const d = await res.json();

  cpuEl.innerText = `CPU\n${d.metrics.cpu}%`;
  ramEl.innerText = `RAM\n${d.metrics.ram}%`;
  diskEl.innerText = `Disk\n${d.metrics.disk}%`;
  healthEl.innerText = `Health\n${d.health_score}`;

  fixesEl.innerHTML = d.fixes.map(f => `<li>${f}</li>`).join("");

  uptimeEl.innerText = `⏱ Uptime: ${Math.floor(d.uptime / 60)} min`;

  if (d.alert) {
    alertBox.innerText = d.alert;
    alertBox.classList.remove("hidden");
  } else {
    alertBox.classList.add("hidden");
  }

  labels.push(new Date().toLocaleTimeString());
  cpuData.push(d.metrics.cpu);
  ramData.push(d.metrics.ram);
  diskData.push(d.metrics.disk);

  if (labels.length > 15) {
    labels.shift();
    cpuData.shift();
    ramData.shift();
    diskData.shift();
  }

  chart.update();
}

/* 📋 TABLE */
async function loadTable() {
  const res = await fetch("/api/last-records");
  const rows = await res.json();

  tableBody.innerHTML = rows.map(r => `
    <tr>
      <td>${r.timestamp}</td>
      <td>${r.cpu}</td>
      <td>${r.ram}</td>
      <td>${r.disk}</td>
      <td>${r.health_score}</td>
    </tr>
  `).join("");
}

/* ⬇ CSV */
downloadBtn.onclick = () => window.open("/api/download-csv");

/* AUTO */
setInterval(fetchHealth, 3000);
setInterval(loadTable, 5000);
fetchHealth();
loadTable();
