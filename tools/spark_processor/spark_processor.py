# Run pip install pyspark==3.5.6 to install PySpark.
from pyspark.sql import SparkSession
from pyspark.sql.functions import count
from datetime import datetime
import sys, psutil, os

class SimpleTimer:
    def __init__(self):
        self.start()

    def start(self):
        self.start_time = datetime.now()

    def stop(self) -> int:
        self.stop_time = datetime.now()
        return (self.stop_time - self.start_time).total_seconds() * 1000 


def help():
    print("Reads the raw data and processed data csv files. Checks if the number of processed children per parent matches the expected children count and prints the children which were not processed.")
    print("Usage:")
    print("  pandas_processor <rawdata.csv> <processed_data.csv>")


def get_memory_mb(process: psutil.Process) -> None:
    memory_bytes = process.memory_info().rss
    return memory_bytes / (1024 * 1024)


def process(raw_data_file: str, processed_data_file: str):
    process = psutil.Process(os.getpid())
    timer = SimpleTimer()
    spark = SparkSession.builder.appName("Sample").getOrCreate()

    timer.start()
    raw_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(raw_data_file)
    print("Took", timer.stop(), "ms to load", os.path.basename(raw_data_file), "memory:", get_memory_mb(process), "MBs.")
    print(raw_df.head())

    timer.start()
    processed_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(processed_data_file)
    print("Took", timer.stop(), "ms to load", os.path.basename(processed_data_file), "memory:", get_memory_mb(process), "MBs.")
    print(processed_df.head())

    # Step 1
    timer.start()
    dfA = raw_df[raw_df["ActionType"] == "FirstEntry"][["ParentName", "ExpectedChildrenCount"]]
    dfB = processed_df.groupby("ParentName").count() #.reset_index(name="ChildrenFoundCount")
    result = dfA.join(dfB, on="ParentName", how="inner")
    print(result.show(4))
    print("Took", timer.stop(), "ms to select FirstEntry and group by processed rows on ParentName.", os.path.basename(processed_data_file), "memory:", get_memory_mb(process), "MBs.")

    spark.stop()
    

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        help()
        return 1

    raw_data_file = argv[1]
    if not os.path.exists(raw_data_file):
        print("Could not find file", raw_data_file)
        return 1

    processed_data_file = argv[2]
    if not os.path.exists(processed_data_file):
        print("Could not find file", raw_data_file)
        return 1

    timer = SimpleTimer()
    process(raw_data_file, processed_data_file)
    input("Total time: {0} ms. Press enter to exit.".format(timer.stop()))


sys.exit(main(sys.argv))
