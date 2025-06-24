from Test.TestSignalRequest import set_take_profit_market, set_take_profit

if __name__ == '__main__':
    set_take_profit(170,"Sell", take_profit_percentage=30)
    # set_take_profit_market(190, "Buy", take_profit_percentage=30)