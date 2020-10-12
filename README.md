# ukbproject

[![travis-ci](https://travis-ci.com/kenhanscombe/ukbproject.svg?branch=master)](https://travis-ci.com/github/kenhanscombe/ukbproject)
[![codecov](https://codecov.io/gh/kenhanscombe/ukbproject/branch/master/graph/badge.svg)](https://codecov.io/gh/kenhanscombe/ukbproject)

A python CLI to setup a UK Biobank (UKB) project.

**Important: At the moment, because default paths are specific to the
KCL HPC cluster, this CLI is only useful for UKB-approved KCL
reasearchers and their collaborators, with an account on the Rosalind
HPC cluster. This python3 project is in alpha development.**

<span style="color:dodgerblue;">**Contents:**</span>  
1. [Installation](#installation)
2. [Use](#use)  
2.1 [Setup a project directory](#setup)  
2.2 [Download UKB utilities](#download)  
2.3 [Include project data](#include)  
2.4 [Munge the UKB data](#munge)  
2.5 [Add symlinks to sample information and relatedness files](#add)  
3. [Access the data with ukbkings](#access)  
4. [Additional withdrawals](#withdrawals)  
5. [Updates to phenotype data](#updates)

***

<br>

<a name="installation"></a>
## 1. Installation

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

After use (below), exit the environment with `conda deactivate`. To use
the `ukb` CLI on subsequent occasions, simply activate the environment
`conda activate ukb-env`.

<br>

<a name="use"></a>
## 2. Use

For help

```{bash}
ukb --help
```

>**Usage**: ukb [OPTIONS] COMMAND [ARGS]...
>
> Sets up a UKB project on Rosalind storing common data and utilities
> in the parent directory, at resources/ and bin/ respectively.
>
> **Options**:  
> --version  Show the version and exit.  
> --help     Show this message and exit.
>
> **Commands**:  
> clean     Removes defunct file/dir(s) from projects, and sets permissions.  
> create    Creates a skeleton UKB project directory.  
> ...

<br>

Note. usage is similar to `git` with general **options**, and
**commands** that take further **arguments**. For help on commands (e.g.
`ukb create`)

```{bash}
ukb create --help
```

<br>

<a name="setup"></a>
### 2.1 Setup a project directory

At /scratch/datasets/ukbiobank, create a project
directory ukb\<*project_id*\>.

```{bash}
ukb create -p <project_id>
```

This will create the project directory structure in **Figure 1**,
adding symlinks to the genetic in the project genotyped/ and imputed/
folders, and download the required UKB programs and utilites.

<br>

<pre>
ukb&ltproject_id&gt  
├ genotyped  
  ├ ukb_binary_v2.bed  
  └ ukb_binary_v2.bim  
├ imputed  
  ├ ukb_sqc.txt  
  ├ ukb_sqc_fields.txt  
  ├ ukb_imp_chr*.bgen  
  ├ ukb_imp_chr*.bgen.bgi  
  └ ukb_mfi_chr*.txt
├ log  
├ phenotypes  
├ raw  
├ returns  
└ withdrawals
</pre>

**Figure 1** Project directory structure

<br>

<a name="download"></a>
### 2.2 Download UKB utilities

Add UKB file handlers and utilities to the parent directory
/scratch/datasets/ukbiobank folders bin/ and resources/, with
`ukb util`. UKB data encodings (Codings_Showcase.csv, encoding.ukb) are
downloaded to resources/; UKB programs are downloaded to bin/.

<br>

<a name="include"></a>
### 2.3 Include project data

#### 2.3.1 Encrypted phenotype data, keys, withdrawals

Download project-specific encrypted files (\*.enc), associated key
files (\*.key), and withdrawal files
(w\<*project-id*\>_\<*yyyymmdd*\>.csv) must be copied into the project
subdirectory raw/. Change the key file names to match the encrypted
files: ukb\<*project_id*\>.enc pairs with ukb\<*project_id*\>.key. The
first line in each key file should be the project id; the second line
should be the decryption key.

#### 2.3.2 Genetic sample information and relatedness

Add to raw the project-specific key associated with the genetic data
access - rename to ukb<project_id>.key. Download the project-specific
genetic sample information files (.fam and .sample) and relatedness
file (*rel*.dat/.txt) into raw/.

```{bash}
cd /scratch/datasets/ukbiobank/ukb_<project_id>/raw/

/scratch/datasets/ukbiobank/bin/ukbgene cal -c1 -m -aukb<project_id>.key
/scratch/datasets/ukbiobank/bin/ukbgene imp -c1 -m -aukb<project_id>.key
/scratch/datasets/ukbiobank/bin/ukbgene rel -aukb<project_id>.key
```

<br>

<a name="munge"></a>
### 2.4 Munge the UKB data

Process the encrypted UKB files into formats to be read by ukbkings.

```{bash}
ukb munge -p ukb<project_id>
```

The munged phenotype data are written to phenotypes/ and output
information is written to log/, for every <*dataset_id*> (or UKB
basket) (**Figure 2**). For a dry run, in which no files are edited/
written to disk, only details of what would be munged is printed to
standard output, use `ukb munge -p ukb<project_id> -n`.

<br>

<pre>
ukb&ltproject_id&gt  
├ phenotypes  
  ├ ukb&ltdataset_id&gt.csv  
  ├ ukb&ltdataset_id&gt.html  
  └ ukb&ltdataset_id&gt_field_finder.text  
├ log  
  └ ...
</pre>

**Figure 2** Munged phenotype data

<br>

<a name="add"></a>
### 2.5 Add symlinks to sample information and relatedness files

Sample information files (.fam and .sample) and the relatedness file
(*rel*.dat/.txt) should be in raw/. Create symlinks to these project-specific
files in genotyped/ and imputed/ (**Figure 3**).

```{bash}
ukb link \
-p ukb<project_id> \
-f <fam_file_name> \
-s <sample_file_name> \
-r <relatedness_file_name>
```

You can link one or more of these files (they do not all need to be 
passed to the program simultaneously).

<br>

<pre>
ukb&ltproject_id&gt 
├ genotyped
  └ ukb&ltproject_id&gt_cal_chr1_v2_sN.fam 
├ imputed  
  ├ ukb&ltproject_id&gt_imp_chr1_v3_sN.sample  
  └ ukb&ltproject_id&gt_rel_sN.dat
</pre>

**Figure 3** Project-specific sample information and relatedness symlinks.  
N = number of samples with non-negative IDs

<br>

**UKB genetic data resources:**

* [Accessing Genetic Data within UK Biobank](https://biobank.ctsu.ox.ac.uk/crystal/crystal/docs/ukbgene_instruct.html#aut)
* [Resource 531: Description of genetic data types](http://biobank.ndph.ox.ac.uk/showcase/refer.cgi?id=531)
* [Resource 664: Instructions for downloading genetic data using ukbgene](https://biobank.ctsu.ox.ac.uk/crystal/refer.cgi?id=664)
* [Resource 667: UK Biobank Keyfile](http://biobank.ndph.ox.ac.uk/showcase/refer.cgi?id=667)

<br>

<a name="access"></a>
### 3. Access the data with ukbkings

The data should now be available from anywhere on Rosalind through
the [ukbkings](https://kenhanscombe.github.io/ukbkings) R package. Read
[Access UKB data on Rosalind](https://kenhanscombe.github.io/ukbkings/articles/kcl-ukb-access.html)
for a detailed description of usage. The same usage documentation is
included in a package vignette. In R

```{R}
devtools::install_github("kenhanscombe/ukbkings", dependencies = TRUE, force = TRUE)
vignette("Access UKB data on Rosalind")
```

<br>

<a name="withdrawals"></a>
## 4. Additional withdrawals

Each time an updated set of participant withdrawals is received,
replace the w\<*project-id*\>_\<*yyyymmdd*\>.csv file in raw/ with
the new file. To exclude the latest withdrawals you have to generate
your dataset with ukbkings again. Be aware that if any researcher on
your project does run the tool again (to grab some other data say),
this would apply the latest set of withdrawals. 

<br>

<a name="updates"></a>
## 5. Updates to phenotype data

If you receive any new data you would like to incorporate, place the
new .enc and .key files (prepared as described in [Include
project data]) into raw/ and re-run the data munging step
(described in [Munge the UKB data]).
