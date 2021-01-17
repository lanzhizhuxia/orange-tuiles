import okex.account_api as account
import okex.futures_api as future
import okex.spot_api as spot
import pandas as pd
import datetime
import time
from tools.DBTool import DBTool
from tools.ReadConfig import ReadConfig
from sqlalchemy import create_engine
from sqlalchemy.types import DECIMAL, TEXT, Date, DateTime


def get_timestamp(time):
    # now = datetime.datetime.now()
    t = time.isoformat("T", "milliseconds")
    return t + "Z"


def get_okex_spot_accounts(spotAPI, time):
    # okex现货账户信息
    result = spotAPI.get_account_info()
    spotAccount = pd.DataFrame(result, columns=['frozen', 'hold', 'id', 'currency', 'balance', 'available', 'holds'])
    spotAccount['time'] = time
    spotAccount['ts'] = time.timestamp()
    return spotAccount


def save_okex_spot_accounts(spotAccounts, engine):
    dtypedict = {'frozen': DECIMAL(18, 8), 'hold': DECIMAL(18, 8), 'id': TEXT, 'currency': TEXT,
                 'balance': DECIMAL(18, 8), 'available': DECIMAL(18, 8), 'holds': DECIMAL(18, 8), 'data': DateTime,
                 'ts': TEXT}
    spotAccounts.to_sql(name='account_okex_spot', con=engine, chunksize=1000, if_exists='append', index=None,
                        dtype=dtypedict)


def get_okex_spot_fills(spotAPI, instrument_id, after, before):
    # okex现货账户信息
    result = spotAPI.get_fills(instrument_id=instrument_id, order_id='', after=after, before=before, limit='')
    spot_fills = pd.DataFrame(result[0], columns=['ledger_id', 'trade_id', 'instrument_id', 'price', 'size', 'order_id',
                                                  'timestamp', 'exec_type', 'fee', 'side', 'currency'])
    spot_fills['timestamp'] = spot_fills['timestamp'].apply(lambda x: x[:-1])
    return spot_fills


def save_okex_spot_fills(spot_fills, engine):
    dtypedict = {'ledger_id': TEXT, 'trade_id': TEXT, 'instrument_id': TEXT, 'price': DECIMAL(18, 8),
                 'size': TEXT, 'order_id': TEXT, 'timestamp': DateTime, 'exec_type': TEXT,
                 'fee': DECIMAL(18, 8), 'side': TEXT, 'currency': TEXT}
    spot_fills.to_sql(name='account_okex_spot_fill', con=engine, chunksize=1000, if_exists='append', index=None,
                      dtype=dtypedict)


def get_okex_asset_valuation(accountAPI, account_type, currency):
    time.sleep(35)
    result0 = accountAPI.get_asset_valuation(account_type=account_type, valuation_currency=currency)
    asset0 = pd.DataFrame(result0, columns=['account_type', 'balance', 'valuation_currency', 'timestamp'], index=[0])

    def ff(x):
        timeArray = time.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    # okex现货账户信息

    asset0['ts'] = asset0['timestamp'].apply(lambda x: x[:-1])
    asset0['timestamp'] = asset0['timestamp'].apply(lambda x: x[:-1])
    return asset0


def save_okex_asset_valuation(asset_valuation, engine):
    dtypedict = {'account_type': TEXT, 'balance': DECIMAL(18, 8), 'valuation_currency': TEXT, 'timestamp': DateTime,
                 'ts': TEXT}
    asset_valuation.to_sql(name='account_okex_asset_valuation', con=engine, chunksize=1000, if_exists='append',
                           index=None, dtype=dtypedict)



def insert_func(table, conn, keys, data_iter):
    """
    Pandas中to_sql方法的回调函数
    :param table:Pandas的table
    :param conn:数据库驱动连接对象
    :param keys:要存入的字段名
    :param data_iter:DataFrame对象也就是数据迭代器
    :return:
    """
    dbapi_conn = conn.connection
    # 创建数据库游标对象
    with dbapi_conn.cursor() as cursor:
        # 遍历拼接sql语句
        for data_tuple in data_iter:
            sql = """INSERT INTO {TABLE_NAME}(bill_name, room_number, bind_status, community_name, area_m) VALUES('{BILL_NAME}', '{ROOM_NUMBER}', {BIND_STATUS}, '{COMMUNITY_NAME}', {AREA_M}) ON conflict({UNIQUE_LIST}) DO UPDATE SET bill_name='{BILL_NAME}', bind_status={BIND_STATUS}, area_m='{AREA_M}'""".format(
                TABLE_NAME=table.name, UNIQUE_LIST="community_name, room_number",
                BILL_NAME=data_tuple[0], ROOM_NUMBER=data_tuple[2], COMMUNITY_NAME=data_tuple[1],
                BIND_STATUS=data_tuple[3], AREA_M=data_tuple[4])
            cursor.execute(sql)


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


    flag = True
    after = ''
    while (flag):
        query_sql = '''SELECT  ledger_id
FROM orange.account_okex_spot_fill  where instrument_id ='OKB-USDT'  order by `timestamp` limit 1'''

        # print(query_sql)
        res = pd.read_sql(sql=query_sql, con=engine)

        if (after != res['ledger_id'][0]):

            after = res['ledger_id'][0]
            spot_fills = get_okex_spot_fills(spotAPI, "OKB-USDT", after, '')
            save_okex_spot_fills(spot_fills, engine)
            print(after)
        else:
            flag = False

    spotAccounts=get_okex_spot_accounts(spotAPI,now)
    save_okex_spot_accounts(spotAccounts,engine)

    # 0.
    # 预估总资产
    # 1.
    # 币币账户
    # 3.
    # 交割账户
    # 5.
    # 币币杠杆
    # 6.
    # 资金账户
    # 9.
    # 永续合约
    # 12.
    # 期权
    # 15.
    # 交割usdt保证金账户
    # 16.
    # 永续usdt保证金账户
    account_type_list = ['0', '1', '3', '5', '6', '9', '12', '15', '16']
    asset = pd.DataFrame(columns=['account_type', 'balance', 'valuation_currency', 'timestamp', 'ts'], index=[0])
    for account_type in account_type_list:
        res = get_okex_asset_valuation(accountAPI, account_type, "USD")
        print(res)
        save_okex_asset_valuation(res,engine)


if __name__ == '__main__':
    main()
