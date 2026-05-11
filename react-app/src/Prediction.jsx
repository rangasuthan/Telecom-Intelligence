import { useState } from "react";

function Prediction() {
  const [form, setForm] = useState({
    region: "",
    avg_usage: "",
    growth_rate: "",
    variability: ""
  });

  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE}/predict-usage-risk`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          region: form.region,
          avg_usage: Number(form.avg_usage),
          growth_rate: Number(form.growth_rate),
          variability: Number(form.variability)
        })
      });

      const data = await res.json();
      setResult(data);

    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <h2>Risk Prediction</h2>

      <input
        placeholder="Region"
        onChange={e => setForm({ ...form, region: e.target.value })}
      /><br />

      <input
        placeholder="Avg Usage"
        onChange={e => setForm({ ...form, avg_usage: e.target.value })}
      /><br />

      <input
        placeholder="Growth Rate"
        onChange={e => setForm({ ...form, growth_rate: e.target.value })}
      /><br />

      <input
        placeholder="Variability"
        onChange={e => setForm({ ...form, variability: e.target.value })}
      /><br />

      <button onClick={handleSubmit}>Predict</button>

      {result && (
        <div style={{ marginTop: "15px" }}>
          <h3>Results:</h3>

          <p><b>Risk:</b> {result.congestion_risk}</p>

          <p><b>Score:</b> {result.score}</p>

          <p>
            <b>Anomaly:</b> {result.anomaly_flag ? "Yes 🚨" : "No ✅"}
          </p>
        </div>
      )}
    </div>
  );
}

export default Prediction;