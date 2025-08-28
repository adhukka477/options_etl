
from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime, date
from typing import Optional
from greeks import *


class OptionContract(BaseModel):

    contractSymbol: str
    expiry_date: datetime
    option_type: str
    strike: float
    underlying:float
    lastTradeDate: Optional[datetime]
    lastPrice: Optional[float] = Field(default = None)
    bid: Optional[float] = Field(default = None)
    ask: Optional[float] = Field(default = None)
    volume: Optional[int] = Field(default=None)
    openInterest: Optional[int] = Field(default=None)
    impliedVolatility: Optional[float] = Field(default=None)
    delta: Optional[float] = Field(default=None)
    vega: Optional[float] = Field(default=None)
    theta: Optional[float] = Field(default=None)
    gamma: Optional[float] = Field(default=None)
    created_ts: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('delta', pre=True, always=True)
    def add_delta(cls, v, values):
        return calculate_delta(values)

    @validator('vega', pre=True, always=True)
    def add_vega(cls, v, values):
        return calculate_vega(values)

    @validator('theta', pre=True, always=True)
    def add_theta(cls, v, values):
        return calculate_theta(values)

    @validator('gamma', pre=True, always=True)
    def add_gamma(cls, v, values):
        return calculate_gamma(values)


    
    class Config:
        orm_mode = True
