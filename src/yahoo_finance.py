import yfinance as yf
import pandas as pd
import datetime
import pandas_market_calendars as mcal
import holidays

market_open_datetime = datetime.datetime.strptime("08:35:00.00", "%H:%M:%S.%f")
market_close_datetime = datetime.datetime.strptime("15:01:00.00", "%H:%M:%S.%f")
if (
    datetime.datetime.now().time() > market_open_datetime.time()
    and datetime.datetime.now().time() < market_close_datetime.time()
):
    market_open_datetime = datetime.datetime.now()


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
    elif current_datetime.time() >= market_close_datetime.time():
        return "CLOSED"
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
        return (
            yf.Ticker(ticker)
            .history(period="1wk", interval="1d")["Close"]
            .to_list()[-1]
        )
    except:
        return None
