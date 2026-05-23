from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import boto3


def load_outputs(outputs_path: Path) -> dict[str, str]:
    raw_outputs = json.loads(outputs_path.read_text())
    flattened: dict[str, str] = {}
    for key, value in raw_outputs.items():
        if isinstance(value, dict) and "value" in value:
            flattened[key] = str(value["value"])
        else:
            flattened[key] = str(value)
    return flattened


def get_boto3_session(region_name: str | None = None) -> boto3.session.Session:
    return boto3.session.Session(region_name=region_name)


def wait_for_job_run(glue_client: Any, job_name: str, run_id: str, poll_seconds: int = 30) -> None:
    while True:
        response = glue_client.get_job_run(JobName=job_name, RunId=run_id, PredecessorsIncluded=False)
        state = response["JobRun"]["JobRunState"]
        if state == "SUCCEEDED":
            return
        if state in {"FAILED", "STOPPED", "TIMEOUT", "ERROR"}:
            raise RuntimeError(f"Glue job {job_name} terminou com status {state}")
        time.sleep(poll_seconds)


def wait_for_crawler(glue_client: Any, crawler_name: str, poll_seconds: int = 15) -> None:
    while True:
        crawler = glue_client.get_crawler(Name=crawler_name)["Crawler"]
        state = crawler["State"]
        last_status = crawler.get("LastCrawl", {}).get("Status")
        if state == "READY" and last_status == "FAILED":
            message = crawler.get("LastCrawl", {}).get("ErrorMessage", "Crawler falhou.")
            raise RuntimeError(f"Glue crawler {crawler_name} falhou: {message}")
        if state == "READY":
            return
        time.sleep(poll_seconds)


def wait_for_athena_query(athena_client: Any, query_execution_id: str, poll_seconds: int = 3) -> None:
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response["QueryExecution"]["Status"]
        state = status["State"]
        if state == "SUCCEEDED":
            return
        if state in {"FAILED", "CANCELLED"}:
            reason = status.get("StateChangeReason", "Consulta falhou.")
            raise RuntimeError(f"Athena query {query_execution_id} terminou com status {state}: {reason}")
        time.sleep(poll_seconds)
