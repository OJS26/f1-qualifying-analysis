DROPPED_LABELS = ["DNS", "DNQ", "DNP", "DSQ"]

def drop_non_starters(df):
    """Remove rows where the driver did not start the race (DNS), did not qualify (DNQ), did not participate (DNP), or was disqualified (DSQ)."""
    keep = ~df["position_text"].isin(DROPPED_LABELS)
    return df[keep].copy()


def fill_pit_lane_grid(df):
    """Give blank-grid starters a slot behind the last gridded car."""
    df = df.copy()
    df["grid"] = df["grid_position_number"]
    blanks = df[df["grid"].isna()]
    for race_id, group in blanks.groupby("race_id"):
        last = df.loc[df["race_id"] == race_id, "grid"].max()
        order = group.sort_values(
            "qualification_position_number", na_position="last"
        ).index
        for k, idx in enumerate(order, start=1):
            df.loc[idx, "grid"] = last + k
    return df


def flag_sprint_grid(df):
    """Mark races where the Sunday grid was set by a Sprint race."""
    df = df.copy()
    df["is_sprint_grid"] = df["qualifying_format"] == "SPRINT_RACE"
    return df


def add_finish_score(df):
    """Finishing score in [0, 1]: winner = 1, DNF/NC = 0"""
    df = df.copy()
    n = df.groupby("race_id")["driver_id"].transform("count")
    score = (n - df["position_number"] + 1) / n
    df["finish_score"] = score.fillna(0.0)
    return df


def team_race_scores(df):
    """One row per team per race: mean finish score of its drivers."""
    out = (
        df.groupby(["race_id", "year", "round", "constructor_id"], as_index=False)
        ["finish_score"]
        .mean()
        .rename(columns={"finish_score": "team_score"})
    )
    return out.sort_values(["year", "round"]).reset_index(drop=True)


def lineage_labels(chron):
    """Map each team ID to the latest name in its lineage."""
    latest = (
        chron.sort_values("year_from")
        .groupby("constructor_id")["other_constructor_id"]
        .last()
    )
    return latest.to_dict()


def add_lineage(df, labels):
    """Add a 'team' column: the lineage label, or the ID itself if standalone."""
    df = df.copy()
    df["team"] = df["constructor_id"].map(labels).fillna(df["constructor_id"])
    return df


def add_team_form(teams, halflife=6):
    """Team form before each race: exponentially weighted mean of past scores."""
    teams = teams.sort_values(["year", "round"]).copy()
    teams["team_form"] = teams.groupby("team")["team_score"].transform(
        lambda s: s.shift(1).ewm(halflife=halflife).mean()
    )
    return teams


def add_teammate_gap(df):
    """Finish score minus the mean score of teammates in the same race."""
    df = df.copy()
    grp = df.groupby(["race_id", "constructor_id"])["finish_score"]
    total = grp.transform("sum")
    count = grp.transform("count")
    mate_mean = (total - df["finish_score"]) / (count - 1)
    df["teammate_gap"] = df["finish_score"] - mate_mean
    return df


def add_driver_rel(df, halflife=15):
    """Driver skill before each race: EWMA of past teammate gaps."""
    df = df.sort_values(["year", "round"]).copy()
    df["driver_rel"] = df.groupby("driver_id")["teammate_gap"].transform(
        lambda s: s.shift(1).ewm(halflife=halflife).mean()
    )
    return df


def build_table(raw, chron):
    """Raw results in, one clean modelling row per driver per race out."""
    labels = lineage_labels(chron)

    df = drop_non_starters(raw)
    df = fill_pit_lane_grid(df)
    df = flag_sprint_grid(df)
    df = add_finish_score(df)
    df = add_teammate_gap(df)
    df = add_driver_rel(df)

    teams = team_race_scores(df)
    teams = add_lineage(teams, labels)
    teams = add_team_form(teams)

    form = teams[["race_id", "constructor_id", "team", "team_form"]]
    return df.merge(form, on=["race_id", "constructor_id"], how="left")