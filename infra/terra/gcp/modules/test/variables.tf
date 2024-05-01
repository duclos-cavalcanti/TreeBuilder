variable "machine" {
    description = "Machine Type"
    type        = string
    default     = "e2-standard-4"
}

variable "image" {
    description = "Machine Image"
    type        = string
    default     = "ubuntu-base-disk"
}

variable "bucket" {
    description = "Bucket Name"
    type        = string
    default     = "treedrop-nyu-systems"
}

variable "pwd" {
    description = "Path"
    type        = string
    default     = "/path"
}
