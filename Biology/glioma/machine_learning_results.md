# Machine Learning Results
Machine learning modelling was performed to predict disease outcomes. Predictions were made to detect __normal and cancer samples__ and distinguish between __cancer grades__ and __cancer cell types__. Two models, Lasso Logistic Regression and Random Forest, were used.

## Data Preprocessing and Feature Selection
Standardisation was applied to datasets used for Lasso logistic regression. Differential genes (adjusted p-value < 0.05) were selected for modelling. Further feature selection is done by exploiting the inherent feature selection capability in the prediction model. For instance, for LASSO logistic regression, genes with non-zero coefficients were selected while for random forest, selection was done recursively by dropping features with zero importance scores until non-zero scores were obtained for all features.

## Model development and evaluation
The gene expression dataset was split into train and test sets (75/25), where the training set was used to develop a model and the test set was used to evaluate their performance. Performance was evaluated based on six metrics: accuracy, recall, precision, F1, Area under the receiver's operating characteristics (AUROC), and specificity. The precision-recall curve (PRC), AUROC curve, and confusion matrix were used to visualise model performance. In addition, to select optimal features, a hyperparameter tuning technique (5-cross validation) was applied and the optimal parameter set with the highest AUROC score was selected as the best model to fit the train data and predict the test data.

## Results
### Normal vs Cancer

__Table 1: Model performance evaluation on test data__

Model               |Accuracy |AUC     |Recall   |Precision |F1      |Specificity
--------------------|---------|--------|---------|----------|--------|-----------
Logistic Regression |0.980583 |0.998168|0.983516 |0.994444  |0.98895 | 0.958333
Random Forest       |0.995146 |0.999542|1.0      |0.994536  |0.99726 | 0.958333

![lr_perf](imgs/ml_imgs/lr_perf_chart.png)

___Figure 1: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Logistic Regression___


![rf_perf](imgs/ml_imgs/rf_perf_chart.png)

___Figure 2: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Random Forest___

From the results above, both models could efficiently classify cancer and normal samples from gene expression levels with high performance recorded in all the evaluation metrics. By in-class performance, we see that out of the 24 normal samples, 1 was incorrectly identified by both models, while 3 out of the 182 cancer samples were incorrectly classified by logistic regression (LR). This transcends to 88% precision, 96% recall for normal samples for LR, and 99% precision, 98% recall and 99% F1-score for cancer samples. For RF, perfect scores were recorded for precision and recall for normal and cancer samples, respectively, and 99% precision and 96% recall for cancer and normal samples, respectively. By evaluating the number of genes selected by each model, 83 were selected by LR while 144 by RF with only 23 common genes between them. Some of these are AATK, CPLX3, RBBP7, UHRF1, YBX1, DPYSL3, and KRT19.

### Astrocyte cancer grades 
The number of samples for each cancer grade includes 198 (G1), 166 (G2), 127 (G3), and 235 (G4). The classes were slightly imbalanced.

__Table 2: Model performance evaluation on test data__

Model               |Accuracy |AUC     |Recall   |Precision |F1      |Specificity
--------------------|---------|--------|---------|----------|--------|-----------
Logistic Regression |0.884615 |0.97748 |0.884615 |0.888191  |0.882421| 0.964953
Random Forest       |0.857143 |0.972568|0.857143 |0.867143  |0.864168| 0.959284

![lr_perf_grade](imgs/ml_imgs/lr_perf_chart_grade.png)

___Figure 3: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Logistic Regression by cancer grades___


![rf_perf_grade](imgs/ml_imgs/rf_perf_chart_grade.png)

___Figure 4: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Random Forest by cancer grades___

From Table 2, both models have performance over 85% for all the evaluation metrics. However, when we look at their performance for each cancer grade from the confusion matrix (Figures 3&4), we see that the models could distinguish grades 1&2 (G1 & G2) from other grades (G3 and G4). For instance, no samples were misclassified as G1 for LR with only 2 misclassification for RF. When we look at the number of G1 & G2 samples misclassified, we see that only 2 G1 samples were misclassified to be G4 by LR. Only one G1 sample was misclassified as G3 by RF. On the other hand, 1 and 2 G2 samples were misclassified by both models to be G3 & G4, respectively. Similarly, by evaluating their performance for G3 and G4, we see that 31-50% of G3 samples were misclassified as G1, G2 or G4, while 8-11% of G4 were misclassified as either G1, G2, or G3, by the models. The high misclassification rate for G3 could be because it lies between the transition of tumour cells from being benign to mildly aggressive and then to it spreading to other cells.

By default logistic regression deals with binary classes, but can be extended to more than two classes by applying a one-vs-rest technique where models are fit for each class where the positive class is encoded as 1 and the rest as 0. The number of non-zero features selected by each model for each class includes 1298, 1103, 1034, and 1235 for G1, G2, G3, and G4, respectively. By visualising in a Venn diagram (Figure 5), 11 genes were common for all grades. These include: `C10orf25`, `CDC20B`, `CLIC5`, `CTNNA3`, `DLK2`, `EDARADD`, `HLX`, `ISL2`, `MAPK4`, `MBD3L1`, and `SLC13A4`, indicating that these genes could play as prognostic biomarkers for identifying cancer progression. This was further extended to find the number of common genes in both LR and RF models and from the result, 385 common genes were found out of the total 732 genes selected by RF. Figure 6 shows the top 20 genes selected by RF.

