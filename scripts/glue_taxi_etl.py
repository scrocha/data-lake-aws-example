from __future__ import annotations

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def prepare_trips(raw_df: DataFrame) -> DataFrame:
    return (
        raw_df.withColumnRenamed("tpep_pickup_datetime", "pickup_datetime")
        .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime")
        .withColumnRenamed("PULocationID", "pickup_location_id")
        .withColumnRenamed("DOLocationID", "dropoff_location_id")
        .select(
            F.col("pickup_datetime").cast("timestamp").alias("pickup_datetime"),
            F.col("dropoff_datetime").cast("timestamp").alias("dropoff_datetime"),
            F.col("passenger_count").cast("int").alias("passenger_count"),
            F.col("trip_distance").cast("double").alias("trip_distance"),
            F.col("payment_type").cast("string").alias("payment_type"),
            F.col("fare_amount").cast("double").alias("fare_amount"),
            F.col("tip_amount").cast("double").alias("tip_amount"),
            F.col("total_amount").cast("double").alias("total_amount"),
            F.col("pickup_location_id").cast("int").alias("pickup_location_id"),
            F.col("dropoff_location_id").cast("int").alias("dropoff_location_id"),
        )
        .filter(F.col("pickup_datetime").isNotNull())
        .filter(F.col("dropoff_datetime").isNotNull())
        .filter(F.col("trip_distance") > 0)
        .filter(F.col("fare_amount") >= 0)
        .filter(F.col("total_amount") >= 0)
        .withColumn("year", F.year("pickup_datetime"))
        .withColumn("month", F.month("pickup_datetime"))
    )


def aggregate_metrics(df: DataFrame) -> DataFrame:
    return df.groupBy("year", "month", "payment_type").agg(
        F.count("*").alias("total_trips"),
        F.avg("trip_distance").alias("avg_distance"),
        F.avg("fare_amount").alias("avg_fare"),
        F.avg("tip_amount").alias("avg_tip"),
        F.sum("total_amount").alias("total_revenue"),
    )


def main() -> None:
    args = getResolvedOptions(
        sys.argv,
        [
            "JOB_NAME",
            "raw_database",
            "raw_table",
            "processed_bucket",
        ],
    )

    sc = SparkContext()
    glue_context = GlueContext(sc)
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    raw_dynamic_frame = glue_context.create_dynamic_frame.from_catalog(
        database=args["raw_database"],
        table_name=args["raw_table"],
    )

    clean_df = prepare_trips(raw_dynamic_frame.toDF())
    metrics_df = aggregate_metrics(clean_df)

    processed_root = f"s3://{args['processed_bucket']}/processed"
    clean_path = f"{processed_root}/taxi_trips_clean/"
    metrics_path = f"{processed_root}/taxi_monthly_metrics/"

    clean_df.write.mode("overwrite").partitionBy("year", "month").parquet(clean_path)
    metrics_df.write.mode("overwrite").partitionBy("year", "month").parquet(metrics_path)

    job.commit()


if __name__ == "__main__":
    main()
