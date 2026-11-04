output "cluster_id" {
  description = "EKS Cluster ID"
  value       = aws_eks_cluster.eks.id
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.eks.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.eks.vpc_config[0].cluster_security_group_id
}

output "kubectl_config_command" {
  description = "Command to configure kubectl credentials"
  value       = "aws eks --region ${var.region} update-kubeconfig --name ${aws_eks_cluster.eks.name}"
}
