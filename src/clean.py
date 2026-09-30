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