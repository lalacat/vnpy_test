import random
from datetime import datetime

from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.app.cta_strategy.strategies.boll_channel_strategy import BollChannelStrategy


p1 = random.randrange(4, 50, 2)  # 布林带窗口
p2 = random.randrange(4, 50, 2)  # 布林带通道阈值
p3 = random.randrange(4, 50, 2)  # CCI窗口
p4 = random.randrange(18, 40, 2)  # ATR窗口


engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="IF88.CFFEX",
    interval="1m",
    start=datetime(2018, 9, 1),
    end=datetime(2019, 1, 1),
    rate=0,
    slippage=0,
    size=300,
    pricetick=0.2,
    capital=1_000_000,
)

setting = {'boll_window': p1,  # 布林带窗口
           'boll_dev': p2,  # 布林带通道阈值
           'cci_window': p3,  # CCI窗口
           'atr_window': p4, }  # ATR窗口

# 加载策略
# engine.initStrategy(TurtleTradingStrategy, setting)
engine.add_strategy(BollChannelStrategy, setting)
engine.load_data()
engine.run_backtesting()
engine.calculate_result()
result = engine.calculate_statistics(Output=False)