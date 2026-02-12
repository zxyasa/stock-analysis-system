# data_fetcher.py

import os
import datetime
import tempfile
import pandas as pd
import requests
import time

# ========== 0. Yahoo指数采集 ==========
def fetch_yahoo_indices(output_dir):
    try:
        import yfinance as yf
    except ImportError:
        print("未安装 yfinance，无法采集Yahoo指数。")
        return False
    index_codes = {
        "上证指数": "000001.SS",
        "深证成指": "399001.SZ",
        "创业板指": "399006.SZ"
    }
    result = []
    for name, code in index_codes.items():
        try:
            df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
            if df.empty or len(df) == 0:
                print(f"{name} 无数据")
                continue
            closes = df["Close"]
            if len(closes) == 1:
                latest_value = closes.iloc[-1]
                latest_date = closes.index[-1]
                pct_chg = "-"
            else:
                latest_value = closes.iloc[-1]
                latest_date = closes.index[-1]
                prev_value = closes.iloc[-2]
                latest_value = latest_value.iloc[0] if hasattr(latest_value, "iloc") else latest_value
                prev_value = prev_value.iloc[0] if hasattr(prev_value, "iloc") else prev_value
                pct_chg = (float(latest_value) - float(prev_value)) / float(prev_value) * 100
                pct_chg = f"{pct_chg:.2f}%"
            latest_value = latest_value.iloc[0] if hasattr(latest_value, "iloc") else latest_value
            result.append({
                "指数": name,
                "收盘点位": round(float(latest_value), 2),
                "涨跌幅": pct_chg,
                "日期": str(latest_date)[:10]
            })
        except Exception as e:
            print(f"采集{name}失败: {e}")
    df_out = pd.DataFrame(result)
    out_path = os.path.join(output_dir, "指数.csv")
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✅ Yahoo指数收盘数据写入 {out_path}")
    return True

# ==== 1. 港股与中概股行情 ====
def fetch_hk_and_china_stocks(output_dir):
    import yfinance as yf
    tickers = {
        "腾讯控股": "0700.HK",
        "阿里巴巴": "9988.HK",
        "比亚迪": "1211.HK",
        "KWEB中概ETF": "KWEB"
    }
    result = []
    for name, code in tickers.items():
        df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
        if not df.empty:
            close_col = df["Close"]
            latest_raw = close_col.iloc[-1]
            latest_value = float(latest_raw.item() if hasattr(latest_raw, "item") else latest_raw)
            if len(close_col) > 1:
                prev_raw = close_col.iloc[-2]
                prev_value = float(prev_raw.item() if hasattr(prev_raw, "item") else prev_raw)
            else:
                prev_value = latest_value
            if prev_value != 0:
                pct_chg = (latest_value - prev_value) / prev_value * 100
                pct_chg = f"{pct_chg:.2f}%"
            else:
                pct_chg = "0.00%"
            result.append({
                "名称": name, "代码": code,
                "收盘": round(latest_value, 2),
                "涨跌幅": pct_chg
            })
    pd.DataFrame(result).to_csv(f"{output_dir}/港股与中概股行情.csv", index=False)

# ==== 2. 美股主要指数/科技股/中概ETF ====
def fetch_us_indexes_etf(output_dir):
    import yfinance as yf
    tickers = {
        "纳斯达克": "^IXIC",
        "标普500": "^GSPC",
        "道琼斯": "^DJI",
        "特斯拉": "TSLA",
        "苹果": "AAPL",
        "KWEB": "KWEB"
    }
    result = []
    for name, code in tickers.items():
        df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
        if not df.empty:
            close_col = df["Close"]
            latest_value = close_col.iloc[-1].item() if hasattr(close_col.iloc[-1], "item") else float(close_col.iloc[-1])
            if len(close_col) > 1:
                prev_value = close_col.iloc[-2].item() if hasattr(close_col.iloc[-2], "item") else float(close_col.iloc[-2])
            else:
                prev_value = latest_value
            if prev_value != 0:
                pct_chg = (latest_value - prev_value) / prev_value * 100
                pct_chg = f"{pct_chg:.2f}%"
            else:
                pct_chg = "0.00%"
            result.append({
                "名称": name, "代码": code,
                "收盘": round(latest_value, 2),
                "涨跌幅": pct_chg
            })
    pd.DataFrame(result).to_csv(f"{output_dir}/美股主要指数.csv", index=False)

