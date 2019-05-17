import random
import multiprocessing
import numpy as np
from deap import creator, base, tools, algorithms
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.boll_channel_strategy import BollChannelStrategy
from datetime import datetime
import multiprocessing           #多进程
from scoop import futures

def parameter_generate():
    '''
    根据设置的起始值，终止值和步进，随机生成待优化的策略参数
    '''
    parameter_list = []
    p1 = random.randrange(4,50,2)      #布林带窗口
    p2 = random.randrange(4,50,2)      #布林带通道阈值
    p3 = random.randrange(4,50,2)      #CCI窗口
    p4 = random.randrange(18,40,2)     #ATR窗口

    parameter_list.append(p1)
    parameter_list.append(p2)
    parameter_list.append(p3)
    parameter_list.append(p4)

    return parameter_list

def object_func(strategy_avg):
    """
    本函数为优化目标函数，根据随机生成的策略参数，运行回测后自动返回2个结果指标：收益回撤比和夏普比率
    """
    # 创建回测引擎对象
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="IF88.CFFEX",
        interval="1m",
        start=datetime(2018, 9, 1),
        end=datetime(2019, 1,1),
        rate=0,
        slippage=0,
        size=300,
        pricetick=0.2,
        capital=1_000_000,
    )

    setting = {'boll_window': strategy_avg[0],       #布林带窗口
               'boll_dev': strategy_avg[1],        #布林带通道阈值
               'cci_window': strategy_avg[2],         #CCI窗口
               'atr_window': strategy_avg[3],}    #ATR窗口

    #加载策略
    #engine.initStrategy(TurtleTradingStrategy, setting)
    engine.add_strategy(BollChannelStrategy, setting)
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    result = engine.calculate_statistics(Output=False)

    return_drawdown_ratio = round(result['return_drawdown_ratio'],2)  #收益回撤比
    sharpe_ratio= round(result['sharpe_ratio'],2)                   #夏普比率
    return return_drawdown_ratio , sharpe_ratio

#设置优化方向：最大化收益回撤比，最大化夏普比率
creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0)) # 1.0 求最大值；-1.0 求最小值
creator.create("Individual", list, fitness=creator.FitnessMulti)

def optimize():
    """"""
    toolbox = base.Toolbox()  #Toolbox是deap库内置的工具箱，里面包含遗传算法中所用到的各种函数

    # 初始化
    toolbox.register("individual", tools.initIterate, creator.Individual,parameter_generate) # 注册个体：随机生成的策略参数parameter_generate()
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)               #注册种群：个体形成种群
    toolbox.register("mate", tools.cxTwoPoint)                                               #注册交叉：两点交叉
    toolbox.register("mutate", tools.mutUniformInt,low = 4,up = 40,indpb=0.6)                #注册变异：随机生成一定区间内的整数
    toolbox.register("evaluate", object_func)                                                #注册评估：优化目标函数object_func()
    toolbox.register("select", tools.selNSGA2)       #注册选择:NSGA-II(带精英策略的非支配排序的遗传算法)
    #pool = multiprocessing.Pool()
    #toolbox.register("map", pool.map)
    #toolbox.register("map", futures.map)

    #遗传算法参数设置
    MU = 40                                  #设置每一代选择的个体数
    LAMBDA = 160                             #设置每一代产生的子女数
    pop = toolbox.population(400)            #设置族群里面的个体数量
    CXPB, MUTPB, NGEN = 0.5, 0.35,40        #分别为种群内部个体的交叉概率、变异概率、产生种群代数
    hof = tools.ParetoFront()                #解的集合：帕累托前沿(非占优最优集)

    #解的集合的描述统计信息
    #集合内平均值，标准差，最小值，最大值可以体现集合的收敛程度
    #收敛程度低可以增加算法的迭代次数
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    np.set_printoptions(suppress=True)            #对numpy默认输出的科学计数法转换
    stats.register("mean", np.mean, axis=0)       #统计目标优化函数结果的平均值
    stats.register("std", np.std, axis=0)         #统计目标优化函数结果的标准差
    stats.register("min", np.min, axis=0)         #统计目标优化函数结果的最小值
    stats.register("max", np.max, axis=0)         #统计目标优化函数结果的最大值

    #运行算法
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)     #esMuPlusLambda是一种基于(μ+λ)选择策略的多目标优化分段遗传算法

    return pop

optimize()