import duckdb
from dotenv import dotenv_values
from sqlmesh.core.config.connection import DuckDBAttachOptions
from sqlmesh import model

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
            PORT '{secrets["MYSQL_TCP_PORT"]}',
            DATABASE '{secrets["MYSQL_DATABASE"]}',
            USER '{secrets["MYSQL_USER"]}',
            PASSWORD '{secrets["MYSQL_PWD"]}'
        );
        ATTACH 'ducklake:mysql:' AS my_ducklake (DATA_PATH '{secrets["DUCKLAKE_GCS_BUCKET"]}', METADATA_SCHEMA '{secrets["MYSQL_DATABASE"]}');
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


def write_data():
    duckdb.sql(
        f"""
        COPY(
            SELECT
                protocolSection.identificationModule.nctId AS nct_id,
                protocolSection.identificationModule.briefTitle AS brief_title,
                protocolSection.conditionsModule.conditions AS condition,
                LIST_TRANSFORM(protocolSection.armsInterventionsModule.interventions, x -> x.name) AS intervention_names,
                protocolSection.statusModule.overallStatus AS overall_status,
                DATE(try_strptime(protocolSection.statusModule.startDateStruct.date, '%Y-%m-%d')) AS start_date,
                DATE(try_strptime(protocolSection.statusModule.primaryCompletionDateStruct.date, '%Y-%m-%d')) AS primary_completion_date,
                YEAR(start_date) AS start_year,
                MONTH(start_date) AS start_month
            FROM 
                read_ndjson(
                    [
                        '{secrets["RAW_GCS_BUCKET"]}NCT00000579.json',
                        '{secrets["RAW_GCS_BUCKET"]}NCT00000679.json',
                        '{secrets["RAW_GCS_BUCKET"]}NCT00676884.json',
                    ],
                    ignore_errors=true, 
                    auto_detect=true
                )
            WHERE
                start_date IS NOT NULL
        ) TO '{secrets["DUCKLAKE_GCS_BUCKET"]}'
        (FORMAT parquet, COMPRESSION zstd, PARTITION_BY (start_year, start_month), OVERWRITE_OR_IGNORE)
        """
    )
    print("data writted!")


def read_data():
    duckdb.sql(
        f"""
        SELECT * FROM read_parquet('{secrets["DUCKLAKE_GCS_BUCKET"]}*/*/*.parquet', hive_partitioning=false);
        """
    ).show()

# columns={nct_id: 'VARCHAR', brief_title: 'VARCHAR', condition: 'VARCHAR[]', intervention_names: 'VARCHAR[]', overall_status: 'VARCHAR', start_date: 'DATE', primary_completion_date: 'DATE'}

def main():
    configure_cloud_storage()
    # configure_ducklake()
    # write_data()
    read_data()
    # duckdb.sql(
    #     f"""
    #         SELECT 
    #             nct_id,
    #             brief_title,
    #             conditions,
    #             intervention_names,
    #             overall_status,
    #             CASE 
    #                 WHEN try_strptime(start_date, '%Y-%m-%d') IS NOT NULL 
    #                     THEN DATE(strptime(start_date, '%Y-%m-%d'))
    #                 WHEN try_strptime(start_date, '%Y-%m') IS NOT NULL 
    #                     THEN DATE(strptime(start_date || '-01', '%Y-%m-%d'))
    #                 ELSE 
    #                     NULL
    #             END AS start_date,
    #             CASE 
    #                 WHEN try_strptime(completion_date, '%Y-%m-%d') IS NOT NULL 
    #                     THEN DATE(strptime(completion_date, '%Y-%m-%d'))
    #                 WHEN try_strptime(completion_date, '%Y-%m') IS NOT NULL 
    #                     THEN DATE(strptime(completion_date || '-01', '%Y-%m-%d'))
    #                 ELSE 
    #                     NULL
    #             END AS completion_date
    #         FROM (
    #             SELECT
    #                 protocolSection.identificationModule.nctId AS nct_id,
    #                 protocolSection.identificationModule.briefTitle AS brief_title,
    #                 protocolSection.conditionsModule.conditions AS conditions,
    #                 LIST_TRANSFORM(protocolSection.armsInterventionsModule.interventions, x -> x.name) AS intervention_names,
    #                 protocolSection.statusModule.overallStatus AS overall_status,
    #                 protocolSection.statusModule.startDateStruct.date AS start_date,
    #                 protocolSection.statusModule.primaryCompletionDateStruct.date AS completion_date,
    #             FROM 
    #                 read_ndjson(
    #                     "./dummy/*.json",
    #                     ignore_errors=true, 
    #                     auto_detect=true
    #                 )
    #             WHERE 
    #                 start_date IS NOT NULL
    #         ) AS raw_data;
    #     """
    # ).show()


                        # [
                        #     '{secrets["RAW_GCS_BUCKET"]}NCT00000579.json',
                        #     '{secrets["RAW_GCS_BUCKET"]}NCT00000679.json',
                        #     '{secrets["RAW_GCS_BUCKET"]}NCT00676884.json',
                        # ],

if __name__ == "__main__":
    main()
