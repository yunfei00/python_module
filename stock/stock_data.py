"""
获取所有股票数据 并按照获取时间存取 存放当前日期
"""

# date：日期，数据对应的时间点。
# open：开盘价，当天交易开始时的价格。
# high：最高价，当天交易中的最高价格。
# low：最低价，当天交易中的最低价格。
# close：收盘价，交易结束时的价格。
# volume：成交量，交易的股票或合约数量。
# amount：成交金额，交易的总金额（通常是价格×数量）。
# outstanding_share：流通在外的股份数，即公司已发行且在市场上流通的股份总数。
# turnover：换手率，表示股票在一定时间内的交易活跃程度，通常为成交股数占流通股数的比例。

import akshare as ak
import pandas as pd
import os
import time
import json


class StockData:
    """
    股票数据获取和分析接口
    """
    def __init__(self):
        pass

    @staticmethod
    def get_one_stock_data(code):
        """
        获取一支股票信息
        """
        # 判断股票类型
        if code.isdigit():
            if len(code) > 5:
                if code.startswith('0') or code.startswith('3'):
                    prefix = 'sz'
                    market = 'A股(深市)'
                elif code.startswith('6'):
                    prefix = 'sh'
                    market = 'A股(沪市)'
                else:
                    print(f"{code} 无法识别为 A股，跳过")
                symbol = f"{prefix}{code}"
                print(f'symbol is {symbol}')
                df = ak.stock_zh_a_daily(symbol=symbol)
            else:
                symbol = code
                market = '港股'
                print(f'symbol is {symbol}')
                df = ak.stock_hk_daily(symbol=symbol)

        if df.empty:
            print(f"{code} ({market}) 未获取到数据")

        return df

    @staticmethod
    def get_all_a_stocks():
        """
        获取A股全市场股票列表 包括上证主板A股 上证科创板 深圳A股列表
        Returns
        """

        sh_main = ak.stock_info_sh_name_code(symbol="主板A股")
        sh_star_market = ak.stock_info_sh_name_code(symbol="科创板")
        sz = ak.stock_info_sz_name_code(symbol="A股列表")
        sh_main['market'] = 'sh'
        sh_star_market['market'] = 'sh'
        sz['market'] = 'sz'

        sh_main = sh_main[['证券代码', '证券简称', 'market']]
        sh_main.columns = ['code', 'name', 'market']

        sh_star_market = sh_star_market[['证券代码', '证券简称', 'market']]
        sh_star_market.columns = ['code', 'name', 'market']

        sz = sz[['A股代码', 'A股简称', 'market']]
        sz.columns = ['code', 'name', 'market']

        # print(sh_main.head())
        # print(sh_star_market.head())
        # print(sz.head())

        df_a = pd.concat([sh_main, sh_star_market, sz], ignore_index=True)
        # print(df_a.head())
        # df_a.shape

        return df_a[['code', 'name', 'market']]

    @staticmethod
    def get_all_hk_stocks():
        """
        获取所有港股数据列表
        """
        hk_stock_df = ak.stock_hk_spot_em()  # 东方财富港股行情接口
        return hk_stock_df[['代码', '名称']]

    @staticmethod
    def save_stocks_history_batch(
            stock_list,
            start_date=None,
            end_date=None,
            save_dir="stock_data",
            filetype="csv",
            delay=1,
            retries=3,
            batch_size=50,
            log_file="download_log.json"
    ):
        """
        分批下载 A股 + 港股历史日线数据，支持断点续传
        """
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 加载下载日志
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                download_log = json.load(f)
        else:
            download_log = {}

        total = len(stock_list)
        for i in range(0, total, batch_size):
            if i + batch_size > total:
                batch = stock_list[i:total]
            else:
                batch = stock_list[i:i + batch_size]
            print(f"\n正在处理第 {i + 1}-{i + len(batch)} / {total} 支股票")

            for code in batch:
                # 检查日志是否已下载
                if download_log.get(code) == "success":
                    print(f"{code} 已下载，跳过")
                    continue

                attempt = 0
                while attempt < retries:
                    try:
                        # 判断股票类型
                        if code.isdigit():
                            if len(code) > 5:
                                if code.startswith('0') or code.startswith('3'):
                                    prefix = 'sz'
                                    market = 'A股(深市)'
                                elif code.startswith('6'):
                                    prefix = 'sh'
                                    market = 'A股(沪市)'
                                else:
                                    print(f"{code} 无法识别为 A股，跳过")
                                symbol = f"{prefix}{code}"
                                print(f'symbol is {symbol}')
                                df = ak.stock_zh_a_daily(symbol=symbol)
                            else:
                                symbol = code
                                market = '港股'
                                print(f'symbol is {symbol}')
                                df = ak.stock_hk_daily(symbol=symbol)

                        if df.empty:
                            print(f"{code} ({market}) 未获取到数据")
                            download_log[code] = "empty"
                            break

                        # 筛选日期
                        if start_date:
                            df = df[df['date'] >= start_date]
                        if end_date:
                            df = df[df['date'] <= end_date]

                        # 按年份保存
                        df['year'] = pd.to_datetime(df['date']).dt.year
                        for year, group in df.groupby('year'):
                            year_dir = os.path.join(save_dir, str(year))
                            if not os.path.exists(year_dir):
                                os.makedirs(year_dir)
                            filename = os.path.join(year_dir, f"{symbol}.{filetype}")
                            if filetype == "csv":
                                group.drop(columns=['year']).to_csv(filename, index=False, encoding="utf-8-sig")
                            elif filetype == "xlsx":
                                group.drop(columns=['year']).to_excel(filename, index=False, engine="openpyxl")

                        print(f"{code} ({market}) 数据已保存")
                        download_log[code] = "success"
                        with open(log_file, 'w', encoding='utf-8') as f:
                            json.dump(download_log, f, ensure_ascii=False, indent=2)
                        time.sleep(delay)
                        break  # 成功跳出重试循环

                    except Exception as e:
                        attempt += 1
                        print(f"{code} 获取失败，第 {attempt} 次重试：{e}")
                        time.sleep(5)

                if attempt == retries:
                    print(f"{code} 获取失败，已达到最大重试次数 {retries}")
                    download_log[code] = "fail"
                    with open(log_file, 'w', encoding='utf-8') as f:
                        json.dump(download_log, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    stock_a = StockData.get_all_a_stocks()
    print('a stock shape is ', stock_a.shape)

    stock_hk = StockData.get_all_hk_stocks()
    print('hk stock shape is ', stock_hk.shape)

    all_stock = stock_a['code'].to_list() + stock_hk['代码'].to_list()
    print(f'总共有 {len(all_stock)} 股票')

    StockData.save_stocks_history_batch(all_stock)
