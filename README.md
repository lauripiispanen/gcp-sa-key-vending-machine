GCP Service Account token vending machine
==========

This project is a WIP to build a vending machine that creates a service account key that is automatically deleted after a configurable period.

**Deploy:**

```gcloud deployment-manager deployments create token-vendor --template=token-vendor.jinja```