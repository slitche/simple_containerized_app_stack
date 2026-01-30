# Security Group allowing SSH access from GitHub Actions runner IP
resource "aws_security_group" "app-sg" {
  name        = "app-sg"
  description = "app security group"

# Allow my IP to access via SSH
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }


# allow GitHub Actions runner IP to access via SSH
  ingress {
    description = "SSH from GitHub Actions runner IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}