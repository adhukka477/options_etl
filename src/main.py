
from src.postgres_conn import Session, engine
from models.db_models import Base, make_option_model
import yfinance as yf
import pandas as pd

from models.pydantic_models import OptionContract

tickers = ['SPY']

def main():

    OptionsDbModels = {ticker:make_option_model(ticker) for ticker in tickers}
    Base.metadata.create_all(engine)

    for ticker in tickers:
        options_exp_dates = yf.Ticker(ticker).options
        puts_chain = calls_chain = []
        for exp in options_exp_dates:
            opt = yf.Ticker(ticker).option_chain(exp)
            puts = opt.puts
            puts['option_type'] = 'PUT'
            puts_chain.append(opt.puts)
            calls = opt.calls
            calls['option_type'] = 'CALL'
            calls_chain.append(opt.calls)

        options_chain = pd.concat(puts_chain + calls_chain)
        validated_chain = [OptionContract(**x) for x in options_chain.to_dict(orient='records')]

        # Insert into DB
        with Session() as session:
            db_model = OptionsDbModels[ticker]
            db_objs = [db_model(
                contract_symbol=opt.contractSymbol,
                expiry_date=opt.expiry_date,
                option_type=opt.option_type,
                strike=opt.strike,
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
                vanna=opt.vanna,
                charm=opt.charm,
                veta=opt.veta,
                vomma=opt.vomma,
                speed=opt.speed,
                zomma=opt.zomma,
                color=opt.color,
                ultima=opt.ultima
            ) for opt in validated_chain]

            session.bulk_save_objects(db_objs)
            session.commit()