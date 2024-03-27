<h1 align="center">Master Thesis</h1>
<p align="center">
   VM Selection and Scheduling Heuristic for Financial Exchanges in the Cloud
</p>
<br>

<!-- __Abstract:__ _Not defined yet._ -->

_Master Thesis_ work co-advised by: 
- [Dr.Anirudh Sivaraman](https://anirudhsk.github.io/) and [PhD. Muhammad Haseeeb](https://haseeblums.github.io/) from [Systems@NYU](https://news.cs.nyu.edu/).
- [PhD. Navidreza Asadi](https://nrasadi.github.io/) and the [Chair of Communication Networks](https://www.ce.cit.tum.de/en/lkn/home/) at [TUM](https://www.cit.tum.de/en/cit/home/). 

## Introduction

Financial exchanges consider a migration to the cloud for scalability, robustness, and cost-efficiency.
[Jasper](https://arxiv.org/abs/2402.09527) presents a scalable and fair multicast solution for cloud-based exchanges, 
addressing the lack of cloud-native mechanisms for such. 
To achieve this, Jasper employs an overlay multicast tree, leveraging clock synchronization, kernel-bypass techniques, 
and more.
However, there are opportunities for enhancement by confronting the issue of inconsistent VM performance 
within identical instances. [LemonDrop](https://searchworks.stanford.edu/view/14423035) tackles this problem, detecting under-performing VMs in a cluster and selecting a subset of VMs optimized for a given application's latency needs.
Yet, we believe that LemonDrop's approach of using time-expensive all-to-all latency measurements and an optimization routine 
for the framed Quadratic Assignment Problem (QAP) is overly complex. 
The proposed work aims to develop a simpler and scalable heuristic, that achieves reasonably good results
within Jasper's time constraints.

- [Project Kickoff](https://docs.google.com/presentation/d/1XlgH70a5laUlEAKua7f3ALofkX98AMYdCSO5etTrlyw/edit?usp=sharing) 
- [Project Proposal](docs/assets/Kickoff.pdf)
- [Project Wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki)

## 1. Setup and Installation

1. Clone the repo
   ```bash
   git clone --recursive https://github.com/duclos-cavalcanti/msc-thesis.git
    # recursive flag needed to include submodule
   ```

2. Install Dependencies _([Ubuntu 22.04 Jammy machine](https://releases.ubuntu.com/jammy/))_
    - Build Tools
   ```bash
    sudo apt install meson cmake ninja build-essential git pkg-config
    sudo apt install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen
    sudo apt-get install linux-image-$(uname -r) -yq
    sudo apt-get install linux-headers-$(uname -r) -yq
    pip install pyelftools meson
   ```

    - Network Tools
   ```bash
   sudo apt install ethtool net-tools inetutils-traceroute tcpdump
   ```
More on further setup, please see [the wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki/Setup).

## 2. Usage

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

## 4. References
- [DPDK](https://www.dpdk.org/)
- [eBPF](https://ebpf.io/)
- [AWS](https://docs.aws.amazon.com/cli/?nc2=h_ql_doc_cli)
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
