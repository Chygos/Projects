
## Load libraries
suppressMessages(library(tidyverse))
suppressMessages(library(limma))
suppressMessages(library(tidyheatmaps))
suppressMessages(library(enrichR))
suppressMessages(library(clusterProfiler))
suppressMessages(library(rbioapi))
suppressMessages(library(wordcloud2))
suppressMessages(library(igraph))
suppressMessages(library(ggVennDiagram))


## load datasets
expr_data <- read.csv('glioma_cancer_exprs.csv', row.names = 1)
metadata <- read.csv('glioma_cancer_metadata.csv')

head(expr_data[, 1:5])
head(metadata)


## Data Cleaning

# Adding new features to our metadata
metadata <- metadata |>
  mutate(across(-sample_id, \(x) factor(x)),
         is_tumour = factor(ifelse(tumor_grade == 'Normal', 'Normal', 'Tumor'), 
                            labels = c('Normal', 'Tumor')),
         cell_type = str_replace(tumor_class, 
                                 'glioblastoma|astrocytoma|oligoastrocytoma', 
                                 'astrocyte'),
         cell_type = str_replace(
           cell_type, 'olig.+glioma$', 'oligodendrocyte') |> as.factor())



table(metadata$is_tumour)
table(metadata$cell_type)


## function that plots a volcano plot
plot_volcano <- function(model.fit, lfc_cutoff=2, p.value=0.05,
                         coef.pos=NULL, title='Volcano plot'){
  res <- topTable(model.fit, n=Inf, coef = coef.pos)
  res <- res |>
    mutate(status = ifelse(logFC > lfc_cutoff & adj.P.Val < p.value, 'Up', 
                           ifelse(logFC < -lfc_cutoff & adj.P.Val < p.value, 'Down', 
                                  'NS')) |> factor(levels=c('NS','Down','Up'))) |>
    mutate(genes = rownames(res))
  
  fig <- res |>
    ggplot(aes(logFC, -log10(adj.P.Val), color=status)) + 
    geom_point(alpha=0.7) +
    geom_vline(xintercept = c(-lfc_cutoff, lfc_cutoff), linetype='dashed') +
    geom_hline(yintercept = -log10(p.value), linetype='dashed') +
    theme_bw() +
    theme(legend.position = 'top', 
          legend.key = element_blank(),
          panel.grid = element_blank(),
          legend.title = element_text(face='bold', size=10),
          plot.title = element_text(face='bold')) +
    labs(title=title, x='Log2 Fold change', y='Log 10 pvalue', 
         color='Regulation') +
    scale_color_manual(values=c('#2C2D2D', 'forestgreen', 'indianred'))
  
  top_up <- res |> filter(status == 'Up') |> slice_min(adj.P.Val, n=5)
  top_down <- res |> filter(status == 'Down') |> slice_min(adj.P.Val, n=5)
  
  fig +
    ggrepel::geom_text_repel(data = top_up, mapping=aes(logFC, -log10(adj.P.Val), 
                                                        label=genes), 
              size=3, color='#231F20', fontface='bold',
              arrow = arrow(length = unit(0.02, "npc")), box.padding = 1) +
    ggrepel::geom_text_repel(data=top_down, mapping=aes(logFC, -log10(adj.P.Val), 
                                                        label=genes), 
              size=3, color='#231F20', fontface='bold',
              arrow = arrow(length = unit(0.02, "npc")), box.padding = 1)
}


## Differential gene expression analysis


## Normal vs tumour

# design matrix for Limma
design <- model.matrix(~0 + metadata$is_tumour)
colnames(design) <- c('Normal', 'Tumour')

# instantiate a contrast matrix
const.matrix <- makeContrasts(NormalvsCancer = Tumour-Normal, 
                              levels = colnames(design))


# fit model on defined contrasts 
model_fit <- lmFit(expr_data, design)
model_fit <- contrasts.fit(model_fit, const.matrix)
ebfit <- eBayes(model_fit)


# number of differential genes at |lfc| > 2
summary(decideTests(ebfit, lfc=2))


# differentially expressed genes by LFC of 2
normal_vs_tumour_DED <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, p.value=0.05)
head(normal_vs_tumour_DED)


## save file
topTable(ebfit, n=Inf, p.value = 0.05) |>
  write.csv('normal_vs_cancer_DGE_result.csv', row.names = T)


plot_volcano(ebfit, title='Normal vs Tumour tissues')


## Tumour grades

astrocytes <- which(metadata$cell_type == 'astrocyte')


