import { useEffect, useState } from "react";
import { submitIncident, fetchIncidents, healthCheck } from "../api";

function Dashboard() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const res = await fetchIncidents();
    setHistory(res.data);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const sendIncident = async () => {
    if (!description.trim()) return;
    const res = await submitIncident(description);
    setResult(res.data);
    loadHistory();
  };

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <div className="dashboard">
      <button className="logout" onClick={logout}>Logout</button>

      <h2>RoadSenseAI Dashboard</h2>

      <textarea
        placeholder="Describe incident..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <button onClick={sendIncident}>Analyze</button>

      {result && (
        <div className="result">
          <h3>Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      <h3>History</h3>
      {history.map((h) => (
        <div key={h.id} className="history-item">
          {h.description}
        </div>
      ))}
    </div>
  );
}

export default Dashboard;
