-- sqlfluff: disable=L014,L025
MODEL (
  name studies.incremental,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column start_date,
    partition_by_time_column false
  ),
  partitioned_by (start_year, start_month)
);

SELECT 
    protocolSection.identificationModule.nctId AS nct_id,
    protocolSection.identificationModule.briefTitle AS brief_title,
    protocolSection.conditionsModule.conditions AS conditions,
    LIST_TRANSFORM(protocolSection.armsInterventionsModule.interventions, x -> x.name) AS intervention_names,
    protocolSection.statusModule.overallStatus AS overall_status,
    CASE 
        WHEN try_strptime(protocolSection.statusModule.startDateStruct.date, '%Y-%m-%d') IS NOT NULL 
            THEN DATE(strptime(protocolSection.statusModule.startDateStruct.date, '%Y-%m-%d'))
        WHEN try_strptime(protocolSection.statusModule.startDateStruct.date, '%Y-%m') IS NOT NULL 
            THEN DATE(strptime(protocolSection.statusModule.startDateStruct.date || '-01', '%Y-%m-%d'))
        ELSE 
            NULL
    END AS start_date,
    CASE 
        WHEN try_strptime(protocolSection.statusModule.primaryCompletionDateStruct.date, '%Y-%m-%d') IS NOT NULL 
            THEN DATE(strptime(protocolSection.statusModule.primaryCompletionDateStruct.date, '%Y-%m-%d'))
        WHEN try_strptime(protocolSection.statusModule.primaryCompletionDateStruct.date, '%Y-%m') IS NOT NULL 
            THEN DATE(strptime(protocolSection.statusModule.primaryCompletionDateStruct.date || '-01', '%Y-%m-%d'))
        ELSE 
            NULL
    END AS completion_date,
    YEAR(start_date) AS start_year,
    MONTH(start_date) AS start_month
FROM 
    read_ndjson(
        CONCAT(@RAW_GCS_BUCKET, '*.json'),
        ignore_errors=true, 
        auto_detect=true
    )
WHERE 
  start_date IS NOT NULL 
  AND start_date BETWEEN @start_date AND @end_date;