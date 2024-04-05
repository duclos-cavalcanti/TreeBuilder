variable "exposed_port" {
    description = "Port number on host machine"
    type        = number
    default     = 8080
}

variable "container_name" {
    description = "Container's Name"
    type        = string
    default     = "base"
}
