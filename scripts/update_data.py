#!/usr/bin/env python3
"""彩票数据自动更新脚本 - 从500.com爬取最新数据"""
import re
import csv
import os
import sys
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def fetch_500com(url):
    """请求500.com"""
    import urllib.request
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    try:
        return raw.decode('gb2312')
    except:
        return raw.decode('gbk', errors='ignore')

def get_latest_period(csv_path):
    """读取CSV中最新期号"""
    if not os.path.exists(csv_path):
        return None
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 2:
        return None
    return rows[-1][0].strip()

def parse_html(filepath, lottery_type):
    """解析500.com HTML"""
    with open(filepath, 'rb') as f:
        content = f.read()
    try:
        text = content.decode('gb2312')
    except:
        text = content.decode('gbk', errors='ignore')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    data_rows = []
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        vals = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
        if len(vals) >= 10 and vals[0].isdigit() and len(vals[1]) >= 5:
            data_rows.append(vals)
    return data_rows

def update_ssq():
    """更新双色球数据"""
    print("🔴 更新双色球...")
    csv_path = os.path.join(DATA_DIR, 'ssq.csv')
    latest = get_latest_period(csv_path)
    print(f"  当前最新期: {latest}")

    # 爬取最新数据（取最近200期足够覆盖更新）
    url = "https://datachart.500.com/ssq/history/newinc/history.php?start=25001&end=99999"
    import tempfile
    tmp = tempfile.mktemp(suffix='.html')
    os.system(f'curl -s -H "User-Agent: Mozilla/5.0" "{url}" -o "{tmp}"')

    raw_rows = parse_html(tmp, 'ssq')
    os.unlink(tmp)
    print(f"  爬取到 {len(raw_rows)} 期数据")

    # 解析
    new_rows = []
    for row in raw_rows:
        try:
            period = row[1]
            reds = [int(row[i]) for i in range(2, 8)]
            blue = int(row[8])
            sales = row[10].replace(',', '')
            p1count = row[11].replace(',', '')
            p1amount = row[12].replace(',', '')
            p2count = row[13].replace(',', '')
            p2amount = row[14].replace(',', '')
            pool = row[15].replace(',', '')
            date = row[16] if len(row) > 16 else ''
            new_rows.append([period, date] + reds + [blue, sales, p1count, p1amount, p2count, p2amount, pool])
        except (ValueError, IndexError):
            continue

    if not new_rows:
        print("  ❌ 未获取到新数据")
        return False

    # 读取现有数据
    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if row:
                    existing[row[0].strip()] = row

    # 合并
    for row in new_rows:
        existing[row[0]] = row

    # 按期号排序写入
    sorted_rows = sorted(existing.values(), key=lambda x: x[0])
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['期号', '开奖日期', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '销售额', '一等奖注数', '一等奖金额', '二等奖注数', '二等奖金额', '奖池余额'])
        writer.writerows(sorted_rows)

    print(f"  ✅ 双色球更新完成，共 {len(sorted_rows)} 期")
    return True

def update_dlt():
    """更新大乐透数据"""
    print("🔵 更新大乐透...")
    csv_path = os.path.join(DATA_DIR, 'dlt.csv')
    latest = get_latest_period(csv_path)
    print(f"  当前最新期: {latest}")

    url = "https://datachart.500.com/dlt/history/newinc/history.php?start=25001&end=99999"
    import tempfile
    tmp = tempfile.mktemp(suffix='.html')
    os.system(f'curl -s -H "User-Agent: Mozilla/5.0" "{url}" -o "{tmp}"')

    raw_rows = parse_html(tmp, 'dlt')
    os.unlink(tmp)
    print(f"  爬取到 {len(raw_rows)} 期数据")

    new_rows = []
    for row in raw_rows:
        try:
            period = row[1]
            reds = [int(row[i]) for i in range(2, 7)]
            blues = [int(row[i]) for i in range(7, 9)]
            sales = row[9].replace(',', '')
            p1count = row[10].replace(',', '')
            p1amount = row[11].replace(',', '')
            p2count = row[12].replace(',', '')
            p2amount = row[13].replace(',', '')
            pool = row[14].replace(',', '')
            date = row[15] if len(row) > 15 else ''
            new_rows.append([period, date] + reds + blues + [sales, p1count, p1amount, p2count, p2amount, pool])
        except (ValueError, IndexError):
            continue

    if not new_rows:
        print("  ❌ 未获取到新数据")
        return False

    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if row:
                    existing[row[0].strip()] = row

    for row in new_rows:
        existing[row[0]] = row

    sorted_rows = sorted(existing.values(), key=lambda x: x[0])
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['期号', '开奖日期', '前区1', '前区2', '前区3', '前区4', '前区5', '后区1', '后区2', '销售额', '一等奖注数', '一等奖金额', '二等奖注数', '二等奖金额', '奖池余额'])
        writer.writerows(sorted_rows)

    print(f"  ✅ 大乐透更新完成，共 {len(sorted_rows)} 期")
    return True

if __name__ == '__main__':
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ssq_ok = update_ssq()
    dlt_ok = update_dlt()
    if ssq_ok or dlt_ok:
        print("\n🎉 数据已更新，需要git push")
        sys.exit(0)
    else:
        print("\n💤 无新数据")
        sys.exit(1)
