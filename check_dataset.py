import pandas as pd

data = pd.read_csv("data/chronos_x_events.csv")

print("CHRONOS-X DATASET LOADED SUCCESSFULLY")
print("-------------------------------------")

print("Total event records:", len(data))
print("Total scenarios:", data["scenario_id"].nunique())

print("\nAvailable scenarios:")
print(data["scenario_id"].unique())

print("\nFirst five records:")
print(data.head())

print("\nDataset information:")
data.info()