# ==== 3. 大宗商品/期货/外汇 ====
def fetch_commodities_fx(output_dir):
    import yfinance as yf
    tickers = {
        "黄金": "GC=F",
        "原油": "CL=F",
        "铜": "HG=F",
        "布伦特原油": "BZ=F", 
        "美元指数": "DX-Y.NYB",
        "离岸人民币": "CNH=X"
    }
    result = []
    for name, code in tickers.items():
        df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
        if not df.empty:
            latest = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2] if len(df) > 1 else latest
            latest_val = float(latest.item() if hasattr(latest, "item") else latest)
            prev_val = float(prev.item() if hasattr(prev, "item") else prev)
            if prev_val != 0:
                pct_chg = (latest_val - prev_val) / prev_val * 100
                pct_chg_str = f"{pct_chg:.2f}%"
            else:
                pct_chg_str = "0.00%"
            result.append({
                "名称": name, "代码": code,
                "收盘": round(latest_val, 2),
                "涨跌幅": pct_chg_str
            })
    pd.DataFrame(result).to_csv(f"{output_dir}/期货外汇.csv", index=False)

# ==== 4. 全球ETF资金流 ====
def fetch_global_etf(output_dir):
    import yfinance as yf
    tickers = {
        "A股ETF-ASHR": "ASHR",
        "中概ETF-KWEB": "KWEB",
        "恒生ETF-EWH": "EWH"
    }
    result = []
    for name, code in tickers.items():
        df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
        if not df.empty:
            latest = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2] if len(df) > 1 else latest
            latest_val = float(latest.item() if hasattr(latest, "item") else latest)
            prev_val = float(prev.item() if hasattr(prev, "item") else prev)
            if prev_val != 0:
                pct_chg = (latest_val - prev_val) / prev_val * 100
                pct_chg_str = f"{pct_chg:.2f}%"
            else:
                pct_chg_str = "0.00%"
            result.append({
                "名称": name, "代码": code,
                "收盘": round(latest_val, 2),
                "涨跌幅": pct_chg_str
            })
    pd.DataFrame(result).to_csv(f"{output_dir}/全球ETF资金流.csv", index=False)

# ==== 5. 全球主要利率/中美利差 ====
def fetch_global_rates_macro(output_dir):
    url = "https://tradingeconomics.com/united-states/interest-rate"
    rate = "N/A"
    try:
        resp = requests.get(url, timeout=15)
        if resp.ok:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                rate_span = soup.find("span", {"class": "datatable-item datatable-item-last"})
                if rate_span:
                    rate = rate_span.text.strip()
            except Exception:
                pass
    except Exception as e:
        print(f"⚠️ 全球主要利率采集失败: {e}")
    pd.DataFrame([{"美国基准利率": rate}]).to_csv(f"{output_dir}/全球主要利率.csv", index=False)

# ==== 6. 美股盘前异动榜 ====
def fetch_us_premarket_movers(output_dir):
    url = "https://finviz.com/premarket.ashx"
    df = pd.DataFrame()
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.ok:
            df = pd.read_html(resp.text)[2]
    except Exception as e:
        print(f"⚠️ 美股盘前异动榜采集失败: {e}")
    df.to_csv(f"{output_dir}/美股盘前异动榜.csv", index=False)

# ==== 7. 国际主要指数 ====
def fetch_international_indexes(output_dir):
    import yfinance as yf
    tickers = {
        "恒生指数": "^HSI",
        "新加坡STI": "^STI",
        "日经225": "^N225",
        "富时A50": "XCHA.DE",
        "德国DAX": "^GDAXI"
    }
    result = []
    for name, code in tickers.items():
        try:
            df = yf.download(code, period="2d", interval="1d", progress=False, auto_adjust=False)
            if not df.empty:
                latest = df["Close"].iloc[-1]
                prev = df["Close"].iloc[-2] if len(df) > 1 else latest
                latest_val = float(latest.item() if hasattr(latest, "item") else latest)
                prev_val = float(prev.item() if hasattr(prev, "item") else prev)
                if prev_val != 0:
                    pct_chg = (latest_val - prev_val) / prev_val * 100
                    pct_chg_str = f"{pct_chg:.2f}%"
                else:
                    pct_chg_str = "0.00%"
                result.append({
                    "名称": name, "代码": code,
                    "收盘": round(latest_val, 2),
                    "涨跌幅": pct_chg_str
                })
        except Exception:
            continue
    pd.DataFrame(result).to_csv(f"{output_dir}/主要指数.csv", index=False)

