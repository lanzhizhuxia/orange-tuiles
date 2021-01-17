import pandas as pd
import datetime
import time
from sqlalchemy import create_engine
from sqlalchemy.types import INTEGER, TEXT,  DateTime, DECIMAL


class Kline():

    def __init__(self,spotAPI,engine):
        self.spotAPI =spotAPI
        self.engine= engine


    def get_timestamp(self,time):
        if time =='':
            return ''
        else:
            #now = datetime.datetime.now()
            t = time.isoformat("T", "milliseconds")
            return t + "Z"


    def get_okex_spot_kline(self,instrument_id ,start,end, granularity):

        def ff(x):
            timeArray = time.strptime(x["time"], "%Y-%m-%dT%H:%M:%S.000Z")
            timeStamp = int(time.mktime(timeArray))
            return timeStamp

        result = self.spotAPI.get_kline(instrument_id=instrument_id, start=self.get_timestamp(start), end=self.get_timestamp(end), granularity=granularity)
        okb = pd.DataFrame(result, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        if len(okb) == 0:
            okb["instrument_id"] = instrument_id
            okb['time'] = ''
            return okb

        okb["instrument_id"]=instrument_id
        okb['ts'] = okb.apply(lambda x: ff(x), axis=1)
        okb['time'] = okb['time'].apply(lambda x: x[:-1])

        #okb['time'] = okb['time'].apply(lambda x : x.strftime('%Y-%m-%d %H:%M:%S'))

        return okb



    def save_okex_spot_kline(self,okbkline,tablename,duplicates):

        if len(okbkline) == 0:
            print("[save_okex_spot_kline]okbkline is null.........")
            return

        if(duplicates):

            list1 = '"{}"'.format('","'.join(str(i) for i in okbkline["time"].values.tolist()))

            query_sql='''SELECT *
                FROM {}
                where time in ({});'''.format(tablename,list1)

            #print(query_sql)
            df = pd.read_sql(sql=query_sql, con=self.engine)
            df['ts'] = df['ts'].astype('int64')

            temp=okbkline.append(df)
            temp2 = temp.append(df)
            diff = temp2.drop_duplicates(subset=['ts'], keep=False)

        else:
            diff=okbkline

        dtypedict = {'instrument_id': TEXT, 'open': DECIMAL(18, 8), 'high': DECIMAL(18, 8), 'low': DECIMAL(18, 8),
                     'close': DECIMAL(18, 8), 'volume': DECIMAL(18, 8), 'time': DateTime,'ts': TEXT}
        diff.to_sql(name=tablename, con=self.engine, chunksize=1000, if_exists='append', index=None,dtype=dtypedict)

        # okbkline86400=get_okex_spot_kline("OKB-USDT",start,end,86400)
        #
        # okbkline86400.to_sql(name='kline_okex_1d', con=engine, chunksize=1000, if_exists='append', index=None,dtype=dtypedict)


def main():
    print("kline")


if __name__ == '__main__':
    main()