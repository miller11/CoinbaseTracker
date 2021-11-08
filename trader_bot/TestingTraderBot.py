from MockTraderBot import MockTraderBot, TraderBotConfig
from InvestmentUtil import InvestmentUtil
import time


class TestingTraderBot(MockTraderBot):
    def __init__(self, config: TraderBotConfig, investment_util: InvestmentUtil):
        super().__init__(config, investment_util)

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
        transaction = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'amount': str(amount),
            'currency_pair': self.currency_pair
        }

        print(transaction)

