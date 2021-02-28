
import pandas as pd

from pyalgotrade.barfeed import csvfeed
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown, trades
from pyalgotrade import plotter

from python import AS001
from util import get_pandas_timeframe_frequency

# %% Runner methods

def run_AS001(asset, 
              csvFilePath, 
              pandasTimeFrame, 
              ema1_period, 
              ema2_period,  
              ema3_period):
    
    strategyName = 'AS001: {}'.format(asset)

    freq = get_pandas_timeframe_frequency(pandasTimeFrame)
        
    # Load the bar feed from the CSV file
    feed = csvfeed.GenericBarFeed(frequency=freq, maxLen=10000000)
    feed.addBarsFromCSV(asset, csvFilePath)    

    # Evaluate the strategy with the feed.
    strategy = AS001.AS001Strategy(feed, asset, ema1_period, ema2_period, ema3_period)           
    
    return run_analyze_plot(strategyName, strategy, asset, feed)

# %% Helper methods

def run_analyze_plot(strategyName, strategy, asset, feed):
    """"""
    
    # Attach different analyzers to a strategy before executing it.
    returnsAnalyzer = returns.Returns(maxLen=1000000)
    strategy.attachAnalyzer(returnsAnalyzer)
    
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strategy.attachAnalyzer(sharpeRatioAnalyzer)
    
    drawDownAnalyzer = drawdown.DrawDown()
    strategy.attachAnalyzer(drawDownAnalyzer)
    
    tradesAnalyzer = trades.Trades()
    strategy.attachAnalyzer(tradesAnalyzer)
    
    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(strategy)
    
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Strategy returns", returnsAnalyzer.getReturns())
    
    # Run the strategy.
    strategy.run()
    
    # Print performances
    print_performance_results(strategyName, strategy, returnsAnalyzer, sharpeRatioAnalyzer, drawDownAnalyzer, tradesAnalyzer)
    
    # Plot the strategy.
    plt.plot()
    
    fromTime = feed[asset][0].getDateTime()
    toTime = feed[asset][-1].getDateTime()
    
    df = pd.DataFrame(index=pd.date_range(fromTime, toTime))
    
    tradeReturns = tradesAnalyzer.getAllReturns()
    sequenceDataSeries = returnsAnalyzer.getReturns()
    dateTimes = sequenceDataSeries.getDateTimes()

    dtIndex = 0
    for dt in dateTimes:
        df.at[dt, strategyName] = sequenceDataSeries.__getitem__(dtIndex)
        dtIndex = dtIndex + 1
    
    return tradeReturns, df    

def print_performance_results(name, strategy, returnsAnalyzer, sharpeRatioAnalyzer, drawDownAnalyzer, tradesAnalyzer):
    """"""

    print("")
    print('=== Performance Summary ({}) ==='.format(name))
    print("Final portfolio value: $%.2f" % strategy.getResult())
    print("Cumulative returns: %.2f %%" % (returnsAnalyzer.getCumulativeReturns()[-1] * 100))    
    print("Anualized Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(riskFreeRate=0, annualized=True)))
    print("Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100))
    print("Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration()))    
    
    print("")
    print('=== Trades Summary ({}) ==='.format(name))
    print("Total trades: %d" % (tradesAnalyzer.getCount()))
    print("Winning trades: %d" % (tradesAnalyzer.getProfitableCount()))
    print("Losing trades: %d" % (tradesAnalyzer.getUnprofitableCount()))
    
    if tradesAnalyzer.getCount() > 0:        
        rets = tradesAnalyzer.getAllReturns()
        print("Avg. return: %.2f %%" % (rets.mean() * 100))
        print("Returns std. dev.: %.2f %%" % (rets.std() * 100))
        print("Max. return: %.2f %%" % (rets.max() * 100))
        print("Min. return: %.2f %%" % (rets.min() * 100))  
        
        profits = tradesAnalyzer.getAll()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))    

