from .MockTraderBot import MockTraderBot
from trader_bot.TraderBot import TraderBotConfig
from .InvestmentUtil import InvestmentUtil
import time


class TestingTraderBot(MockTraderBot):
    def __init__(self, config: TraderBotConfig, investment_util: InvestmentUtil):
        super().__init__(config, investment_util)
        self.last_transaction = None

    def _record_decision(self, decision, reason, margin=None):
        self.decision = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'decision': decision,
            'reason': reason
        }

        print(self.decision)

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

    def _get_last_transaction(self):
        return self.last_transaction

    def set_last_transaction(self, last_transaction):
        self.last_transaction = last_transaction
