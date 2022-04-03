from util.FtxClient import FtxClient
import os
import time
import math
import matplotlib.pyplot as plt
import pandas as pd


#
# the Exponential Hull Moving Average (EHMA) has those weighted moving averages replaced with exponential moving averages.
#

api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
subaccount_name = os.environ['SUBACCOUNT_NAME']
client = FtxClient(api_key, api_secret, subaccount_name)

pair_symbol = "ETH/USDT"
symbol_coin = "ETH"
symbol_stablecoin = "USDT"
resolution = 3600
# resolution = 86400
limit = 10000
my_truncate = 5


# nomenclature : https://oxfordstrat.com/trading-strategies/hull-moving-average/
lookback = 750
ema_1 = 'ema1'
ema_2 = 'wma2'
ehma = 'ehma'


def append_emas(series):
    multiplier1 = 2.0 / (lookback + 1)
    multiplier2 = 2.0 / (lookback // 2 + 1)
    series[0].update({ ema_1: series[0]['close'] })
    series[0].update({ ema_2: series[0]['close'] })
    for i in range(1, len(series)):
        series[i].update({ ema_1: series[i-1][ema_1] * (1-multiplier1) + series[i]['close'] * multiplier1 })
        series[i].update({ ema_2: series[i-1][ema_2] * (1-multiplier2) + series[i]['close'] * multiplier2 })


def append_delta_and_ehma(series):
    # doute sur le math.ceil. Tester
    multiplier3 = 2.0 / (math.ceil(lookback ** 0.5) + 1)
    # multiplier3 = 2.0 / (int(lookback ** 0.5) + 1)
    delta = 2 * series[0][ema_2] - series[0][ema_1]
    series[0].update({ 'delta': delta })
    series[0].update({ ehma: series[0]['delta'] })
    for index in range(1, len(series)):
        delta = 2 * series[index][ema_2] - series[index][ema_1]
        series[index].update({ 'delta': delta })
        series[index].update({ ehma: series[index-1][ehma] * (1-multiplier3) + series[index]['delta'] * multiplier3 })


data = client.get_historical_prices(market=pair_symbol,
                                    resolution=resolution,
                                    start_time=round(time.time() - resolution * limit),
                                    end_time=round(time.time()))

append_emas(data)
append_delta_and_ehma(data)

print(data[-1])

# last_data = data[-250:]
last_data = data

for index in range(0, len(last_data)):
    last_data[index].update({'ts': last_data[index]['time'] / 1000 })

df = pd.DataFrame.from_dict(last_data)
print(df)

plt.figure(figsize=(20, 10))
plt.plot(df['ts'], df['close'], color="black")
plt.plot(df['ts'], df['ehma'], color="blue")
plt.title("EHMA")
plt.xticks(rotation='30')
plt.xlabel('time')
plt.show()

