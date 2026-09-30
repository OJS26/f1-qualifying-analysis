-- One row per driver per race, 2006-2026 (2026 is the holdout)
-- Raw values onnly: no cleaning rules applied here

SELECT 
    rr.race_id,
    r.year,
    r.round,
    r.date,
    r.circuit_id,
    rr.driver_id,
    rr.constructor_id,
    rr.qualification_position_number,
    rr.qualification_position_text,
    rr.grid_position_number,
    rr.grid_position_text,
    rr.position_number,
    rr.position_text
FROM race_result rr
JOIN race r ON r.id = rr.race_id
WHERE r.year BETWEEN 2006 AND 2026
ORDER BY r.year, r.round, rr.position_display_order;