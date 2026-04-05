SELECT
    s."ContentId",
    c."Name" AS task_name,
    COUNT(*) AS submissions,
    ROUND(AVG(s."Grade"::int), 2) AS avg_grade,
    MIN(s."Grade"::int) AS min_grade,
    MAX(s."Grade"::int) AS max_grade,
    SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) AS low_grades,
    SUM(CASE WHEN s."Grade"::int = 0 THEN 1 ELSE 0 END) AS zero_grades
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
GROUP BY s."ContentId", c."Name"
ORDER BY s."ContentId";
