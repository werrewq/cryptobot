from Test.TestSignalRequest import open_short, open_long, set_take_profit, set_stop_loss

# Проверяем буффер запросов
# Должно выполниться
# 1. open_short
# 2. open_long
# 3. set_stop_loss
# 4. set_take_profit

if __name__ == '__main__':
    set_take_profit(5000, "Sell", take_profit_percentage=30)
    set_stop_loss(1000,"Sell")
    open_long()
    open_short()

