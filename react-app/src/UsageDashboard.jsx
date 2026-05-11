import { useEffect, useState } from "react";

function UsageDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const url = `${import.meta.env.VITE_API_BASE}/usage/summary`;

        console.log("Calling API:", url);

        const res = await fetch(url);

        const text = await res.text();  // ✅ ALWAYS read text first

        // 🚨 Check if response is HTML (error page)
        if (text.startsWith("<")) {
          throw new Error("Backend returned HTML instead of JSON");
        }

        const json = JSON.parse(text); // ✅ safe parse

        setData(json);

      } catch (err) {
        console.error("Fetch error:", err);
        setError("Failed to load API data");
      }
    }

    fetchData();
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!data) return <p>Loading... ⏳</p>;

  return (
    <div>
      <h2>Usage Summary</h2>
      <p>Total Calls: {data.total_calls}</p>
      <p>Total SMS: {data.total_sms}</p>
      <p>Total Internet: {data.total_internet_mb}</p>
      <p>Peak Hour: {data.peak_hour}</p>
      <p>Busiest Region: {data.busiest_region}</p>
    </div>
  );
}

export default UsageDashboard;
``