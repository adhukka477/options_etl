
from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime, date
from typing import Optional


class OptionContract(BaseModel):

    contractSymbol: str
    expiry_date: date
    option_type: str
    strike: float
    lastTradeDate: Optional[datetime]
    lastPrice: Optional[float]
    bid: Optional[float]
    ask: Optional[float]
    volume: Optional[int]
    openInterest: Optional[int]
    impliedVolatility: Optional[float]
    delta: Optional[float]
    vega: Optional[float]
    theta: Optional[float]
    gamma: Optional[float]
    vanna: Optional[float]
    charm: Optional[float]
    veta: Optional[float]
    vomma: Optional[float]
    speed: Optional[float]
    zomma: Optional[float]
    color: Optional[float]
    ultima: Optional[float]
    created_ts: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('delta')
    def add_delta(cls, v, values):
        return v

    @field_validator('vega')
    def add_vega(cls, v, values):
        return v

    @field_validator('theta')
    def add_theta(cls, v, values):
        return v

    @field_validator('gamma')
    def add_gamma(cls, v, values):
        return v

    @field_validator('vanna')
    def add_vanna(cls, v, values):
        return v

    @field_validator('charm')
    def add_charm(cls, v, values):
        return v

    @field_validator('veta')
    def add_veta(cls, v, values):
        return v

    @field_validator('vomma')
    def add_vomma(cls, v, values):
        return v

    @field_validator('speed')
    def add_speed(cls, v, values):
        return v

    @field_validator('zomma')
    def add_zomma(cls, v, values):
        return v

    @field_validator('color')
    def add_color(cls, v, values):
        return v

    @field_validator('ultima')
    def add_ultima(cls, v, values):
        return v
    
    class Config:
        orm_mode = True
