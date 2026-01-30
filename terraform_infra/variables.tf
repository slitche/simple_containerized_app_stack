
variable "my_ip" {
  description = "My IP address for security group rules"
  type        = string
  default = "136.158.61.51/32"
}

variable "ssh_user" {
  description = "SSH user for EC2 instance"
  type        = string
  default = "ubuntu"
}


variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "ami" {
  description = "AMI - us-east-1 UBUNTU"
  type        = string
  default     = "ami-0ecb62995f68bb549"
}

variable "instance_type" {
  description = "Instance type for EC2 instances"
  type        = string
  default     = "t3.micro"
}

variable "vpc_id" {
  description = "VPC ID where resources will be deployed"
  type        = string
  default     = "vpc-0b1a89f0204ae0513"
}

# variable "ssh_private_key" {
#   description = "SSH private key for EC2 instance access. defined in GitHub Secrets"
#   type        = string
# }

# variable "tf_state_file" {
#   description = "Terraform state file key"
#   type        = string
# }

# variable "tf_s3_bucket" {
#   description = "Terraform state file key"
#   type        = string
# }
