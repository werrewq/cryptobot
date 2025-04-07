import logging
from enum import Enum
from decimal import *

from bot.data.api.CoinPairInfo import CoinPairInfo


def count_decimal_places(str_number: str) -> int:
    # Проверяем, есть ли дробная часть
    if '.' in str_number:
        # Возвращаем количество знаков после запятой
        return len(str_number.split('.')[1])
    return 0  # Если дробной части нет

def floor_qty(value, coin_pair_info: CoinPairInfo):
    return _floor(value, coin_pair_info.qty_decimals)

def floor_price(value, coin_pair_info: CoinPairInfo):
    return _floor(value, coin_pair_info.price_decimals)

def _floor(value, decimals):
    """
    Для аргументов цены нужно отбросить (округлить вниз)
    до колва знаков заданных в фильтрах цены
    """
    logging.debug(f"_floor value = {value}, decimals = {decimals} \n")
    d_value = Decimal(str(value))
    d_factor = Decimal('1.' + '0' * decimals)
    # Округляем вниз
    res = d_value.quantize(d_factor, rounding=ROUND_FLOOR)
    return float(res)

class PositionType(Enum):
    LONG = "Buy"
    SHORT = "Sell"