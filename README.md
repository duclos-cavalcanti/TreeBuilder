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
However, a vital concern is the lack of support for fair and performant multicast 
in the public cloud. Exchanges need to disseminate market data to market participants 
(MPs) both fast and fairly. Every MP has to receive market state updates 
almost simultaneously to not create an unfair advantage among MPs.

Different than the current exchange's on-premise data centers, the cloud does not 
offer native mechanisms for fair data delivery. Recent work, namely Jasper, 
has addressed this gap, offering a solution that creates an overlay multicast tree, leveraging 
up-to-date advancements in clock synchronization, kernel by-passing, and hedging, 
to present a scalable and fair multicast on the cloud. Jasper offers a commendable 
alternative, outperforming contemporary efforts, and Amazon's in-house multicast solution, 
as well as addressing known irregularities regarding network latency in the cloud.

[LemonDrop](https://searchworks.stanford.edu/view/14423035), a component 
of a larger body of work, tackles the real issue of inconsistent VM performance within identical instance configurations 
in the cloud. Under-performing VMs within a given instance class are called _Lemons_. 
LemonDrop was developed to select and schedule a subset of VMs optimized for a given application's latency needs, by quickly 
detecting lemon VMs, repositioning them across the system, or dropping them completely.
It does so by framing the selection and scheduling of VMs as a Quadratic Assignment Problem, where 
traffic flow between facilities, each assigned to a location, is to be minimized.
LemonDrop treats services within an application as facilities and the VMs themselves as the locations. 

Within the context of Jasper, lemons have the potential to drastically affect the overall system's performance.
Inspired by LemonDrop's VM selection method, this work here aims to develop a simpler heuristic that 
can achieve reasonably good results adapted to the smaller problem set of a multicast tree. 
Therefore, significant improvements could be brought to Jasper's deployment and performance as a 
cloud tenant solution for financial exchanges in the cloud.

- [Project Kickoff](https://docs.google.com/presentation/d/1XlgH70a5laUlEAKua7f3ALofkX98AMYdCSO5etTrlyw/edit?usp=sharing) 
- [Project Proposal](docs/assets/Kickoff.pdf)
- [Project Wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki)

## 1. Setup

1. Clone the repo
   ```bash
   git clone --recursive https://github.com/duclos-cavalcanti/msc-thesis.git
    # recursive flag needed to include submodule
   ```

## 2. Dependencies
All are based on a [Ubuntu 22.04 Jammy machine](https://releases.ubuntu.com/jammy/).

1. Build Tools
   ```bash
    sudo apt install meson cmake ninja build-essential git pkg-config
    sudo apt install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen
    sudo apt-get install linux-image-$(uname -r) -yq
    sudo apt-get install linux-headers-$(uname -r) -yq
    pip install pyelftools meson
   ```

2. Network Tools
   ```bash
   sudo apt install ethtool net-tools inetutils-traceroute tcpdump
   ```

More on further setup, please see [the wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki/Setup).

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
