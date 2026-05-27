#!/usr/bin/env python3
"""彩票数据自动更新脚本 - 从500.com爬取最新数据"""
import re
import csv
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_latest_period(csv_path):
    if not os.path.exists(csv_path):
        return None
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 2:
        return None
    return rows[-1][0].strip()

def parse_html(filepath):
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
    print("🔴 更新双色球...")
    csv_path = os.path.join(DATA_DIR, 'ssq.csv')
    latest = get_latest_period(csv_path)
    print(f"  当前最新期: {latest}")
    url = "https://datachart.500.com/ssq/history/newinc/history.php?start=25001&end=99999"
    import tempfile
    tmp = tempfile.mktemp(suffix='.html')
    os.system(f'curl -s -H "User-Agent: Mozilla/5.0" "{url}" -o "{tmp}"')
    raw_rows = parse_html(tmp)
    os.unlink(tmp)
    print(f"  爬取到 {len(raw_rows)} 期数据")
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
    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:
                    existing[row[0].strip()] = row
    for row in new_rows:
        existing[row[0]] = row
    sorted_rows = sorted(existing.values(), key=lambda x: x[0])
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['期号', '开奖日期', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '销售额', '一等奖注数', '一等奖金额', '二等奖注数', '二等奖金额', '奖池余额'])
        writer.writerows(sorted_rows)
    print(f"  ✅ 双色球更新完成，共 {len(sorted_rows)} 期")
    return True

def update_dlt():
    print("🔵 更新大乐透...")
    csv_path = os.path.join(DATA_DIR, 'dlt.csv')
    latest = get_latest_period(csv_path)
    print(f"  当前最新期: {latest}")
    url = "https://datachart.500.com/dlt/history/newinc/history.php?start=25001&end=99999"
    import tempfile
    tmp = tempfile.mktemp(suffix='.html')
    os.system(f'curl -s -H "User-Agent: Mozilla/5.0" "{url}" -o "{tmp}"')
    raw_rows = parse_html(tmp)
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
            next(reader)
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

def update_kl8():
    print("🟢 更新快乐8...")
    csv_path = os.path.join(DATA_DIR, 'kl8.csv')
    latest = get_latest_period(csv_path)
    print(f"  当前最新期: {latest}")
    url = "https://kaijiang.500.com/static/info/kaijiang/xml/kl8/list.xml"
    import tempfile
    tmp = tempfile.mktemp(suffix='.xml')
    os.system(f'curl -s -H "User-Agent: Mozilla/5.0" "{url}" -o "{tmp}"')
    try:
        tree = ET.parse(tmp)
        root = tree.getroot()
    except:
        print("  ❌ XML解析失败")
        os.unlink(tmp)
        return False
    os.unlink(tmp)
    xml_rows = root.findall('row')
    print(f"  爬取到 {len(xml_rows)} 期数据")
    new_data = {}
    for row in xml_rows:
        expect = row.attrib.get('expect', '')
        opencode = row.attrib.get('opencode', '')
        opentime = row.attrib.get('opentime', '')
        date = opentime.split(' ')[0] if opentime else ''
        nums = opencode.split(',')
        if len(nums) != 20:
            continue
        new_data[expect] = [expect, date] + nums
    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:
                    existing[row[0].strip()] = row
    for k, v in new_data.items():
        existing[k] = v
    sorted_rows = sorted(existing.values(), key=lambda x: x[0])
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['期号', '开奖日期'] + [f'号码{i+1}' for i in range(20)])
        writer.writerows(sorted_rows)
    print(f"  ✅ 快乐8更新完成，共 {len(sorted_rows)} 期")
    return True

if __name__ == '__main__':
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ssq_ok = update_ssq()
    dlt_ok = update_dlt()
    kl8_ok = update_kl8()
    if ssq_ok or dlt_ok or kl8_ok:
        print("\n🎉 数据已更新，需要git push")
        sys.exit(0)
    else:
        print("\n💤 无新数据")
        sys.exit(1)
