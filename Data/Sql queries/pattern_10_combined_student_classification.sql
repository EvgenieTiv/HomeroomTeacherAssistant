WITH student_base AS (
    SELECT
        s."UserId",
        COUNT(*) AS submissions,
        AVG(s."Grade"::int) AS avg_grade,
        MIN(s."Grade"::int) AS min_grade,
        MAX(s."Grade"::int) AS max_grade,
        SUM(CASE WHEN s."Grade"::int = 0 THEN 1 ELSE 0 END) AS zero_grades,
        SUM(CASE WHEN s."Grade"::int < 60 THEN 1 ELSE 0 END) AS low_grades,
        SUM(CASE WHEN s."CreatedDate" > c."LastAllowedDate" THEN 1 ELSE 0 END) AS late_submissions
    FROM "Solutions" s
    JOIN "Content" c ON s."ContentId" = c."Id"
    WHERE c."CourseId" = 2
      AND c."ContentType" = 0
    GROUP BY s."UserId"
)
SELECT
    "UserId",
    submissions,
    ROUND(avg_grade, 2) AS avg_grade,
    min_grade,
    max_grade,
    zero_grades,
    low_grades,
    late_submissions,
    CASE WHEN avg_grade < 40 OR zero_grades >= 5 THEN TRUE ELSE FALSE END AS struggling_all_topics,
    CASE WHEN avg_grade >= 60 AND low_grades BETWEEN 1 AND 3 THEN TRUE ELSE FALSE END AS weak_in_few_topics,
    CASE WHEN avg_grade >= 90 THEN TRUE ELSE FALSE END AS excellent,
    CASE WHEN submissions >= 5 AND (max_grade - min_grade) >= 50 THEN TRUE ELSE FALSE END AS unstable,
    CASE WHEN late_submissions >= 3 THEN TRUE ELSE FALSE END AS often_late
FROM student_base
ORDER BY avg_grade ASC, "UserId";
