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
// Save user data in local storage
function saveUserData() {
  const prevElectricity = document.getElementById("prevElectricity").value;
  const currElectricity = document.getElementById("currElectricity").value;
  const prevWater = document.getElementById("prevWater").value;
  const currWater = document.getElementById("currWater").value;

  localStorage.setItem("prevElectricity", prevElectricity);
  localStorage.setItem("currElectricity", currElectricity);
  localStorage.setItem("prevWater", prevWater);
  localStorage.setItem("currWater", currWater);
}

// Load user data from local storage
function loadUserData() {
  const prevElectricity = localStorage.getItem("prevElectricity");
  const currElectricity = localStorage.getItem("currElectricity");
  const prevWater = localStorage.getItem("prevWater");
  const currWater = localStorage.getItem("currWater");

  if (prevElectricity) document.getElementById("prevElectricity").value = prevElectricity;
  if (currElectricity) document.getElementById("currElectricity").value = currElectricity;
  if (prevWater) document.getElementById("prevWater").value = prevWater;
  if (currWater) document.getElementById("currWater").value = currWater;
}

// Automatically load data when the page loads
window.onload = function () {
  loadUserData();
};

// Save data when the Calculate button is clicked
document.getElementById("calculateBtn").addEventListener("click", saveUserData);

// Set a cookie
function setCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

// Get a cookie value
function getCookie(name) {
  const cookies = document.cookie.split("; ");
  for (let cookie of cookies) {
    const [key, value] = cookie.split("=");
    if (key === name) return decodeURIComponent(value);
  }
  return null;
}

// Save user input data in cookies
function saveUserData() {
  // Get input values
  const prevElectricity = document.getElementById("prevElectricity").value;
  const currElectricity = document.getElementById("currElectricity").value;
  const prevWater = document.getElementById("prevWater").value;
  const currWater = document.getElementById("currWater").value;

  // Save each input to a cookie
  setCookie("prevElectricity", prevElectricity, 30); // Save for 30 days
  setCookie("currElectricity", currElectricity, 30);
  setCookie("prevWater", prevWater, 30);
  setCookie("currWater", currWater, 30);
}

// Load user input data from cookies
function loadUserData() {
  // Get cookie values
  const prevElectricity = getCookie("prevElectricity");
  const currElectricity = getCookie("currElectricity");
  const prevWater = getCookie("prevWater");
  const currWater = getCookie("currWater");

  // Populate input fields with cookie values if they exist
  if (prevElectricity) document.getElementById("prevElectricity").value = prevElectricity;
  if (currElectricity) document.getElementById("currElectricity").value = currElectricity;
  if (prevWater) document.getElementById("prevWater").value = prevWater;
  if (currWater) document.getElementById("currWater").value = currWater;
}

// Automatically load data when the page loads
window.onload = function () {
  loadUserData();
};

// Save data when the Calculate button is clicked
document.getElementById("calculateBtn").addEventListener("click", saveUserData);
