SELECT
    s."ContentId",
    c."Name" AS task_name,
    COUNT(*) AS total_submissions,
    SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) AS low_grades,
    ROUND(
        100.0 * SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS low_grade_percent,
    ROUND(AVG(s."Grade"::int), 2) AS avg_grade
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
GROUP BY s."ContentId", c."Name"
HAVING 100.0 * SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) / COUNT(*) >= 80
ORDER BY low_grade_percent DESC, avg_grade ASC;
