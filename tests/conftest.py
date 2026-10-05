import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def returns() -> pd.DataFrame:
    """Four years of synthetic daily simple returns for three assets with different vols."""
    rng = np.random.default_rng(42)
    idx = pd.bdate_range("2018-01-01", "2021-12-31")
    vols = np.array([0.18, 0.07, 0.15]) / np.sqrt(252)
    data = rng.normal(0.0002, vols, size=(len(idx), 3))
    return pd.DataFrame(data, index=idx, columns=["EQ", "FX", "AU"])
