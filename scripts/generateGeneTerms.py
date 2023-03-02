"""
This script is used to build a word-list of relevant gene terms from the HUGO gene list
"""
import argparse
import sys
import codecs
from collections import defaultdict
import gzip

def cleanupQuotes(text):
	"""
	Removes quotes if text starts and ends with them

	Args:
		text (str): Text to cleanup

	Returns:
		Text with quotes removed from start and end (if they existed) or original string (if not)
	"""
	if text.startswith('"') and text.endswith('"'):
		return text[1:-1]
	else:
	 	return text

def loadHGNCToUMLSTerms(filename):
	"""
	Loads the UMLS metathesaurus and extracts mappings from Hugo GeneIDs to UMLS terms

	Args:
		filename (str): Filename of UMLS Concept file (MRCONSO.RRF)

	Returns:
		Dictionary where each key (CUID) points to a list of strings (terms)
	"""
	mapping = defaultdict(list)
	with codecs.open(filename,'r','utf8') as f:
		for line in f:
			split = line.split('|')
			cuid = split[0]
			lang = split[1]
			externalID = split[13]
			term = split[14]
			if lang != 'ENG':
				continue

			if externalID.startswith('HGNC:'):
				mapping[externalID].append(term)
	return mapping

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate term list from NCBI gene resource')
	parser.add_argument('--ncbiGeneInfoFile', required=True, type=str, help='Path to NCBI Gene Info file')
	parser.add_argument('--umlsConceptFile', required=True, type=str, help='Path on the MRCONSO.RRF file in UMLS metathesaurus')
	parser.add_argument('--geneStopwords',required=True,type=str,help='Stopword file for genes')
	parser.add_argument('--customAdditions', required=False, type=str, help='Some custom additions to the wordlist')
	parser.add_argument('--customDeletions', required=False, type=str, help='Some custom deletions from the wordlist')
	parser.add_argument('--outFile', required=True, type=str, help='Path to output wordlist file')
	args = parser.parse_args()

	genes = []

	print("Loading metathesaurus...")
	hugoToMetathesaurus = loadHGNCToUMLSTerms(args.umlsConceptFile)

	print("Loading stopwords...")
	with codecs.open(args.geneStopwords,'r','utf8') as f:
		geneStopwords = [ line.strip().lower() for line in f ]
		geneStopwords = set(geneStopwords)

	customAdditions = defaultdict(list)
	if args.customAdditions:
		print("Loading additions...")
		with codecs.open(args.customAdditions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				customAdditions[termid] += terms.split('|')
	customDeletions = defaultdict(list)
	if args.customDeletions:
		print("Loading deletions...")
		with codecs.open(args.customDeletions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				customDeletions[termid] += terms.split('|')

	print("Processing")
	skipCount = 0
	with gzip.open(args.ncbiGeneInfoFile,'rt',encoding='utf8') as ncbiF:
		for line in ncbiF:
			split = line.rstrip('\n\r').split('\t')

			# Get the relevant fields for the gene
			taxonomy_id = split[0]
			entrez_gene_id = split[1]
			type_of_gene = split[9]


			# Only select human genes
			if taxonomy_id == '9606' and type_of_gene == 'protein-coding':
				ncbi_id = split[1]
				symbol = split[2]
				synonyms = split[4].split('|')
				dbXrefs = split[5].split('|')
				nomenclature_symbol = split[10]
				nomenclature_full = split[11]

				hugo_id = None
				for dbXref in dbXrefs:
					if dbXref.startswith('HGNC:'):
						hugo_id = dbXref[5:]

				if hugo_id is None:
					skipCount += 1
					continue

				# Gather up the names from the NCBI file
				allNames = [symbol,nomenclature_symbol,nomenclature_full] + synonyms

				# Add in names from the Metathesaurus
				metathesaurusTerms = []
				if hugo_id in hugoToMetathesaurus:
					metathesaurusTerms = hugoToMetathesaurus[hugo_id]
				allNames = allNames + metathesaurusTerms

				allNames += customAdditions[hugo_id]

				allNames = [ x.strip().lower() for x in allNames ]
				allNames = [ x for x in allNames if x ]
				allNames = [ x for x in allNames if x != '-' ]
				allNames = [ cleanupQuotes(x) for x in allNames ]

				# Try adding a few extra synonyms (by removing the final word gene, e.g. KRAS gene -> KRAS)
				extraNames = []
				for name in allNames:
					if name.endswith(' gene'):
						extraNames.append(name[:-len(' gene')])
				allNames = allNames + extraNames

				allNames = [ x for x in allNames if not x in customDeletions[hugo_id] ]
				
				# Remove instances with commas
				allNames = [ x for x in allNames if not "," in x ]

				# Remove any syndromes
				endings_to_skip = ['syndrome','cancer','disease']
				allNames = [ x for x in allNames if not any (x.lower().endswith(ending) for ending in endings_to_skip) ]

				# Remove any duplicates
				noDuplicates = sorted(list(set(allNames)))
				noDuplicates = [ g for g in noDuplicates if not g in geneStopwords ]
				noDuplicates = [ g for g in noDuplicates if len(g) >= 3 ]

				if len(noDuplicates) > 0:

					numeric_id = int(hugo_id.replace('HGNC:',''))

					gene = (numeric_id,hugo_id,symbol,noDuplicates,entrez_gene_id)
					genes.append(gene)

	print("%d items skipped as no HUGO ID could be found" % skipCount)
	genes = sorted(genes)

	with codecs.open(args.outFile,'w','utf8') as outF:
		for _,hugo_id,singleName,synonyms,entrez_gene_id in genes:
			# Then output to the file
			line = u"%s\t%s\t%s\t%s" % (hugo_id, singleName, u"|".join(synonyms), entrez_gene_id)
			outF.write(line + "\n")

	print("Successfully output to %s" % args.outFile)

		