# ==== 8. 同花顺“涨停雷达” ====
def fetch_tonghuashun_limit_up(output_dir):
    try:
        url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        params = {"page": 1, "limit": 50, "_": int(time.time() * 1000)}
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict) and "data" in data and "info" in data["data"]:
                df = pd.DataFrame(data["data"]["info"])
                if not df.empty:
                    df.to_csv(f"{output_dir}/同花顺涨停雷.csv", index=False)
    except Exception:
        pass

# ==== 9. 东方财富主力资金流向 ====
def fetch_eastmoney_fund_flow(output_dir):
    try:
        base_urls = [
            "https://push2.eastmoney.com",
            "https://push2delay.eastmoney.com",
            "http://push2.eastmoney.com",
            "http://push2delay.eastmoney.com"
        ]
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        params = {
            "pn": "1","pz": "100","po": "1","np": "1",
            "ut": "b2884a393a59ad64002292a3e90d46a5","fltt": "2","invt": "2",
            "fid": "f62","fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87",
            "_": int(time.time() * 1000)
        }
        for base_url in base_urls:
            try:
                url = f"{base_url}/api/qt/clist/get"
                res = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("data") and data["data"].get("diff"):
                        df = pd.DataFrame(data["data"]["diff"])
                        if not df.empty:
                            columns_map = {
                                "f12": "代码","f14": "名称","f2": "最新价","f3": "涨跌幅",
                                "f62": "主力净流入","f66": "超大单净流入","f69": "大单净流入",
                                "f75": "中单净流入","f78": "小单净流入"
                            }
                            df = df.rename(columns=columns_map)
                            df = df[list(columns_map.values())]
                            df.to_csv(f"{output_dir}/东方财富主力资金流向.csv", index=False)
                            return True
            except Exception:
                continue
    except Exception:
        pass

# ==== 10. 微博热搜榜 ====
def fetch_weibo_hot_search(output_dir):
    try:
        url = "https://weibo.com/ajax/statuses/hot_band"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://s.weibo.com/top/summary"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        if "data" in data and "band_list" in data["data"]:
            hot_list = data["data"]["band_list"]
            hot_words = [item["word"] for item in hot_list if "word" in item]
            df = pd.DataFrame({"热搜词": hot_words})
            if not df.empty:
                df.to_csv(f"{output_dir}/微博热搜榜.csv", index=False)
    except Exception:
        pass

