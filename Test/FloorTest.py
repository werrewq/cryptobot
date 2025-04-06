from bot.data.api.ApiHelpers import floor_qty
from bot.data.api.CoinPairInfo import CoinPairInfo

if __name__ == '__main__':
    res = floor_qty(120.4323123515213123, CoinPairInfo(10, 3, 0.001))
    res = res * 10.1
    print(res)