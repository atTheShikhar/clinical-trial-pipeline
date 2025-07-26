# variables.tf

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "Region for the GCP resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone to deploy the VM"
  type        = string
  default     = "us-central1-a"
}

variable "gcp_credentials_file" {
  description = "Path to the GCP service account key JSON"
  type        = string
  sensitive   = true
}