## design matrix
design <- model.matrix(~ 0 + factor(metadata[astrocytes, 'tumor_grade']))
colnames(design) <- str_extract(colnames(design), 'G[0-9]$')


# instantiate a contrast matrix
const.matrix <- makeContrasts(G1vsG2 = G2-G1,
                              G2vsG3 = G3-G2,
                              G3vsG4 = G4-G3,
                              levels = design)

model_fit <- lmFit(expr_data[, astrocytes], design)
model_fit <- contrasts.fit(model_fit, const.matrix)

ebfit <- eBayes(model_fit)

# number of differential genes at |lfc| > 2
summary(decideTests(ebfit, lfc=1.5))

# differentially expressed genes by LFC of 2

G1_vs_G2 <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=1.5, 
                     p.value=0.05, coef='G1vsG2')

G2_vs_G3 <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=1.5, 
                     p.value=0.05, coef='G2vsG3')

G3_vs_G4 <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=1.5, 
                     p.value=0.05, coef='G3vsG4')

plot_volcano(ebfit, title='Differential Genes in Grade1 vs Grade2', coef='G1vsG2')

plot_volcano(ebfit, title='Differential Genes in Grade2 vs Grade3', 
             coef='G2vsG3',lfc_cutoff = 1)

plot_volcano(ebfit, title='Differential Genes in Grade3 vs Grade4', 
             coef='G3vsG4', lfc_cutoff = 1)

# save result into file
#for (i in colnames(const.matrix)){
#  topTable(ebfit, coef=i, p.value = 0.05, n=Inf) |>
#  write.csv(paste0(i, '_DGE_result.csv'), row.names = T)  
#}


# getting differential gene in all grades

sig.genes <- list(G1_vs_G2, G2_vs_G3, G3_vs_G4) |>
  map(.f = function(x) filter(x, adj.P.Val < 0.05, abs(logFC) > 1) |> 
        rownames_to_column(var='gene') |>
        pull(gene))


genes <- rownames(expr_data) 
similar.genes = genes
for (i in 1:length(sig.genes)) similar.genes <- intersect(similar.genes, sig.genes[[i]])

print(similar.genes)


names(sig.genes) <- c('G1-G2', 'G2-G3', 'G3-G4')


## Draw common genes
ggVennDiagram::ggVennDiagram(sig.genes, label_alpha = 0, set_color = 'dimgray',
                             set_size = 3.8,label = 'count', label_size = 3.4) +
  ggplot2::scale_fill_gradient(low='#fcfcfc', high='indianred') +
  theme_minimal() +
  theme(axis.title = element_blank(), 
        axis.text = element_blank(),
        plot.title = element_text(face='bold', size=12),
        legend.position = 'none',
        panel.grid = element_blank()) +
  labs(title='Number of common genes by Tumour grades')


## Common gene CHI3L1

expr_data[similar.genes, ] |>
  rownames_to_column('gene') |>
  pivot_longer(-gene, names_to = 'sample', values_to = 'expr_level') |>
  inner_join(metadata[, c('sample_id', 'tumor_grade', 'cell_type')], 
             by=c('sample' = 'sample_id')) |>
  dplyr::filter(cell_type %in% 'astrocyte') |>
  ggplot(aes(tumor_grade, expr_level, fill=tumor_grade)) +
  geom_boxplot() +
  theme_light() +
  theme(legend.position = 'none', 
        plot.title = element_text(face='bold', size=12),
        panel.grid.major.x = element_blank()) +
  labs(title='Expression Levels of CHI3L1 gene in astrocytoma tumour grades', 
       y='Expression levels', x='\nTumor Grade')


### C. Cell types
cell_types <- which(!metadata$cell_type %in% c('normal', 'high grade glioma'))

## design matrix
design <- model.matrix(~ 0 + factor(metadata[cell_types, 'cell_type']))
colnames(design) <- c('AC', 'EC', 'MGC', 'OGC')
  
# AC -> Astrocytoma
# EC -> Ependymoma
# MG -> mixed glioma
# OGC -> oligodendrocytoma/oligodendroglioma

# instantiate a contrast matrix
const.matrix <- makeContrasts(ACvsEC = AC-EC,
                              ACvsMGC = AC-MGC,
                              ACvsOGC = AC-OGC,
                              ECvsMGC = EC-MGC,
                              ECvsOGC = EC-OGC,
                              MGCvsOGC = MGC-OGC,
                              levels = design)

model_fit <- lmFit(expr_data[, cell_types], design)
model_fit <- contrasts.fit(model_fit, const.matrix)


ebfit <- eBayes(model_fit)


# number of differential genes at |lfc| > 2
summary(decideTests(ebfit, lfc=2))


