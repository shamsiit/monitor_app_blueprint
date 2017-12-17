import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template
import collections
import json
from random import randint
import threading
import time
from flask import g

from influxdb import DataFrameClient
import json
import dateutil.parser as parser
import time
from datetime import datetime,timedelta

from pandas.tslib import Timestamp
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from statsmodels.tsa.stattools import adfuller
#%matplotlib inline
from matplotlib.pylab import rcParams
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima_model import ARIMA

def getNetstatDetailsDefault(host, port, user, password, dbname, host_name, field_name):
	client = DataFrameClient(host, port, user, password, dbname)
	query="SELECT mean("+field_name+") FROM netstat WHERE host ='"+host_name+"' AND time > now() - 7d GROUP BY time(1h) fill(0)"
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	dict["mean"]=json.loads(dataframe['mean'].to_json(orient='values',force_ascii=True))
	li = dataframe['mean'].tolist()
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)
	dict["time"] = list_final
	dict["unit"] = " "

	return dict,query

def getNetstatDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date):
	datetime_object1 = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
	datetime_object2 = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
	diff = (datetime_object2-datetime_object1).total_seconds()
	group_val = int(diff / 500)
	if(group_val < 10):
		group_val = 10
	client = DataFrameClient(host, port, user, password, dbname)
	query="SELECT mean("+field_name+") FROM netstat  WHERE host='"+host_name+"' AND (time >= '"+from_date+"' AND time <= '"+to_date+"') GROUP BY time("+str(group_val)+"s) fill(0)"
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	dict["mean"]=json.loads(dataframe['mean'].to_json(orient='values',force_ascii=True))
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)
	dict["time"] = list_final
	dict["unit"] = " "

	return dict,query	

def getNetstatFieldList(host, port, user, password, dbname):
	client = DataFrameClient(host, port, user, password, dbname)
	query ="show field keys from netstat"
	data = client.query(query)
	dataframe = data['netstat']
	field_list = []
	for x in dataframe:
		field_list.append(x['fieldKey'])

	return field_list 		

def netstat_arima(host, port, user, password, dbname, query,number_of_prediction):

	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		dt = datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S")
		dt64 = np.datetime64(dt)
		list_final.append(dt64)

	dataframe2 = pd.DataFrame({'mean' : dataframe['mean'].tolist()},index=list_final)
	ts = dataframe2['mean']
	test_stationarity(ts)

	#ts_log = np.log(ts)
	#plt.plot(ts_log)

	#moving_avg = pd.rolling_mean(ts_log,12)
	#plt.plot(ts_log)
	#plt.plot(moving_avg, color='red')

	#ts_log_moving_avg_diff = ts_log - moving_avg
	#print ts_log_moving_avg_diff.head(12)

	#ts_log_moving_avg_diff.dropna(inplace=True)
	#test_stationarity(ts_log_moving_avg_diff)


	#expwighted_avg = pd.ewma(ts_log, halflife=12)
	#plt.plot(ts_log)
	#plt.plot(expwighted_avg, color='red')

	#ts_log_ewma_diff = ts_log - expwighted_avg
	#test_stationarity(ts_log_ewma_diff)

	#ts_log_diff = ts_log - ts_log.shift()
	#plt.plot(ts_log_diff)

	#ts_log_diff.dropna(inplace=True)
	#test_stationarity(ts_log_diff)

	ts_diff = ts - ts.shift()
	#plt.plot(ts_diff)

	ts_diff.dropna(inplace=True)
	test_stationarity(ts_diff)
	"""
	decomposition = seasonal_decompose(ts)

	trend = decomposition.trend
	seasonal = decomposition.seasonal
	residual = decomposition.resid


	plt.subplot(411)
	plt.plot(ts, label='Original')
	plt.legend(loc='best')
	plt.subplot(412)
	plt.plot(trend, label='Trend')
	plt.legend(loc='best')
	plt.subplot(413)
	plt.plot(seasonal,label='Seasonality')
	plt.legend(loc='best')
	plt.subplot(414)
	plt.plot(residual, label='Residuals')
	plt.legend(loc='best')
	plt.tight_layout()
	"""
	"""
	lag_acf = acf(ts_diff, nlags=20)
	lag_pacf = pacf(ts_diff, nlags=20, method='ols')

	#Plot ACF: 
	plt.subplot(121) 
	plt.plot(lag_acf)
	plt.axhline(y=0,linestyle='--',color='gray')
	plt.axhline(y=-1.96/np.sqrt(len(ts_diff)),linestyle='--',color='gray')
	plt.axhline(y=1.96/np.sqrt(len(ts_diff)),linestyle='--',color='gray')
	plt.title('Autocorrelation Function')
	#Plot PACF:
	plt.subplot(122)
	plt.plot(lag_pacf)
	plt.axhline(y=0,linestyle='--',color='gray')
	plt.axhline(y=-1.96/np.sqrt(len(ts_diff)),linestyle='--',color='gray')
	plt.axhline(y=1.96/np.sqrt(len(ts_diff)),linestyle='--',color='gray')
	plt.title('Partial Autocorrelation Function')
	plt.tight_layout()
	"""

	model = ARIMA(ts, order=(1, 1, 1))  
	results_ARIMA = model.fit(disp=-1)
	print(results_ARIMA.summary())

	length = len(ts)

	s = length
	e = length+number_of_prediction

	predicted_values = results_ARIMA.predict(start=s,end=e)

	values = results_ARIMA.fittedvalues.append(predicted_values)

	predictions_ARIMA_diff = pd.Series(values, copy=True)

	predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()

	predictions_ARIMA = pd.Series(data=ts.ix[0], index=values.index)


	predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum,fill_value=0)

	list = predictions_ARIMA.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)

	dict["mean"] = predictions_ARIMA.tolist()
	dict["time"] = list_final
	dict["unit"] = "%"

	return dict

