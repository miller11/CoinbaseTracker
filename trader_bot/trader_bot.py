from TraderBot import TraderBotConfig, TraderBot
from MockTraderBot import MockTraderBot
from TestingTraderBot import TestingTraderBot

if __name__ == '__main__':
    # ETH account
    json_body = "{\n  \"account_id\": \"bec75c28-d95a-52a9-8edf-d0947a133eda\",\n  " \
                "\"default_buy\": 100,\n  " \
                "\"interval\": \"30m\",\n  " \
                "\"short_term_periods\": 5,\n  " \
                "\"long_term_periods\": 20\n}"

    bot_config = TraderBotConfig(json_body)

    # TraderBot(bot_config).execute_actions()

    trader_bot = TestingTraderBot(bot_config).setup()

    print(trader_bot.get_buy_price())
    trader_bot.execute_actions()
