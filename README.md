<h1 align="center">Master Thesis</h1>
<p align="center">
   VM Selection and Scheduling Heuristic for Multicasting on the Cloud
</p>
<br>

<!-- __Abstract:__ _Not defined yet._ -->

_Master Thesis_ work performed at NYU co-advised by [Dr.Anirudh Sivaraman](https://anirudhsk.github.io/) and his team at [Systems@NYU](https://news.cs.nyu.edu/) 
and supervised by the [Chair of Communication Networks](https://www.ce.cit.tum.de/en/lkn/home/) from the School of CIT at [TUM](https://www.cit.tum.de/en/cit/home/). 
This contribution builds upon current research of Dr.Anirudh Sivaraman, lead by [PhD. Muhammad Haseeb](https://haseeblums.github.io/) on
[Jasper: Scalable and Fair Multicast for Financial Exchanges in the Cloud](https://arxiv.org/abs/2402.09527.).

## Introduction

__Jasper__ was made to be a scalable and fair multicast prototype for financial exchanges in the cloud. In the context of High-Frequency Trading (HFT), data regarding the market state has to be disseminated to a large number of market agents at extremely low latencies, as well as done so in an acceptably fair manner. That means, all market agents should be able to perceive an equal market state within any given moment, as well as be notified of changes to said state simultaneously. This ensures a fair and balanced playing field among participants.

There is interest both in academia and in the industry to move the current financial exchange infrastructure to the public cloud. The benefits are clear and among others include better scalability, a more robust infrastructure, flexible resource allocation and potential cost savings. However, a major and understandable concern is the feasibility to implement a fair multicast service for a large number of market participants within acceptable latencies. The public cloud does not currently offer such a service or hardware that supports _multicasting_ for cloud tenants.

Jasper, in a quick summary, employs a tree-like structure of VMS in the cloud, combined with DPDK kernel bypassing and shallow copies of packets to illustrate a competitive prototype of _multicasting_ on the cloud up to 1000 and even 5000 recipients.

The goal of this master thesis would be to build upon the [PhD Thesis from Dr. Vighnesh Sachidananda](https://searchworks.stanford.edu/view/14423035), more specifically on the technique displayed in __Chapter 3, called LemonDrop__. This PhD thesis, on a very high level, addresses the issue of uneven VMS within a cluster. Many times, during deployment or autoscaling of machines on the cloud, there can be VMs that severely underperform even within the same configuration/instance class. These "stragglers" depending on where they are located in the cloud cluster can cause the larger application to suffer greatly in terms of performance/latency. This is specially the case with the Jasper project, where if there are stragglers in initial layers of the tree, this will hugely affect the message propagation.

The idea would be then to adapt __LemonDrop__ to a simpler heuristic that, in the same spirit, from a set of VMS deployed onto a cloud, chooses a subset from it that best facilitates an application's communication patterns. In this case, that application would be Jasper and therefore the heuristic would be mostly focused on choosing the subset based on Jasper's tree-like structure

- [Kickoff](https://docs.google.com/presentation/d/1XlgH70a5laUlEAKua7f3ALofkX98AMYdCSO5etTrlyw/edit?usp=sharing)

Check out the [_wiki_](https://github.com/duclos-cavalcanti/master-arbeit/wiki) for more!

## 1. Setup

1. Clone the repo
   ```bash
   git clone --recursive https://github.com/duclos-cavalcanti/msc-thesis.git
    # recursive flag needed to include submodule
   ```

## 2. Dependencies
All are based on a [Ubuntu 22.04 Jammy machine](https://releases.ubuntu.com/jammy/).

### Build Tools
   ```bash
    sudo apt install meson cmake ninja build-essential git pkg-config
    sudo apt install libprotobuf-c-dev libprotobuf-dev protobuf-compiler protobuf-codegen
    sudo apt-get install linux-image-$(uname -r) -yq
    sudo apt-get install linux-headers-$(uname -r) -yq
    pip install pyelftools meson
   ```

### Network Tools
   ```bash
   sudo apt install ethtool net-tools inetutils-traceroute tcpdump
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
gcloud init                         # iniit gcloud on system
gcloud auth login                   # login into google cloud account used for cloud development
gcloud config set project <VALUE>   # set project name, here it's multicast1
```

3. Optional
```bash 
gcloud components install gsutil
```

### AWS
```bash
echo "UNTESTED YET"
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
