import argparse
from googlesearch import search
import json
import time
import os

#for url in search('egfr gene', stop=10):
#	print(url)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Do a lot of Google searches to identify misnamed genes')
	parser.add_argument('--genes',type=str,required=True,help='Gene list generated by Biowordlists')
	parser.add_argument('--searchResults',type=str,required=True,help='Output JSON file with search results')
	args = parser.parse_args()

	with open(args.searchResults) as f:
		results = json.load(f)
	print("Loaded %d genes already processed" % len(results))

	genes = set()
	with open(args.genes) as f:
		for line in f:
			gene_hugo_id,name,terms,gene_entrez_id = line.strip('\n').split('\t')
			terms = terms.split('|')
			genes.update(terms)
