from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from urllib.request import urlretrieve

from common import get_boto3_session, load_outputs


DEFAULT_HTTP_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def build_paths(year: int, month: int, taxi_type: str) -> tuple[str, str]:
    month_str = f"{month:02d}"
    filename = f"{taxi_type}_tripdata_{year}-{month_str}.parquet"
    source_key = f"trip data/{filename}"
    destination_key = f"raw/nyc_taxi/year={year}/month={month_str}/{filename}"
    return source_key, destination_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copia dados públicos do NYC Taxi para a zona raw do Data Lake.")
    parser.add_argument("--outputs", type=Path, default=Path("outputs.json"))
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--months", type=int, nargs="+", required=True)
    parser.add_argument("--taxi-type", default="yellow", choices=["yellow", "green"])
    parser.add_argument("--http-base-url", default=DEFAULT_HTTP_BASE_URL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = load_outputs(args.outputs)
    session = get_boto3_session(outputs.get("aws_region"))
    s3_client = session.client("s3")
    bucket_name = outputs["data_lake_bucket_name"]

    for month in args.months:
        _, destination_key = build_paths(args.year, month, args.taxi_type)
        month_str = f"{month:02d}"
        filename = f"{args.taxi_type}_tripdata_{args.year}-{month_str}.parquet"
        download_url = f"{args.http_base_url}/{filename}"

        print(f"Baixando {download_url}", flush=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(temp_dir) / filename
            urlretrieve(download_url, local_path)
            print(f"Enviando para s3://{bucket_name}/{destination_key}", flush=True)
            s3_client.upload_file(str(local_path), bucket_name, destination_key)

    print("Ingestão raw concluída.", flush=True)


if __name__ == "__main__":
    main()