def netstat_ar(host, port, user, password, dbname, query,number_of_prediction):

	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		dt = datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S")
		dt64 = np.datetime64(dt)
		list_final.append(dt64)

	dataframe2 = pd.DataFrame({'mean' : dataframe['mean'].tolist()},index=list_final)
	ts = dataframe2['mean']
	test_stationarity(ts)


	ts_diff = ts - ts.shift()
	#plt.plot(ts_diff)

	ts_diff.dropna(inplace=True)
	test_stationarity(ts_diff)


	model = ARIMA(ts, order=(1, 1, 0))  
	results_ARIMA = model.fit(disp=-1)
	print(results_ARIMA.summary())

	length = len(ts)

	s = length
	e = length+number_of_prediction

	predicted_values = results_ARIMA.predict(start=s,end=e)

	values = results_ARIMA.fittedvalues.append(predicted_values)

	predictions_ARIMA_diff = pd.Series(values, copy=True)

	predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()

	predictions_ARIMA = pd.Series(data=ts.ix[0], index=values.index)


	predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum,fill_value=0)

	list = predictions_ARIMA.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)

	dict["mean"] = predictions_ARIMA.tolist()
	dict["time"] = list_final
	dict["unit"] = "%"

	return dict
	
def netstat_ma(host, port, user, password, dbname, query,number_of_prediction):

	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		dt = datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S")
		dt64 = np.datetime64(dt)
		list_final.append(dt64)

	dataframe2 = pd.DataFrame({'mean' : dataframe['mean'].tolist()},index=list_final)
	ts = dataframe2['mean']
	test_stationarity(ts)


	ts_diff = ts - ts.shift()
	#plt.plot(ts_diff)

	ts_diff.dropna(inplace=True)
	test_stationarity(ts_diff)


	model = ARIMA(ts, order=(0, 1, 1))  
	results_ARIMA = model.fit(disp=-1)
	print(results_ARIMA.summary())

	length = len(ts)

	s = length
	e = length+number_of_prediction

	predicted_values = results_ARIMA.predict(start=s,end=e)

	values = results_ARIMA.fittedvalues.append(predicted_values)

	predictions_ARIMA_diff = pd.Series(values, copy=True)

	predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()

	predictions_ARIMA = pd.Series(data=ts.ix[0], index=values.index)


	predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum,fill_value=0)

	list = predictions_ARIMA.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)

	dict["mean"] = predictions_ARIMA.tolist()
	dict["time"] = list_final
	dict["unit"] = "%"

	return dict

def test_stationarity(timeseries):
    
    #Determing rolling statistics
    rolmean = pd.rolling_mean(timeseries, window=24)
    rolstd = pd.rolling_std(timeseries, window=24)

    #Plot rolling statistics:
    #orig = plt.plot(timeseries, color='blue',label='Original')
    #mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    #std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    #plt.legend(loc='best')
    #plt.title('Rolling Mean & Standard Deviation')
    #plt.show(block=False)
    
    #Perform Dickey-Fuller test:
    print 'Results of Dickey-Fuller Test:'
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print dfoutput


