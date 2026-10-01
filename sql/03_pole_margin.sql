-- Pole-sitter's margin over second place in qualifying, in milliseconds.
SELECT race_id, gap_millis AS pole_margin_ms
FROM qualifying_result
WHERE position_number = 2;