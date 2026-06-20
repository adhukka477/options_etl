import requests


def get_optionable_tickers():
    
    tickers = requests.get(url = "http://localhost:80/companies/symbols")

    optionable_tickers = [x["symbol"] for x in tickers.json() if (x.get("is_optionable", False) and not x.get("is_archived", True))]

    return optionable_tickers

tickers = get_optionable_tickers()