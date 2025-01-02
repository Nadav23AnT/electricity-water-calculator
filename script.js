let historyCount = 0; // Counter for history entries

document.getElementById("calculateBtn").addEventListener("click", function () {
  const prevElectricity = parseFloat(
    document.getElementById("prevElectricity").value
  );
  const currElectricity = parseFloat(
    document.getElementById("currElectricity").value
  );
  const prevWater = parseFloat(document.getElementById("prevWater").value);
  const currWater = parseFloat(document.getElementById("currWater").value);
  const electricityRate = parseFloat(
    document.getElementById("electricityRate").value
  );
  const waterRate1 = parseFloat(document.getElementById("waterRate1").value);
  const waterRate2 = parseFloat(document.getElementById("waterRate2").value);
  const waterLimit = parseFloat(document.getElementById("waterLimit").value);

  if (
    isNaN(prevElectricity) ||
    isNaN(currElectricity) ||
    isNaN(prevWater) ||
    isNaN(currWater)
  ) {
    showResults(
      "❌ Please enter valid readings for electricity and water.",
      "danger"
    );
    return;
  }

  if (currElectricity < prevElectricity || currWater < prevWater) {
    showResults(
      "❌ Current readings must be greater than previous readings.",
      "danger"
    );
    return;
  }

  const electricityConsumption = currElectricity - prevElectricity;
  const waterConsumption = currWater - prevWater;

  const electricityCost = electricityConsumption * electricityRate;
  let waterCost;
  if (waterConsumption <= waterLimit) {
    waterCost = waterConsumption * waterRate1;
  } else {
    const tier1Cost = waterLimit * waterRate1;
    const tier2Cost = (waterConsumption - waterLimit) * waterRate2;
    waterCost = tier1Cost + tier2Cost;
  }

  const totalCost = electricityCost + waterCost;

  const resultHTML = `
    ⚡ <strong>Electricity:</strong> ${electricityCost.toFixed(2)} ILS<br>
    💧 <strong>Water:</strong> ${waterCost.toFixed(2)} ILS<br>
  `;
  showResults(resultHTML, "success");

  const totalCostHTML = `🤑 Total Cost: ${totalCost.toFixed(2)} ILS`;
  document.getElementById("totalCost").style.display = "block";
  document.getElementById("totalCost").innerHTML = totalCostHTML;

  updateChart(
    electricityConsumption,
    waterConsumption,
    electricityCost,
    waterCost
  );
  updateHistory(electricityCost, waterCost, totalCost);
});

function showResults(message, type) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = message;
  resultsDiv.className = `alert alert-${type} mt-3`;
  resultsDiv.style.display = "block";
}

function updateHistory(electricityCost, waterCost, totalCost) {
  historyCount++; // Increment history count
  const historyBody = document.getElementById("historyBody");
  const row = `
    <tr>
      <td>${historyCount}</td>
      <td>${electricityCost.toFixed(2)}</td>
      <td>${waterCost.toFixed(2)}</td>
      <td>${totalCost.toFixed(2)}</td>
    </tr>
  `;
  historyBody.insertAdjacentHTML("beforeend", row);
}

// Chart.js setup
const ctx = document.getElementById("costChart").getContext("2d");
const costChart = new Chart(ctx, {
  type: "doughnut",
  data: {
    labels: ["Electricity Cost", "Water Cost"],
    datasets: [
      {
        label: "Costs (ILS)",
        data: [0, 0],
        backgroundColor: ["#ff6347", "#ffd700"],
        borderWidth: 1,
        hoverOffset: 10,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: true, // Ensure the chart scales nicely
    plugins: {
      legend: {
        position: "bottom",
      },
    },
  },
});


function updateChart(
  electricityConsumption,
  waterConsumption,
  electricityCost,
  waterCost
) {
  // 4) Only set electricityCost and waterCost
  costChart.data.datasets[0].data = [electricityCost, waterCost];
  costChart.update();
}
