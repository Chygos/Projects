## R code obtains GPL data (annotated or not) of given platform ID for

############# Title #####################

## each Geo ID and Writes to a file

library(GEOquery)
library(stringr)



# load series and platform data from GEO
# "GPL10558", "GPL21572", "GPL17692"
fetch_gene_ids <- function(gpl_id, probe_ids) {
  gpl <- getGEO(GEO = gpl_id, AnnotGPL = TRUE)

  # extract data tables
  gpl_data <- Table(gpl)
  # get gene info of probe IDs
  gene_info <- gpl_data[gpl_data$ID %in% probe_ids, ]
  return(gene_info)
}

files <- list.files(path = "./microarray",
                    pattern = "*exprs*.csv",
                    full.names = TRUE)


# GPL IDs for the datasets
gpls <- read.csv("microarray_gpl_ids.csv")

gpl_ids <- gpls$GPL_ID
gpl_files <- gpls$file


for (i in seq(1, length(gpl_ids))) {
  # get file, GPL_ID and file basename
  gpl_file <- gpl_files[i]
  gpl_id <- gpl_ids[i]
  file <- files[grepl(gpl_file, files)]

  file_id <- stringr::str_extract(basename(gpl_file), "^GSE\\d+")

  # check if file containing gene id names exisits
  gene_id_name <- paste0(file_id, "_", gpl_id, "_gene_ids.csv")
  if (!file.exists(gene_id_name)) {
    # read file and fetch gene IDs of illumina probeset IDs
    df <- read.csv(file)
    illumina_ids <- as.vector(df[, 1])
    gene_ids <- fetch_gene_ids(gpl_id, illumina_ids)
    write.csv(gene_ids,
              paste0(file_id, "_", gpl_id, "_gene_ids.csv"),
              row.names = FALSE)
  }
}