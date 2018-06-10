#!/bin/bash
set -ex

cat stopwords_cancer.txt stopwords_selected.txt > stopwords_cancer.combined.txt
cat stopwords_drugs.txt stopwords_selected.txt > stopwords_drugs.combined.txt
cat stopwords_genes.txt stopwords_selected.txt > stopwords_genes.combined.txt
cat stopwords_hpo.txt stopwords_selected.txt > stopwords_hpo.combined.txt

python generateCancerTerms.py --diseaseOntologyFile ../../cancermine/doid.obo --cancerStopwords stopwords_cancer.combined.txt --umlsConceptFile /projects/bioracle/ncbiData/umls/2016AB/META/MRCONSO.RRF --outFile terms_cancer.txt


python generateGeneTerms.py --ncbiGeneInfoFile ../../cancermine/ncbi_gene_info --geneStopwords stopwords_genes.combined.txt --outFile terms_genes.txt

python generateHPOWordlist.py --ontologyFile hp.obo --stopwordsFile stopwords_hpo.combined.txt --umlsConceptFile /projects/bioracle/ncbiData/umls/2016AB/META/MRCONSO.RRF --outFile terms_phenotype.txt

python generateDrugTerms.py --wikidataFile wikidata.json --drugStopwords stopwords_drugs.combined.txt --outFile terms_drugs.wikidata.txt


cat terms_drugs.wikidata.txt terms_drugs.custom.txt > terms_drugs.txt
