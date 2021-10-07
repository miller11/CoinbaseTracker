from bot.TraderBot import TraderBotConfig
from bot.TraderBot import TraderBot

if __name__ == '__main__':
    bot_config = TraderBotConfig(account_id='bec75c28-d95a-52a9-8edf-d0947a133eda', default_buy=100,
                                 interval='30m', short_term_periods=5, long_term_periods=20)

    TraderBot(bot_config).execute_actions()
