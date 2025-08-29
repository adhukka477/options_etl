import math
from datetime import datetime as dt
from py_vollib.black_scholes.greeks.analytical import delta, gamma, vega, theta

    # S = 100      # Spot
    # K = 100      # Strike
    # t = 30/365   # Time to expiry (in years)
    # r = 0.05     # Risk-free
    # sigma = 0.2  # Volatility
    # flag = 'c'   # 'c' for call, 'p' for put



def calculate_delta(data):
    
    flag = 'c' if data["option_type"].lower() == 'CALL' else 'p'
    S = data["strike"]
    K = data["underlying_price"]
    t = (data["expiry_date"] - dt.now()).total_seconds() / (365 * 24 * 60 * 60)
    sigma = data["impliedVolatility"]
    return delta(flag=flag, S=S, K=K, t = t, r=0.05, sigma=sigma)

def calculate_gamma(data):
    
    flag = 'c' if data["option_type"].lower() == 'CALL' else 'p'
    S = data["strike"]
    K = data["underlying_price"]
    t = (data["expiry_date"] - dt.now()).total_seconds() / (365 * 24 * 60 * 60)
    sigma = data["impliedVolatility"]
    
    return gamma(flag=flag, S=S, K=K, t = t, r=0.05, sigma=sigma)

def calculate_theta(data):
    
    flag = 'c' if data["option_type"].lower() == 'CALL' else 'p'
    S = data["strike"]
    K = data["underlying_price"]
    t = (data["expiry_date"] - dt.now()).total_seconds() / (365 * 24 * 60 * 60)
    sigma = data["impliedVolatility"]
    
    return theta(flag=flag, S=S, K=K, t = t, r=0.05, sigma=sigma)

def calculate_vega(data):
    
    flag = 'c' if data["option_type"].lower() == 'CALL' else 'p'
    S = data["strike"]
    K = data["underlying_price"]
    t = (data["expiry_date"] - dt.now()).total_seconds() / (365 * 24 * 60 * 60)
    sigma = data["impliedVolatility"]
    
    return vega(flag=flag, S=S, K=K, t = t, r=0.05, sigma=sigma)