def netstat_holt(host, port, user, password, dbname , query,number_of_prediction):
	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		dt = datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S")
		dt64 = np.datetime64(dt)
		list_final.append(dt64)

	dataframe2 = pd.DataFrame({'mean' : dataframe['mean'].tolist()},index=list_final)
	ts = dataframe2['mean'] 
	predict = double_exponential_smoothing(ts, alpha=0.3, beta=0.3,number_of_prediction=number_of_prediction)
	list = predict.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)

	dict["mean"] = predict.tolist()
	dict["time"] = list_final
	dict["unit"] = "%"
	
	return dict

def netstat_holtwinter(host, port, user, password, dbname , query,number_of_prediction):
	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query(query)
	dataframe = data['netstat']
	dict={}
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		dt = datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S")
		dt64 = np.datetime64(dt)
		list_final.append(dt64)

	dataframe2 = pd.DataFrame({'mean' : dataframe['mean'].tolist()},index=list_final)
	ts = dataframe2['mean'] 
	predict = triple_exponential_smoothing(ts, 24, 0.3, 0.029, 0.3, number_of_prediction)
	list = predict.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)

	dict["mean"] = predict.tolist()
	dict["time"] = list_final
	dict["unit"] = "%"
	
	return dict	



def average(series):
    return float(sum(series))/len(series)

def average(series, n=None):
    if n is None:
        return average(series, len(series))
    return float(sum(series[-n:]))/n

def moving_average(series, n):
    return average(series[-n:])

def weighted_average(series, weights):
    result = 0.0
    weights.reverse()
    for n in range(len(weights)):
        result += series[-n-1] * weights[n]
    return result

def exponential_smoothing(series, alpha):
    result = [series[0]] # first value is same as series
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    #ser =  pd.Series(result,index = series.index.tolist())
    return result

def double_exponential_smoothing(series, alpha, beta,number_of_prediction):
    time_list = series.index.tolist()
    print len(time_list)
    length = len(time_list)
    to_date = str(series.index.tolist()[length-1])
    from_date = str(series.index.tolist()[length-2])

    datetime_object1 = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    datetime_object2 = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
    diff = (datetime_object2-datetime_object1).total_seconds()
    s_len = number_of_prediction
    for n in range(0,s_len):
        datetime_object3 = datetime.strptime(str(time_list[len(time_list)-1]), '%Y-%m-%d %H:%M:%S')
        time_list.append(Timestamp(datetime_object3 + timedelta(seconds=int(diff))))


    print len(time_list)
    result = [series[0]]
    for n in range(1, len(series)+s_len):
        if n == 1:
            level, trend = series[0], series[1] - series[0]
        if n >= len(series): # we are forecasting
          value = result[-1]
        else:
          value = series[n]
        last_level, level = level, alpha*value + (1-alpha)*(level+trend)
        trend = beta*(level-last_level) + (1-beta)*trend
        result.append(level+trend)
    ser =  pd.Series(result,index = time_list)
    return ser


def initial_trend(series, slen):
    sum = 0.0
    for i in range(slen):
        sum += float(series[i+slen] - series[i]) / slen
    return sum / slen

def initial_seasonal_components(series, slen):
    seasonals = {}
    season_averages = []
    n_seasons = int(len(series)/slen)
    # compute season averages
    for j in range(n_seasons):
        season_averages.append(sum(series[slen*j:slen*j+slen])/float(slen))
    # compute initial values
    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen*j+i]-season_averages[j]
        seasonals[i] = sum_of_vals_over_avg/n_seasons
    return seasonals

def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    
    time_list = series.index.tolist()
    print len(time_list)
    length = len(time_list)
    to_date = str(series.index.tolist()[length-1])
    from_date = str(series.index.tolist()[length-2])

    datetime_object1 = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    datetime_object2 = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
    diff = (datetime_object2-datetime_object1).total_seconds()
    for n in range(0,n_preds):
        datetime_object3 = datetime.strptime(str(time_list[len(time_list)-1]), '%Y-%m-%d %H:%M:%S')
        time_list.append(Timestamp(datetime_object3 + timedelta(seconds=int(diff))))


    print len(time_list)
    
    result = []
    seasonals = initial_seasonal_components(series, slen)
    for i in range(len(series)+n_preds):
        if i == 0: # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            continue
        if i >= len(series): # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m*trend) + seasonals[i%slen])
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha*(val-seasonals[i%slen]) + (1-alpha)*(smooth+trend)
            trend = beta * (smooth-last_smooth) + (1-beta)*trend
            seasonals[i%slen] = gamma*(val-smooth) + (1-gamma)*seasonals[i%slen]
            result.append(smooth+trend+seasonals[i%slen])
    ser =  pd.Series(result,index = time_list)
    return ser


