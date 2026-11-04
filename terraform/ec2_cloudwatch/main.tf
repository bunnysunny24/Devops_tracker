# Terraform Configuration for Practical 5: EC2 + CloudWatch Monitoring

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "ap-south-1" # Mumbai region / or change to your preferred region
}

variable "instance_type" {
  default = "t3.medium"
}

variable "key_name" {
  default = "practical5-key"
}

# 1. Security Group (Port 22 SSH, Port 80 HTTP, Port 8080 Jenkins, Port 9090 Prometheus, Port 3000 Grafana)
resource "aws_security_group" "web_sg" {
  name        = "practical5-ecommerce-sg"
  description = "Allow inbound HTTP, SSH, and Monitoring traffic"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP Web Traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Application Direct Port"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana Dashboard"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus UI"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. IAM Role for CloudWatch Agent integration
resource "aws_iam_role" "cloudwatch_role" {
  name = "practical5-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cw_agent_policy" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role_name  = aws_iam_role.cloudwatch_role.name
}

resource "aws_iam_instance_profile" "cw_profile" {
  name = "practical5-cw-profile"
  role = aws_iam_role.cloudwatch_role.name
}

# 3. AWS EC2 Instance (Ubuntu 24.04 LTS)
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "ecommerce_server" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = var.instance_type
  key_name             = var.key_name
  security_groups      = [aws_security_group.web_sg.name]
  iam_instance_profile = aws_iam_instance_profile.cw_profile.name

  tags = {
    Name        = "Practical-5-Ecommerce-Monitoring"
    Environment = "production"
  }
}

# 4. Amazon CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/practical5/application"
  retention_in_days = 7
}

# 5. CloudWatch CPU Metric Alarm (> 70% for 2 periods)
resource "aws_cloudwatch_metric_alarm" "cpu_high_alarm" {
  alarm_name          = "practical5-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 70
  alarm_description   = "Triggers when average EC2 CPU exceeds 70% for 10 minutes"
  
  dimensions = {
    InstanceId = aws_instance.ecommerce_server.id
  }
}

output "instance_public_ip" {
  value = aws_instance.ecommerce_server.public_ip
}
