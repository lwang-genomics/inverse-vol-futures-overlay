"""Study configuration: instruments, backtest parameters and analysis periods."""

import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "prices.csv"
FIG_DIR = ROOT / "figures"
RES_DIR = ROOT / "results"
REPORT_DIR = ROOT / "report"

# label -> Yahoo Finance symbol
TICKERS = {
    # Futures: Yahoo continuous front month (not back-adjusted); used only for the roll-bias check
    "ES": "ES=F",  # E-mini S&P 500
    "DX": "DX-Y.NYB",  # ICE US Dollar Index (DX=F has no Yahoo history)
    "GC": "GC=F",  # COMEX gold
    "ZN": "ZN=F",  # CBOT 10-year T-note
    # US-listed ETFs
    "SPY": "SPY",
    "UUP": "UUP",
    "GLD": "GLD",
    "IEF": "IEF",  # iShares 7-10y Treasury
    # UCITS equity sleeves, London USD lines
    "CSPX": "CSPX.L",  # iShares Core S&P 500 UCITS (Acc); same fund as SXR8 (Xetra)
    "VWRD": "VWRD.L",  # Vanguard FTSE All-World UCITS (Dist); same fund as VWCE (Acc)
    "VWRA": "VWRA.L",  # Vanguard FTSE All-World UCITS (Acc), 2019+; used as a check
    # Long-history world-equity proxy (US-listed, US close): SPY + total international
    "VGTSX": "VGTSX",  # Vanguard Total International Stock Index (incl. EM), from 1996
    "ACWI": "ACWI",  # iShares MSCI ACWI, from 2008; used to validate the proxy
    # Risk-free rate for ETF/UCITS Sharpe ratios (futures returns are already excess returns)
    "TBILL": "^IRX",  # 13-week T-bill yield, % p.a.
}
START = "2000-01-01"

# Futures returns: back-adjusted (Panama) daily futures from the open-source pysystemtrade project, pinned to one
# commit, so that each roll's price gap is not counted as a return and carry is included. Its free data end on
# SPLICE_END; afterwards each leg continues with the excess return over T-bills of a total-return ETF on the same
# asset. The Yahoo front-month series (TICKERS) are kept only to measure the bias of unadjusted rolls.
FUTURES_COMMIT = "4420802541a561b8de1b95ef3b43ccc708b2e987"
FUTURES_URL = "https://raw.githubusercontent.com/pst-group/pysystemtrade/{}/data/futures/{}"
SPLICE_END = "2024-03-28"
BACKADJ = {  # study label -> (pysystemtrade instrument, ETF used after SPLICE_END)
    "ES": ("SP500", "SPY"),
    "DX": ("DX", "UUP"),
    "GC": ("GOLD", "GLD"),
    "ZN": ("US10", "IEF"),
}
END = date.today().isoformat()  # yfinance `end` is exclusive -> last complete session

# Backtest
TRADING_DAYS = 252
LOOKBACK_DAYS = 252  # trailing ~1y window for inverse-vol estimation
MIN_TRAIN_DAYS = 200
COST_BPS = 10.0  # cost per unit of traded notional (spread + commission + slippage)
MAIN_FREQ = 3  # rebalance every 3 months, at quarter-end close
FREQS = {"Monthly": 1, "Quarterly": 3, "Semi-annual": 6, "Annual": 12}
TRAD_WEIGHTS = (0.60, 0.30, 0.10)  # equity / 10y Treasury / gold
VOL_TARGET = 0.10  # ex-ante volatility target for the futures overlay
MAX_LEVERAGE = 3.0

# Statistics and display
BOOT_BLOCK = 63  # moving-block bootstrap: ~3-month blocks
BOOT_N = 2000
ROLL_CORR_WINDOW = 52  # weeks: correlations use weekly returns (futures settle at different times of day)
ROLL_SHARPE_WINDOW = 3 * 252
DISPLAY_LOG_TARGET = math.log(1.10)  # path-shape plots: 10% avg annual endpoint
WORLD_US_WEIGHT = 0.50  # world proxy = 50% SPY + 50% VGTSX (calibrated to ACWI, 2008+)

# Baskets are ordered [equity, defensive, gold]
FUT_USD = ["ES", "DX", "GC"]
FUT_TRAD = ["ES", "ZN", "GC"]
ETF_USD = ["SPY", "UUP", "GLD"]
ETF_TRAD = ["SPY", "IEF", "GLD"]

PORTS = ["iv_usd", "iv_trad", "fixed_trad"]
PORT_LABELS = {
    "iv_usd": "Inv-vol USD",
    "iv_trad": "Inv-vol Trad",
    "fixed_trad": "Fixed 60/30/10",
}

STRESS_PERIODS = {
    "2002 dot-com bear (final leg)": ("2002-01-01", "2002-10-09"),
    "2007–09 GFC": ("2007-10-09", "2009-03-09"),
    "2018 Q4 sell-off": ("2018-09-20", "2018-12-24"),
    "2020 COVID crash": ("2020-02-19", "2020-03-23"),
    "2022 rate shock": ("2022-01-03", "2022-10-12"),
    "2025 tariff shock": ("2025-02-19", "2025-04-08"),
}
REGIMES = {
    "2001–07": ("2001-01-01", "2007-06-30"),
    "GFC\n2007–09": ("2007-07-01", "2009-06-30"),
    "QE era\n2009–19": ("2009-07-01", "2019-12-31"),
    "COVID\n2020–21": ("2020-01-01", "2021-12-31"),
    "Inflation\n2022–26": ("2022-01-01", "2100-01-01"),
}
SUBPERIODS = {
    "2001–2012": ("2001-01-01", "2012-12-31"),
    "2013–2021": ("2013-01-01", "2021-12-31"),
    "2022–2026": ("2022-01-01", "2100-01-01"),
}
EQUITY_ERAS = {
    "2000–2011": ("2000-01-01", "2011-12-31"),
    "2012–2026": ("2012-01-01", "2100-01-01"),
}
