import argparse
import codecs
from collections import defaultdict

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Make an exhaustive list of gene inhibitors given a list of genes')
	parser.add_argument('--geneTerms',required=True,type=str,help='Gene terms to use as input')
	parser.add_argument('--customDeletions', required=False, type=str, help='Some custom deletions from the wordlist')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()

	customDeletions = defaultdict(list)
	if args.customDeletions:
		print("Loading deletions...")
		with codecs.open(args.customDeletions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				customDeletions[termid] += terms.split('|')
	
	with codecs.open(args.geneTerms,'r','utf-8') as inGenes, codecs.open(args.outFile,'w','utf-8') as outDrugs:
		for line in inGenes:
			geneid,singlegeneterm,allgeneterms,entrez_gene_id = line.strip().split('\t')
			allgeneterms = allgeneterms.split('|')

			drugid = "inhibitor|%s" % geneid
			singledrugterm = "%s inhibitor" % singlegeneterm

			alldrugterms = []
			alldrugterms += [ "%s inhibitor" % g for g in allgeneterms ]
			alldrugterms += [ "%s inhibitors" % g for g in allgeneterms ]
			alldrugterms += [ "inhibitor of %s" % g for g in allgeneterms ]
			alldrugterms += [ "inhibitors of %s" % g for g in allgeneterms ]

			alldrugterms += [ d.lower() for d in alldrugterms ]

			alldrugterms = [ d for d in alldrugterms if not d in customDeletions[drugid] ]

			alldrugterms = sorted(list(set(alldrugterms)))

			outDrugs.write("%s\t%s\t%s\n" % (drugid,singledrugterm,"|".join(alldrugterms)))

	print("Done")

