import okex.futures_api as future
import okex.account_api as account
import okex.spot_api as spot
import pandas as pd
import datetime
import time
from tools.DBTool import DBTool
from tools.ReadConfig import ReadConfig
from sqlalchemy import create_engine
from sqlalchemy.types import DECIMAL, TEXT, Date, DateTime


# earned_profit_asset 已获利润资产
# earned_profit_cost 已获利润资产
# net_current_cost 当前净持仓成本
# net_current_asset 当前净持仓资产
# total_position_asset  累计持仓资产
# total_position_cost 累计持仓成本
# net_current_cost_price 当前净持仓成本价


def get_timestamp(time):
    # now = datetime.datetime.now()
    t = time.isoformat("T", "milliseconds")
    return t + "Z"


# 获得累计持仓资产
def get_total_position_asset(engine, instrument_id):
    query_sql = '''SELECT sum(size) as v,currency,side
            FROM account_okex_spot_fill
            where instrument_id ='{}' 
            and fee != '0'
            and currency = '{}'
      group by currency,side;'''.format(instrument_id, instrument_id.split("-")[0])

    # print(query_sql)
    df = pd.read_sql(sql=query_sql, con=engine)
    return df['v'][0]


# 获得已获利润资产
def get_earned_profit_asset(engine, instrument_id):
    query_sql = '''SELECT sum(size)as v,currency,side
            FROM account_okex_spot_fill
            where instrument_id ='{}' 
            and fee = '0'
            and currency = '{}'
      group by currency,side;'''.format(instrument_id, instrument_id.split("-")[0])

    # print(query_sql)
    df = pd.read_sql(sql=query_sql, con=engine)
    return df['v'][0]


# 获得累计持仓资产
def get_earned_profit_cost(engine, instrument_id):
    query_sql = '''SELECT sum(size)as v,currency,side
            FROM account_okex_spot_fill
            where instrument_id ='{}' 
            and fee != '0'
            and currency = '{}'
      group by currency,side;'''.format(instrument_id, instrument_id.split("-")[1])

    # print(query_sql)
    df = pd.read_sql(sql=query_sql, con=engine)
    return df['v'][0]


# 获得累计持仓成本
def get_total_position_cost(engine, instrument_id):
    query_sql = '''SELECT sum(size)as v,currency,side
            FROM account_okex_spot_fill
            where instrument_id ='{}' 
            and fee = '0'
            and currency = '{}'
      group by currency,side;'''.format(instrument_id, instrument_id.split("-")[1])

    # print(query_sql)
    df = pd.read_sql(sql=query_sql, con=engine)
    return df['v'][0]


def main():
    config = ReadConfig()

    # 初始化数据库连接
    engine = create_engine(config.get_dbURL())

    okex_api_key = config.get_okex("OKEX_API_KEY")
    okex_secret_key = config.get_okex("OKEX_SECRET_KEY")
    okex_passphrase = config.get_okex("OKEX_PASSPHRASE")

    spotAPI = spot.SpotAPI(okex_api_key, okex_secret_key, okex_passphrase, False)
    accountAPI = account.AccountAPI(okex_api_key, okex_secret_key, okex_passphrase, False)

    now = datetime.datetime.now()

    #  已获利润资产
    earned_profit_asset = get_earned_profit_asset(engine, 'OKB-USDT')
    #  已获利润资产
    earned_profit_cost = get_earned_profit_cost(engine, 'OKB-USDT')
    #   累计持仓资产
    total_position_asset = get_total_position_asset(engine, 'OKB-USDT')
    #  累计持仓成本
    total_position_cost = get_total_position_cost(engine, 'OKB-USDT')
    # net_current_cost 当前净持仓成本
    net_current_cost = total_position_cost - earned_profit_cost
    #  当前净持仓资产
    net_current_asset = total_position_asset - earned_profit_asset
    #  当前净持仓成本价
    net_current_cost_price = net_current_cost / net_current_asset


    print("earned_profit_asset:{},\n"
          "earned_profit_cost:{},\n"
          "total_position_asset:{},\n"
          "total_position_cost:{},\n"
          "net_current_cost:{},\n"
          "net_current_asset={},\n"
          "net_current_cost_price={}\n".format(earned_profit_asset,
                                             earned_profit_cost,
                                             total_position_asset,
                                             total_position_cost,
                                             net_current_cost,
                                             net_current_asset,
                                             net_current_cost_price))

if __name__ == '__main__':
    main()
