from trader_bot.TraderBot import TraderBotConfig
from MockTraderBot import MockTraderBot
from TestingTraderBot import TestingTraderBot
from InvestmentUtil import InvestmentUtil

if __name__ == '__main__':
    # ETH account
    json_body = "{\n  \"account_id\": \"bec75c28-d95a-52a9-8edf-d0947a133eda\",\n  " \
                "\"currency\": \"ETH\",\n  " \
                "\"default_buy\": 100,\n  " \
                "\"interval\": \"30m\",\n  " \
                "\"short_term_periods\": 5,\n  " \
                "\"long_term_periods\": 20\n}"

    bot_config = TraderBotConfig(json_body)

    investment_util = InvestmentUtil(currency_pair=bot_config.get_currency_pair(), interval=bot_config.interval,
                                     short_term_periods=bot_config.short_term_periods,
                                     long_term_periods=bot_config.long_term_periods)
    # TraderBot(bot_config).execute_actions()

    trader_bot = TestingTraderBot(bot_config, investment_util).setup()

    print(trader_bot.get_buy_price())
    trader_bot.execute_actions()
