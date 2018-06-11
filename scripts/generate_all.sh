#!/bin/bash
set -eux

UMLSDIR=/projects/bioracle/ncbiData/umls/2017AB/META

DO_URL=https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid-non-classified.obo
GENE_URL=ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz

rm -f doid-non-classified.obo gene_info.gz gene_info

wget -O doid-non-classified.obo $DO_URL
wget -O gene_info.gz $GENE_URL
gunzip gene_info.gz
rm -f gene_info.gz

cat stopwords_cancer.txt stopwords_selected.txt | sort -u > stopwords_cancer.combined.txt
cat stopwords_drugs.txt stopwords_selected.txt | sort -u > stopwords_drugs.combined.txt
cat stopwords_genes.txt stopwords_selected.txt | sort -u > stopwords_genes.combined.txt

python generateCancerTerms.py --diseaseOntologyFile doid-non-classified.obo --cancerStopwords stopwords_cancer.combined.txt --umlsConceptFile $UMLSDIR/MRCONSO.RRF --customAdditions additions_cancer.txt --customDeletions deletions_cancer.txt --outFile terms_cancer.txt

python generateGeneTerms.py --ncbiGeneInfoFile gene_info --umlsConceptFile $UMLSDIR/MRCONSO.RRF --geneStopwords stopwords_genes.combined.txt --customAdditions additions_genes.txt --customDeletions deletions_genes.txt --outFile terms_genes.txt

python generateDrugTerms_sparql.py --drugStopwords stopwords_drugs.combined.txt --customAdditions additions_drugs.txt --outFile terms_drugs.wikidata.txt
python generateDrugTerms_geneinhibitors.py --geneTerms terms_genes.txt --outFile terms_drugs.inhibitors.txt
cat terms_drugs.wikidata.txt terms_drugs.inhibitors.txt terms_drugs.custom.txt > terms_drugs.txt

