terraform {
  required_version = ">= 1.6.0"

  backend "gcs" {
    bucket = "clinical-terraform-state"
    prefix = "envs/prod"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.45"
    }
  }
}
