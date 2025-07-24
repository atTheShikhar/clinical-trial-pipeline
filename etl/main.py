import duckdb
from dotenv import dotenv_values

secrets = dotenv_values(".env")

def configure_ducklake(flavour="duckdb"):
    print("configuring ducklake...")
    if flavour!="duckdb":
        raise NotImplemented
    duckdb.sql("INSTALL ducklake;")
    duckdb.sql(f"""
        CREATE SECRET (
            TYPE mysql,
            HOST '{secrets["MYSQL_HOST"]}',
            PORT 3306,
            DATABASE '{secrets["MYSQL_DB"]}',
            USER '{secrets["MYSQL_USER"]}',
            PASSWORD '{secrets["MYSQL_PASS"]}'
        );
        ATTACH 'ducklake:mysql:' AS my_ducklake (DATA_PATH 'gs://shikhar-clinical-trials-ducklake/trials');
    """)
    duckdb.sql("USE my_ducklake;")
    print("ducklake configured")
    

def configure_cloud_storage(flavour="gcloud"):
    print("configuring storage...")
    if flavour!="gcloud":
        raise NotImplemented
    duckdb.sql(
        f"""
        INSTALL httpfs;
        LOAD httpfs;
        CREATE SECRET (
            TYPE gcs,
            KEY_ID '{secrets["GCP_KEY_ID"]}',
            SECRET '{secrets["GCP_SECRET"]}'
        );
        """
    )
    print("storage configured")

# TODO: write partitioned data

def write_data():
    # duckdb.read_json()
    duckdb.sql(
        """
        COPY(
            SELECT
                protocolSection.identificationModule.nctId AS nct_id,
                protocolSection.identificationModule.briefTitle AS brief_title,
                protocolSection.conditionsModule.conditions AS condition,
                LIST_TRANSFORM(protocolSection.armsInterventionsModule.interventions, x -> x.name) AS intervention_names,
                protocolSection.statusModule.overallStatus AS overall_status,
                CASE
                    WHEN protocolSection.statusModule.startDateStruct.date ~ '^\d{4}-\d{2}-\d{2}$' THEN CAST(protocolSection.statusModule.startDateStruct.date AS DATE)
                    WHEN protocolSection.statusModule.startDateStruct.date ~ '^\d{4}-\d{2}$' THEN CAST(protocolSection.statusModule.startDateStruct.date || '-01' AS DATE)
                    WHEN protocolSection.statusModule.startDateStruct.date ~ '^\d{4}$' THEN CAST(protocolSection.statusModule.startDateStruct.date || '-01-01' AS DATE)
                    ELSE NULL
                END AS start_date,
                CASE
                    WHEN protocolSection.statusModule.primaryCompletionDateStruct.date ~ '^\d{4}-\d{2}-\d{2}$' THEN CAST(protocolSection.statusModule.primaryCompletionDateStruct.date AS DATE)
                    WHEN protocolSection.statusModule.primaryCompletionDateStruct.date ~ '^\d{4}-\d{2}$' THEN CAST(protocolSection.statusModule.primaryCompletionDateStruct.date || '-01' AS DATE)
                    WHEN protocolSection.statusModule.primaryCompletionDateStruct.date ~ '^\d{4}$' THEN CAST(protocolSection.statusModule.primaryCompletionDateStruct.date || '-01-01' AS DATE)
                    ELSE NULL
                END AS primary_completion_date,
                YEAR(start_date) AS start_year,
                MONTH(start_date) AS start_month
            FROM 
                read_json(
                    'gs://shikhar-clinical-trials-raw/*.json', 
                    ignore_errors=true, 
                    auto_detect=true
                )
        ) TO 'gs://shikhar-clinical-trials-ducklake/trials'
        (FORMAT parquet, COMPRESSION zstd, PARTITION_BY (start_year, start_month), OVERWRITE_OR_IGNORE)
        """
    )
    print("data writted!")


def read_data():
    duckdb.sql(
        """
        SELECT * FROM read_parquet('gs://shikhar-clinical-trials-ducklake/trials/*/*/*.parquet', hive_partitioning=false);
        """
    ).show()

# columns={nct_id: 'VARCHAR', brief_title: 'VARCHAR', condition: 'VARCHAR[]', intervention_names: 'VARCHAR[]', overall_status: 'VARCHAR', start_date: 'DATE', primary_completion_date: 'DATE'}

def main():
    configure_cloud_storage()
    configure_ducklake()
    write_data()
    read_data()
    # duckdb.read_json_objects("dummy/*.json")   
    # con = duckdb.connect("db.db")
    # con.sql("SELECT * FROM sqlmesh_example__dev.seed_model").show()
    # print(df)
    # print("Hello from etl!")
    # duckdb.sql("SELECT * FROM read_parquet('trials.parquet')").show()


if __name__ == "__main__":
    main()
