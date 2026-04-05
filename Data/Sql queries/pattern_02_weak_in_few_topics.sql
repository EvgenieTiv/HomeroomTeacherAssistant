WITH student_stats AS (
    SELECT
        s."UserId",
        COUNT(*) AS total_submissions,
        ROUND(AVG(s."Grade"::int), 2) AS avg_grade,
        SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) AS low_grade_count
    FROM "Solutions" s
    JOIN "Content" c ON s."ContentId" = c."Id"
    WHERE c."CourseId" = 2
      AND c."ContentType" = 0
    GROUP BY s."UserId"
)
SELECT *
FROM student_stats
WHERE avg_grade >= 60
  AND low_grade_count BETWEEN 1 AND 3
ORDER BY low_grade_count DESC, avg_grade DESC;
