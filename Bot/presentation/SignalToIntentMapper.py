from Bot.domain.TradeIntent import TradeIntent, LongIntent, ShortIntent


class SignalToIntentMapper:

   def map(self, signal) -> TradeIntent:
       buy_or_sell = str(signal["signal"])
       close = float(signal["price"])
# TODO Доделать заполнение LongIntent и ShortIntent
# TODO Добавить обработку currency
       currency_name = "ALGO"
       match buy_or_sell:
           case "open_long":
               return LongIntent(currency_name= currency_name, message= "long")
           case "open_short":
               return ShortIntent(currency_name= currency_name, message= "short")
           case _:
               raise TypeError('Unsupported trade intent')