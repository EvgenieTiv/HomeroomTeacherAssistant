import React from "react";
import "../styles/journal.css";

function formatShortDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-GB");
}

function cellClass(cell) {
  if (!cell || cell.status === "missing") return "journal-cell missing";

  const grade = cell.grade ?? null;
  const isLate = cell.is_late ?? false;

  if (grade !== null && grade < 60) return "journal-cell low-grade";
  if (isLate) return "journal-cell late";

  return "journal-cell normal";
}

function JournalTable({ journalData }) {
  if (!journalData || !journalData.rows || journalData.rows.length === 0) {
    return (
      <div className="journal-wrapper">
        <h2>Assignment Journal</h2>
        <p>No journal data loaded yet.</p>
      </div>
    );
  }

  const { assignments, rows } = journalData;

  return (
    <div className="journal-wrapper">
      <h2>Assignment Journal</h2>

      <div className="journal-scroll">
        <table className="journal-table">
          <thead>
            <tr>
              <th className="sticky-col student-col">Student</th>
              {assignments.map((assignment) => (
                <th key={assignment.assignment_id} className="assignment-col">
                  <div className="assignment-header-date">
                    {formatShortDate(assignment.created_date)}
                  </div>
                  <div className="assignment-header-title">
                    {assignment.title}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row) => (
              <tr key={row.student_id}>
                <td className="sticky-col student-col">
                  <div className="student-name">
                    {row.FirstName} {row.LastName}
                  </div>
                  <div className="student-email">{row.Email}</div>
                </td>

                {row.cells.map((cell, index) => {
                  const grade = cell?.grade ?? null;
                  const submittedAt = cell?.submitted_at ?? null;
                  const isLate = cell?.is_late ?? false;

                  return (
                    <td
                      key={`${row.student_id}-${index}`}
                      className={cellClass(cell)}
                    >
                      {cell?.status === "missing" ? (
                        <div className="cell-content">
                          <div className="cell-status">Not submitted</div>
                        </div>
                      ) : (
                        <div className="cell-content">
                          <div className="cell-grade">
                            Grade: {grade ?? "-"}
                          </div>

                          <div className="cell-date">
                            {formatShortDate(submittedAt)}
                          </div>

                          {isLate && (
                            <div className="cell-late-flag">Late</div>
                          )}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default JournalTable;