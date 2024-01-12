<h1 align="center">Master Thesis</h1>
<p align="center">
   High Performance Multicasting on the Cloud
</p>
<br>

<details open>
<summary> <b>ROADMAP</b> </summary>
<p>

- To-do
    - [ ] AWS to GCP
- Academia
    - [X] Email Prof.

</p>
</details>
<details closed>
 <summary>
     <b>PAPERS & <a href="https://github.com/duclos-cavalcanti/master-arbeit/wiki/Documentation">NOTES</a></b> 
 </summary>
 <p>

 <table>
 <tr> <th>Title</th> <th>Date</th> </tr>

 <tr>
     <td>
     <a href="www.google.com">
     Foobar
     </a>
     <td> <em>2023</em> </td> 
 </tr>

 </table> 

 </p>
</details>

## Introduction

__Abstract:__ _Not defined yet._

- [Kickoff](https://docs.google.com/presentation/d/1jYG-S1xyy03R2H4vy9wFlQLlAAt9CFZ3rXdfz10VZpw/edit?usp=sharing)
- [Presentation](https://docs.google.com/presentation/d/1jYG-S1xyy03R2H4vy9wFlQLlAAt9CFZ3rXdfz10VZpw/edit?usp=sharing)

Check out the [_wiki_](https://github.com/duclos-cavalcanti/master-arbeit/wiki) for more!

## 1. Setup

1. Clone the repo
   ```bash
   git clone --recursive https://github.com/duclos-cavalcanti/msc-thesis.git
    # recursive flag needed to include submodule
   ```

## 2. Dependencies
All are based on a [Ubuntu 22.04 Jammy machine](https://releases.ubuntu.com/jammy/).

### Network Tools
   ```bash
   sudo apt install net-tools inetutils-traceroute
   ```

### Google Cloud Platform (GCP)
1. Installation
```bash
sudo apt-get install apt-transport-https ca-certificates gnupg
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update
sudo apt-get install google-cloud-sdk
```

2. Configuration 
```bash 
gcloud init
```

3. Optional
```bash 
gcloud components install gsutil
```

### AWS
   ```bash

   ```

## 3. Usage

1. Build
    ```bash 
    make build
    ```

2. Run
    ```bash 
    make run
    ```

## 3. License
This project is released under the BSD 3-Clause license. See [LICENSE](LICENSE).

## 4. Resources 
- [DPDK](https://www.dpdk.org/)
    + [DPDK on Linux](http://doc.dpdk.org/guides/linux_gsg/intro.html)
- [eBPF](https://ebpf.io/)
- [AWS-CLI](https://docs.aws.amazon.com/cli/?nc2=h_ql_doc_cli)
- [GCP](https://cloud.google.com/)

---
<p align="center">
<a href="https://github.com/duclos-cavalcanti/master-arbeit/LICENSE">
  <img src="https://img.shields.io/badge/license-BSD3-yellow.svg" />
</a>
<a>
  <img src="https://img.shields.io/github/languages/code-size/duclos-cavalcanti/master-arbeit.svg" />
</a>
<a>
  <img src="https://img.shields.io/github/commit-activity/m/duclos-cavalcanti/master-arbeit.svg" />
</a>
</p>
