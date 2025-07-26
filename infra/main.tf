provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_storage_bucket" "raw_bucket" {
  name          = "shikhar-clinical-trials-raw"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "ducklake_bucket" {
  name          = "shikhar-clinical-trials-ducklake"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  public_access_prevention = "enforced"
}

resource "google_artifact_registry_repository" "query_api_repo" {
  provider = google

  location      = var.region
  repository_id = "query-api"
  description   = "Docker repository for query-api Cloud Run service"
  format        = "DOCKER"

}

# First Service Account: Full access to both buckets
resource "google_service_account" "bucket_rw_sa" {
  account_id   = "clinical-rw-access"
  display_name = "Read/Write access to both buckets"
}

# Second Service Account: Read-only access to ducklake bucket
resource "google_service_account" "bucket_ro_sa" {
  account_id   = "ducklake-ro-access"
  display_name = "Read-only access to ducklake bucket"
}

# Grant RW access to both buckets for clinical-rw-access
resource "google_storage_bucket_iam_member" "rw_sa_raw" {
  bucket = google_storage_bucket.raw_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.bucket_rw_sa.email}"
}

resource "google_storage_bucket_iam_member" "rw_sa_ducklake" {
  bucket = google_storage_bucket.ducklake_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.bucket_rw_sa.email}"
}

# Grant RO access to ducklake bucket for ducklake-ro-access
resource "google_storage_bucket_iam_member" "ro_sa_ducklake" {
  bucket = google_storage_bucket.ducklake_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.bucket_ro_sa.email}"
}


# Provisions Google Cloud Run service with placeholder image
resource "google_cloud_run_v2_service" "query_api" {
  name     = "query-api"
  location = var.region

  template {
    containers {
      image = "gcr.io/cloudrun/hello" # Placeholder image
      ports {
        container_port = 8000
      }
      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 4
    }

    max_instance_request_concurrency = 5
    timeout                          = "60s"
  }

  ingress = "INGRESS_TRAFFIC_ALL"

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow public access to the query-api cloud run service
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.query_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}



# resource "google_compute_instance" "vm_instance" {
#   name         = "shikhar-vm"
#   machine_type = "e2-standard-2" # 2 vCPU, 4 GB RAM
#   zone         = var.zone

#   boot_disk {
#     initialize_params {
#       image = "debian-cloud/debian-12"
#       size  = 20 # in GB
#       type  = "pd-balanced"
#     }

#     auto_delete = true
#   }

#   network_interface {
#     network = "default"

#     access_config {
#       # This allocates a public IP
#     }
#   }

#   metadata = {
#     enable-oslogin = "TRUE" # Enables SSH via IAM or OS Login
#   }

#   tags = ["ssh-enabled"]
# }


# resource "google_compute_firewall" "allow_ssh" {
#   name    = "allow-ssh"
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports    = ["22"]
#   }

#   source_ranges = ["0.0.0.0/0"]
#   target_tags   = ["ssh-enabled"]
# }
