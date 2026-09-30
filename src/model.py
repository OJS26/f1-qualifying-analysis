def prepare(table):
    """Fill first-race blanks and mark each race's winner."""
    df = table.copy()
    df["team_form"] = df["team_form"].fillna(0.5)
    df["driver_rel"] = df["driver_rel"].fillna(0.0)
    df["won"] = (df["position_number"] == 1).astype(int)
    return df