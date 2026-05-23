from __future__ import annotations

import argparse
from pathlib import Path

from common import get_boto3_session, load_outputs, wait_for_athena_query


SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
QUERY_FILES = [
    "01_monthly_revenue.sql",
    "02_payment_type.sql",
    "03_partition_pruning.sql",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa queries Athena da demo.")
    parser.add_argument("--outputs", type=Path, default=Path("outputs.json"))
    return parser.parse_args()


def render_sql(template_path: Path, database_name: str) -> str:
    return template_path.read_text().format(database=database_name)


def print_query_results(athena_client, execution_id: str) -> None:
    paginator = athena_client.get_paginator("get_query_results")
    skip_header = True
    for page in paginator.paginate(QueryExecutionId=execution_id):
        rows = page["ResultSet"]["Rows"]
        for row in rows:
            if skip_header:
                skip_header = False
                continue
            values = [column.get("VarCharValue", "") for column in row["Data"]]
            print(" | ".join(values))


def execute_named_query(athena_client, outputs: dict[str, str], filename: str) -> None:
    database_name = outputs["glue_processed_database_name"]
    query = render_sql(SQL_DIR / filename, database_name)
    print(f"\n=== {filename} ===", flush=True)
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database_name},
        WorkGroup=outputs["athena_workgroup_name"],
        ResultConfiguration={"OutputLocation": outputs["athena_results_s3_uri"]},
    )
    execution_id = response["QueryExecutionId"]
    wait_for_athena_query(athena_client, execution_id)
    print_query_results(athena_client, execution_id)


def main() -> None:
    args = parse_args()
    outputs = load_outputs(args.outputs)
    session = get_boto3_session(outputs.get("aws_region"))
    athena_client = session.client("athena")

    for filename in QUERY_FILES:
        execute_named_query(athena_client, outputs, filename)


if __name__ == "__main__":
    main()
