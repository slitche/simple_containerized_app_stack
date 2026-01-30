terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    # this should be retained so that terraform will create state file in s3 bucket
    # even if there's an error in provisioning

    # backend config variables are defined in GitHub Actions workflow file/CLI
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Need to get my IP address for security group since GitHub Actions runners have dynamic IPs..
# and we have to upload files via SSH
data "http" "myip" {
  url = "https://checkip.amazonaws.com/"
}
