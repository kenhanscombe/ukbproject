package_list <- c("disk.frame", "optparse")
package_install <- package_list[!(package_list %in% installed.packages()[,"Package"])]
if(length(package_install)) {
    install.packages(package_install, repos='http://cran.us.r-project.org')
}

suppressPackageStartupMessages(suppressWarnings(library(tidyverse)))
suppressPackageStartupMessages(suppressWarnings(library(disk.frame)))
suppressPackageStartupMessages(suppressWarnings(library(optparse)))

# args <- commandArgs(trailingOnly = TRUE)
# prj_dir <- args[1]

option_list = list(
    make_option(c("-p", "--prj-dir"), action = "store", default = NA,
                type = "character",
                help = "Path to the project directory."),
    make_option(c("-r", "--raw-dir"), action = "store", default = NA,
                type = "character",
                help = "Path to the project raw directory.")
)

opt <- parse_args(OptionParser(option_list = option_list))

# records <- list.files(opt$raw_dir)
print(file.path(opt$raw_dir))
