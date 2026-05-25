# Exemplo de Data Lake na AWS (S3 + Glue + Athena)

Implementação simples de hello world de Data Lake na AWS, usando:

- `Amazon S3` como storage em zonas `raw` e `processed`
- `AWS Glue` para crawler, catálogo e ETL
- `Amazon Athena` para consultas SQL serverless
- `Terraform` para infraestrutura
- `Python + uv` para scripts operacionais

O caso prático usa o dataset público `NYC Taxi Trip Records` e monta um pipeline pequeno, direto e fácil de demonstrar:

```text
Download HTTP -> S3 Raw -> Glue Crawler
              -> Glue ETL -> S3 Processed
              -> Athena
```

## Ideia da demo

A proposta aqui não é construir um data lake completo de producao.
O objetivo é mostrar, da forma mais simples:

- dados chegando no `S3`
- schema sendo descoberto pelo `Glue Crawler`
- transformacao simples com `Glue Job`
- consulta SQL no `Athena`

## Estrutura

```text
.
├── pyproject.toml
├── scripts/
│   ├── athena_queries.py
│   ├── common.py
│   ├── glue_taxi_etl.py
│   ├── ingest_raw.py
│   └── run_pipeline.py
├── sql/
│   ├── 01_monthly_revenue.sql
│   ├── 02_payment_type.sql
│   └── 03_partition_pruning.sql
└── terraform/
    ├── locals.tf
    ├── main.tf
    ├── outputs.tf
    ├── providers.tf
    ├── terraform.tf
    ├── variables.tf
```

## Pré-requisitos

- Conta AWS com permissões para `S3`, `Glue` e `Athena`
- Credenciais AWS configuradas localmente
- `terraform` instalado
- `uv` instalado

## Ambiente local

```bash
uv sync
```

## Infraestrutura

Crie os recursos:

```bash
cd terraform
terraform init
terraform apply -auto-approve
terraform output -json > ../outputs.json
cd ..
```

Recursos criados:

- bucket S3 do Data Lake
- Glue databases `raw` e `processed`
- Glue crawlers
- Glue job em PySpark
- workgroup Athena

Observação:
esta versão foi simplificada para contas de laboratório com restrições de `IAM`. O Terraform reaproveita uma role já existente chamada `LabRole` para o Glue e evita etapas de governança mais avançadas.

## Ingestão para a zona Raw

Exemplo com janeiro, fevereiro e março de 2024:

```bash
uv run python scripts/ingest_raw.py \
  --outputs outputs.json \
  --year 2024 \
  --months 1 2 3
```

Os arquivos serão enviados para:

```text
raw/nyc_taxi/year=2024/month=01/
raw/nyc_taxi/year=2024/month=02/
raw/nyc_taxi/year=2024/month=03/
```

## Execução do pipeline

```bash
uv run python scripts/run_pipeline.py --outputs outputs.json
```

Esse script faz só três passos:

1. executa o crawler da zona raw
2. dispara o Glue job
3. executa o crawler da zona processed

## Consultas Athena

```bash
uv run python scripts/athena_queries.py --outputs outputs.json
```

Consultas incluídas:

- corridas e receita por mês
- receita por tipo de pagamento
- exemplo de partition pruning

## Saídas esperadas

O Glue ETL gera dois datasets:

- `processed/taxi_trips_clean/`
- `processed/taxi_monthly_metrics/`

As tabelas são particionadas por `year` e `month`, o que ajuda a demonstrar redução de custo no Athena.

## Mapeamento com a apresentação

- `S3 como fundação do Data Lake`: bucket central com zonas `raw` e `processed`
- `Glue Crawlers`: descoberta automática de schema
- `Glue Data Catalog`: catálogo central
- `Glue ETL`: limpeza e agregação na zona `processed`
- `Athena`: SQL serverless sobre dados em S3

## Observações importantes

- O crawler raw produz a tabela lida pelo Glue job, e o `run_pipeline.py` descobre esse nome automaticamente.
- O Glue job está preparado para o schema do dataset `yellow taxi`, com colunas como `tpep_pickup_datetime`, `trip_distance`, `fare_amount` e `payment_type`.
- O Terraform reutiliza por padrão uma role IAM já existente chamada `LabRole` para executar os recursos do Glue, o que é mais compatível com contas de laboratório.
- O projeto foi reduzido ao essencial para a demo: `S3 + Glue + Athena`.
- Nao ha Lake Formation, multiplas roles nem orquestracao mais sofisticada, porque a meta aqui e manter um exemplo curto e executavel em conta de laboratorio.
- Para evitar custo desnecessário, destrua os recursos ao final:

```bash
cd terraform
terraform destroy -auto-approve
```
