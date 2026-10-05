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


def build_drivers(pa, pg, pc):
    """One row per driver per test race, with each model's win chance."""
    keys = ["race_id", "driver_id"]
    out = pa[keys + ["year", "round", "team", "grid",
                     "qualification_position_number", "position_number", "won", "p"]]
    out = out.rename(columns={"p": "p_base"})
    out = out.merge(pg[keys + ["p"]].rename(columns={"p": "p_grid"}), on=keys)
    out = out.merge(pc[keys + ["p"]].rename(columns={"p": "p_grid_pole"}), on=keys)
    return out


def build_pairs(pairs, table):
    """Neighbouring qualifiers with both cars' grid slots and finishes."""
    pairs = pairs[pairs["gap_ms"] >= 0]
    res = table.set_index(["race_id", "driver_id"])[["position_number", "grid"]]
    out = pairs.join(res, on=["race_id", "driver_id"])
    out = out.join(res.add_suffix("_back"), on=["race_id", "driver_id_back"])
    out = out.dropna(subset=["position_number", "position_number_back"]).copy()

    out["front_ahead"] = (out["position_number"] < out["position_number_back"]).astype(int)
    out["flipped"] = (out["grid"] > out["grid_back"]).astype(int)
    out["slot_ahead_won"] = np.where(out["flipped"] == 1, 1 - out["front_ahead"], out["front_ahead"])
    out["near_tie"] = (out["gap_ms"] < 100).astype(int)
    return out[["race_id", "year", "driver_id", "driver_id_back", "qpos", "group",
                "gap_ms", "grid", "grid_back", "position_number", "position_number_back",
                "front_ahead", "flipped", "slot_ahead_won", "near_tie"]]
