import pandas as pd

df = pd.read_csv('Export_Data.csv')

print("=== โครงสร้างข้อมูลเบื้องต้น ===")
print(df.info())

df['Time'] = pd.to_datetime(df['Time'])
df = df.sort_values('Time').reset_index(drop=True)
