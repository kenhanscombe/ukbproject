package_list <- c("disk.frame", "optparse")
package_install <- package_list[!(package_list %in% installed.packages()[,"Package"])]
if(length(package_install)) {
    install.packages(package_install, repos='http://cran.us.r-project.org')
}

suppressPackageStartupMessages(suppressWarnings(library(tidyverse)))
suppressPackageStartupMessages(suppressWarnings(library(disk.frame)))
suppressPackageStartupMessages(suppressWarnings(library(optparse)))

# Set up disk.frame with multiple workers and allow unlimited amount of
# data to be passed from worker to worker
setup_disk.frame()
options(future.globals.maxSize = Inf)

option_list = list(
    make_option(c("-p", "--prj-dir"), action = "store", type = "character",
                default = NA, help = "Path to the project directory.")
)

opt <- parse_args(OptionParser(option_list = option_list),
                  positional_arguments = TRUE,
                  convert_hyphens_to_underscores = TRUE)

# Note. opt is a list of 2: opt$options, a list of named options; and
# opt$args, a character vector of positional arguments (the individual
# records). See print(str(opt))

raw_dir <- file.path(opt$options$prj_dir, "raw")
rec_dir <- file.path(opt$options$prj_dir, "records")
rec_paths <- map_chr(opt$args, ~file.path(raw_dir, .))
diskf_paths <- str_replace(rec_paths, "txt", "df") %>%
    str_replace("raw", "records")

pwalk(list(infile = rec_paths, outdir = diskf_paths),
      csv_to_disk.frame, backend = "data.table")
