# Overview

The primary objective of this script is to fetch all the clinical trials data from [ClinicalTrials.gov](https://clinicaltrials.gov/) public REST API and upload to `GCS` bucket.

## Basic Workflow
1. This script downloads all public studies compressed in single `.zip` file.
2. Extracts the content of the `.zip` file.
3. Streams individual `.json` file blobs to `GCS` bucket via Google Cloud python client.
4. The upload happens in concurrent fashion with maximum workers set by `MAX_WORKERS` variable.


## Setup Instructions
1. Create a Google Cloud Storage bucket.
2. Create a [Service Account](https://cloud.google.com/iam/docs/service-accounts-create) on Google Cloud with write access to the bucket created in step 1.
3. Generate the [Service Account key](https://cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-console) file 
4. Set the following environment variables.
    - `GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account_creds.json"`
    - `GCS_BUCKET_NAME="<your_gcs_bucket_name>"`

## Usage 
1. Make sure [Docker](https://docs.docker.com/engine/install/debian/#installation-methods) is installed.
2. Build the docker image:
```bash
docker build -t gcs-uploader .
```
3. Run the image:
```bash
docker run --rm --name dataloader gcs-uploader
# OR in detach mode
docker run -d --rm --name dataloader gcs-uploader
```
