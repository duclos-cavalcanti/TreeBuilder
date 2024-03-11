<h1 align="center">Master Thesis</h1>
<p align="center">
   VM Selection and Scheduling Heuristic for Financial Exchanges in the Cloud
</p>
<br>

<!-- __Abstract:__ _Not defined yet._ -->

_Master Thesis_ work co-advised by [Dr.Anirudh Sivaraman](https://anirudhsk.github.io/) and [PhD. Muhammad Haseeeb](https://haseeblums.github.io/) from [Systems@NYU](https://news.cs.nyu.edu/), as
well as supervised by [PhD. Navidreza Asadi](https://nrasadi.github.io/) and the [Chair of Communication Networks](https://www.ce.cit.tum.de/en/lkn/home/) at [TUM](https://www.cit.tum.de/en/cit/home/). 
This contribution builds upon on [Jasper: Scalable and Fair Multicast for Financial Exchanges in the Cloud](https://arxiv.org/abs/2402.09527.) and extends it to include a heuristic for better VM 
selection in the context of Jasper's tree-like network structure.

## Introduction

Financial exchanges have shown interest in migrating their current infrastructure 
to the public cloud. The benefits are agreed upon by both the industry and 
academia, promising a more scalable, robust, and cost-efficient infrastructure. 
However, in contrast to the exchange's on-premise data centers, the public cloud does not 
currently offer native mechanisms for fair and performant data delivery. 
Exchanges need to disseminate market data to market participants (MPs) both fast and 
virtually simultaneously to not create unfair advantages among MPs.

[Jasper](https://arxiv.org/abs/2402.09527.), addressed this by presenting a scalable and fair multicast 
for financial exchanges in the cloud. It does so via the employment of an overlay multicast tree and leveraging 
up-to-date advancements in clock synchronization, kernel by-passing, and hedging to simultaneously 
achieve considerable performance and fairness. Jasper offers a commendable alternative, 
outperforming a previous system CloudEx and Amazon's commercial multicast solution.

Moreover, [LemonDrop](https://searchworks.stanford.edu/view/14423035) tackles the real issue of 
inconsistent VM performance within identical instance configurations in the cloud. 
LemonDrop was developed to select and schedule a subset of VMs optimized for a given application's latency needs, by quickly 
detecting under-performing VMs (_Lemons or Stragglers_).
It does so by framing the selection and scheduling of VMs as a Quadratic Assignment Problem (QAP), where 
traffic flow between facilities, each assigned to a location, is to be minimized. 
LemonDrop treats services within an application as facilities and the VMs themselves as the locations. 

Straggler VMs have the potential to drastically affect Jasper's overall system performance.
Inspired by LemonDrop's VM selection method, this work aims to develop a simpler heuristic that 
can achieve reasonably good results adapted to the smaller problem set of a multicast tree. 

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
