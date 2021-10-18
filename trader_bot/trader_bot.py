from TraderBot import TraderBotConfig, TraderBot
from MockTraderBot import MockTraderBot
from TestingTraderBot import TestingTraderBot

if __name__ == '__main__':
    # ETH account
    json_body = "{\n  \"account_id\": \"f476634d-d6eb-52aa-a338-70d1d4de65e0\",\n  " \
                "\"default_buy\": 100,\n  " \
                "\"interval\": \"30m\",\n  " \
                "\"short_term_periods\": 5,\n  " \
                "\"long_term_periods\": 20\n}"

    bot_config = TraderBotConfig(json_body)

    # TraderBot(bot_config).execute_actions()

    trader_bot = TestingTraderBot(bot_config).setup()

    trader_bot.execute_actions()
