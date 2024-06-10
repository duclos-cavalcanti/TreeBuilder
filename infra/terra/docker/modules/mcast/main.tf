terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0.1"
        }
    }
}

variable "rargs" {
    description = "List of addrs"
    type        = list(string)
    default     = ["-r", "10", 
                   "-d", "10", 
                   "-a", "localhost:8080", "localhost:8081",
                   "-R"
                  ]
}

variable "cargs" {
    description = "List of addrs"
    type        = list(list(string))
    default     = [
        ["-i", "localhost", 
         "-p", "8080", 
         "-a", "localhost:8082", "localhost:8083",
         "-r", "10", 
         "-d", "10"],
        ["-i", "localhost", 
         "-p", "8081", 
         "-a", "localhost:8084", "localhost:8085",
         "-r", "10", 
         "-d", "10"],
        ["-i", "localhost", 
         "-p", "8082", 
         "-r", "10", 
         "-d", "10",
         "-L"],
        ["-i", "localhost", 
         "-p", "8083", 
         "-r", "10", 
         "-d", "10",
         "-L"],
        ["-i", "localhost", 
         "-p", "8084", 
         "-r", "10", 
         "-d", "10",
         "-L"],
        ["-i", "localhost", 
         "-p", "8085", 
         "-r", "10", 
         "-d", "10",
         "-L"],
    ]
}

resource "docker_container" "root0" {
    name  = "root0"
    image = "ubuntu-base:jammy"

    upload {
        file = "/root.sh"
        source = "${path.cwd}/modules/mcast/scripts/root.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"
    entrypoint = concat(["/bin/bash", "/root.sh", "ROOT0"], var.rargs)

    rm         = true
    tty        = true
    stdin_open = true
}

resource "docker_container" "children" {
    count = length(var.cargs)
    name  = "child${count.index}"
    image = "ubuntu-base:jammy"

    upload {
        file = "/child.sh"
        source = "${path.cwd}/modules/mcast/scripts/child.sh"
        executable = true
    }

    upload {
        file = "/work/project.tar.gz"
        source = "${path.cwd}/extract/project.tar.gz"
        executable = false
    }

    network_mode = "host"
    entrypoint = concat(["/bin/bash", "/child.sh", "CHILD${count.index}"], var.cargs[count.index])

    rm         = true
    tty        = true
    stdin_open = true
}
