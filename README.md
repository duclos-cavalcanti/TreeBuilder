<h1 align="center">Master Thesis</h1>
<p align="center">
   VM Selection Heuristic for Financial Exchanges in the Cloud
</p>
<br>

<!-- __Abstract:__ _Not defined yet._ -->

_Master Thesis_ work co-advised by: 
- [PhD. Muhammad Haseeeb](https://haseeblums.github.io/) and [Dr.Anirudh Sivaraman](https://anirudhsk.github.io/) from [Systems@NYU](https://news.cs.nyu.edu/).
- [PhD. Navidreza Asadi](https://nrasadi.github.io/) and [Prof. Dr.-Ing. Wolfgang Kellerer](https://www.ce.cit.tum.de/en/lkn/team/staff/kellerer-wolfgang/) from  the [LKN](https://www.ce.cit.tum.de/en/lkn/home/) at TUM.

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
- [Project Wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki/)

## 1. Setup and Installation
The general project worflow consists of three parts. The creation and deployment of images on a given cloud provider _(or locally)_,
managing these running images _(instances)_, and finally individual programs that are to be run on any given instance.
To be able to create/deploy/manage images on a given cloud provider, we use [Terraform](https://developer.hashicorp.com/terraform). Currently 
the project is mostly focused on [Google Cloud's Platform](https://cloud.google.com/?hl=en) and optionally [Dockers](https://docs.docker.com/engine/install/ubuntu/)
for local development. To communicate across nodes on a cluster, this work also leverages [ZeroMQ](https://zeromq.org/) both via _python_ and _c++_ bindings.

1. Clone project.
   ```bash
   git clone --recursive https://github.com/duclos-cavalcanti/master-arbeit.git
    # recursive flag needed to include submodule
   ```

2. Install Dependencies. 
    - _Currently based on [Ubuntu 22.04 Jammy](https://releases.ubuntu.com/jammy/)_
    - See _[wiki](https://github.com/duclos-cavalcanti/master-arbeit/wiki/Setup)_ for detailed setup.

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
- [Jasper](https://arxiv.org/abs/2402.09527)
- [CloudEx](https://dl.acm.org/doi/10.1145/3458336.3465278)
- [LemonDrop](https://searchworks.stanford.edu/view/14423035)

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
