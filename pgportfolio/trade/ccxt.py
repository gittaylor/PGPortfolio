from __future__ import absolute_import, division, print_function
import time
import numpy as np
import logging
import ccxt

from pgportfolio.trade.trader import Trader
from pgportfolio.marketdata.datamatrices import DataMatrices
from pgportfolio.tools.configprocess import parse_time
from pgportfolio.tools.trade import calculate_pv_after_commission

from pgportfolio.test import state

class CCXTtrader(Trader):
    def __init__(self, config, net_dir=None, agent=None, agent_type="nn"):
        state.pdb_try_again(state.CCXTtrader__init__, self, config, net_dir, agent, agent_type)

    @property
    def test_pv(self):
        return self._test_pv

    @property
    def test_pc_vector(self):
        return np.array(self._test_pc_vector, dtype=np.float32)

    def finish_trading(self):
        self._test_pv = self._total_capital

        """
        fig, ax = plt.subplots()
        ax.bar(np.arange(len(self._rolling_trainer.data_matrices.sample_count)),
               self._rolling_trainer.data_matrices.sample_count)
        fig.tight_layout()
        plt.show()
        """

    def _log_trading_info(self, time, omega):
        pass

    def _initialize_data_base(self):
        pass

    def _write_into_database(self):
        pass

    def _get_matrix_X(self):
        panel = self._data_matrices._history_manager.get_global_panel(parse_time(self._start), parse_time(self._start+self._period*self.steps), features=self._data_matrices._features)
        self._test_set.append(panel)
        # x=previous prices
        return np.array(panel)[:, :, :-1]

    def _get_matrix_y(self):
        # y=current metric changes. last vetor is the future price
        last_frame = np.array(self._test_set[-1])
        metric_changes = last_frame[:, :, -1] / last_frame[:, :, -2]
        # return the first metric only (for compatibility with BackTest)
        # one could consider other measures of success that combine features f(open, close, high, low, vol)
        return metric_changes[0, :]

    def rolling_train(self, online_sample=None):
        # currently, trader.py doesn't provide online_sample
        self._rolling_trainer.rolling_train()

    def generate_history_matrix(self):
        inputs = state.pdb_try_again(state.get_matrix_X, self)
        # inputs = self._get_matrix_X()
        if self._agent_type == "traditional":
            inputs = np.concatenate([np.ones([1, 1, inputs.shape[2]]), inputs], axis=1)
            inputs = inputs[:, :, 1:] / inputs[:, :, :-1]
        return inputs

    def trade_by_strategy(self, omega):
        logging.info("the step is {}".format(self._steps))
        logging.debug("the raw omega is {}".format(omega))
        
        future_price = np.concatenate((np.ones(1), self._get_matrix_y()))
        pv_after_commission = calculate_pv_after_commission(omega, self._last_omega, self._commission_rate)
        portfolio_change = pv_after_commission * np.dot(omega, future_price)
        self._total_capital *= portfolio_change
        self._last_omega = pv_after_commission * omega * \
            future_price /\
            portfolio_change
        logging.debug("the portfolio change this period is : {}".format(portfolio_change))
        self._test_pc_vector.append(portfolio_change)
        
class TransferAssets(dict):
    def __init__(self, **kwargs):
        super(TransferAssets, self).__init__(**kwargs)
        # initiate exchange list
        for exchange in self._get_ccxt_exchange_list():
            if exchange in self and 'apiKey' in self[exchange] and 'secret' in self[exchange]:
                self[exchange]['obj'] = getattr(ccxt, exchange)({'apiKey': self[exchange]['apiKey'], 'secret': self[exchange]['secret']})
        # add coin pairs from each exchange

        # add known trade times from history, if povided

    def add_coin_pair(self, exchange, coin1, coin2, trade_times=[], trade_amounts=[], ):
        pass
    
    def get_balances(self):
        return [exchange['obj'].fetch_balance() for exchange in self]

    def _get_key(self, exchange, coin1, coin2):
        return '|'.join([exchange, coin1, coin2])

    def _get_key_parts(self, key):
        return key.split('|')

    def _get_exchange_list(self):
        return self.keys()

    def _get_ccxt_exchange_list(self):
        # find all words that start with a lower case letter
        return [i for i in dir(ccxt) if i[0] in [chr(j) for j in range(97,123)]]

    def trade_coin_pair(self, exchange, coin1, coin2, quantity, price=None):
        """
        performs a trade using ccxt
        :param exchange: the exchange code
        :param coin1: the coin to buy
        :param coin2: the coin to sell
        :param quantity: the quantity of coin1
        :param price: the price is coin2 units. produces a limit order if provided, a market order if not provided
        """
        pass
    
    def trade_portfolio_change(self, portfolio_change, coin_list, trade_fraction=0.5):
        pass
