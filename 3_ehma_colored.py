from util.FtxClient import FtxClient
import os
import time
import math
import matplotlib.pyplot as plt

#
# the Exponential Hull Moving Average (EHMA) has those weighted moving averages replaced with exponential moving averages.
#

api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
subaccount_name = os.environ['SUBACCOUNT_NAME']
client = FtxClient(api_key, api_secret, subaccount_name)

pair_symbol = "BTC/USDT"
symbol_coin = "BTC"
symbol_stablecoin = "USDT"
resolution = 604800
limit = 1000
my_truncate = 5


# nomenclature : https://oxfordstrat.com/trading-strategies/hull-moving-average/
lookback = 20
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
        # couleurs
        if series[index][ehma] == series[index - 1][ehma]:
            series[index].update({'color': series[index - 1]['color']})
        elif series[index][ehma] > series[index - 1][ehma]:
            series[index].update({'color': 'green'})
        else:
            series[index].update({'color': 'red'})


data = client.get_historical_prices(market=pair_symbol,
                                    resolution=resolution,
                                    start_time=round(time.time() - resolution * limit),
                                    end_time=round(time.time()))

append_emas(data)
append_delta_and_ehma(data)

last_data = data[-100:]

for index in range(0, len(last_data)):
    last_data[index].update({'info_date': last_data[index]['startTime'][0:10] })

for index in range(0, len(last_data)):
    # changements de couleurs
    if last_data[index-1]['color'] == 'red' and last_data[index]['color'] == 'green':
        print('buying at ', last_data[index]['close'])
    if last_data[index-1]['color'] == 'green' and last_data[index]['color'] == 'red':
        print('selling at ', last_data[index]['close'])

# df = pd.DataFrame.from_dict(last_data)
fig, ax = plt.subplots()

for datum in last_data:
    ax.plot(datum['info_date'], datum['close'], 'o', color='black')
    ax.plot(datum['info_date'], datum['ehma'], 'o', color=datum['color'], picker=True)

plt.xticks(rotation='90')
plt.show()
