let cpuData = [];
let ramData = [];
let labels = [];

const ctx = document.getElementById("sysChart").getContext("2d");

const chart = new Chart(ctx,{
  type:'line',
  data:{
    labels:labels,
    datasets:[
      {label:'CPU',data:cpuData,borderWidth:2},
      {label:'RAM',data:ramData,borderWidth:2}
    ]
  },
  options:{
    responsive:true,
    animation:false,
    scales:{y:{min:0,max:100}}
  }
});

async function loadStats(){
  const stats = await fetch("/stats").then(r=>r.json());
  const health = await fetch("/health").then(r=>r.json());

  document.getElementById("cpu").innerText = stats.cpu + "%";
  document.getElementById("ram").innerText = stats.ram + "%";
  document.getElementById("disk").innerText = stats.disk + "%";
  document.getElementById("health").innerText = health.score + "%";

  document.getElementById("status").innerText =
    health.anomaly ? "⚠ Threat Detected" : health.status;

  if(cpuData.length > 20){
    cpuData.shift();
    ramData.shift();
    labels.shift();
  }

  cpuData.push(stats.cpu);
  ramData.push(stats.ram);
  labels.push("");

  chart.update();

  const list = document.getElementById("threatList");
  if(health.killed){
    health.killed.forEach(app=>{
      const li = document.createElement("li");
      li.innerText = `Terminated: ${app}`;
      list.prepend(li);
    });
  }
}

setInterval(loadStats,1000);
loadStats();
