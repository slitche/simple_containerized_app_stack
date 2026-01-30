# Security Group
resource "aws_security_group" "app-sg" {
  name        = "app-sg"
  description = "app security group"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# EC2 Instance
resource "aws_instance" "app-server" {
  ami                    = var.ami
  instance_type          = var.instance_type
  key_name               = "monitoring_keypair" # Ensure this key pair exists in your AWS account
  vpc_security_group_ids = [aws_security_group.app-sg.id]
  user_data              = file("../setup/install_docker.sh") # Script to install Docker on launch

  tags = {
    Name = "app-Server"
  }
}


resource "null_resource" "copy_and_run" {
  depends_on = [aws_instance.app-server]

  #trigger will re-run the copy_and_run if instance changes
  triggers = {
    instance_id = aws_instance.app-server.id
  }
  # Define the SSH connection once
  connection {
    type = "ssh"
    user = var.ssh_user # or ec2-user depending on your AMI
    private_key = var.ssh_private_key
    # private_key = file("../monitoring_keypair.pem")
    host        = aws_instance.app-server.public_ip
  }


  provisioner "file" {
    source      = "../setup/"
    destination = "/home/${var.ssh_user}"
  }


  # Run the script remotely
  provisioner "remote-exec" {
    inline = [
      "cd /home/${var.ssh_user}/",
      "while ! sudo docker info >/dev/null 2>&1; do echo 'Waiting for Docker to be ready...'; sleep 5; done",
      "sudo docker compose up -d --build",

      # THis part is for testing the app if integrations work
      "sed 's/<private_IP>/${aws_instance.app-server.private_ip}/g' test_docker_compose-integrations.sh > test.sh",
      "chmod +x test.sh",
      "sleep 50",  # wait for a bit to ensure the app is up 
      "sudo ./test.sh"
    ]
  }

}




# public IP
output "app_public_ip" {
  value = aws_instance.app-server.public_ip
}

# private IP
output "app_private_ip" {
  value = aws_instance.app-server.private_ip
}

