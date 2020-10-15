import argparse
import codecs
from collections import defaultdict
import xml.etree.cElementTree as etree

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Generate protein word-list based on UniProt data')
	parser.add_argument('--uniprotXML',type=str,required=True,help='Uniprot XML file')
	parser.add_argument('--proteinStopwords',required=True,type=str,help='Stopword file for proteins')
	parser.add_argument('--customAdditions', required=False, type=str, help='Some custom additions to the wordlist')
	parser.add_argument('--customDeletions', required=False, type=str, help='Some custom deletions from the wordlist')
	parser.add_argument('--outFile', required=True, type=str, help='Path to output wordlist file')
	args = parser.parse_args()

	print("Loading stopwords...")
	with codecs.open(args.proteinStopwords,'r','utf8') as f:
		proteinStopwords = [ line.strip().lower() for line in f ]
		proteinStopwords = set(proteinStopwords)

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
				customDeletions[termid] += terms.lower().split('|')

	with open(args.uniprotXML, 'r') as openfile, open(args.outFile,'w') as outF:

		# Skip to the article element in the file
		for event, elem in etree.iterparse(openfile, events=('start', 'end', 'start-ns', 'end-ns')):
			#print(event,elem)
			if event=='end' and elem.tag=='{http://uniprot.org/uniprot}entry':
			
				taxonomies = elem.findall('./{http://uniprot.org/uniprot}organism/{http://uniprot.org/uniprot}dbReference')
				isHuman = False
				for taxonomy in taxonomies:
					if taxonomy.attrib['type'] == 'NCBI Taxonomy' and taxonomy.attrib['id'] == '9606':
						isHuman = True
						break

				if isHuman:
					accessions = elem.findall('./{http://uniprot.org/uniprot}accession')
					accession = accessions[0].text

					names = elem.findall('./{http://uniprot.org/uniprot}name')
					assert len(names) == 1
					name = names[0].text



					recommendedNames = elem.findall('./{http://uniprot.org/uniprot}protein/{http://uniprot.org/uniprot}recommendedName/{http://uniprot.org/uniprot}fullName')
					recommendedNames = [ x.text for x in recommendedNames ]
					
					alternativeNames = elem.findall('./{http://uniprot.org/uniprot}protein/{http://uniprot.org/uniprot}alternativeName/{http://uniprot.org/uniprot}fullName')
					alternativeNames = [ x.text for x in alternativeNames ]

					#print(accession,name,recommendedNames,alternativeNames)

					allNames = [name] + recommendedNames + alternativeNames
					allNames = [ x for x in allNames if len(x) >= 3 ]

					trimProtein = [ x[:-len(" protein")] for x in allNames if x.lower().endswith(' protein') ]

					allNames += trimProtein

					allNames = [ x for x in allNames if not x.lower() in proteinStopwords ]

					allNames += customAdditions[accession]

					allNames = [ x for x in allNames if not x.lower() in customDeletions[accession] ]

					allNames = sorted(list(set(allNames)))
					if len(allNames) > 0:
						for n in allNames:
							assert not "|" in n, "| found in %s with accession %s" % (n,accession)
						allNamesTxt = "|".join(allNames)

						outData = [ accession, name, allNamesTxt ]
						outLine = "\t".join(outData)
						outF.write(outLine + "\n")
					#break

				elem.clear()


