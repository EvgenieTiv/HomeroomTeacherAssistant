SELECT
    s."UserId",
    COUNT(*) AS total_submissions,
    ROUND(AVG(s."Grade"::int), 2) AS avg_grade,
    MIN(s."Grade"::int) AS min_grade,
    MAX(s."Grade"::int) AS max_grade
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
GROUP BY s."UserId"
HAVING AVG(s."Grade"::int) >= 90
ORDER BY avg_grade DESC;
