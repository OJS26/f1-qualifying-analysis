import numpy as np
from scipy.optimize import minimize

def prepare(table):
    """Fill first-race blanks and mark each race's winner."""
    df = table.copy()
    df["team_form"] = df["team_form"].fillna(0.5)
    df["driver_rel"] = df["driver_rel"].fillna(0.0)
    df["won"] = (df["position_number"] == 1).astype(int)
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