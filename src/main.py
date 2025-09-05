import pytz
from postgres_conn import Session, engine, init_pgconn
from models.db_models import Base, make_option_model
import yfinance as yf
import pandas as pd
import datetime
from models.pydantic_models import OptionContract
import time
import pandas_market_calendars as mcal
import holidays

init_pgconn()

market_open_datetime = datetime.datetime.strptime("08:31:00.00", "%H:%M:%S.%f")
market_close_datetime = datetime.datetime.strptime("15:01:00.00", "%H:%M:%S.%f")

tickers = ["SPY"]
OptionsDbModels = {ticker: make_option_model(ticker) for ticker in tickers}
Base.metadata.create_all(engine)


def calculate_exp_time(date):

    # 3:00 PM local time
    t = datetime.time(15, 0)

    # Combine into datetime
    dt = datetime.datetime.combine(datetime.datetime.strptime(date, "%Y-%m-%d"), t)

    # # Attach timezone (CST/CDT via America/Chicago)
    # cst = pytz.timezone("America/Chicago")
    # dt_cst = cst.localize(dt)

    return dt


def insert(ticker, data):

    # Insert into DB
    with Session() as session:
        db_model = OptionsDbModels[ticker]
        db_objs = [
            db_model(
                contract_symbol=opt.contractSymbol,
                expiry_date=opt.expiry_date,
                option_type=opt.option_type,
                strike=opt.strike,
                underlying_price=opt.underlying_price,
                last_trade_date=opt.lastTradeDate,
                last_price=opt.lastPrice,
                bid=opt.bid,
                ask=opt.ask,
                volume=opt.volume,
                open_interest=opt.openInterest,
                implied_volatility=opt.impliedVolatility,
                delta=opt.delta,
                vega=opt.vega,
                theta=opt.theta,
                gamma=opt.gamma,
            )
            for opt in data
        ]

        session.bulk_save_objects(db_objs)
        session.commit()


def fetch_options_chain(ticker, exp_dates):

    puts_chain = []
    calls_chain = []
    for exp in exp_dates:
        opt = yf.Ticker(ticker).option_chain(exp)
        puts = opt.puts
        puts["option_type"] = "PUT"
        puts["expiry_date"] = calculate_exp_time(date=exp)
        puts_chain.append(opt.puts)
        calls = opt.calls
        calls["option_type"] = "CALL"
        calls["expiry_date"] = calculate_exp_time(date=exp)
        calls_chain.append(opt.calls)

    chain = pd.concat(puts_chain + calls_chain)
    chain.dropna(inplace=True)

    return chain


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


def log_status_update(status):
    match status:
        case "OPEN":
            print("Markets Are Open!")
        case "CLOSED":
            print("Markets Are Closed!")
        case "HOLIDAY":
            print("Market Holiday!")
        case "WEEKEND":
            print("Markets Closed for Weekend!")


def main():

    print("Starting ETL Process")
    previous_status = None
    next_capture_datetime = market_open_datetime

    while True:

        current_datetime = datetime.datetime.now()

        market_status = check_market_status(current_datetime)
        if market_status != previous_status:
            log_status_update(market_status)
        previous_status = market_status

        if current_datetime.time() >= market_close_datetime.time():
            next_capture_datetime = market_open_datetime

        if market_status == "OPEN":
            if (
                current_datetime.time() >= next_capture_datetime.time()
                and current_datetime.time() <= market_close_datetime.time()
            ):
                print(f"{current_datetime} - Fetching Data")
                for ticker in tickers:
                    options_exp_dates = yf.Ticker(ticker).options[0]
                    options_chain = fetch_options_chain(
                        ticker=ticker, exp_dates=[options_exp_dates]
                    )
                    options_chain["underlying_price"] = (
                        yf.Ticker(ticker)
                        .history(period="1d", interval="1d")["Close"]
                        .to_list()[-1]
                    )
                    validated_chain = [
                        OptionContract(**x)
                        for x in options_chain.to_dict(orient="records")
                    ]
                    insert(ticker=ticker, data=validated_chain)

                next_capture_datetime = next_capture_datetime + datetime.timedelta(
                    minutes=1
                )

        time.sleep(1)


main()
