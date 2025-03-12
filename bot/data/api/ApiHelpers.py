from enum import Enum

from bot.data.api.CoinPairInfo import CoinPairInfo


def count_decimal_places(str_number: str) -> int:
    # Проверяем, есть ли дробная часть
    if '.' in str_number:
        # Возвращаем количество знаков после запятой
        return len(str_number.split('.')[1])
    return 0  # Если дробной части нет

def float_trunc(f, prec):
    """
    Ещё один способ отбросить от float лишнее без округлений
    :param f:
    :param prec:
    :return:
    """
    l, r = f"{float(f):.12f}".split('.') # 12 дб достаточно для всех монет
    return  float(f'{l}.{r[:prec]}')

def round_down(value, decimals):
    """
    Ещё один способ отбросить от float лишнее без округлений
    :return:
    """
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def floor_qty(value, coin_pair_info: CoinPairInfo):
    return _floor(value, coin_pair_info.qty_decimals)

def floor_price(value, coin_pair_info: CoinPairInfo):
    return _floor(value, coin_pair_info.price_decimals)

def _floor(value, decimals):
    """
    Для аргументов цены нужно отбросить (округлить вниз)
    до колва знаков заданных в фильтрах цены
    """
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

class PositionType(Enum):
    LONG = "Buy"
    SHORT = "Sell"