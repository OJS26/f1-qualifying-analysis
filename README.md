# How much does Saturday tell us about Sunday?

How much extra information does F1 qualifying give about a race result, beyond what we already know about the car and the team?

## The answer

Qualifying cuts the field of plausible winners from about **5.7 drivers to 3.7**. In log-loss terms, adding the starting grid improves out-of-sample winner prediction by **0.44 nats per race** (95% range 0.33 to 0.55), tested on 329 races from 2010 to 2025.

The result holds up against:
- a baseline that knows each team's true full-season strength (gain 0.36)
- Friday practice pace (gain 0.38)
- both dominant and close seasons, every era tested, and every circuit

This is a **predictive** result. It says nothing about whether pole position *causes* wins.

## Key numbers

| Question | Result |
|---|---|
| Pole-sitter wins | 52.6% of 329 races |
| Prediction loss, car and driver only | 1.747 |
| Prediction loss, adding the grid | 1.306 |
| Gain from the grid | 0.441 (95% range 0.326 to 0.554) |
| Gain when the baseline knows the full season | 0.359 |
| Gain when the baseline includes Friday practice | 0.384 |

*Full method, caveats and how to reproduce it: see below.*