SELECT
    s."UserId",
    COUNT(*) AS total_submissions,
    SUM(CASE WHEN s."CreatedDate" > c."LastAllowedDate" THEN 1 ELSE 0 END) AS late_submissions,
    SUM(CASE WHEN s."Grade"::int = 0 THEN 1 ELSE 0 END) AS zero_grades
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
GROUP BY s."UserId"
HAVING SUM(CASE WHEN s."CreatedDate" > c."LastAllowedDate" THEN 1 ELSE 0 END) >= 3
ORDER BY late_submissions DESC, zero_grades DESC;
