# BioWordlists

[![Travis CI](https://travis-ci.org/jakelever/biowordlists.svg?branch=master)](https://travis-ci.org/jakelever/biowordlists)

This is an ancillary repo for several other projects providing auto-generated wordlists with some additional curation. The topics are outlined below. The goal is to create a reliable set of wordlists for different biomedical topics for text mining purposes. In particular, lists are trimmed for stopwords and other common English words to reduce ambiguity. Contributions are greatly appreciated.

Each of the generated wordlists is a tab-delimited file. The first column is a unique identifier, second is the name for the term, the third is a pipe-delimited list of synonyms.

This project uses the [PubRunner](https://github.com/jakelever/pubrunner) framework to manage downloading the dependencies and executing the scripts. It then uploads them to [Zenodo](https://zenodo.org/) where they can be easily accessed by other projects.

**Genes:** This is a list of all human genes with synonyms. The first column is the [HUGO](https://www.genenames.org/) gene ID and the fourth column is the Entrez gene ID. Genes are built using the [NCBI Gene resource](https://www.ncbi.nlm.nih.gov/gene) with synonyms from the [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html).

**Drugs:** This is a list of all drugs from the [WikiData](https://www.wikidata.org) resource. It also includes some more general terms and inhibitors terms for all genes in the gene list.

**Cancers:** This is a list of specific cancer types from the [Disease Ontology](http://disease-ontology.org/). General cancer terms have been removed and synonyms added from the UMLS Metathesaurus.

## Running It

The key dependencies are [PubRunner](https://github.com/jakelever/pubrunner) and the [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html). You can install PubRunner through [pip](https://pypi.org/). After installing the UMLS Metathesaurus (using Metamorphsys), you need to edit [resources/METATHESAURUS.yml](https://github.com/jakelever/biowordlists/blob/master/resources/METATHESAURUS.yml) to point towards your local instance. Then you can execute the command below:

```
pubrunner .
```

There is also a test mode (that is used for the [TravisCI](https://travis-ci.org/jakelever/biowordlists) test). It runs the same code but uses an empty UMLS metathesaurus and a tiny NCBI gene resource. To use it:

```
pubrunner --test .
```

## Contributing

Contributions are very welcome. If you find any conflicting terms or obviously mistakes, please create a ticket or contribute to the associated additions, deletions or stopwords file.

## License

The associated code is distributed under the terms of the [MIT license](http://opensource.org/licenses/MIT).

## Issues

If you encounter any problems, please [file an issue](https://github.com/jakelever/biowordlists/issues) along with a detailed description.
