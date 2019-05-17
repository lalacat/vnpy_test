from vnpy.event import EventEngine
from vnpy.trader.engine import LogEngine

logengine = LogEngine()
eventEngine = EventEngine()
eventEngine.start()