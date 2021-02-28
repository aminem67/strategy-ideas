# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 22:42:33 2021

@author: Amin
"""

import math

import pandas as pd
import numpy as np

from pyalgotrade import strategy, dataseries
from pyalgotrade.broker.backtesting import Broker
from pyalgotrade.broker.backtesting import TradePercentage
import pyalgotrade.talibext.indicator as talib


class AS002Strategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, long_period, short_period):
        super(AS002Strategy, self).__init__(feed, Broker(100000, feed, commission=TradePercentage(0.00075)))
        
        self.__instrument = instrument
        self.__long_period = long_period
        self.__short_period = short_period        
        
        self.__position = None   

    def onBars(self, bars):

        bar = bars[self.__instrument]           
        close = bar.getClose()
        closeDs = self.getFeed().getDataSeries(self.__instrument).getCloseDataSeries()
        
        qty = 1                
       
        mom_long = talib.MOM(closeDs, count=self.__long_period+1, timeperiod=self.__long_period)  
        mom_short = talib.MOM(closeDs, count=self.__short_period+1, timeperiod=self.__short_period)  
        
        # Wait for enough bars to be available to calculate indicators.
        if (len(mom_long) < 1) or math.isnan(mom_long[-1]):
            return 
        
        buy_condition = (mom_long[-1] > 0) and (mom_short[-1] > 0)
        sell_condition = (mom_long[-1] < 0) or (mom_short[-1] < 0)
        
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if buy_condition:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, qty)

        # Else, Check for Stop-loss or Exit.        
        elif not self.__position.exitActive():            
            if sell_condition:                
                self.__position.exitMarket()
        
    def onEnterOk(self, position):        
        order = position.getEntryOrder()
        message = '[{}] | BUY qty: {} - filled: {} at $ {}.'.format(order.getSubmitDateTime(), 
                                                                   order.getQuantity(),
                                                                   order.getFilled(),
                                                                   order.getAvgFillPrice())
        print(message)  

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):        
        self.__position = None
        
        order = position.getExitOrder()
        message = '[{}] | SELL qty: {} - filled: {} at $ {}.'.format(order.getSubmitDateTime(), 
                                                                   order.getQuantity(),
                                                                   order.getFilled(),
                                                                   order.getAvgFillPrice())
        print(message)       

    def onExitCanceled(self, position):        
        self.__position.exitMarket()    
            

