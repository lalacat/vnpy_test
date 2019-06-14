import inspect
import traceback
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules
import logging

from vnpy.app.cta_backtester import BacktesterEngine
from vnpy.trader.engine import BaseEngine

logger = logging.getLogger(__name__)

def import_spider(path):
    # 导入爬虫包
    spiders = []

    spider = import_module(path)
    spiders.append(spider)

    if hasattr(spider, "__path__"):

        for _, subpath, ispkg in iter_modules(spider.__path__):
            # 取得模块的绝对路径
            fullpath = path + "." + subpath

            # 判断是模块包还是模块
            if ispkg:
                # 是模块包的话重新调用本方法将模块包下的所以模块都导入
                spiders += import_spider(fullpath)
            else:
                # 是模块的话就直接导入到结果中
                submod = import_module(fullpath)
                spiders.append(submod)
    else:
        logger.error("路径不对，脚本放在根目录下")
    return spiders
_found = {}
_spiders = {}
def _load_spiders(module):
        for spcls in _iter_spider_classes(module):
            _found[spcls.name].append((module.__name__,spcls.__name__))
            _spiders[spcls.name] =spcls

def _iter_spider_classes(module):
        for obj in vars(module).values():
            """
            vars（）实现返回对象object的属性和属性值的字典对象
            要过滤出obj是类的信息，其中类的信息包括，模块导入其他模块的类的信息，模块中的父类，模块中所有定义的类
            因此，条件过滤分别是：
            1.判断obj的类型为class
            2.判断是否继承父类，因此命令包中__init__文件中定义的就是整个包中所需要的父类
            3.判断类是否为模块本身定义的类还是导入其他模块的类(感觉第二个条件包含此条件了有些多余)
            4.剔除父类
            """
            if inspect.isclass(obj) and \
                    issubclass(obj, BaseEngine) and \
                    obj.__module__ == module.__name__ and \
                    getattr(obj,"name",None):
                yield obj

def _load_all_spiders(self):
    # 根据设置的包名中导入爬虫，因为可能用户会针对不同的爬虫对象设置不同的包名
    for name in self._spider_modules:
        try:
            for module in import_spider(name):
                self._load_spiders(module)
        # ImportError 包含ModuleNotFoundError
        except  ImportError as e:
            if self.warn_only:
                msg = ("\n{tb}Could not load spiders from module '{modname}'. "
                       "See above traceback for details.".format(
                    modname="crawler.commands", tb=traceback.format_exc()))
                logger.warn(msg, RuntimeWarning)
            else:
                raise
    self._check_name_duplicates()


# backtester = BacktesterEngine("_","_")
# # print(backtester.classes)
# app_path = Path(__file__).parent.parent
# print(app_path)
# path1 = app_path.joinpath("cta_strategy", "strategies")
spiders = import_spider('vnpy.app.cta_strategy.strategies')
for i in spiders:
    print(i)