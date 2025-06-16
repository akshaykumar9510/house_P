document.getElementById("predictForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());

  // Convert string to float
  Object.keys(data).forEach(key => {
    data[key] = parseFloat(data[key]);
  });

  const response = await fetch("https://your-api-url.onrender.com/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  document.getElementById("result").innerText = "Predicted Price: $" + (result.predicted_price * 100000).toFixed(2);
});