# differentially expressed genes by LFC of 2

AC_vs_EC <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, 
                     p.value=0.05, coef='ACvsEC')

AC_vs_MGC <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, 
                     p.value=0.05, coef='ACvsMGC')

AC_vs_OGC <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, 
                     p.value=0.05, coef='ACvsOGC')

EC_vs_MGC <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, 
                     p.value=0.05, coef='ECvsMGC')

EC_vs_OGC <- topTable(ebfit, sort.by = 'P', n=Inf, lfc=2, 
                     p.value=0.05, coef='ECvsOGC')


plot_volcano(ebfit, title='Differential Genes in Astrocytoma vs Ependymoma', 
             coef=1, lfc_cutoff = 2)

plot_volcano(ebfit, title='Differential Genes in Astrocytoma vs Mixed Gliomas', 
             coef=2, lfc_cutoff = 2)

plot_volcano(ebfit, title='Differential Genes in Astrocytoma vs Oligodendroglioma', 
             coef=3, lfc_cutoff = 2)

plot_volcano(ebfit, title='Differential Genes in Ependymoma vs Mixed glioma', 
             coef=4, lfc_cutoff = 2)

plot_volcano(ebfit, title='Differential Genes in Ependymoma vs Oligodendroglioma', 
             coef=5, lfc_cutoff = 2)


# save result into file
#for (i in colnames(const.matrix)){
#  topTable(ebfit, coef=i, p.value = 0.05, n=Inf) |>
#  write.csv(paste0(i, '_DGE_result.csv'), row.names = T)  
#}


# getting differential gene in all grades

sig.genes <- list(AC_vs_EC, AC_vs_MGC, AC_vs_OGC,
                  EC_vs_OGC, EC_vs_MGC) |>
  map(.f = function(x) filter(x, adj.P.Val < 0.05, abs(logFC) > 1.5) |> 
        rownames_to_column(var='gene') |>
        pull(gene))


similar.genes = genes
for (i in 1:length(sig.genes)) similar.genes <- intersect(similar.genes, sig.genes[[i]])

print(similar.genes)


names(sig.genes) <- c('AC-EC', 'AC-MGC', 'AC-OGC', 'EC-OGC', 'EC-MGC')

ggVennDiagram::ggVennDiagram(sig.genes, label_alpha = 0, set_color = 'dimgray',
                             set_size = 3.4,label = 'count', label_size = 3.4) +
  ggplot2::scale_fill_gradient(low='#fcfcfc', high='indianred') +
  theme_minimal() +
  theme(axis.title = element_blank(), 
        axis.text = element_blank(),
        plot.title = element_text(face='bold', size=12),
        legend.position = 'none',
        panel.grid = element_blank()) +
  labs(title='Number of common genes by cancer cell types')


## ----fig.height=6, fig.width=10, fig.cap='Expression levels of common genes implicated in all glial-cell type cancers'------------
expr_data[similar.genes, ] |>
  rownames_to_column('gene') |>
  pivot_longer(-gene, names_to = 'sample', values_to = 'expr_level') |>
  inner_join(metadata[, c('sample_id', 'cell_type')], 
             by=c('sample' = 'sample_id')) |>
  dplyr::filter(!cell_type %in% c('normal', 'high grade glioma')) |>
  ggplot(aes(cell_type, expr_level, fill=cell_type)) +
  geom_boxplot() +
  facet_wrap(~gene, nrow = 3) +
  theme_light() +
  theme(legend.position = 'none', 
        plot.title = element_text(face='bold'),
        panel.grid.major.x = element_blank(),
        strip.background = element_rect(fill='#454545'),
        strip.text = element_text(face = 'bold', color='white')) +
  scale_x_discrete(labels=c('AST', 'EP', 'MG', 'OGC')) +
  labs(title='Expression Levels of common genes in all glioma cell types', 
       y='Expression levels', x='\nCell cancer type')


## Functional Enrichment Analysis
# databases
dbs <- enrichR::listEnrichrDbs()

# head(dbs)

# dbs$libraryName[grep('(^GO|KEGG|Reac|Wiki)', dbs$libraryName)]


# get libraries for GO and pathways
db_GO <- dbs[grepl('^GO', dbs$libraryName), 3]
db_pw <- dbs[grepl('^KEGG_\\d+_Human|^Reactome', dbs$libraryName), 3]


## function to get functional enrichment
get_FEA <- function(genes.list, selected_database){
  res <- enrichR::enrichr(genes.list, selected_database)
  res <- res |> 
    map(function(x) x |> 
          dplyr::filter(Adjusted.P.value < 0.05) |> 
    mutate(Term=str_remove_all(Term, '\\(GO:.+\\)$|R-HSA-\\d+$|'))
  )
  
  return(res)
}


