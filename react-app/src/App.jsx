import { useState } from "react";
import UsageDashboard from "./UsageDashboard";
import RegionExplorer from "./RegionExplorer";
import PeakTraffic from "./PeakTraffic";
import Prediction from "./Prediction";

function App() {
  const [page, setPage] = useState("dashboard");

  return (
    <div style={{ padding: "20px" }}>
      <h1>Telecom Dashboard</h1>

      <button onClick={() => setPage("dashboard")}>Dashboard</button>
      <button onClick={() => setPage("region")}>Region</button>
      <button onClick={() => setPage("peak")}>Peak</button>
      <button onClick={() => setPage("predict")}>Predict</button>

      <hr />

      {page === "dashboard" && <UsageDashboard />}
      {page === "region" && <RegionExplorer />}
      {page === "peak" && <PeakTraffic />}
      {page === "predict" && <Prediction />}
    </div>
  );
}

export default App;