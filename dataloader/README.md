# Dataloader

The primary objective of this script is to fetch all the clinical trials data from [ClinicalTrials.gov](https://clinicaltrials.gov/) public REST API and upload to `GCS` bucket.

## Basic Working
1. This script downloads all public studies compressed in single `.zip` file.
2. Extracts the content of the `.zip` file.
3. Streams individual `.json` file blobs to `GCS` bucket via Google Cloud python client.
4. The upload happends in concurrent fashion with maximum set by `MAX_WORKERS` variable.


## Setup Instructions
1. Create a Google Cloud Storage bucket.
2. Create a Service Account on Google Cloud with write access to the bucket created in step 1.
3. Set the following environment variables.
    - `GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account_creds.json"`
    - `GCS_BUCKET_NAME="<your_gcs_bucket_name>"`
4. Make sure [Docker](https://docs.docker.com/engine/install/debian/#installation-methods) is installed.
5. Build the docker image:
```bash
docker build -t gcs-uploader .
```
6. Run the image:
```bash
docker run --rm --name dataloader gcs-uploader
# OR in detach mode
docker run -d --rm --name dataloader gcs-uploader
```
