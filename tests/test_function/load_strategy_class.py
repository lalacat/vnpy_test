import multiprocessing

from vnpy.app.cta_strategy import CtaEngine

# cta = CtaEngine(None,None)

# cta.load_strategy_class()
# cta.load_strategy_setting()
# cta.load_strategy_data()
# print(cta.strategy_data)

a  = 100_000_000
pool = multiprocessing.cpu_count()
print(a)
