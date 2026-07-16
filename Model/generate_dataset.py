import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dataset.csv"

np.random.seed(42)

NUM_ROWS = 12000

start_date = datetime(2022,1,1)

rows=[]

for i in range(NUM_ROWS):

    date = start_date + timedelta(days=i%1095)

    lat = np.random.uniform(13.0,13.4)
    lon = np.random.uniform(100.7,101.1)

    B2=np.random.uniform(0.02,0.18)
    B3=np.random.uniform(0.02,0.20)
    B4=np.random.uniform(0.01,0.18)
    B5=np.random.uniform(0.03,0.25)
    B8=np.random.uniform(0.05,0.35)

    ndwi=(B3-B8)/(B3+B8+1e-6)
    ndci=(B5-B4)/(B5+B4+1e-6)

    temp=np.random.normal(30,2)

    wind=np.random.uniform(0,12)

    humidity=np.random.uniform(55,95)

    rain=max(0,np.random.normal(5,8))

    do=np.random.normal(6.5,1.2)

    chlorophyll=max(
        0,
        ndci*55+
        temp*0.8-
        wind*1.5+
        np.random.normal(0,3)
    )

    score=(
        ndci*4+
        temp*0.12-
        wind*0.25-
        do*0.15+
        chlorophyll*0.02
    )

    probability=1/(1+np.exp(-(score-2.2)))

    bloom=np.random.rand()<probability

    rows.append([
        date,
        lat,
        lon,
        B2,
        B3,
        B4,
        B5,
        B8,
        ndwi,
        ndci,
        temp,
        wind,
        humidity,
        rain,
        do,
        chlorophyll,
        int(bloom)
    ])

columns=[
"date",
"latitude",
"longitude",
"B2",
"B3",
"B4",
"B5",
"B8",
"NDWI",
"NDCI",
"Temperature",
"WindSpeed",
"Humidity",
"Rainfall",
"DO",
"Chlorophyll",
"Bloom"
]

df=pd.DataFrame(rows,columns=columns)

DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(DATA_PATH,index=False)

print(df.head())

print()

print(df["Bloom"].value_counts())

print()

print(f"Dataset Saved: {DATA_PATH}")