![venn_cancer_grades](imgs/ml_imgs/lr_venn_tumor_grades.png)

___Figure 5: Venn diagram showing common genes by cancer grade types for logistic regression___

<img src="imgs/ml_imgs/rf_varimp_grade.png" alt="rf_top_features_cancer_grades" width="800" height="600">

___Figure 6: Top 20 genes selected by Random forest___

### Cancer cell types
The number of samples for each cancer cell type includes 498 for astrocytoma (AC), 118 for ependymoma (EP), 63 for oligodendrocytoma (OGC), and 15 for mixed glioma (MGC). Weights were applied to evaluation metrics to account for the class imbalance.

__Table 3: Model performance evaluation on test data__

Model               |Accuracy |AUC     |Recall   |Precision |F1      |Specificity
--------------------|---------|--------|---------|----------|--------|-----------
Logistic Regression |0.91954  |0.957765|0.91954  |0.895321  |0.904553| 0.942156
Random Forest       |0.902299 |0.959442|0.902299 |0.873879  |0.885584| 0.921274


From Table 3, the models were performing well overall. However, when we look at their class-level performance, we see that both models were doing badly on some cell types (mixed gliomas and oligodendrocytoma). This could be because of the huge class imbalance between them and the other cell types. However, the LR model seems to perform better than the RF model in all evaluation metrics except AUC with a slightly higher performance.

![lr_perf_cell_type](imgs/ml_imgs/lr_perf_chart_cell_type.png)

___Figure 7: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Logistic Regression by cancer cell types___


![rf_perf_cell_type](imgs/ml_imgs/rf_perf_chart_cell_type.png)

___Figure 8: Visualisation showing Area under the receiver's operating characteristics and precision-recall curves and confusion matrix for Random Forest by cancer cell types___

Figures 7 and 8 show the area under the receiver's operating characteristic curve (AUROC), precision-recall curve, and confusion matrix charts for LR and RF models. From the AUROC and PRC results, we see good model performance for both models for astrocytoma and ependymoma, fairly good performance for oligodendrocytoma but bad performance for mixed glioma samples. From the confusion matrix, no mixed glioma sample was correctly detected by any of the models, with high misclassification rates for oligodendrocytoma. It could be seen that these cell types were misclassified as astrocytomas. This misclassification could be because of the imbalanced nature of the dataset where both models are biased towards the majority class (astrocytoma). Another reason could be because of the overlap of cellular features in histology, location of the brain they originated from, molecular markers, or possibly due to incorrect labelling during biopsy.

To improve the sensitivity of the models to minority class samples, latent features obtained from linear discriminant analysis were added. This led to improved performance of the models on mixed glioma but higher misclassifications on astrocytoma and ependymoma cell types. Results can be found [here](images/ml_imgs/lr_lda_perf_chart_cell_type.png) and [here](images/ml_imgs/rf_lda_perf_chart_cell_type.png) for LR and RF, respectively.

To distinguish between cancer types, a total of 144 was selected by LR: 69 for astrocytoma, 34 for ependymoma, 7 for mixed gliomas, and 56 for oligodendrocytoma. No common gene was found for all the cell types. Furthermore, seven overlapping genes were found between ependymoma and astrocytoma, while 16 were found for astrocytoma and oligodendrocytoma and 6 for ependymoma and astrocytoma (Figure 9). Additionally, 439 genes with non-zero scores were selected by RF, with only 40 common genes with LR.

![venn_lr_cell_type](imgs/ml_imgs/lr_venn_tumor_cell_type.png)

___Figure 9: Venn diagram showing overlapping genes used by LR for each cell type___

# Summary

The expression of genes in the human cell can be dysregulated in disease outcomes due to genetic and non-genetic factors. Here, we identified diagnostic and prognostic biomarkers that can act as potential therapeutic targets using differential gene expression analysis and machine learning techniques. We identified hub genes that whose dysregulation may affect downward biological processes. Similarly, we see that machine learning models can help to identify biomarkers with high predictive power to distinguish between various disease outcomes. From result, models could separate cancer from normal samples with high accuracy. Also, they could accurately distinguish between different cancer grades and types with some difficulty at distinguishing between some cancer cell types.

From these results, we see that machine learning models show great potential at predicting disease outcomes using gene expression data. However, further analysis needs to be done to validate the findings. One step is by identifying hub genes whose mutations affect downstream biological processes. Another is by conducting experimental studies to validate the effect of these biomarkers on biological processes, their molecular function, and key pathways that are affected by their dysregulation and also by designing drug molecules that can potentially target them for therapeutic interventions.
