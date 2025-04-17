from pandas import DataFrame
from tinkoff.invest import MoneyValue, Quotation

def cast_money(v):
    return v.units + v.nano / 1e9 if isinstance(v, (Quotation, MoneyValue)) else v

def float_to_quotation(value: float) -> Quotation:
    sign = -1 if value < 0 else 1
    abs_value = abs(value)
    units = int(abs_value)
    nano = int(round((abs_value - units) * 1_000_000))
    return Quotation(units=sign * units, nano=sign * nano)

def to_dict(o):
    return {k: cast_money(v) for k, v in o.__dict__.items()}


def to_df(data: list, ) -> DataFrame:
    return DataFrame([to_dict(r) for r in data])