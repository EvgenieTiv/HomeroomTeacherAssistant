SELECT
    s."UserId",
    COUNT(*) AS total_submissions,
    ROUND(AVG(s."Grade"::int), 2) AS avg_grade,
    SUM(CASE WHEN s."Grade"::int = 0 THEN 1 ELSE 0 END) AS zero_grades,
    SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) AS low_grades
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
GROUP BY s."UserId"
HAVING AVG(s."Grade"::int) < 40
    OR SUM(CASE WHEN s."Grade"::int = 0 THEN 1 ELSE 0 END) >= 5
ORDER BY avg_grade ASC, zero_grades DESC;
