import numpy as np
from scipy.optimize import minimize
import pandas as pd

def prepare(table):
    """Fill first-race blanks and mark each race's winner."""
    df = table.copy()
    df["team_form"] = df["team_form"].fillna(0.5)
    df["driver_rel"] = df["driver_rel"].fillna(0.0)
    df["won"] = (df["position_number"] == 1).astype(int)
    df["log_grid"] = np.log(df["grid"])
    df["is_pole"] = (df["grid"] == 1).astype(int)
    if "team_pace" in df:
        df["team_pace"] = df["team_pace"].fillna(
            df.groupby("race_id")["team_pace"].transform("median")
        )
        df["team_pace"] = df["team_pace"].fillna(df["team_pace"].median())
    return df


def neg_log_lik(beta, X, won, race):
    """Negative log-likelihood of the winners under a conditional logit."""
    eta = X @ beta
    top = eta.groupby(race).transform("max")
    lse = top + np.log(np.exp(eta - top).groupby(race).transform("sum"))
    return -(eta - lse)[won == 1].sum()


def fit(X, won, race):
    """Find the weights that minimise the negative log-likelihood."""
    start = np.zeros(X.shape[1])
    result = minimize(neg_log_lik, start, args=(X, won, race), method="BFGS")
    return result.x


def walk_forward(data, cols, years=range(2010,2026)):
    """Train on years before Y, score year Y, for each Y."""
    rows = []
    for y in years:
        train = data[data["year"] < y]
        test = data[data["year"] == y]
        beta = fit(train[cols], train["won"], train["race_id"])
        nll = neg_log_lik(beta, test[cols], test["won"], test["race_id"])
        rows.append({"year": y, "races": test["race_id"].nunique(), "nll": nll})
    return pd.DataFrame(rows)


def win_prob(beta, X, race):
    """Each driver's win probability within their race."""
    eta = X @ beta
    top = eta.groupby(race).transform("max")
    e = np.exp(eta - top)
    return e / e.groupby(race).transform("sum")


def walk_forward_probs(data, cols, years=range(2010, 2026)):
    """Out-of-sample win probabilities for every test race."""
    out = []
    for y in years:
        train = data[data["year"] < y]
        test = data[data["year"] == y].copy()
        beta = fit(train[cols], train["won"], train["race_id"])
        test["p"] = win_prob(beta, test[cols], test["race_id"])
        out.append(test)
    return pd.concat(out)


def temper(p, race, T):
    """Flatten (T > 1) or sharpen (T < 1) probabilities within each race."""
    q = p ** (1 / T)
    return q / q.groupby(race).transform("sum")


def add_season_strength(data):
    """Each team's average score over the whole season (uses future races: oracle only)."""
    df = data.copy()
    df["season_form"] = df.groupby(["year", "team"])["finish_score"].transform("mean")
    return df