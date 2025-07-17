import logging
import pytz
from datetime import datetime, time, timedelta
import pandas as pd
import numpy as np
import requests
from tinkoff.invest import Client, CandleInterval, InstrumentIdType
from tinkoff.invest.services import Services
from tinkoff.invest.utils import now

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Константы для состояний
class FisherState:
    PAUSE = "PAUSE"
    LONG = "LONG"
    SHORT = "SHORT"


class TradingState:
    PAUSE = "PAUSE"
    LONG = "LONG"
    SHORT = "SHORT"
    LONG_REVERT = "LONG_REVERT"
    SHORT_REVERT = "SHORT_REVERT"


class TaurusStrategy:
    def __init__(self, token, account_id, figi):
        self.token = token
        self.account_id = account_id
        self.figi = figi
        self.trading_state = TradingState.PAUSE
        self.fisher_state = FisherState.PAUSE
        self.fisher_state_30 = FisherState.PAUSE

        # Параметры стратегии
        self.small_offset = 1
        self.big_offset = 6
        self.timeframe = "15m"
        self.ATRperiod = 5
        self.BBperiod = 20
        self.BBdeviation = 1.0
        self.UseATRfilter = True

        # Время работы
        self.start_date = datetime(2024, 7, 7)
        self.block_start_time = time(21, 30)
        self.block_end_time = time(6, 59)
        self.restart_end_minute = 29
        self.close_after_time = time(21, 30)

        # Данные
        self.historical_h1_data = None
        self.historical_m30_data = None
        self.historical_m15_data = None
        self.historical_m1_data = None

    async def initialize(self):
        """Инициализация данных"""
        async with Client(self.token) as client:
            # Загрузка исторических данных
            self.historical_h1_data = await self.load_history(client, CandleInterval.CANDLE_INTERVAL_HOUR)
            self.historical_m30_data = await self.load_history(client, CandleInterval.CANDLE_INTERVAL_30_MIN)
            self.historical_m15_data = await self.load_history(client, CandleInterval.CANDLE_INTERVAL_15_MIN)
            self.historical_m1_data = await self.load_history(client, CandleInterval.CANDLE_INTERVAL_1_MIN)

    async def load_history(self, client: Client, interval):
        """Загрузка исторических данных"""
        candles = await client.market_data.get_candles(
            figi=self.figi,
            from_=now() - timedelta(days=30),
            to=now(),
            interval=interval
        )
        return self.candles_to_dataframe(candles.candles)

    def candles_to_dataframe(self, candles):
        """Конвертация свечей в DataFrame"""
        data = {
            'time': [c.time for c in candles],
            'open': [c.open.units + c.open.nano / 1e9 for c in candles],
            'high': [c.high.units + c.high.nano / 1e9 for c in candles],
            'low': [c.low.units + c.low.nano / 1e9 for c in candles],
            'close': [c.close.units + c.close.nano / 1e9 for c in candles],
            'volume': [c.volume for c in candles]
        }
        return pd.DataFrame(data).set_index('time')

    def round_fisher(self, val):
        """Округление для Fisher Transform"""
        return 0.999 if val > 0.99 else -0.999 if val < -0.99 else val

    def fisher_transform(self, data, length=9):
        """Fisher Transform индикатор"""
        high = data['high'].rolling(length).max()
        low = data['low'].rolling(length).min()

        value = 0.0
        fish = 0.0

        results = []
        for i in range(len(data)):
            hl2 = (data['high'][i] + data['low'][i]) / 2
            val = 0.0
            if i > 0:
                val = self.round_fisher(0.66 * ((hl2 - low[i]) / (high[i] - low[i]) - 0.5) + 0.67 * value)
            value = val

            fish_val = 0.5 * np.log((1 + value) / (1 - value)) + 0.5 * (fish if i > 0 else 0)
            fish = fish_val

            trigger = fish if i > 0 else 0
            results.append((fish_val, trigger))

        return pd.DataFrame(results, columns=['fish', 'trigger'], index=data.index)

    def compute_follow_line(self, data):
        """Вычисление Follow Line"""
        close = data['close']
        high = data['high']
        low = data['low']

        # Bollinger Bands
        sma = close.rolling(self.BBperiod).mean()
        stdev = close.rolling(self.BBperiod).std()
        BB_upper = sma + stdev * self.BBdeviation
        BB_lower = sma - stdev * self.BBdeviation

        # ATR
        tr = pd.DataFrame({
            'hl': high - low,
            'hc': abs(high - close.shift()),
            'lc': abs(low - close.shift())
        }).max(axis=1)
        atr = tr.rolling(self.ATRperiod).mean()

        # Follow Line логика
        follow_line = pd.Series(np.nan, index=data.index)
        bb_signal = pd.Series(0, index=data.index)
        i_trend = pd.Series(0, index=data.index)

        for i in range(1, len(data)):
            # Определение BB сигнала
            if close[i] > BB_upper[i]:
                bb_signal[i] = 1
            elif close[i] < BB_lower[i]:
                bb_signal[i] = -1

            # Buy signal logic
            if bb_signal[i] == 1:
                if self.UseATRfilter:
                    follow_line[i] = low[i] - atr[i]
                else:
                    follow_line[i] = low[i]

                if follow_line[i] < follow_line[i - 1]:
                    follow_line[i] = follow_line[i - 1]

            # Sell signal logic
            if bb_signal[i] == -1:
                if self.UseATRfilter:
                    follow_line[i] = high[i] + atr[i]
                else:
                    follow_line[i] = high[i]

                if follow_line[i] > follow_line[i - 1]:
                    follow_line[i] = follow_line[i - 1]

            # Trend direction
            if follow_line[i] > follow_line[i - 1]:
                i_trend[i] = 1
            elif follow_line[i] < follow_line[i - 1]:
                i_trend[i] = -1

        return follow_line

    def is_weekday(self, dt):
        """Проверка буднего дня"""
        return dt.weekday() < 5  # Пн-Пт

    def in_block_time(self, dt):
        """Проверка блокировочного времени"""
        if not self.is_weekday(dt):
            return False

        current_time = dt.time()
        # Вечерняя часть: с 21:30 до полуночи
        if (current_time >= self.block_start_time) or (current_time <= self.block_end_time):
            return True
        return False

    def can_open_position(self, dt):
        """Можно ли открывать позиции"""
        return (self.is_weekday(dt) and
                not self.in_block_time(dt) and
                dt >= self.start_date)

    def can_restart_position(self, dt):
        """Утреннее возобновление позиции"""
        current_time = dt.time()
        return (current_time.hour == 7 and current_time.minute <= self.restart_end_minute) or \
            (current_time.hour > 7 and current_time < self.close_after_time)

    def close_all_now(self, dt):
        """Пора закрывать все позиции"""
        current_time = dt.time()
        return (current_time >= self.close_after_time)

    def get_long_offset(self, above_fl):
        """Получение offset для long"""
        return self.small_offset if above_fl else self.big_offset

    def get_short_offset(self, under_fl):
        """Получение offset для Short"""
        return self.small_offset if under_fl else self.big_offset
