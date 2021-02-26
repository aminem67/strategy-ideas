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


class AS001Strategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, ema1_period, ema2_period, ema3_period):
        super(AS001Strategy, self).__init__(feed, Broker(100000, feed, commission=TradePercentage(0.00075)))
        
        self.__instrument = instrument
        self.__ema1_period = ema1_period
        self.__ema2_period = ema2_period
        self.__ema3_period = ema3_period
        self.__hlc3 = dataseries.SequenceDataSeries()
        
        self.__position = None   

    def onBars(self, bars):

        bar = bars[self.__instrument]   
        high = bar.getHigh()
        low = bar.getLow()
        close = bar.getClose()
        hlc3 = (high + low + close) / 3
        self.__hlc3.appendWithDateTime(bar.getDateTime(), hlc3)
        
        qty = 1                
       
        ema1 = talib.EMA(self.__hlc3, count=self.__ema1_period+1, timeperiod=self.__ema1_period)
        ema2 = talib.EMA(self.__hlc3, count=self.__ema2_period+1, timeperiod=self.__ema2_period)
        ema3 = talib.EMA(self.__hlc3, count=self.__ema3_period+1, timeperiod=self.__ema3_period)
        
        # Wait for enough bars to be available to calculate indicators.
        if (len(ema3) < 2) or math.isnan(ema3[-2]):
            return        
        
        buy_condition = self.is_increasing(ema1, 1) and self.is_increasing(ema2, 1) and self.is_increasing(ema3, 1)
        sell_condition = self.is_decreasing(ema1, 1) and self.is_decreasing(ema2, 1) and self.is_decreasing(ema3, 1) 
        
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
        
    def is_increasing(self, ds, count):
        index = count+1 if count >= 1 else 2
        if (len(ds) >= index) and (not math.isnan(ds[-index])):
            for i in range(1, index):
                if ds[-i] <= ds[-(i+1)]:
                    return False

            return True
        else:
            return False

    def is_decreasing(self, ds, count):
        index = count+1 if count >= 1 else 2
        if (len(ds) >= index) and (not math.isnan(ds[-index])):
            for i in range(1, index):
                if ds[-i] >= ds[-(i+1)]:
                    return False

            return True
        else:
            return False

