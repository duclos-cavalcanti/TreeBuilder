<h1 align="center">TreeFinder</h1>
<p align="center">
   M.Sc. Thesis - VM Selection Heuristic for Financial Exchanges in the Cloud
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
- [Project Documentation](https://drive.google.com/file/d/1DzhmxgvQ93I39EnXY3HDdw66yohh432I/view?usp=sharing)
- [SIGCOMM24 POSTER - Jasper, A Scalable and Fair Multicast for Fin. Exch. in the Cloud](https://sigcomm24posterdemo.hotcrp.com/paper/47?cap=hcav47KhCcppMuxCoAApCEhcdjiFGC)


```bash
git clone --recursive https://github.com/duclos-cavalcanti/master-arbeit.git
```

## Setup and Installation
The general project worflow consists of three parts:
1. Creation and Deployment of images on a given cloud provider _(or locally via dockers)_,
2. Managing Instances _(deployed images)_  
3. Running individual programs on any given instance.

<table div align="center">
<tr> <th>Category</th> <th>Tool(s)</th> </tr>

<tr>
    <td>
        Build
    <td> 
        <a href="https://cmake.org/">
        CMake
        </a>,
        <a href="https://mesonbuild.com/">
        Meson
        </a>,
        <a href="https://gitlab.freedesktop.org/pkg-config/pkg-config">
        Pkg-Config
        </a>
    </td> 
</tr>
<tr>
    <td>
        Containers / Virtualization
    <td> 
        <a href="https://docs.docker.com/engine/install/ubuntu/">
        Docker
        </a>,
        <a href="https://developer.hashicorp.com/packer/docs?ajs_aid=402f72bb-ce20-40b3-8bcb-ef538f141337&product_intent=packer">
        Packer
        </a>,
        <a href="https://developer.hashicorp.com/vagrant/install">
        Vagrant
        </a>,
        <a href="https://www.virtualbox.org/">
        VirtualBox
        </a>
    </td> 
</tr>
<tr>
    <td>
        Cloud
    <td> 
        <a href="https://developer.hashicorp.com/terraform/docs">
        Terraform
        </a>,
        <a href="https://cloud.google.com/">
        GCP
        </a>,
        <a href="https://aws.amazon.com/">
        AWS
        </a>
    </td> 
</tr>
<tr>
    <td>
        Libraries
    <td> 
        <a href="https://www.dpdk.org/">
        DPDK
        </a>,
        <a href="https://zeromq.org/">
        ZeroMQ
        </a>,
        <a href="https://protobuf.dev/">
        Protobufs
        </a>
    </td> 
</tr>
<tr>
    <td>
        Python
    <td> 
        <a href="https://www.dpdk.org/">
        pyzmq
        </a>,
        <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html">
        boto3
        </a>
    </td> 
</tr>

</table> 

See _[Setup](https://github.com/duclos-cavalcanti/master-arbeit/wiki/Setup)_ on the wiki.

##  Usage
See _[Getting Started](https://github.com/duclos-cavalcanti/master-arbeit/wiki/Getting-Started)_ on the wiki.

## License
This project is released under the BSD 3-Clause license. See [LICENSE](LICENSE).

## References
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