## Gene Ontology
# GO for normal vs tumour samples
GO_results_nt_up <- get_FEA(row.names(
  normal_vs_tumour_DED |> 
    filter(logFC > 2)), selected_database = db_GO)


# GO for normal vs tumour samples
GO_results_nt_down <- get_FEA(row.names(
  normal_vs_tumour_DED |> 
    filter(logFC < -2)), selected_database = db_GO)


## ----fig.cap='Biological processes for upregulated genes in tumour conditions'----------------------------------------------------
plotEnrich(GO_results_nt_up$GO_Biological_Process_2023, numChar = 70) +
  theme_bw() +
  theme(panel.grid = element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Biological Process (Normal vs Tumour)', x='')


## ----fig.cap='Biological processes for downregulated genes in tumour conditions'--------------------------------------------------
plotEnrich(GO_results_nt_down$GO_Biological_Process_2023, numChar = 70) +
  theme_bw() +
  theme(panel.grid = element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=11)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Biological Process for Down (Normal vs Tumour)', x='')


## ----fig.cap='Cellular compartment for upregulated genes in tumour conditions'----------------------------------------------------
plotEnrich(GO_results_nt_up$GO_Cellular_Component_2023, numChar = 70) +
  theme_minimal() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Cellular Component (Normal vs Tumour)', x='')


## ----fig.cap='Cellular compartments for downregulated genes in tumour conditions'-------------------------------------------------
plotEnrich(GO_results_nt_down$GO_Cellular_Component_2023, numChar = 60) +
  theme_bw() +
  theme(panel.grid = element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=11)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Cellular Component for Down (Normal vs Tumour)', x='')


## ----fig.height=3.5, fig.width=7, fig.cap='Molecular function for upregulated genes in tumour conditions'-------------------------
plotEnrich(GO_results_nt_up$GO_Molecular_Function_2023, numChar = 70) +
  theme_minimal() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Molecular Function (Normal vs Tumour)', x='')


## ----fig.height=3.5, fig.width=7, fig.cap='Molecular function for downregulated genes in tumour conditions'-----------------------
plotEnrich(GO_results_nt_down$GO_Molecular_Function_2023, 
           numChar = 70, showTerms = 4) +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Molecular Function Down (Normal vs Tumour)', x='')


## Pathway Analysis
# Pathway for normal vs tumour samples
PW_results_nt_up <- get_FEA(row.names(
  normal_vs_tumour_DED |> 
    filter(logFC > 2)), selected_database = db_pw)

PW_results_nt_down <- get_FEA(row.names(
  normal_vs_tumour_DED |> 
    filter(logFC < -2)), selected_database = db_pw)


## ----fig.cap='KEGG pathway for upregulated genes in tumour conditions'------------------------------------------------------------
plotEnrich(PW_results_nt_up$KEGG_2021_Human, 
           numChar = 70) +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='KEGG Pathway Up (Normal vs Tumour)', x='')


## ----fig.cap='KEGG pathway for downregulated genes in tumour conditions'----------------------------------------------------------
plotEnrich(PW_results_nt_down$KEGG_2021_Human, 
           numChar = 70) +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='KEGG Pathway Down (Normal vs Tumour)', x='')


## ----fig.cap='Biological processes for CHI3L1 common gene in tumour grades of astrocytoma'----------------------------------------
res <- get_FEA("CHI3L1", db_GO)

plotEnrich(res$GO_Biological_Process_2023, y = 'Ratio') +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Biological Processes', x='')

res$GO_Molecular_Function_2023 |> 
  dplyr::select(-5,-6) |>
  kableExtra::kable(caption = 'Molecular function for CHI3L1 gene')

res$GO_Cellular_Component_2023 |> 
  dplyr::select(-5,-6) |> 
  kableExtra::kable(caption = 'Cellular compartment for CHI3L1 gene')


## ---------------------------------------------------------------------------------------------------------------------------------
similar.genes.celltype <- c("C9orf24", "CITED1", "CNR1", "CRLF1", "DACH1", 
                            "EFCAB1", "GABRG1", "LRP2BP", "MKX", "PPP1R1B", 
                            "RELN", "RSPH1", "SPAG6", "SRPX", "VIPR2") 


# Pathway for normal vs tumour samples
GO_results <- get_FEA(similar.genes.celltype, selected_database = db_GO)

PW_results <- get_FEA(similar.genes.celltype, selected_database = db_pw)

