# Overview

This REST API can be used to execute `SQL` queries on the DuckDB database. The server logic is written in [FastAPI](https://fastapi.tiangolo.com/).

## Basic Workflow

1. This server exposes a HTTP endpoint named `/query`.
2. Users can pass `SQL` statements in the request body and the server will do the followings:
    - Validate `SQL` query.
    - Execute the query.
    - Return the response of the query in `JSON` format.
3. The database on which the query is executed depends on the value of environment variable with the name `environment`. Depending on the value:
    - `dev`: The query is run on a `local.duckdb` file. 
    - `prod`: The query will be executed on `.parquet` files hosted on the Google Cloud Storage bucket.
4. The schema definition for DuckLake db is as follows:
```
{
    nct_id: 'VARCHAR', 
    brief_title: 'VARCHAR', 
    conditions: 'VARCHAR[]', 
    intervention_names: 'VARCHAR[]', 
    overall_status: 'VARCHAR', 
    start_date: 'DATE', 
    primary_completion_date: 'DATE',
    start_year: 'INT',
    start_month: 'INT'
}
```
4. Any unexpected error generated on the server is handled by global exception handlers.
5. Basic api key authentication is added.


> Developer Note: While running in "dev" mode, make sure the `local.duckdb` file has the relevant tables on which the queries are executed. You can also run the command `python generate_dummy_data.py` to generate a dummy table `t1` on the local db file.



## Setup Instructions

1. Create a [Service Account](https://cloud.google.com/iam/docs/service-accounts-create) on Google Cloud with read access to the bucket on which DuckLake data is setup.
2. Generate the [HMAC keys](https://cloud.google.com/storage/docs/authentication/managing-hmackeys) for the above service account. This will be used by DuckDB to authenticate with Google Cloud in order to access GCS bucket.
4. Set the following environment variables.
```env
STORAGE_BUCKET="gs://<ducklake_gcs_bucket_name>"
STORAGE_ACCESS_ID="<HMAC Access_ID>"
STORAGE_SECRET="<HMAC Secret>"
MYSQL_USER="<Mysql username>"
MYSQL_PASS="Mysql password"
MYSQL_HOST="<Mysql Hostname>"
MYSQL_DB="<Your DuckLake Metadata Dbname>"
ENVIRONMENT="<'prod' or 'dev'>"
SERVER_API_KEY="Basic key which will be used by the client to authenticate"
```

## Usage

1. Make sure [Docker](https://docs.docker.com/engine/install/debian/#installation-methods) is installed.
2. Build the docker image:
```bash
docker build -t clinical-trials-api .
```
3. Run the image:
```bash
docker run -p 8000:8000 --name trials-api clinical-trials-api
```
4. When run locally, this server will be exposed at `http://localhost:8000`.
5. The Swagger docs can be at on `/active-docs` endpoint.
6. You can also execute the `/query` endpoint using the following curl command:
```curl
curl -X 'POST' \
  '<BASE_URL>/query' \
  -H 'accept: application/json' \
  -H 'x-api-token: <SERVER_API_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
  "sql": "SELECT * FROM t1;"
}'
```
> Replace <BASE_URL> and <SERVER_API_TOKEN> accordingly

