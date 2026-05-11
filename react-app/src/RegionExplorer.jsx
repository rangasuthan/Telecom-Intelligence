import { useState } from "react";

function RegionExplorer() {
  const [region, setRegion] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setError(null);
      setData(null);

      const res = await fetch(`${import.meta.env.VITE_API_BASE}/usage/region/${region}`);

      if (!res.ok) {
        throw new Error("Region not found");
      }

      const json = await res.json();
      setData(json);

    } catch (err) {
      console.error(err);
      setError("Error fetching region data");
    }
  };

  return (
    <div>
      <h2>Region Explorer</h2>

      <input value={region} onChange={(e) => setRegion(e.target.value)} />
      <button onClick={fetchData}>Search</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {data && (
        <table border="1">
          <thead>
            <tr>
              <th>Hour</th>
              <th>Calls</th>
              <th>SMS</th>
              <th>Internet</th>
            </tr>
          </thead>
          <tbody>
            {data.hourly_distribution.map((r, i) => (
              <tr key={i}>
                <td>{r.hour}</td>
                <td>{r.calls}</td>
                <td>{r.sms}</td>
                <td>{r.internet_mb}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default RegionExplorer;