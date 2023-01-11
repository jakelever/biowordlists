#!/bin/bash
set -eux
set -o pipefail


DO_URL=https://github.com/DiseaseOntology/HumanDiseaseOntology/blob/main/src/ontology/doid-non-classified.obo?raw=true
GENE_URL=ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
UNIPROT_URL=ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.xml.gz

# Update this to point to the MRCONSO.RRF file
UMLS_MRCONSO=$PWD/../umls/2022AB/META/MRCONSO.RRF

mkdir working
cd working

SCRIPTS=../scripts

rm -f doid-non-classified.obo gene_info.gz gene_info uniprot_sprot.xml.gz uniprot_sprot.xml

wget -O doid-non-classified.obo $DO_URL

wget -O gene_info.gz $GENE_URL
gunzip gene_info.gz
rm -f gene_info.gz

wget -O uniprot_sprot.xml.gz $UNIPROT_URL
gunzip uniprot_sprot.xml.gz
rm -f uniprot_sprot.xml.gz

ln -s ../custom/* .
ln -s ../predefined/* .

cat stopwords_cancers.txt stopwords_selected.txt | sort -u > stopwords_cancers.combined.txt
cat stopwords_drugs.txt stopwords_selected.txt | sort -u > stopwords_drugs.combined.txt
cat stopwords_genes.txt stopwords_selected.txt | sort -u > stopwords_genes.combined.txt
cat stopwords_proteins.txt stopwords_selected.txt | sort -u > stopwords_proteins.combined.txt

python $SCRIPTS/generateCancerTerms.py --diseaseOntologyFile doid-non-classified.obo --cancerStopwords stopwords_cancers.combined.txt --umlsConceptFile $UMLS_MRCONSO --customAdditions additions_cancers.tsv --customDeletions deletions_cancers.tsv --outFile terms_cancers.tsv

python $SCRIPTS/generateGeneTerms.py --ncbiGeneInfoFile gene_info --umlsConceptFile $UMLS_MRCONSO --geneStopwords stopwords_genes.combined.txt --customAdditions additions_genes.tsv --customDeletions deletions_genes.tsv --outFile terms_genes.tsv

python $SCRIPTS/generateDrugTerms_sparql.py --drugStopwords stopwords_drugs.combined.txt --customAdditions additions_drugs.tsv --customDeletions deletions_drugs.tsv --outFile terms_drugs.wikidata.tsv
python $SCRIPTS/generateDrugTerms_geneinhibitors.py --geneTerms terms_genes.tsv --customDeletions deletions_drugs.tsv --outFile terms_drugs.inhibitors.tsv
cat terms_drugs.wikidata.tsv terms_drugs.inhibitors.tsv terms_drugs.custom.tsv > terms_drugs.tsv

python $SCRIPTS/generateProteinTerms.py --uniprotXML uniprot_sprot.xml --proteinStopwords stopwords_proteins.combined.txt --customAdditions additions_proteins.tsv --outFile terms_proteins.tsv

