#!/usr/bin/env python3
# วิเคราะห์ WHEN&HOW เพิ่มเติม: ช่วงเวลา (ชั่วโมง) + วันในสัปดาห์ ที่ถูกโจมตี
# input: /tmp/attack_by_hour.txt  (date hour total crash slow)  เฉพาะทราฟฟิกของ 19 IP คนร้าย
import csv, datetime, collections

rows = []
with open('/tmp/attack_by_hour.txt') as f:
    for line in f:
        p = line.split()
        if len(p) < 5:
            continue
        d, h, tot, crash, slow = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])
        rows.append((d, h, tot, crash, slow))

WD_TH = ['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์','อาทิตย์']
WD_EN = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

by_hour   = collections.defaultdict(lambda: [0,0,0])      # hour -> [tot,crash,slow]
by_wd     = collections.defaultdict(lambda: [0,0,0,set()])# wd  -> [tot,crash,slow, set(dates)]
heat      = collections.defaultdict(int)                  # (wd,hour) -> tot
attack_dates = set()

for d, h, tot, crash, slow in rows:
    wd = datetime.date.fromisoformat(d).weekday()  # 0=Mon
    by_hour[h][0]+=tot; by_hour[h][1]+=crash; by_hour[h][2]+=slow
    by_wd[wd][0]+=tot;  by_wd[wd][1]+=crash;  by_wd[wd][2]+=slow; by_wd[wd][3].add(d)
    heat[(wd,h)] += tot
    if tot>0: attack_dates.add(d)

grand = sum(v[0] for v in by_hour.values())

print("="*64)
print("WHEN & HOW (เพิ่มเติม) — วิเคราะห์จากทราฟฟิก 19 IP คนร้ายเท่านั้น")
print(f"ทราฟฟิกโจมตีรวม = {grand:,} requests  ·  จำนวนวันที่มีโจมตี = {len(attack_dates)} วัน")
print("="*64)

# ---- ตารางตามชั่วโมง ----
print("\n[A] โจมตีตามช่วงชั่วโมงของวัน (00–23)")
print(f"{'ชม.':>4} | {'requests':>12} | {'ล่ม500/504':>11} | {'หน่วง':>9} | bar")
mx = max(v[0] for v in by_hour.values())
for h in range(24):
    tot,crash,slow = by_hour.get(h,[0,0,0])
    bar = '█'*int(40*tot/mx) if mx else ''
    print(f"{h:02d}   | {tot:12,} | {crash:11,} | {slow:9,} | {bar}")

# ---- ตารางตามวันในสัปดาห์ ----
print("\n[B] โจมตีตามวันในสัปดาห์ (รวมทั้งช่วง 2 ปี)")
print(f"{'วัน':<10} | {'#วันจริง':>7} | {'requests':>12} | {'เฉลี่ย/วัน':>10} | {'ล่ม':>10} | {'หน่วง':>9} | bar")
mxw = max(v[0] for v in by_wd.values())
order = sorted(by_wd.keys())
for wd in range(7):
    tot,crash,slow,dates = by_wd.get(wd,[0,0,0,set()])
    nd = len(dates)
    avg = tot/nd if nd else 0
    bar = '█'*int(40*tot/mxw) if mxw else ''
    print(f"{WD_TH[wd]:<8} | {nd:7d} | {tot:12,} | {avg:10,.0f} | {crash:10,} | {slow:9,} | {bar}")

# จัดอันดับวันที่หนักสุด
ranked = sorted(range(7), key=lambda w: by_wd[w][0], reverse=True)
print("\n  อันดับวันที่ถูกโจมตีหนักที่สุด (ตาม requests รวม):")
for i,wd in enumerate(ranked,1):
    print(f"    {i}. {WD_TH[wd]:<10} {by_wd[wd][0]:>12,} req")

# ---- heatmap วัน x ชั่วโมง ----
print("\n[C] Heatmap วันในสัปดาห์ × ชั่วโมง  (ความเข้ม = ปริมาณโจมตี)")
hmax = max(heat.values()) if heat else 1
shades = ' .:-=+*#%@'
header = '     ' + ''.join(f'{h:>2}'[-1] for h in range(24))
print('      0         1         2  (ชั่วโมง 0-23)')
print(header)
for wd in range(7):
    line = f'{WD_EN[wd]:<4} '
    for h in range(24):
        v = heat.get((wd,h),0)
        idx = 0 if v==0 else min(len(shades)-1, 1+int((len(shades)-2)*v/hmax))
        line += shades[idx]
    print(line)
print(f"\n  สเกล: '{shades}'  (ซ้าย=น้อย → ขวา=มากสุด {hmax:,} req/ช่อง)")
