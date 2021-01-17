import datetime
import pandas as pd
import os
import time
import logging
import traceback

from flask import Flask
from sqlalchemy import create_engine
from markupsafe import escape



import okex.spot_api as spot
import okex.account_api as account

from tools.ReadConfig import ReadConfig
from kline.kline import Kline
from account.account import Account


app = Flask(__name__)

@app.route("/")
def index():
    return """
    <h1>Python Flask in Docker!</h1>
    <p>A sample web-app for running Flask inside Docker.</p>
    <p>22222222222.</p>
    """

@app.route("/assetValuation")
@app.route("/assetValuation/<accountType>")
@app.route("/assetValuation/<accountType>/<currency>")
def save_asset_Valuation(accountType='0',currency='USD'):
    config = ReadConfig()

    # 初始化数据库连接
    engine = create_engine(config.get_dbURL())

    okex_api_key = config.get_okex("OKEX_API_KEY")
    okex_secret_key = config.get_okex("OKEX_SECRET_KEY")
    okex_passphrase = config.get_okex("OKEX_PASSPHRASE")

    spotAPI = spot.SpotAPI(okex_api_key, okex_secret_key, okex_passphrase, False)
    accountAPI = account.AccountAPI(okex_api_key, okex_secret_key, okex_passphrase, False)

    accountClient=Account(spotAPI,accountAPI,engine)

    now = datetime.datetime.now()


    asset = pd.DataFrame(columns=['account_type', 'balance', 'valuation_currency', 'timestamp', 'ts'], index=[0])

    res = accountClient.get_okex_asset_valuation(accountType, currency)
    print(res)
    accountClient.save_okex_asset_valuation(res)

    return """
        <h1>更新资产完成</h1>
        <p>/assetValuation</p>
        <p>/assetValuation/accountType</p>
        <p>/assetValuation/accountType/currency</p>
        <p>0：预估总资产</p>
        <p>1：币币账户</p>
        <p>3：交割账户</p>
        <p>5：币币杠杆</p>
        <p>6：资金账户</p>
        <p>9：永续合约</p>
        <p>12：期权</p>
        <p>15：交割usdt保证金账户</p>
        <p>16：永续usdt保证金账户</p>
        <p>{}</p>
        """.format(res)


@app.route("/kline")
@app.route("/kline/<instrumentId>")
def save_kline(instrumentId="OKB-USDT"):
    app.logger.info('instrument_id:{}'.format(instrumentId))

    config= ReadConfig()

    # 初始化数据库连接
    engine = create_engine(config.get_dbURL())

    okex_api_key = config.get_okex("OKEX_API_KEY")
    okex_secret_key = config.get_okex("OKEX_SECRET_KEY")
    okex_passphrase = config.get_okex("OKEX_PASSPHRASE")

    spotAPI = spot.SpotAPI(okex_api_key, okex_secret_key, okex_passphrase, False)

    kline = Kline(spotAPI,engine)

    now = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    end = now
    start = now - datetime.timedelta(days=1)

    for i in range(5):

        kline900 = kline.get_okex_spot_kline(instrumentId, start, end, 900)
        try:
            kline.save_okex_spot_kline(kline900, "kline_okex_15", True)
        except Exception:
            app.logger.error(traceback.format_exc())  # 用法


        end = end - datetime.timedelta(days=i)
        start = start - datetime.timedelta(days=1)



    end=now
    start=end - datetime.timedelta(days=200)

    for i in range(5):

        print(i,end,start)

        kline86400 = kline.get_okex_spot_kline( instrumentId, start, end, 86400)
        kline.save_okex_spot_kline(kline86400, "kline_okex_1d", True)

        end = end - datetime.timedelta(days=200)
        start = start - datetime.timedelta(days=200)

    return """
    <h1>{}</h1>
    <p>15分钟和1日线kline搜集完成。</p>
    <p>/kline/DOT-USDT</p>
    """.format(instrumentId)


if __name__ == "__main__":
    app.debug = True
    handler = logging.FileHandler('flask.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')

