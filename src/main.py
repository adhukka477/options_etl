import pytz
from postgres_conn import Session, init_pgconn
from models.db_models import OptionsEodHistory
from yahoo_finance import (
    check_market_status,
    fetch_last_price,
    fetch_options_chain,
    available_exp_dates,
)
import datetime
from models.pydantic_models import OptionContract
import time
from tickers import tickers
from sqlalchemy.dialects.postgresql import insert
import numpy as np

np.seterr(all="ignore")


init_pgconn()

cst = pytz.timezone("US/Central")


def insert_options(ticker, data):

    # Insert into DB with upsert on conflict
    with Session() as session:
        rows = [
            {
                "symbol": str(ticker).upper(),
                "contract_symbol": opt.contractSymbol,
                "expiry_date": opt.expiry_date,
                "option_type": opt.option_type,
                "strike": opt.strike,
                "underlying_price": opt.underlying_price,
                "last_trade_date": opt.lastTradeDate,
                "last_price": opt.lastPrice,
                "bid": opt.bid,
                "ask": opt.ask,
                "volume": opt.volume,
                "open_interest": opt.openInterest,
                "implied_volatility": opt.impliedVolatility,
                "delta": opt.delta,
                "vega": opt.vega,
                "theta": opt.theta,
                "gamma": opt.gamma,
            }
            for opt in data
        ]

    stmt = insert(OptionsEodHistory).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="options_eod_history_unique",
        set_={
            "last_trade_date": stmt.excluded.last_trade_date,
            "last_price": stmt.excluded.last_price,
            "bid": stmt.excluded.bid,
            "ask": stmt.excluded.ask,
            "volume": stmt.excluded.volume,
            "open_interest": stmt.excluded.open_interest,
            "implied_volatility": stmt.excluded.implied_volatility,
            "delta": stmt.excluded.delta,
            "vega": stmt.excluded.vega,
            "theta": stmt.excluded.theta,
            "gamma": stmt.excluded.gamma,
        },
    )

    session.execute(stmt)
    session.commit()


def on_market_close_time():
    """Check if current time is between 3:30pm and 3:31pm CST"""
    current_time_cst = datetime.datetime.now(cst)
    current_hour = current_time_cst.hour
    current_minute = current_time_cst.minute

    return current_hour == 15 and 30 <= current_minute <= 31


def main():

    while True:
        time.sleep(1)
        # if ( True
        #     # on_market_close_time()
        #     # and check_market_status(datetime.datetime.now()) == "OPEN"
        # ):
        if True:
            print(
                f"*************  Starting ETL Process -- {datetime.datetime.now(cst)} CST  *************"
            )

            for ticker in tickers:
                options_exp_dates = available_exp_dates(ticker)
                if options_exp_dates:
                    options_chain = fetch_options_chain(
                        ticker=ticker, exp_dates=options_exp_dates
                    )
                else:
                    print(f"No options expiration dates found for {ticker}")
                    continue
                if not options_chain.empty:

                    validated_chain = []
                    underlying_price = fetch_last_price(ticker)
                    for x in options_chain.to_dict(orient="records"):
                        try:
                            x["underlying_price"] = underlying_price
                            validated_chain.append(OptionContract(**x))
                        except:
                            continue
                    insert_options(ticker=ticker, data=validated_chain)
                    print(f"Inserted {len(validated_chain)} records for {ticker}")
                else:
                    print(f"No options data found for {ticker}")
                    continue
                time.sleep(3)


main()
