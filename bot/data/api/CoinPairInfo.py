from dataclasses import dataclass

@dataclass
class CoinPairInfo:
    """
    Фильтры заданного инструмента
    price_decimals - макс колво знаков в аргументах цены,
    qty_decimals - макс размер ордера в БВ
    min_qty - мин размер ордера в Базовой Валюте,
    """
    price_decimals: int
    qty_decimals: int
    min_qty: float