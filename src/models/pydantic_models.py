from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime, date
from typing import Optional
from greeks import *


class OptionContract(BaseModel):

    contractSymbol: str
    expiry_date: datetime
    option_type: str
    strike: float
    underlying_price: float
    lastTradeDate: Optional[datetime]
    lastPrice: Optional[float] = Field(default=None)
    bid: Optional[float] = Field(default=None)
    ask: Optional[float] = Field(default=None)
    volume: Optional[int] = Field(default=None)
    openInterest: Optional[int] = Field(default=None)
    impliedVolatility: Optional[float] = Field(default=None)
    delta: Optional[float] = Field(default=None)
    vega: Optional[float] = Field(default=None)
    theta: Optional[float] = Field(default=None)
    gamma: Optional[float] = Field(default=None)
    created_ts: Optional[datetime] = Field(default_factory=datetime.now)

    # --- Clean up NaN or None values
    @validator(
        "lastPrice",
        "bid",
        "ask",
        "volume",
        "openInterest",
        "impliedVolatility",
        "delta",
        "vega",
        "theta",
        "gamma",
        pre=True,
        always=True,
    )
    def clean_nan_values(cls, v):
        if v is None:
            return None
        try:
            if isinstance(v, float) and math.isnan(v):
                return None
        except TypeError:
            pass
        return v

    @validator("delta", pre=True, always=True)
    def add_delta(cls, v, values):
        try:
            result = calculate_delta(values)
            if math.isnan(result):
                result = None
        except:
            result = None
        return result

    @validator("vega", pre=True, always=True)
    def add_vega(cls, v, values):
        try:
            result = calculate_vega(values)
            if math.isnan(result):
                result = None
        except:
            result = None
        return result

    @validator("theta", pre=True, always=True)
    def add_theta(cls, v, values):
        try:
            result = calculate_theta(values)
            if math.isnan(result):
                result = None
        except:
            result = None
        return result

    @validator("gamma", pre=True, always=True)
    def add_gamma(cls, v, values):
        try:
            result = calculate_gamma(values)
            if math.isnan(result):
                result = None
        except:
            result = None
        return result

    class Config:
        orm_mode = True
