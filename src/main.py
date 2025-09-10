import pytz
from postgres_conn import Session, engine, init_pgconn
from models.db_models import Base, make_option_model
from yahoo_finance import (
    fetch_options_chain,
    market_close_datetime,
    market_open_datetime,
    check_market_status,
    available_exp_dates,
    fetch_last_price,
)
import datetime
from models.pydantic_models import OptionContract
import time


tickers = ["SPY"]

init_pgconn()
OptionsDbModels = {ticker: make_option_model(ticker) for ticker in tickers}
Base.metadata.create_all(engine)


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
                    options_exp_dates = available_exp_dates(ticker)[0]
                    options_chain = fetch_options_chain(
                        ticker=ticker, exp_dates=[options_exp_dates]
                    )
                    options_chain["underlying_price"] = fetch_last_price(ticker)
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
