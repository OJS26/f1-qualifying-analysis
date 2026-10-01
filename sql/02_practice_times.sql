-- Practice lap times from FP1 and FP2, one row per driver per session.
SELECT race_id, driver_id, time_millis
FROM free_practice_1_result
UNION ALL
SELECT race_id, driver_id, time_millis
FROM free_practice_2_result;