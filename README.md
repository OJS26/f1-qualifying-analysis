# How much does Saturday tell us about Sunday?

How much extra information does F1 qualifying give about a race result, beyond what we already know about the car and the team?

**Live dashboard:** [How much does Saturday tell us about Sunday?](https://public.tableau.com/app/profile/oliver.strachan/viz/HowmuchdoesSaturdaytellusaboutSunday-anF1analysis_17913068630510/Dashboard1)

## The answer

Qualifying cuts the field of plausible winners from about **5.7 drivers to 3.7**, and lifts the typical chance given to the eventual winner from **17% to 27%**. This is tested on 329 races from 2010 to 2025, with every race scored by a model that had never seen it.

The accuracy score behind it is log loss, which measures how surprised the model is by the real winner (lower is better, and the unit is called a nat). Adding the starting grid cuts it by **0.44 per race** (95% range 0.33 to 0.55).

The result holds up against:
- a baseline that knows each team's true full-season strength (gain 0.36)
- Friday practice pace (gain 0.38)
- both dominant and close seasons, every era tested, and every circuit

## Key numbers

| Question | Result |
|---|---|
| Fastest qualifier wins | 52.6% of 329 races |
| Driver on grid slot 1 wins | 52.3% of 329 races |
| Prediction loss, car and driver only | 1.747 |
| Prediction loss, adding the grid | 1.306 |
| Gain from the grid | 0.441 (95% range 0.326 to 0.554) |
| Gain when the baseline knows the full season | 0.359 |
| Gain when the baseline includes Friday practice | 0.384 |

*Full method, caveats and how to reproduce it: see below.*


## How it works

**The question, in plain words.** Before qualifying, what do we already know about who will win? Mainly how strong the car is, and a little about the driver. The model asks how much *better* the prediction gets once we also know the starting grid.

**Baseline (knows everything except qualifying).**
- *Team form*: the team's recent finishing results, with recent races counting more (a result 6 races ago counts half as much). A retirement scores zero.
- *Driver edge*: how the driver has done against his teammate, who has the same car, averaged over a longer window (half-weight at 15 races).
- Both are built only from earlier races, so nothing from the future leaks in.

**The model.** Each driver gets a score, and a driver's chance of winning is their score compared with everyone else in that race (a conditional logit). Adding the grid means adding the log of the starting position as one more input.

**How it's tested.** Walk-forward: to predict 2015, fit the model on 2006 to 2014 only, then score 2015. Repeat for every year from 2010 to 2025 (329 races). Every race is scored by a model that has never seen it. The score is log loss on the actual winner, and 2026 (15 races, new regulations) is left untouched as a holdout.

**Robustness checks.** An "oracle" baseline that knows each team's full-season strength; Friday practice pace; dominant vs close seasons; three eras; every circuit (permutation test); pole margin; and a bootstrap range on the headline gain.

**Pace vs starting slot (suggestive only).** Two checks on whether the starting slot itself helps, beyond pace: neighbouring cars that qualified within 0.1 s of each other (front car finished ahead 53.5% of the time), and pairs where a penalty flipped the grid order (the car that started ahead finished ahead 60.2% of the time, on only 108 pairs). Both lean the same way, neither is strong.

## The dashboard

The findings are published as a Tableau dashboard: [How much does Saturday tell us about Sunday?](https://public.tableau.com/app/profile/oliver.strachan/viz/HowmuchdoesSaturdaytellusaboutSunday-anF1analysis_17913068630510/Dashboard1). The packaged workbook is also in this repo at `tableau/F1 Analysis.twbx`.

Each section asks one question and answers it with a different kind of chart:

1. **How often does the driver on pole actually win?** A ring and a season-by-season bar chart.
2. **How often would we expect them to win before qualifying?** A dumbbell chart, baseline against actual.
3. **How quickly does the win chance fall as drivers start further back?** Bars with a baseline line.
4. **Does Saturday only matter when one car is dominant?** A slope chart.
5. **Does Saturday matter more at some tracks than others?** An interactive map. Click a circuit for its numbers, and click it again to reset.
6. **Does starting in front help beyond pure pace?** Overlapping curves for the two slot-vs-pace checks.

### Data behind it

The notebook `notebooks/02_tableau_exports.ipynb` builds these files in `data/processed/`:

| File | What it holds | Used by |
|---|---|---|
| `races.csv` | One row per test race (329), with the grid's gain, pole result and circuit | Tiles, sections 1 to 5 |
| `drivers.csv` | One row per driver per test race, with each model's win chance | Section 3 |
| `pairs.csv` | Neighbouring qualifiers with both cars' grid slots and finishes | Section 6 checks |
| `checks.csv` | The two slot-vs-pace results with their rough 95% ranges | Builds `curves.csv` |
| `curves.csv` | Bell-curve points drawn from those ranges | Section 6 |
| `forest.csv` | Input for a chart that was dropped | Not used |

The pairs in `pairs.csv` run from 2006 to 2025 (393 races, 4,861 pairs), because nothing is fitted in that check. The rest of the dashboard covers 2010 to 2025.

The workbook carries its own copy of the data. If you re-export the CSVs, open the workbook, use **Data → Refresh**, and save again.

## Caveats

- **Predictive, not causal.** Nothing here shows that pole position causes wins.
- **Retirements count as zero**, so team form partly measures reliability, not only speed.
- **Practice pace is a noisy proxy.** Teams run different fuel loads and programmes on Friday, so qualifying adding value beyond it partly reflects that noise.
- **The oracle baseline uses future races** and is a deliberately tough comparison, not a real forecaster.
- **Sprint weekends:** in the 6 races where a sprint race set the 2021-22 grid, the grid is not a qualifying result. They are kept in the main model and flagged.
- **Three races have no pole-sitter in the data** (one DNS, two disqualified after the race). They count as non-wins in the pole win rate.
- **Early seasons are scored on little history.** 2010 is predicted from only 2006-09, which probably inflates the 2010-13 gain.
- **Circuits have only 8 to 17 races each**, so circuit averages are noisy.
- **The pole flag is an addition** to the original method, used to correct overconfidence at the top. Results with and without it are both shown.
- **Not reconciled with an earlier build:** an earlier version of this analysis found a gain of +0.29 against Friday practice (here +0.38) and a baseline loss of 1.72 (here 1.747). The practice-pace definitions differ, and I have not traced the rest.
- **Weather and grid-penalty reasons are not in the data.**

## Reproduce it

1. Clone the repo and create the environment:

```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
```


2. Download `f1db-sqlite.zip` from the f1db releases (version v2026.15.1 was used), unzip it, and put `f1db.db` in `data/raw/`.
3. Open `notebooks/01_explore_db.ipynb` and choose **Run All** to rebuild the analysis and every result in the tables above. (the notebook is the exploratory log, in the order it was written, and that the results in the README come from it cell by cell, not necessarily with Run All.)
4. Open `notebooks/02_tableau_exports.ipynb` and choose **Run All** to regenerate the files in `data/processed/`. The dashboard is the packaged workbook in `tableau/`, or the published link above.

## Project layout

```
sql/         queries that load results, practice times, pole margins, qualifying times
src/         clean.py (cleaning and features), model.py (model and testing), export.py (files for Tableau)
notebooks/   01_explore_db (the exploratory analysis) and 02_tableau_exports (builds the dashboard files)
data/raw/    the f1db database (not committed)
data/processed/  CSV files used by the dashboard
tableau/     the packaged Tableau workbook
```

## Data

Race data comes from [f1db](https://github.com/f1db/f1db), licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The data was filtered, cleaned and combined with derived features for this analysis, so it is modified from the original. No endorsement by f1db is implied.