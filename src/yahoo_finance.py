import yfinance as yf
import pandas as pd
import datetime
import shutil
from pathlib import Path
import pandas_market_calendars as mcal
import holidays


YF_CACHE_DIR = Path(__file__).resolve().parents[1] / ".yfinance_cache"
YF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
yf.set_tz_cache_location(str(YF_CACHE_DIR))


def _clear_yfinance_cache():
    if YF_CACHE_DIR.exists() and YF_CACHE_DIR.is_dir():
        shutil.rmtree(YF_CACHE_DIR, ignore_errors=True)
    YF_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _is_corrupt_cache_error(exc: Exception) -> bool:
    return "database disk image is malformed" in str(exc).lower()

def available_exp_dates(ticker):
    try:
        dates = sorted(yf.Ticker(ticker).options)
        return dates
    except:
        print(f"Failed to fetch exp dates for {ticker}")
        return None


def check_market_status(current_datetime):

    # Get the NYSE calendar
    nyse = mcal.get_calendar("NYSE")
    us_holidays = holidays.US(years=current_datetime.year)

    # Check if it's a weekend, holiday, or past market close time
    if current_datetime.weekday() >= 5:
        return "WEEKEND"
    elif current_datetime in us_holidays:
        return "HOLIDAY"
    else:
        return "OPEN"


def calculate_exp_time(date):

    # 3:00 PM local time
    t = datetime.time(15, 0)

    # Combine into datetime
    dt = datetime.datetime.combine(datetime.datetime.strptime(date, "%Y-%m-%d"), t)

    # # Attach timezone (CST/CDT via America/Chicago)
    # cst = pytz.timezone("America/Chicago")
    # dt_cst = cst.localize(dt)

    return dt


def fetch_options_chain(ticker, exp_dates):

    puts_chain = []
    calls_chain = []
    for exp in exp_dates:
        try:
            opt = yf.Ticker(ticker).option_chain(exp)
            puts = opt.puts
            puts["option_type"] = "PUT"
            puts["expiry_date"] = calculate_exp_time(date=exp)
            puts_chain.append(opt.puts)
            calls = opt.calls
            calls["option_type"] = "CALL"
            calls["expiry_date"] = calculate_exp_time(date=exp)
            calls_chain.append(opt.calls)
        except:
            print(f"Failed to Fetch Chain for {ticker}")
            continue

    if puts_chain and calls_chain:
        chain = pd.concat(puts_chain + calls_chain)
        chain.dropna(inplace=True)

        return chain

    else:
        return pd.DataFrame()


def fetch_last_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1wk", interval="1d")["Close"].to_list()
        # Drop NaN values and return the last valid price
        data = [price for price in data if pd.notna(price)]
        if data:
            return data[-1]
        else:
            return None
    except:
        return None
    

def fetch_price_history(ticker):
    try:
        data = yf.Ticker(ticker).history(period="max", interval="1d", actions=False)
    except Exception as exc:
        if _is_corrupt_cache_error(exc):
            # yfinance keeps a local sqlite cache; remove it and retry once.
            _clear_yfinance_cache()
            data = yf.Ticker(ticker).history(period="max", interval="1d", actions=False)
        else:
            raise
    return data.reset_index()