plotEnrich(GO_results$GO_Biological_Process_2017, y = 'Ratio') +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Biological processes for common genes in glioma cells', x='')


plotEnrich(GO_results$GO_Molecular_Function_2023, y = 'Ratio') +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_fill_gradient(low='indianred', high='steelblue', 
                      guide = guide_colorbar(reverse = T)) +
  labs(title='Molecular function for common genes in glioma cells', x='')



GO_results$GO_Cellular_Component_2018 |>
  dplyr::select(-5,-6) |>
  kableExtra::kable(caption = 'Cell compartment for common genes in glioma cells')


PW_results$KEGG_2021_Human |>
  dplyr::select(-5,-6) |>
  kableExtra::kable(caption = 'KEGG pathway for common genes in glioma cells')


## Protein-protein Interactions (PPI)
sig.genes <- rownames(normal_vs_tumour_DED)

# get mapped gene ids
mapped_proteins <- rba_string_map_ids(sig.genes, species = 9606)$stringId

gene_ppi <- rba_string_interactions_network(mapped_proteins, 
                                            species=9606)


# visualise
# get number of interactions for each gene
n_gene_interactions <- graph_from_data_frame(gene_ppi) |>
  degree() |>
  sort(decreasing=T) |>
  data.frame() |>
  set_names('n_degrees') |>
  rownames_to_column('geneID') |>
  inner_join(distinct(gene_ppi[, c(1,3)]), by=c('geneID' = 'stringId_A'))

n_gene_interactions |>
  ggplot(aes(n_degrees)) +
  geom_histogram(fill='steelblue', color='white', bins=50) +
  theme_bw() +
  theme(panel.grid=element_blank(), 
        axis.text = element_text(size=8),
        axis.title.x = element_text(size=8),
        legend.title = element_text(size=9),
        plot.title=element_text(face='bold', size=12)) +
  scale_x_continuous(breaks=seq(0,120,10)) +
  labs(title='Number of protein-protein interactions of significant genes')


wordcloud::wordcloud(n_gene_interactions$preferredName_A, 
                     n_gene_interactions$n_degrees,
                     min.freq = 10, 
                     scale = c(1.5,.52), 
                     random.order = F,
                     colors='darkgreen'
                     )


## Clustering
t <- expr_data[rownames(normal_vs_tumour_DED |> filter(logFC < -2)), ] |>
  rownames_to_column(var='Gene') |>
  pivot_longer(-Gene, names_to = 'samples') |>
  inner_join(metadata, by=c('samples' = 'sample_id')) |>
  arrange(tumor_type, tumor_grade)


## create heatmaps

# downregulated genes
tidyheatmaps::tidy_heatmap(t, rows = 'Gene', width = 8,
                           colors = c("#145afc","#ffffff","#ee4445"),
                           height = 20, columns='samples', 
                           annotation_col = c('tumor_type', 'tumor_grade'),
                           values='value',show_colnames = F, show_rownames = F,
                           #filename='downregulated_genes_cluster_heatmap.png',
                           #gaps_row ='tumor_type',
                           fontsize_row = 5, main = 'Downregulated genes',
                           scale='row', cluster_rows = TRUE, cluster_cols = T)


## upregulated
t <- expr_data[rownames(normal_vs_tumour_DED |> filter(logFC > 2.)), ] |>
  rownames_to_column(var='Gene') |>
  pivot_longer(-Gene, names_to = 'samples') |>
  inner_join(metadata, by=c('samples' = 'sample_id')) |>
  arrange(tumor_grade)

select_genes <- (t |> distinct(Gene) |> pull(Gene))

tidyheatmaps::tidy_heatmap(t, rows = 'Gene', width = 8,
                           colors = c("#145afc","#ffffff","#ee4445"),
                           height = 15, columns='samples', 
                           annotation_col = c('tumor_grade', 'tumor_type'),
                           #filename='upregulated_genes_cluster_heatmap.png',
                           values='value',show_colnames = F, show_rownames = F,
                           #show_selected_col_labels = metadata$sample_id[seq(1,500,50)],
                           #show_selected_row_labels = select_genes[seq(1, length(select_genes), 20)],
                           fontsize_row = 5, main = 'Upregulated genes',
                           scale='row', cluster_rows = T, cluster_cols = T)


# Find optimal clusters
expr_data_t <- t(expr_data)
opt_clust <- factoextra::fviz_nbclust(scale(expr_data_t), kmeans, 'wss')
opt_clust

km <- kmeans(scale(t(expr_data)), centers = 4)


##
factoextra::fviz_cluster(km, expr_data_t, labelsize = 0)