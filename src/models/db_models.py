from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class OptionsEodHistory(Base):
    """
    SQLAlchemy model for options_dba.options_eod_history table.
    Stores end-of-day historical options data.
    """

    __tablename__ = "options_eod_history"
    __table_args__ = {"schema": "options_dba"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    contract_symbol = Column(String(32), nullable=False, index=True)
    expiry_date = Column(Date, nullable=False, index=True)
    option_type = Column(String(4), nullable=False, index=True)  # 'C' or 'P'
    strike = Column(Numeric(10, 2), nullable=False, index=True)
    underlying_price = Column(Numeric(10, 4), nullable=False)
    last_trade_date = Column(DateTime(timezone=True), nullable=True)
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
    report_date = Column(Date, server_default=func.current_date(), nullable=False)
