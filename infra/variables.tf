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

variable "mysql_user" {
  description = "MySQL username"
  type        = string
}

variable "mysql_pass" {
  description = "MySQL password"
  type        = string
  sensitive   = true
}

variable "mysql_host" {
  description = "MySQL host address"
  type        = string
}

variable "mysql_db" {
  description = "MySQL database name"
  type        = string
}

variable "storage_bucket" {
  description = "Google Cloud Storage bucket name"
  type        = string
}

variable "storage_access_id" {
  description = "Storage access ID"
  type        = string
}

variable "storage_secret" {
  description = "Storage secret key"
  type        = string
  sensitive   = true
}

variable "server_api_key" {
  description = "Server API key"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment type"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["prod", "dev"], var.environment)
    error_message = "Environment must be either 'prod' or 'dev'."
  }
}

