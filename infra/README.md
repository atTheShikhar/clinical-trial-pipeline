# Overview

These terraform scripts are used to provision following resources:
1. 2 Google Cloud storage buckets. 
    - `shikhar-clinical-trials-raw` 
    - `shikhar-clinical-trials-ducklake`
2. 2 Google Cloud service accounts. 
    - One with `read` access to `shikhar-clinical-trials-ducklake`. Used by FastAPI server to query data.
    - Another with both `read` and `write` access to `shikhar-clinical-trials-raw` and `shikhar-clinical-trials-ducklake`. Used by SQLMesh for data tranformation.
3. Artifact registery where Cloud Run images will be pushed.
4. Google Cloud Run service. This provisioned with a placeholder image. Later on this can be to deploy actual server image.


# Usage 
1. Edit the [Terraform variables](terraform.tfvars) with variables specific to your Google Cloud Project:
```hcl
project_id = "<your project_id>"
region     = "<region used for provisioning>"
zone       = "<zone used for provisioning>"
```
2. Format the terraform scripts:
```bash
terraform fmt
```
3. Plan the changes to check resource state changes, this is basically a dry run before applying he changes.
```bash
terraform plan
```
4. Apply the changes to start provisioning:
```bash
terraform apply
```
5. If you want to remove all provisioned resources, run:
```bash
terraform destroy
```
