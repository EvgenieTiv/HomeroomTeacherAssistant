import React from "react";
import "../styles/dashboard.css";

const MAX_VISIBLE_RECOMMENDATIONS = 8;

function fullName(item) {
  return `${item?.first_name ?? ""} ${item?.last_name ?? ""}`.trim();
}

function formatRate(value) {
  if (value === null || value === undefined) return "-";
  return `${Math.round(value * 100)}%`;
}

function prettyAction(action) {
  if (!action) return "-";

  const mapping = {
    contact_student_and_schedule_follow_up:
      "Contact student and schedule follow-up",
    check_in_with_student: "Check in with student",
    investigate_recent_drop: "Investigate recent performance drop",
    send_reminder_and_monitor_next_assignment:
      "Send reminder and monitor next assignment",
    monitor_next_assignment: "Monitor next assignment",
    praise_student: "Praise student",
  };

  return mapping[action] || action;
}

function priorityClass(priority) {
  if (priority === "high") return "recommendation-priority high";
  if (priority === "medium") return "recommendation-priority medium";
  return "recommendation-priority low";
}

function renderMetrics(item) {
  const bits = [];

  if (item?.average_grade !== null && item?.average_grade !== undefined) {
    bits.push(`Avg grade: ${item.average_grade}`);
  }

  if (
    item?.submission_rate !== null &&
    item?.submission_rate !== undefined
  ) {
    bits.push(`Submission: ${formatRate(item.submission_rate)}`);
  }

  if (item?.grade_drop !== null && item?.grade_drop !== undefined) {
    bits.push(`Drop: ${item.grade_drop}`);
  }

  if (
    item?.days_since_last_submission !== null &&
    item?.days_since_last_submission !== undefined
  ) {
    bits.push(`Last activity: ${item.days_since_last_submission}d ago`);
  }

  return bits.join(" • ");
}

function RecommendationPanel({ recommendations }) {
  if (!recommendations) {
    return (
      <div className="recommendation-panel">
        <h2>AI Recommendations</h2>
        <p>No recommendations loaded yet.</p>
      </div>
    );
  }

  const items = recommendations?.recommendations || [];
  const count = recommendations?.count ?? items.length ?? 0;
  const visibleItems = items.slice(0, MAX_VISIBLE_RECOMMENDATIONS);
  const remainingCount = count - visibleItems.length;

  return (
    <div className="recommendation-panel">
      <h2>AI Recommendations</h2>

      <div className="recommendation-summary">
        <div>
          <span className="recommendation-summary-label">Snapshot date:</span>{" "}
          {recommendations?.snapshot_date ?? "-"}
        </div>
        <div>
          <span className="recommendation-summary-label">Mode:</span>{" "}
          {recommendations?.use_llm ? "LLM" : "Rule-based AI"}
        </div>
        <div>
          <span className="recommendation-summary-label">Cases:</span> {count}
        </div>
      </div>

      {visibleItems.length === 0 ? (
        <p className="recommendation-empty">No students flagged</p>
      ) : (
        <div className="recommendation-student-list">
          {visibleItems.map((item, index) => (
            <div
              key={`${item?.student_id ?? "student"}-${index}`}
              className="recommendation-student-card"
            >
              <div className="recommendation-card-top">
                <div className="recommendation-student-name">
                  {fullName(item) || "Unnamed student"}
                </div>

                <div className={priorityClass(item?.priority)}>
                  {item?.priority ?? "low"}
                </div>
              </div>

              <div className="recommendation-student-email">
                {item?.email ?? "-"}
              </div>

              <div className="recommendation-signal">
                Signal: {item?.primary_signal ?? item?.label ?? "-"}
              </div>

              <div className="recommendation-action">
                Action: {prettyAction(item?.recommended_action)}
              </div>

              <div className="recommendation-reason">
                {item?.short_reason ?? "No reason provided."}
              </div>

              <div className="recommendation-metrics">
                {renderMetrics(item)}
              </div>
            </div>
          ))}

          {remainingCount > 0 && (
            <div className="recommendation-more">
              + {remainingCount} more
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RecommendationPanel;