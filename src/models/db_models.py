from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

def make_option_model(ticker: str):
    """
    Factory function to create a SQLAlchemy model for a specific ticker.
    Each ticker will have its own table: option_<TICKER>
    """
    tablename = f"{ticker.lower()}_options"

    class OptionContract(Base):
        __tablename__ = tablename
        __table_args__ = {"schema": "options_dba"}

        id = Column(Integer, primary_key=True, autoincrement=True)
        contract_symbol = Column(String(32), nullable=False, index=True)
        expiry_date = Column(Date, nullable=False, index=True)
        option_type = Column(String(4), nullable=False, index=True)   # 'C' or 'P'
        strike = Column(Numeric(10, 2), nullable=False, index=True)
        last_trade_date = Column(DateTime, nullable=True)
        last_price = Column(Numeric(10, 4), nullable=True)
        bid = Column(Numeric(10, 4), nullable=True)
        ask = Column(Numeric(10, 4), nullable=True)
        volume = Column(Integer, nullable=True)
        open_interest = Column(Integer, nullable=True)
        implied_volatility = Column(Float, nullable=True)
        delta = Column(Float, nullable=True)
        vega = Column(Float, nullable=True)
        theta = Column(Float, nullable=True)
        gamma = Column(Float, nullable=True)
        created_ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)


    return OptionContract
