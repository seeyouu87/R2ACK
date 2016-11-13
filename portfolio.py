import numpy as np
import pandas as pd
import requests
import json
import singleton
import cubic_spline
import xignite

def get_returnrisk_stock(ISIN):
    data = xignite.get_stock_price_range(ISIN, "11/11/2015", "11/11/2016")
    ret = data["LastClose"].pct_change()
    value = data["LastClose"].values[-1]
    mu = ret.mean()*252
    sig2 = ret.var()
    return mu, np.sqrt(sig2*252), value

def get_return_bond(id, bond_price):
    df = bond_price[bond_price["Valoren"] == int(id)]

    ret = df['YieldToMaturity'].values
    value = df['market_price'].values

    if len(ret) == 1:
        return ret, value
    else:
        return ret[0], value[0]

def compute_portfolio_value(customer_id):
    profile = pd.read_csv("portfolios.csv")
    bond_price = pd.read_csv("bond_spread.csv")

    customer = profile[profile['ClientID'] == customer_id]
    stocks = customer[customer['AssetClass'] == "Stock"]
    bonds = customer[customer['AssetClass'] == "Bond"]
    cash = customer[customer['AssetClass'] == "Cash"]
    w_cash = cash["Quantity"].values[0]

    N = len(stocks)
    mu = np.zeros(N)
    sig = np.zeros(N)
    value = np.zeros(N)
    cov = np.zeros((N, N))

    amt_stock = stocks["Quantity"].values * 1.0
    w_stock_total = amt_stock.sum()
    w_stock = amt_stock / w_stock_total

    amt_bond = bonds["Quantity"].values * 1.0
    w_bond_total = amt_bond.sum()
    w_bond = amt_bond / w_bond_total

    w_total = [w_cash, w_stock_total, w_bond_total]
    w_t = sum(w_total)
    w_total = w_total/w_t

    for i in xrange(0, N):
        ISIN = stocks["InstrumentID"].values[i]
        mu_i, sig_i, v_i = get_returnrisk_stock(ISIN)
        mu[i] = mu_i
        sig[i] = sig_i
        value[i] = v_i

    for i in xrange(0, N):
        for j in xrange(0, N):
            cov[i][j] = sig[i]*sig[j]
    mu_t = mu.dot(w_stock)
    var_t = w_stock.dot(cov.dot(w_stock))
    value_t = value.dot(amt_stock)

    M = len(bonds)
    mu_bond = np.zeros(M)
    value_bond = np.zeros(M)
    for i in xrange(0, M):
        Valoren = bonds["InstrumentID"].values[i]
        mu_i, v_i = get_return_bond(Valoren, bond_price)
        mu_bond[i] = mu_i
        value_bond[i] = v_i

    mu_bond_total = mu_bond.dot(w_bond)
    value_bond_total = value_bond.dot(amt_bond)

    return np.sqrt(mu_t*w_total[1]+mu_bond_total*w_total[2]),\
           var_t*w_total[1],\
           cash["Quantity"].values[0],\
           value_t,\
           value_bond_total/100.0

#json parser
def parse_json_watson(str_js):
    js = json.loads(str_js)
    js = js["resolution"]["solutions"]
    df = pd.DataFrame(js)
    return df[df["status"] == "FRONT"]["solution_ref"]