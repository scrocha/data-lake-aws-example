from __future__ import annotations

import argparse
from pathlib import Path

from common import get_boto3_session, load_outputs, wait_for_crawler, wait_for_job_run


def discover_raw_table_name(glue_client, database_name: str) -> str:
    response = glue_client.get_tables(DatabaseName=database_name)
    table_names = [table["Name"] for table in response["TableList"]]
    if not table_names:
        raise RuntimeError(f"Nenhuma tabela encontrada no database {database_name}.")

    for table_name in table_names:
        if "nyc_taxi" in table_name:
            return table_name
    return table_names[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o pipeline Glue do Data Lake.")
    parser.add_argument("--outputs", type=Path, default=Path("outputs.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = load_outputs(args.outputs)
    session = get_boto3_session(outputs.get("aws_region"))
    glue_client = session.client("glue")

    raw_crawler_name = outputs["glue_raw_crawler_name"]
    processed_crawler_name = outputs["glue_processed_crawler_name"]
    glue_job_name = outputs["glue_job_name"]
    raw_database_name = outputs["glue_raw_database_name"]

    print(f"Iniciando crawler raw: {raw_crawler_name}", flush=True)
    glue_client.start_crawler(Name=raw_crawler_name)
    wait_for_crawler(glue_client, raw_crawler_name)
    print("Crawler raw concluído.", flush=True)

    raw_table = discover_raw_table_name(glue_client, raw_database_name)
    print(f"Tabela raw descoberta no catálogo: {raw_table}", flush=True)

    print(f"Iniciando Glue job: {glue_job_name}", flush=True)
    run_id = glue_client.start_job_run(
        JobName=glue_job_name,
        Arguments={
            "--raw_table": raw_table,
        },
    )["JobRunId"]
    wait_for_job_run(glue_client, glue_job_name, run_id)
    print("Glue job concluído.", flush=True)

    print(f"Iniciando crawler processed: {processed_crawler_name}", flush=True)
    glue_client.start_crawler(Name=processed_crawler_name)
    wait_for_crawler(glue_client, processed_crawler_name)
    print("Crawler processed concluído.", flush=True)


if __name__ == "__main__":
    main()
