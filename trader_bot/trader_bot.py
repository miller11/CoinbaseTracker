from TraderBot import TraderBotConfig
from MockTraderBot import MockTraderBot

if __name__ == '__main__':
    json_body = "{\n  \"account_id\": \"bec75c28-d95a-52a9-8edf-d0947a133eda\",\n  \"default_buy\": 100,\n  \"interval\": \"30m\",\n  \"short_term_periods\": 5,\n  \"long_term_periods\": 20\n}"

    bot_config = TraderBotConfig(json_body)

    # TraderBot(bot_config).execute_actions()

    MockTraderBot(bot_config).execute_actions()
