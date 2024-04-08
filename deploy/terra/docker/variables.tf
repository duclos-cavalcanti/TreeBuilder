variable "name" {
    description = "Container's Name"
    type        = string
    default     = "base"
}

variable "entry" {
    description = "Path to entryscript of docker"
    type        = string
    default     = "/root/entry.sh"
}

variable "pwd" {
    description = "Path to project folder that is injected as a volume"
    type        = string
    default     = "/path"
}

variable "exposed_port" {
    description = "Port number on host machine"
    type        = number
    default     = 8081
}

