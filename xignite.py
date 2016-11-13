import numpy as np
import pandas as pd
import requests
import json
import singleton
import cubic_spline


def getUrl(url):
	response = requests.get(url)
	return response


def get_bond_type():
	base_url = 'http://bonds.xignite.com/'
	action = "xBondMaster.json/ListBondTypes?"+\
			 "_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))['BondTypes']
	df = pd.DataFrame(js)
	return df


def get_bond_corporate(sym_beg = "A", sym_end = "B"):
	base_url = 'http://bonds.xignite.com/'
	action = "xBonds.json/ListSymbols?"+ \
			 "BondType=Corporate&StartSymbol=%s&EndSymbol=%s" % (sym_beg,sym_end) +\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))['Securities']
	df = pd.DataFrame(js)
	return df


def get_bond_agency(sym_beg = "A", sym_end = "B"):
	base_url = 'http://bonds.xignite.com/'
	action = "xBonds.json/ListSymbols?"+ \
			 "BondType=Corporate&StartSymbol=%s&EndSymbol=%s" % (sym_beg,sym_end) +\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))['Securities']
	df = pd.DataFrame(js)
	return df


def get_bond_all(sym_beg = "A", sym_end = "B"):
	base_url = 'http://bonds.xignite.com/'
	action = "xBonds.json/ListSymbols?"+ \
			 "BondType=Corporate&StartSymbol=%s&EndSymbol=%s" % (sym_beg,sym_end) +\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))['Securities']
	df1 = pd.DataFrame(js)
	df1.index = df1['Symbol']

	action = "xBonds.json/ListSymbols?" + \
			 "BondType=Corporate&StartSymbol=%s&EndSymbol=%s" % (sym_beg,sym_end) +\
			 "&_token="
	response = getUrl(base_url + action + singleton.xignite_token)
	js = json.loads(response.text.encode('ascii', 'ignore'))['Securities']
	df2 = pd.DataFrame(js)
	df2.index = df2['Symbol']

	df = pd.concat([df1,df2], axis=0)
	return df


def get_bonds_price_today(lst_bond = None):
	base_url = 'http://bonds.xignite.com/'
	action = "xBonds.json/GetPriceComposites?"+ \
			 "IdentifierType=Valoren&Identifiers=%s&PriceSource=FINRA"%(",".join(lst_bond)) +\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))
	df = pd.DataFrame(map(lambda x: x, js))
	lst_price = [x for x in df['TradedPrice']]
	df_price = pd.DataFrame(lst_price, index = lst_bond)
	df_price['Valoren'] = lst_bond
	return df_price


def get_bonds_price_today_batch(lst_bond = None):
	N = len(lst_bond)
	batch_sz = 200
	n_batches = N / batch_sz

	lst_df = []
	for j in xrange(n_batches):
		print j
		lst_sub = lst_bond[j * batch_sz:(j * batch_sz + batch_sz)]
		df = get_bonds_price_today(lst_sub)
		lst_df.append(df)
		save_csv(df,'bond_%s.csv'%j)

	df_big = pd.concat(lst_df, axis=0)

	save_csv(df_big, 'bond_price.csv')

	return df_big


def get_riskfree_rate_today(name):
	base_url = 'http://www.xignite.com/'
	action = "xRates.json/GetTodaysRate?" + \
			 "RateType=%s" % name + \
			 "&_token="
	response = getUrl(base_url + action + singleton.xignite_token)
	js = json.loads(response.text.encode('ascii', 'ignore'))['Value']
	return float(js)

