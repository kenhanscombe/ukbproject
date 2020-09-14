ukbgen
===

[![travis-ci](https://travis-ci.com/kenhanscombe/ukbgen.svg?branch=master)](https://travis-ci.com/github/kenhanscombe/ukbgen)
[![codecov](https://codecov.io/gh/kenhanscombe/ukbgen/branch/master/graph/badge.svg)](https://codecov.io/gh/kenhanscombe/ukbgen)

A python module and CLI to generate exclusion lists as input for
qctool v2 `--excl-samples` and plink 1.9/ 2.0 `--remove`. The
exclusions are a combination of withdrawals and samples marked as
'redacted' or 'dropout' in the phenotype column of the project
.fam file.

**Note**. This python3 project is in alpha development. KCL Rosalind users load the default python3 module (`module avail python3`).

## Installation

Clone the github repo

```
git clone https://github.com/kenhanscombe/ukbgen.git
```

## Use

For help

```
python ukbexclude.py --help
```

To create exclusion files for genotyped and imputed data

```
python ukexclude.py \
--project <project_id> \
--withdraw <withdrawal_file> \
--fam <fam_file> \
--sample <sample_file> \
--out-dir <output_directory>
```
