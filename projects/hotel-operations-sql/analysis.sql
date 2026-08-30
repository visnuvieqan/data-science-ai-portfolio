-- Extracted from the original DataCamp/DataLab project workbook.
-- Raw course-provided datasets are not redistributed in this public portfolio.

SELECT DISTINCT target_guests FROM branch;

WITH standardised_branch AS (
    SELECT
        id,
        UPPER(TRIM(location)) AS location_clean,
        CASE WHEN TRIM(total_rooms::TEXT) ~ '^-?[0-9]+$' THEN CAST(TRIM(total_rooms::TEXT) AS INTEGER) ELSE NULL END AS total_rooms_num,
        CASE WHEN TRIM(staff_count::TEXT) ~ '^-?[0-9]+$' THEN CAST(TRIM(staff_count::TEXT) AS INTEGER) ELSE NULL END AS staff_count_num,
        CASE WHEN TRIM(opening_date::TEXT) ~ '^-?[0-9]+$' THEN CAST(TRIM(opening_date::TEXT) AS INTEGER) ELSE NULL END AS opening_date_num,
        INITCAP(TRIM(REPLACE(REPLACE(target_guests, 'Busniess', 'Business'), 'B.', 'Business'))) AS target_guests_clean
    FROM branch
)
SELECT
    id,
    CASE WHEN location_clean IN ('EMEA', 'NA', 'LATAM', 'APAC') THEN location_clean ELSE 'Unknown' END AS location,
    CASE WHEN total_rooms_num BETWEEN 1 AND 400 THEN total_rooms_num ELSE 100 END AS total_rooms,
    CASE
        WHEN staff_count_num IS NULL OR staff_count_num < 0
            THEN (CASE WHEN total_rooms_num BETWEEN 1 AND 400 THEN total_rooms_num ELSE 100 END) * 1.5
        ELSE staff_count_num
    END AS staff_count,
    CASE WHEN opening_date_num BETWEEN 2000 AND 2023 THEN opening_date_num ELSE 2023 END AS opening_date,
    CASE WHEN target_guests_clean IN ('Leisure', 'Business') THEN target_guests_clean ELSE 'Leisure' END AS target_guests
FROM standardised_branch;

SELECT
    service_id,
    branch_id,
    ROUND(AVG(time_taken), 2) AS avg_time_taken,
    ROUND(MAX(time_taken)::NUMERIC, 2) AS max_time_taken
FROM request
GROUP BY service_id, branch_id;

SELECT
    s.description,
    b.id AS id,
    b.location,
    r.id AS request_id,
    r.rating
FROM request AS r
JOIN service AS s ON r.service_id = s.id
JOIN branch AS b ON r.branch_id = b.id
WHERE s.description IN ('Meal', 'Laundry')
  AND b.location IN ('EMEA', 'LATAM');

SELECT
    service_id,
    branch_id,
    ROUND(AVG(rating), 2) AS avg_rating
FROM request
GROUP BY service_id, branch_id
HAVING AVG(rating) < 4.5;
