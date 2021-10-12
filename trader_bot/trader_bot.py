from TraderBot import TraderBotConfig, TraderBot
from MockTraderBot import MockTraderBot

if __name__ == '__main__':
    json_body = "{\n  \"account_id\": \"83af70bf-3ddd-5c45-8a1b-4d1139e1f569\",\n  \"default_buy\": 100,\n  \"interval\": \"30m\",\n  \"short_term_periods\": 5,\n  \"long_term_periods\": 20\n}"

    bot_config = TraderBotConfig(json_body)

    #TraderBot(bot_config).execute_actions()

    trader_bot = MockTraderBot(bot_config).setup()

    trader_bot.get_buy_price()
