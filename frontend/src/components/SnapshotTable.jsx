import React from "react";
import "../styles/table.css";

function formatDate(value) {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("en-GB");
}

function formatRate(value) {
  if (value === null || value === undefined) return "-";
  return `${Math.round(value * 100)}%`;
}

function SnapshotTable({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="table-wrapper">
        <h2>Student Snapshot</h2>
        <p>No data loaded yet.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <h2>Student Snapshot</h2>

      <table className="snapshot-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Email</th>
            <th>Total Assignments</th>
            <th>Submitted</th>
            <th>Submission Rate</th>
            <th>Late</th>
            <th>Average Grade</th>
            <th>Recent Avg</th>
            <th>Last Submission</th>
            <th>Days Since Last</th>
          </tr>
        </thead>
        <tbody>
          {data.map((student) => (
            <tr key={student.student_id}>
              <td>{student.FirstName} {student.LastName}</td>
              <td>{student.Email}</td>
              <td>{student.total_assignments_available ?? "-"}</td>
              <td>{student.submitted_assignments ?? "-"}</td>
              <td>{formatRate(student.submission_rate)}</td>
              <td>{student.late_submissions ?? "-"}</td>
              <td>{student.average_grade ?? "-"}</td>
              <td>{student.recent_average_grade ?? "-"}</td>
              <td>{formatDate(student.last_submission_date)}</td>
              <td>{student.days_since_last_submission ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SnapshotTable;