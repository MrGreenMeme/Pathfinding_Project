import pandas

def extract_map_info(filename):
    parts = filename.split("_")
    map_size = parts[0]
    map_number = int(parts[2])
    space_number = int(parts[4].replace(".txt", ""))
    return map_size, map_number, space_number

df = pandas.read_csv("../results/Stats.csv", sep=";")
df_memory = pandas.read_csv("../results/Memory-Consumption.csv", sep=";")

# clean data
df_cleaned = df.dropna(subset=["Map-Filename"])
filtered_df = df_cleaned[(df_cleaned["Map-Filename"].str.strip() != "not found")]
df_memory_cleaned = df_memory.dropna(subset=["Map-Filename"])
filtered_memory_df = df_memory_cleaned[(df_memory_cleaned["Map-Filename"].str.strip() != "not found")]

# temp columns for filtering
filtered_df[["Map-Size", "Map-Number", "Space-Number"]] = filtered_df["Map-Filename"].apply(
    lambda x: pandas.Series(extract_map_info(x))
)

# columns for mean
numeric_columns = ["Path-Length", "Visited-Cubes", "Max-Queue-Size", "Runtime", "Found-Goal"]
average_metrics = filtered_df.groupby(["Algorithm", "Map-Filename", "Map-Size", "Map-Number", "Space-Number"])[numeric_columns].mean().reset_index()
average_metrics = average_metrics.sort_values(by=["Algorithm", "Map-Size", "Map-Number", "Space-Number"])

# drop temp columns
average_metrics = average_metrics.drop(columns=["Map-Size", "Map-Number", "Space-Number"])

average_metrics.to_csv("average-stats.csv", index=False, sep=";")

average_memory_metrics = filtered_memory_df.groupby(["Algorithm", "Map-Filename"]).mean().reset_index()
average_memory_metrics.to_csv("average-memory-consumption.csv", index=False, sep=";")

# combine metrics
combined_metrics = pandas.merge(average_metrics, average_memory_metrics, on=["Algorithm", "Map-Filename"])
combined_metrics.to_csv("results/results.csv", index=False, sep=";")