import { useEffect, useState } from "react";

function PeakTraffic() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE}/usage/peak`);

        if (!res.ok) {
          throw new Error("API error");
        }

        const json = await res.json();
        setData(json);

      } catch (err) {
        console.error(err);
        setError("Failed to load peak data");
      }
    }

    fetchData();
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!data) return <p>Loading... ⏳</p>;

  return (
    <div>
      <h2>Peak Traffic</h2>

      <h3>Top Hours</h3>
      {data.top_hours.map((h, i) => (
        <p key={i}>Hour {h.hour}: {h.total_usage}</p>
      ))}

      <h3>Top Regions</h3>
      {data.top_regions.map((r, i) => (
        <p key={i}>{r.region}: {r.total_usage}</p>
      ))}
    </div>
  );
}

export default PeakTraffic;