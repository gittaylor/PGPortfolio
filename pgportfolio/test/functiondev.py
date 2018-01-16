import logging
import numpy as np
from pgportfolio.tools.trade import calculate_pv_after_commission
import time

def start_trading(self):
    try:
        if not self.__class__.__name__=="BackTest":
            while self._total_steps is None or self._steps < self._total_steps:
                now = time.time()
                next_step_time = self._start + self._period * (self._steps + 1)
                if now > next_step_time:
                    # TODO: sleeptime = self.__trade_body()
                    logging.info("start trading step %s at %s" % (self._steps + 1, time.ctime(now)))
                    self._Trader__trade_body()
                else:
                    logging.info("sleep for %s seconds" % (next_step_time - now))
                    time.sleep(next_step_time - now)
        else:
            #BackTest should never have None self._total_steps
            while self._steps < self._total_steps:
                # TODO: self.__trade_body()
                self._Trader__trade_body()
    finally:
        if self._agent_type=="nn":
            self._agent.recycle()
        self.finish_trading()

def get_matrix_X(self):
    end = self._start + self._period * self._steps
    start = end  - self._period * self._window_size
    panel = self._data_matrices._history_manager.get_global_panel(start, end, features=self._data_matrices._features)
    self._test_set.append(panel)
    # x=previous prices
    return np.array(panel)[:, :, :-1]

from pgportfolio.trade.ccxt import CCXTtrader
from pgportfolio.trade.trader import Trader
from pgportfolio.marketdata.datamatrices import DataMatrices
from pgportfolio.tools.configprocess import parse_time
from pgportfolio.tools.trade import calculate_pv_after_commission
def CCXTtrader__init__(self, config, net_dir, agent, agent_type):
    # Fix Trader to take current_config
    # Fix this so we don't have to use the original config - clunky
    period = config["input"]["global_period"]
    if "steps" in config["trading"]:
        total_steps = config["trading"]["steps"]
    else:
        total_steps = None
    # replace with super()
    Trader.__init__(self, period, config, total_steps, net_dir, initial_BTC=1, agent=None, agent_type=None)
    self._start = time.time()

    self.setup_agent(config, net_dir, agent, agent_type)

    # start_date and end_date automatically set
    config["input"]["end"] = self._start
    if "end_date" in config["input"]:
        del config["input"]["end_date"]
    config["input"]["start"] = self._start - self._window_size
    if "start_date" in config["input"]:
        del config["input"]["start_date"]
    # self._rolling_trainer was setup by Trader.setup_agent
    self._data_matrices = self._rolling_trainer.data_matrices

    self._test_set = []
    # add the current data as a starting point
    get_matrix_X(self)
    # self._get_matrix_X()
    self._test_pv = 1.0
    self._test_pc_vector = []

# update function for loading objects from disk
def update_pgportfolio_trade_CCXTtrader(object):
    pass

