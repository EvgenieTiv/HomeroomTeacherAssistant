import React, { useEffect, useState } from "react";
import RecommendationPanel from "../components/RecommendationPanel";
import JournalTable from "../components/JournalTable";
import {
  getJournalByDate,
  getAiRecommendationsByDate,
} from "../services/api";
import "../styles/dashboard.css";
import "../styles/journal.css";

function Dashboard() {
  const [selectedDate, setSelectedDate] = useState("2025-11-29");
  const [recommendations, setRecommendations] = useState(null);
  const [journalData, setJournalData] = useState(null);
  const [useLlm, setUseLlm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLoadDashboard = async (
    dateToLoad = selectedDate,
    llmMode = useLlm
  ) => {
    if (!dateToLoad) {
      setError("Please select a valid date.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const [journal, aiRecommendations] = await Promise.all([
        getJournalByDate(dateToLoad),
        getAiRecommendationsByDate(dateToLoad, llmMode),
      ]);

      setJournalData(journal || null);
      setRecommendations(aiRecommendations || null);
    } catch (err) {
      setError("Failed to load dashboard data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleLoadDashboard("2025-11-29", false);
  }, []);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Homeroom Teacher Dashboard</h1>

      <div className="dashboard-controls">
        <label htmlFor="snapshot-date">Select date:</label>

        <input
          id="snapshot-date"
          type="date"
          value={selectedDate}
          min="2025-09-01"
          max="2026-06-30"
          onChange={(e) => setSelectedDate(e.target.value)}
        />

        <label className="dashboard-toggle">
          <input
            type="checkbox"
            checked={useLlm}
            onChange={(e) => setUseLlm(e.target.checked)}
          />
          Use LLM recommendations
        </label>

        <button onClick={() => handleLoadDashboard()} disabled={loading}>
          {loading ? "Loading..." : "Load Dashboard"}
        </button>
      </div>

      <div className="dashboard-meta">
        <span className="dashboard-meta-label">Current snapshot date:</span>
        <span className="dashboard-meta-value">{selectedDate}</span>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="dashboard-main-layout">
        <div className="dashboard-journal-area">
          <JournalTable journalData={journalData} />
        </div>

        <div className="dashboard-side-area">
          <RecommendationPanel recommendations={recommendations} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;