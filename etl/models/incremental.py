import pandas as pd
from datetime import datetime
from typing import Any
from sqlmesh import ExecutionContext, model
from sqlmesh.core.model.kind import ModelKindName


@model(
    name="studies.incremental",
    kind=dict(
        name=ModelKindName.INCREMENTAL_BY_TIME_RANGE,
        time_column="start_date",
        partition_by_time_column=False,
    ),
    columns={
        "nct_id": "varchar",
        "brief_title": "varchar",
        "conditions": "varchar[]",
        "intervention_names": "varchar[]",
        "overall_status": "varchar",
        "start_date": "date",
        "primary_completion_date": "date",
        "start_year": "int",
        "start_month": "int"
    },
    partitioned_by=["start_year", "start_month"]
)
def trials_data(
    context: ExecutionContext,
    start: datetime,
    end: datetime,
    execution_time: datetime,
    **kwargs: Any,
) -> pd.DataFrame:
    gcs_bucket = context.var("raw_gcs_bucket")
    df = context.fetchdf(
        f"""
            SELECT
                protocolSection.identificationModule.nctId AS nct_id,
                protocolSection.identificationModule.briefTitle AS brief_title,
                protocolSection.conditionsModule.conditions AS conditions,
                LIST_TRANSFORM(protocolSection.armsInterventionsModule.interventions, x -> x.name) AS intervention_names,
                protocolSection.statusModule.overallStatus AS overall_status,
                DATE(try_strptime(protocolSection.statusModule.startDateStruct.date, '%Y-%m-%d')) AS start_date,
                DATE(try_strptime(protocolSection.statusModule.primaryCompletionDateStruct.date, '%Y-%m-%d')) AS primary_completion_date,
                YEAR(start_date) AS start_year,
                MONTH(start_date) AS start_month
            FROM 
                read_ndjson(
                    CONCAT('{gcs_bucket}', '*.json'),
                    ignore_errors=true, 
                    auto_detect=true
                )
            WHERE 
                start_date IS NOT NULL
                AND start_date BETWEEN '{start}' AND '{end}';
        """
    )
    return df
