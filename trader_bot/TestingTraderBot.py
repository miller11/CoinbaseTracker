from MockTraderBot import MockTraderBot, TraderBotConfig
import time


class TestingTraderBot(MockTraderBot):
    def __init__(self, config: TraderBotConfig):
        super().__init__(config)

    def _record_decision(self, decision, reason, margin=None):
        bot_decision = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'decision': decision,
            'reason': reason
        }

        print(bot_decision)

    def _put_transaction(self, operation, amount):
        return ''

