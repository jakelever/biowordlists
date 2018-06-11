This describes the output files for the [BioWordlists](https://github.com/jakelever/biowordlists) project. These files are ancillary data for other text mining projects.

Each file is a tab-delimited file with one term per line. The first column is a unique ID. The second column is the main name of the term. The third column is a pipe-delimited set of the synonyms for this term (including the main term).

**terms_genes.tsv:** This is a list of all human genes with synonyms. The first column is the [HUGO](https://www.genenames.org/) gene ID. It includes an additional fourth column is the Entrez gene ID. Genes are built using the [NCBI Gene resource](https://www.ncbi.nlm.nih.gov/gene) with synonyms from the [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html).

**terms_drugs.tsv:** This is a list of all drugs from the [WikiData](https://www.wikidata.org) resource. It also includes some more general terms and inhibitors terms for all genes in the gene list.

**terms_cancers.tsv:** This is a list of specific cancer types from the [Disease Ontology](http://disease-ontology.org/). General cancer terms have been removed and synonyms added from the UMLS Metathesaurus.

**terms_variants.tsv:** Common mutations, aberrations and other 'omic events that may occur to a gene, especially in the cancer setting.

**terms_conflicting.tsv:** Several common biomedical terms that are easily confused with other useful concepts. An examples is "Cox Regression". This list is used to identify these to reduce ambiguity.