# ==== 11. 雪球热词 ====
def fetch_xueqiu_hot_words(output_dir):
    try:
        session = requests.Session()
        base_url = "https://xueqiu.com"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        session.get(base_url, headers=headers, timeout=15)
        api_url = f"{base_url}/statuses/hot/listV2.json"
        params = {"since_id": "-1","max_id": "-1","size": "50","_": int(time.time() * 1000)}
        res = session.get(api_url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json()
            keywords = []
            hot_words = ["中船防务", "航发", "军工", "机器人", "宁德", "卫星", "券商", 
                        "新能源", "芯片", "锂电池", "半导体", "AI", "创新药",
                        "光伏", "通信", "ChatGPT", "智能驾驶", "汽车"]
            items = data.get("items", [])
            for item in items:
                text = item.get("title", "") + " " + item.get("text", "")
                found_words = [word for word in hot_words if word in text]
                keywords.extend(found_words)
            if keywords:
                hot_df = pd.DataFrame(pd.Series(keywords).value_counts()).reset_index()
                hot_df.columns = ["热词", "出现次数"]
                hot_df.to_csv(f"{output_dir}/雪球热词.csv", index=False)
    except Exception:
        pass

# ========== 运行所有采集 ==========
def run_all_data_collection(output_dir):
    steps = [
        ("港股与中概股行情", fetch_hk_and_china_stocks),
        ("美股主要指数/科技股/中概ETF", fetch_us_indexes_etf),
        ("大宗商品/期货/外汇", fetch_commodities_fx),
        ("全球ETF资金流", fetch_global_etf),
        ("全球主要利率", fetch_global_rates_macro),
        ("美股盘前异动榜", fetch_us_premarket_movers),
        ("国际主要指数", fetch_international_indexes),
        ("同花顺涨停雷达", fetch_tonghuashun_limit_up),
        ("东方财富主力资金流向", fetch_eastmoney_fund_flow),
        ("微博热搜榜", fetch_weibo_hot_search),
        ("雪球热词", fetch_xueqiu_hot_words),
    ]
    for name, func in steps:
        try:
            func(output_dir)
        except Exception as e:
            print(f"⚠️ 采集步骤失败，已跳过: {name}; error={e}")

# ========== 汇总csv为Markdown ==========
def summarize_csv(path, cols=None, top=5):
    if not os.path.exists(path):
        return "（无数据）"
    if os.path.getsize(path) == 0:
        return "（无数据）"
    try:
        df = pd.read_csv(path)
    except Exception:
        return "（无数据）"
    if df.empty or df.columns.empty:
        return "（无数据）"
    if cols:
        try:
            df = df[cols]
        except Exception:
            return "（无数据）"
    return df.head(top).to_markdown(index=False)

def merge_csvs_to_excel(output_dir, output_excel="全市场数据总览.xlsx"):
    import pandas as pd
    files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
    with pd.ExcelWriter(os.path.join(output_dir, output_excel)) as writer:
        for csv_file in files:
            csv_path = os.path.join(output_dir, csv_file)
            try:
                if os.path.getsize(csv_path) == 0:
                    print(f"⚠️ 跳过空文件：{csv_file}")
                    continue
                df = pd.read_csv(csv_path)
                if df.empty or df.columns.empty:
                    print(f"⚠️ 跳过无内容文件：{csv_file}")
                    continue
                sheet_name = os.path.splitext(csv_file)[0][:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            except Exception as e:
                print(f"⚠️ 文件 {csv_file} 合并失败，原因：{e}")
    print(f"✅ 已合并为 {output_excel}")


def merge_csvs_to_one(output_dir, output_csv="all_data_merged.csv"):
    import pandas as pd
    files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
    dfs = []
    for csv_file in files:
        csv_path = os.path.join(output_dir, csv_file)
        try:
            if os.path.getsize(csv_path) == 0:
                print(f"⚠️ 跳过空文件：{csv_file}")
                continue
            df = pd.read_csv(csv_path)
            if df.empty or df.columns.empty:
                print(f"⚠️ 跳过无内容文件：{csv_file}")
                continue
            df["__来源表__"] = os.path.splitext(csv_file)[0]
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ 文件 {csv_file} 合并失败，原因：{e}")
            continue
    if not dfs:
        print("❗没有可用数据，未生成合并csv")
        return
    df_all = pd.concat(dfs, axis=0, ignore_index=True)
    df_all.to_csv(os.path.join(output_dir, output_csv), index=False)
    print(f"✅ 已合并为 {output_csv}")

# ========== 主入口 ==========
def main():
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    with tempfile.TemporaryDirectory(prefix="stock1_market_data_") as output_dir:
        run_all_data_collection(output_dir)

        report = f"# {today_str} 多市场采集报告\n"

        report += "\n## 港股与中概股行情\n"
        report += summarize_csv(f"{output_dir}/港股与中概股行情.csv", top=5)

        report += "\n\n## 美股主要指数/ETF\n"
        report += summarize_csv(f"{output_dir}/美股主要指数.csv", top=5)

        report += "\n\n## 大宗商品/期货/外汇\n"
        report += summarize_csv(f"{output_dir}/期货外汇.csv", top=5)

        report += "\n\n## 全球ETF资金流\n"
        report += summarize_csv(f"{output_dir}/全球ETF资金流.csv", top=5)

        report += "\n\n## 国际主要指数\n"
        report += summarize_csv(f"{output_dir}/主要指数.csv", top=5)

        report += "\n\n## 东方财富主力资金流向（前10）\n"
        report += summarize_csv(f"{output_dir}/东方财富主力资金流向.csv", top=10)

        report += "\n\n## 同花顺涨停雷达（前10）\n"
        report += summarize_csv(f"{output_dir}/同花顺涨停雷.csv", top=10)

        report += "\n\n## 微博热搜榜（前10）\n"
        report += summarize_csv(f"{output_dir}/微博热搜榜.csv", top=10)

        report += "\n\n## 雪球热词（Top10）\n"
        report += summarize_csv(f"{output_dir}/雪球热词.csv", top=10)

        report += "\n\n*本报告由自动化脚本采集生成*"
        return report
