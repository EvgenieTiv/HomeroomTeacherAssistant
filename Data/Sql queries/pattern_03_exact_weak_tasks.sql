SELECT
    s."UserId",
    s."ContentId",
    c."Name" AS task_name,
    s."Grade"::int AS grade,
    s."CreatedDate"
FROM "Solutions" s
JOIN "Content" c ON s."ContentId" = c."Id"
WHERE c."CourseId" = 2
  AND c."ContentType" = 0
  AND s."UserId" IN (
      SELECT s2."UserId"
      FROM "Solutions" s2
      JOIN "Content" c2 ON s2."ContentId" = c2."Id"
      WHERE c2."CourseId" = 2
        AND c2."ContentType" = 0
      GROUP BY s2."UserId"
      HAVING AVG(s2."Grade"::int) >= 60
         AND SUM(CASE WHEN s2."Grade"::int < 60 THEN 1 ELSE 0 END) BETWEEN 1 AND 3
  )
  AND s."Grade"::int < 60
ORDER BY s."UserId", grade ASC;
