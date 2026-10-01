-- Qualifying lap times by session, 2006-2025, excluding the 6 sprint-grid races.
SELECT qr.race_id, r.year, qr.driver_id,
       qr.position_number AS qpos,
       qr.q1_millis, qr.q2_millis, qr.q3_millis
FROM qualifying_result qr
JOIN race r ON r.id = qr.race_id
WHERE r.year BETWEEN 2006 AND 2025
  AND r.qualifying_format != 'SPRINT_RACE';