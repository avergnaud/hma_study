from FtxClient import FtxClient
import os
import time
import math


api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
subaccount_name = os.environ['SUBACCOUNT_NAME']
client = FtxClient(api_key, api_secret, subaccount_name)

pair_symbol = "ETH/USDT"
symbol_coin = "ETH"
symbol_stablecoin = "USDT"
resolution = 3600
limit = 1000
my_truncate = 5


# nomenclature : https://oxfordstrat.com/trading-strategies/hull-moving-average/
lookback = 20
wma_1 = 'wma1'
wma_2 = 'wma2'

#
# bench
#
def bench_weighted_moving_average(series, lookback = None) -> float:
    if not lookback:
        lookback = len(series)
    if len(series) == 0:
        return 0
    assert 0 < lookback <= len(series)

    wma = 0
    lookback_offset = len(series) - lookback
    for index in range(lookback + lookback_offset - 1, lookback_offset - 1, -1):
        weight = index - lookback_offset + 1
        wma += series[index] * weight
    return wma / ((lookback ** 2 + lookback) / 2)


def bench_hull_moving_average(series, lookback) -> float:
    assert lookback > 0
    hma_series = []
    for k in range(int(lookback ** 0.5), -1, -1):
        s = series[:-k or None]
        wma_half = bench_weighted_moving_average(s, min(lookback // 2, len(s)))
        wma_full = bench_weighted_moving_average(s, min(lookback, len(s)))
        hma_series.append(wma_half * 2 - wma_full)
    return bench_weighted_moving_average(hma_series)
#
# end bench
#


def weighted_moving_average(series, from_index, to_index, field_name, look_back):
    if look_back > to_index - from_index + 1:
        # pas assez de valeurs
        look_back = to_index - from_index + 1
    wma = 0
    for index in range(from_index, to_index + 1):
        weight = index - from_index + 1
        wma += series[index][field_name] * weight
    return wma / ((look_back ** 2 + look_back) / 2)


def append_weighted_moving_average(series, key_name, look_back):
    # if not lookback:
    #     lookback = len(series)

    for index in range(0, len(series)):
        from_index = max(0, index - look_back + 1)
        to_index = index
        wma = weighted_moving_average(series, from_index, to_index, 'close', look_back)
        series[index].update({ key_name: wma })


def append_delta(series):
    for index in range(0, len(series)):
        delta = 2*series[index][wma_2] - series[index][wma_1]
        series[index].update({ 'delta': delta })


def append_hma(series, look_back):
    for index in range(0, len(series)):
        from_index = max(0, index - look_back + 1)
        to_index = index
        wma = weighted_moving_average(series, from_index, to_index, 'delta', look_back)
        series[index].update({ 'hma': wma })


data = client.get_historical_prices(market=pair_symbol,
                                    resolution=resolution,
                                    start_time=round(time.time() - resolution * limit),
                                    end_time=round(time.time()))

append_weighted_moving_average(data, wma_1, lookback)
append_weighted_moving_average(data, wma_2, lookback // 2)
append_delta(data)
append_hma(data, math.ceil(lookback ** 0.5))

print(data[-1])

close = [x['close'] for x in data]
bench_wma_1 = bench_weighted_moving_average(close, lookback)
print(bench_wma_1)
bench_wma_2 = bench_weighted_moving_average(close, lookback // 2)
print(bench_wma_2)
bench_hma = bench_hull_moving_average(close, lookback)
print(bench_hma)