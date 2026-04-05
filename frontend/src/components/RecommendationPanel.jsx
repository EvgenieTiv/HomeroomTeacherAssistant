import React from "react";
import "../styles/dashboard.css";

const MAX_VISIBLE_STUDENTS = 5;

function fullName(student) {
  return `${student?.FirstName ?? ""} ${student?.LastName ?? ""}`.trim();
}

function formatRate(value) {
  if (value === null || value === undefined) return "-";
  return `${Math.round(value * 100)}%`;
}

function getSubtitle(student, type) {
  if (type === "lowPerformance") {
    return `Average grade: ${student?.average_grade ?? "-"}`;
  }

  if (type === "declining") {
    return `Grade drop: ${student?.grade_drop ?? "-"}`;
  }

  if (type === "lowSubmission") {
    return `Submission rate: ${formatRate(student?.submission_rate)}`;
  }

  if (type === "topStudents") {
    return `Average grade: ${student?.average_grade ?? "-"}`;
  }

  return "";
}

function renderStudents(students, type) {
  if (!students || students.length === 0) {
    return <p className="recommendation-empty">No students</p>;
  }

  const visibleStudents = students.slice(0, MAX_VISIBLE_STUDENTS);
  const remainingCount = students.length - visibleStudents.length;

  return (
    <div className="recommendation-student-list">
      {visibleStudents.map((student, index) => (
        <div
          key={`${student?.student_id ?? "student"}-${index}`}
          className="recommendation-student-card"
        >
          <div className="recommendation-student-name">
            {fullName(student) || "Unnamed student"}
          </div>

          <div className="recommendation-student-email">
            {student?.Email ?? "-"}
          </div>

          <div className="recommendation-student-subtitle">
            {getSubtitle(student, type)}
          </div>
        </div>
      ))}

      {remainingCount > 0 && (
        <div className="recommendation-more">
          + {remainingCount} more
        </div>
      )}
    </div>
  );
}

function RecommendationPanel({ recommendations }) {
  if (!recommendations) {
    return (
      <div className="recommendation-panel">
        <h2>Recommendations</h2>
        <p>No recommendations loaded yet.</p>
      </div>
    );
  }

  return (
    <div className="recommendation-panel">
      <h2>Recommendations</h2>

      <div className="recommendation-block">
        <h3>Low Performance</h3>
        {renderStudents(recommendations.lowPerformance, "lowPerformance")}
      </div>

      <div className="recommendation-block">
        <h3>Declining Performance</h3>
        {renderStudents(recommendations.declining, "declining")}
      </div>

      <div className="recommendation-block">
        <h3>Low Submission</h3>
        {renderStudents(recommendations.lowSubmission, "lowSubmission")}
      </div>

      <div className="recommendation-block">
        <h3>Top Students</h3>
        {renderStudents(recommendations.topStudents, "topStudents")}
      </div>
    </div>
  );
}

export default RecommendationPanel;