import React, { useEffect, useState } from "react";
import RecommendationPanel from "../components/RecommendationPanel";
import JournalTable from "../components/JournalTable";
import { getSnapshotByDate, getJournalByDate } from "../services/api";
import "../styles/dashboard.css";
import "../styles/journal.css";

function Dashboard() {
  const [selectedDate, setSelectedDate] = useState("2025-11-29");
  const [recommendations, setRecommendations] = useState(null);
  const [journalData, setJournalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLoadDashboard = async (dateToLoad = selectedDate) => {
    if (!dateToLoad) {
      setError("Please select a valid date.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const [snapshot, journal] = await Promise.all([
        getSnapshotByDate(dateToLoad),
        getJournalByDate(dateToLoad),
      ]);

      setRecommendations({
        lowPerformance: snapshot?.low_performance_students || [],
        declining: snapshot?.declining_performance_students || [],
        lowSubmission: snapshot?.low_submission_students || [],
        topStudents: snapshot?.top_students || [],
      });

      setJournalData(journal || null);
    } catch (err) {
      setError("Failed to load dashboard data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleLoadDashboard("2025-11-29");
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