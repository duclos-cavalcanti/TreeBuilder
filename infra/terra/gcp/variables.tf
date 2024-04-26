variable "machine" {
    description = "Machine Type"
    type        = string
    default     = "e2-standard-4"
}

variable "image" {
    description = "Machine Image"
    type        = string
    default     = "multicast-ebpf-zmq-grub-disk"
}

variable "pwd" {
    description = "Path"
    type        = string
    default     = "/path"
}
