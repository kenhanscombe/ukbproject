ukbproject
===

[![travis-ci](https://travis-ci.com/kenhanscombe/ukbproject.svg?branch=master)](https://travis-ci.com/github/kenhanscombe/ukbproject)
[![codecov](https://codecov.io/gh/kenhanscombe/ukbproject/branch/master/graph/badge.svg)](https://codecov.io/gh/kenhanscombe/ukbproject)

A python CLI to setup a UK Biobank (UKB) project.

**Important: At the moment, because default paths specific to the KCL HOC cluster, this CLI is only useful for UKB-approved KCL reasearchers and their collaborators, with an account on the Rosalind HPC cluster. This python3 project is in alpha development.**

<br>

## Installation

Clone the github repo

```{bash}
git clone https://github.com/kenhanscombe/ukbproject.git
chmod +x munge.py
```

KCL Rosalind users load the default python3 module

```{bash}
module avail python3
module load <default_python3_module>
```

Create and load the conda environment

```{bash}
conda env create -f environment.yml
conda activate ukb-env
python3 -m pip install --editable .
```

After use (below), exit the environment with `conda deactivate`. To use the `ukb` CLI on subsequent occasions, simply activate the environment `conda activate ukb-env`.

<br>

## Use

For help

```{bash}
ukb --help
```

>**Usage**: ukb [OPTIONS] COMMAND [ARGS]...
>
>  Sets up a UKB project on Rosalind storing common data and utilities in the
>  parent directory, at resources/ and bin/ respectively.
>
>**Options**:  
>  --version  Show the version and exit.  
>  --help     Show this message and exit.
>
>**Commands**:  
>  clean     Removes defunct file/dir(s) from projects, and sets permissions.  
>  create    Creates a skeleton UKB project directory.  
> ...

<br>

Notice usage is similar to `git` with general **options**, and **commands** that take further arguments. For help on commands (e.g. `ukb create`)

```{bash}
ukb create --help
```