def get_riskfree_yield():
	r_1m = get_riskfree_rate_today("Libor1Month")
	r_2m = get_riskfree_rate_today("Libor2Month")
	r_3m = get_riskfree_rate_today("Libor3Month")
	r_6m = get_riskfree_rate_today("Libor6Month")
	r_1y = get_riskfree_rate_today("Libor1Year")
	r_2y = get_riskfree_rate_today("TreasuryComposite2Year")
	r_3y = get_riskfree_rate_today("TreasuryComposite3Year")
	r_5y = get_riskfree_rate_today("TreasuryComposite5Year")
	r_10y = get_riskfree_rate_today("TreasuryComposite10Year")
	r_30y = get_riskfree_rate_today("TreasuryComposite30Year")

	x = [1.0 / 12, 2.0 / 12, 3.0 / 12, 6.0 / 12,
		 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
	y = [r_1m,r_2m,r_3m,r_6m,
		 r_1y,r_2y,r_3y,r_5y,r_10y,r_30y]
	return x, y

def save_csv(df, path):
	df.to_csv(path, sep=',', encoding='utf-8')


def calc_spread():
	df = pd.read_csv('bond_price.csv')
	df_m = pd.read_csv('bond_maturity.csv')
	df_r = pd.read_csv('bond_mapping.csv')

	df_1 = df.join(df_m,how='left',lsuffix='Valoren', rsuffix='Valoren')
	df = df_1.join(df_r, how='left', lsuffix='Valoren', rsuffix='Valoren')

	df['market_price'] = (df['DailyHigh'] + df['DailyLow']) / 2.0
	df['model_price'] = df['PriceUsedForCalculations']
	df['YieldToMaturity'] = df['YieldToMaturity']/100.0

	x, y = get_riskfree_yield()

	for i in xrange(1, len(x)):
		if y[i] == 0.0:
			y[i] = 1.1*y[i - 1]

	cs = cubic_spline.Spline(x, y, [0, 1])
	cs.spline_setpoints()

	lst_rf = []
	for i in xrange(len(df)):
		m = df['DurationToMaturity'][i]
		rf = cs.spline([m])[0]
		lst_rf.append(rf)

	df['riskfree'] = lst_rf
	df['Hazzard'] = df['YieldToMaturity'] - df['riskfree']

	df_res = df[['Symbol','Valoren','market_price','model_price','DurationToMaturity',
				 'YieldToMaturity','riskfree','Hazzard','Rating']]
	save_csv(df_res, 'bond_spread.csv')

def crawling_bond_symbol_all():
	lst_char = ["A", "B", "C", "D", "E", "F", "G",
				"H", "I", "J", "K", "L", "M", "N",
				"O", "P", "Q", "R", "S", "T",
				"U", "V", "W", "X", "Y", "Z"]

	lst_df = []
	for i in xrange(0, len(lst_char) - 1):
		sym_beg = lst_char[i]
		sym_end = lst_char[i + 1]
		df = get_bond_all(sym_beg, sym_end)
		save_csv(df, 'bond_%s.csv' % sym_beg)
		lst_df.append(df)

	df_big = pd.concat(lst_df, axis=0)
	save_csv(df_big, 'bond_symbol.csv')

def get_stock_price_range(ISIN, str_beg, str_end):
	base_url = 'http://www.xignite.com/'
	action = "xGlobalHistorical.json/GetGlobalHistoricalQuotesRange?" + \
			 "IdentifierType=ISIN&Identifier=%s&" % ISIN+ \
			 "AdjustmentMethod=SplitAndProportionalCashDividend&"+\
			 "StartDate=%s&EndDate=%s" % (str_beg, str_end) +\
			 "&_token="
	response = getUrl(base_url + action + singleton.xignite_token)
	js = json.loads(response.text.encode('ascii', 'ignore'))['GlobalQuotes']

	df = pd.DataFrame(map(lambda x: x, js))
	df["ISIN"] = ISIN
	df = df.sort(['Date'], ascending=[1])
	return df


def crawling_stock_bond_mapping():
	df_stock = pd.read_csv('Universe.csv')
	df_bond = pd.read_csv('bond_symbol.csv')
	df1 = df_stock[['Exchange Ticker', 'MyName', 'ISIN_Stock']]
	df2 = df_bond[['Symbol', 'IssuerName', 'ISIN', 'Valoren']]

	lst = []
	for i in xrange(len(df1)):
		for j in xrange(len(df2)):
			if df1['MyName'][i] == df2['IssuerName'][j]:
				x = df1.ix[i].tolist() + df2.ix[j].tolist()
				lst.append(x)
	df = pd.DataFrame(lst,
					  columns=['Exchange Ticker', 'MyName', 'ISIN_Stock', 'Symbol', 'IssuerName', 'ISIN', 'Valoren'])
	save_csv(df, 'bond_mapping.csv')
	return df


def crawling_stock_price():
	stock_symbol = pd.read_csv('stock_symbol.csv')['ISIN_Stock']
	for ISIN in stock_symbol:
		print ISIN
		df = get_stock_price_range(ISIN, "11/11/2015", "11/11/2016")
		save_csv(df, 'stock_%s.csv' % ISIN)

def crawling_bond_price():
	bond_symbol = pd.read_csv('bond_mapping.csv')['Valoren'].tolist()
	bond_symbol = map(lambda x: str(x), bond_symbol)
	get_bonds_price_today_batch(bond_symbol)


def get_bond_maturity(lst_bond):
	base_url = "http://bonds.xignite.com/"
	action = "xBonds.json/GetDurationAndConvexities?" + \
			 "IdentifierType=Valoren&Identifiers=%s&PriceSource=FINRA" % (",".join(lst_bond))+\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii', 'ignore'))
	df = pd.DataFrame(map(lambda x: x['BondDuration'], js))
	df['Valoren'] = lst_bond
	df = df[['Valoren','DurationToMaturity']]
	return df

def crawling_bond_maturity():
	lst_bond = pd.read_csv('bond_mapping.csv')['Valoren'].tolist()
	lst_bond = map(lambda x: str(x), lst_bond)

	N = len(lst_bond)
	batch_sz = 200
	n_batches = N / batch_sz

	lst_df = []
	for j in xrange(n_batches):
		lst_sub = lst_bond[j * batch_sz:(j * batch_sz + batch_sz)]
		df = get_bond_maturity(lst_sub)
		lst_df.append(df)
		save_csv(df, 'bond_%s.csv' % j)

	df_big = pd.concat(lst_df, axis=0)

	save_csv(df_big, 'bond_maturity.csv')

	return df_big


def get_stocks_price_today(lst_stock = None):
	base_url = 'http://www.xignite.com/'
	action = "xGlobalHistorical.json/GetGlobalLastClosingPrices?"+\
			 "IdentifierType=ISIN&Identifiers=%s&" %(",".join(lst_stock))+\
			 "AdjustmentMethod=SplitAndProportionalCashDividend"+\
			 "&_token="
	response = getUrl(base_url+action+singleton.xignite_token)
	js = json.loads(response.text.encode('ascii','ignore'))
	df = pd.DataFrame(map(lambda x: x, js))
	df['ISIN'] = lst_stock

	save_csv(df, 'stock_price.csv')
	return df




