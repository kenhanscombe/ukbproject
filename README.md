ukbgen
===

[![Travis build status](https://travis-ci.com/kenhanscombe/ukbgen.svg?branch=master)](https://travis-ci.com/github/kenhanscombe/ukbgen)
<!-- [![Codecov test coverage]()] -->

A python module and CLI to generate exclusion lists as input for
qctool v2 `--excl-samples` and plink 1.9/ 2.0 `--remove`. The
exclusions are a combination of withdrawals and samples marked as
'redacted' or 'dropout' in the phenotype column of the project
.fam file.
