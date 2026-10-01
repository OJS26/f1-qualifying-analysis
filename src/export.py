import numpy as np
import pandas as pd


def race_gains(pa, pg):
    """Per-race loss with and without the grid, for the test years."""
    def loss(p, name):
        w = p[p["won"] == 1]
        return pd.Series(-np.log(w["p"].values), index=w["race_id"].values, name=name)

    return pd.concat([loss(pa, "loss_base"), loss(pg, "loss_grid")], axis=1)


def build_races(data, pa, pg, circuits, margins, dominant_years):
    """One row per test race, ready for Tableau."""
    gains = race_gains(pa, pg)
    gains["gain"] = gains["loss_base"] - gains["loss_grid"]

    pole = pg[pg["grid"] == 1].groupby("race_id").agg(
        pole_driver=("driver_id", "first"),
        pole_won=("won", "max"),
        pole_p_base=("p", "first"),
    )
    pole["pole_p_base"] = pa[pa["grid"] == 1].groupby("race_id")["p"].first()

    info = data.drop_duplicates("race_id").set_index("race_id")[
        ["year", "round", "date", "circuit_id", "is_sprint_grid"]
    ]
    out = info.join(gains, how="inner").join(pole, how="left")
    out = out.join(margins.set_index("race_id"), how="left")
    out["pole_won"] = out["pole_won"].fillna(0).astype(int)
    qual = data[data["qualification_position_number"] == 1].groupby("race_id")["won"].max()
    out["qual_pole_won"] = qual.reindex(out.index).fillna(0).astype(int)
    out["dominant_season"] = out["year"].isin(dominant_years)

    circ = circuits.set_index("id")[["name", "country_id", "latitude", "longitude", "type"]]
    circ.columns = ["circuit_name", "country", "latitude", "longitude", "circuit_type"]
    return out.join(circ, on="circuit_id").rename_axis("race_id").reset_index()