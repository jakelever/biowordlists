# BioWordlists

<p>
<a href="https://travis-ci.org/jakelever/biowordlists">
   <img src="https://travis-ci.org/jakelever/biowordlists.svg?branch=master" />
</a>
<a href="https://doi.org/10.5281/zenodo.1286661">
   <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.1286661.svg" />
</a>
</p>

This is an ancillary repo for several other projects providing auto-generated wordlists with some additional curation. The topics are outlined below. The goal is to create a reliable set of wordlists for different biomedical topics for text mining purposes. In particular, lists are trimmed for stopwords and other common English words to reduce ambiguity. Contributions are greatly appreciated.

Each of the generated wordlists is a tab-delimited file. The first column is a unique identifier, second is the name for the term, the third is a pipe-delimited list of synonyms.

This project has a single main script (generate\_all) which runs all the other scripts. The output files of this project can be found at [Zenodo](https://doi.org/10.5281/zenodo.1286661) where they can be easily accessed by other projects.

**Genes:** This is a list of all human genes with synonyms. The first column is the [HUGO](https://www.genenames.org/) gene ID and the fourth column is the Entrez gene ID. Genes are built using the [NCBI Gene resource](https://www.ncbi.nlm.nih.gov/gene) with synonyms from the [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html).

**Drugs:** This is a list of all drugs from the [WikiData](https://www.wikidata.org) resource. It also includes some more general terms and inhibitors terms for all genes in the gene list.

**Cancers:** This is a list of specific cancer types from the [Disease Ontology](http://disease-ontology.org/). General cancer terms have been removed and synonyms added from the UMLS Metathesaurus.

**Variants:** Common mutations, aberrations and other 'omic events that may occur to a gene, especially in the cancer setting.

**Conflicting:** Several common biomedical terms that are easily confused with other useful concepts. An examples is "Cox Regression". This list is used to identify these to reduce ambiguity.

**Proteins:** Human protein names from [UniProt](https://www.uniprot.org/) with synonyms.

## Dependencies

The only dependency that needs separate installation is the [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html). You can get the MRCONSO.RRF release for that. You must then update the **generate\_all.sh** to link the location of the MRCONSO file. The **generate\_all.sh** script manages the download of other resources, e.g. the Disease Ontology.

## Executing it

To generate the latest version of the wordlists, you can execute the command below:

```
sh generate_all.sh
```

## Individual Scripts

The [scripts/](https://github.com/jakelever/biowordlists/tree/master/scripts) directory contains all the scripts for generating the wordlists. Check the **generate\_all.sh** file for example usage for each script.

## Additional Files

The [custom/](https://github.com/jakelever/biowordlists/tree/master/custom) directory contains additions, deletions and stopwords for the different term types.

The [predefined/](https://github.com/jakelever/biowordlists/tree/master/predefined) directory contains several fully defined word-lists that do not need to be auto-generated. These are the variants, conflicting and a small section of the drug list.

## Versions

New versions are pushed to Zenodo roughly yearly. They will contain updates of all underlying resources. Other significant changes to versions are noted below.
- **v4**: Removed dependency of PubRunner and made use of a simpler BASH script to download resources

## Contributing

Contributions are very welcome. If you find any conflicting terms or obviously mistakes, please create a ticket or contribute to the associated additions, deletions or stopwords file.

## License

The associated code is distributed under the terms of the [MIT license](http://opensource.org/licenses/MIT).

## Issues

If you encounter any problems, please [file an issue](https://github.com/jakelever/biowordlists/issues) along with a detailed description.
