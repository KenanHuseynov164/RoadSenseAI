import { useEffect, useState } from "react";
import { submitIncident, fetchIncidents } from "../api";
import "../assets/mainpage.css";

function Dashboard() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    try {
      const res = await fetchIncidents();
      setHistory(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      const res = await submitIncident(query);
      setResult(res.data);
      setQuery("");
      loadHistory();
    } catch (e) {
      console.error(e);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <>
      <header className="main-header">
        <nav className="nav-container">
          <a className="header-logo">RoadSense AI 🛡️</a>

          <ul className="nav-links">
            <li>
              <a className="nav-item active">Dashboard</a>
            </li>
            <li>
              <a className="nav-item">My History</a>
            </li>
            <li>
              <button className="nav-item logout-btn" onClick={logout}>
                Log Out
              </button>
            </li>
          </ul>
        </nav>
      </header>

      <div className="app-body-wrapper">
        <aside className="sidebar-menu">
          <h3 className="sidebar-title">Menu</h3>

          <ul className="sidebar-nav">
            <li>
              <button
                className="sidebar-item new-chat"
                onClick={() => {
                  setResult(null);
                  setQuery("");
                }}
              >
                <i className="fas fa-edit"></i> New Query
              </button>
            </li>
          </ul>

          <h3 className="sidebar-title">History</h3>

          <ul className="sidebar-history" id="history-list">
            {history.length === 0 && (
              <li className="history-item-placeholder">No recent searches.</li>
            )}
            {history.map((h) => (
              <li key={h.id} className="history-item">
                {h.description.length > 40
                  ? h.description.slice(0, 40) + "..."
                  : h.description}
              </li>
            ))}
          </ul>

          <div className="sidebar-footer">
            <a className="sidebar-item settings">
              <i className="fas fa-cog"></i> Settings &amp; Help
            </a>
          </div>
        </aside>

        <main className="dashboard-main-content">
          <section className="search-module">
            <h1>Quick Law Search</h1>
            <p>Type any question about traffic stops or your rights.</p>

            <form id="search-form" className="search-form" onSubmit={handleSearch}>
              <div className="input-group search-bar">
                <i className="fas fa-search search-icon"></i>

                <input
                  id="query-input"
                  type="text"
                  placeholder="Ask about traffic rules"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  required
                />

                <button type="submit" className="search-btn">
                  Search
                </button>
              </div>
            </form>

            <div className="quick-links">
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setQuery("They stopped me for DUI");
                }}
              >
                #DUI_Rights
              </a>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setQuery("Police stopped me for speeding");
                }}
              >
                #Traffic_Stop_Protocol
              </a>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setQuery("Officer wants to search my vehicle");
                }}
              >
                #Vehicle_Search
              </a>
            </div>
          </section>

          <section className="results-container">
            {result ? (
              <div className="results-box">
                <h3>Result</h3>
                <p>
                  <strong>Articles:</strong>{" "}
                  {result.legal_articles.join(", ")}
                </p>
                <p>
                  <strong>Explanation:</strong> {result.explanation}
                </p>
                <p>
                  <strong>Recommendation:</strong> {result.recommendation}
                </p>
                <p>
                  <strong>What to say:</strong> {result.what_to_say}
                </p>
              </div>
            ) : (
              <h3 className="results-placeholder" id="results-box">
                Your search results will appear here.
              </h3>
            )}
          </section>
        </main>
      </div>

      <footer>
        <p>&copy; 2025 RoadSense AI Project</p>
      </footer>
    </>
  );
}

export default Dashboard;
