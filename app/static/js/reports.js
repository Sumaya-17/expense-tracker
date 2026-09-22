document.addEventListener("DOMContentLoaded", async () => {
  const canvas = document.getElementById("expenseChart"); if (!canvas) return;
  try { const response = await fetch(window.chartDataUrl); const payload = await response.json(); const items = payload.data.categories;
    new Chart(canvas, {type:"doughnut",data:{labels:items.map(x=>x.label),datasets:[{data:items.map(x=>x.value),backgroundColor:["#5b5ce2","#169b62","#e05252","#ee9c38","#23a6c4","#9f5dd8","#52627c"]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}}}});
    const monthly = payload.data.monthly, monthlyCanvas = document.getElementById("monthlyChart");
    if (monthlyCanvas) new Chart(monthlyCanvas,{type:"line",data:{labels:monthly.map(x=>x.label),datasets:[{label:"Income",data:monthly.map(x=>x.income),borderColor:"#169b62",backgroundColor:"#169b6222",tension:.35,fill:true},{label:"Expenses",data:monthly.map(x=>x.expenses),borderColor:"#e05252",backgroundColor:"#e0525222",tension:.35,fill:true}]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},scales:{y:{beginAtZero:true}}}});
  } catch (_error) { canvas.parentElement.innerHTML = "<p class='text-muted text-center pt-5'>Chart data is unavailable right now.</p>"; }
});
