#import sparql
import SPARQLWrapper
import argparse
import codecs
import six
import time
import urllib.error
from collections import defaultdict

USER_AGENT = 'biowordlists/1.0 (https://github.com/jakelever/biowordlists; jake.lever@gmail.com)'

def runQuery(query, maxAttempts=6):
	endpoint = 'https://query.wikidata.org/sparql'
	sparql = SPARQLWrapper.SPARQLWrapper(endpoint, agent=USER_AGENT)
	sparql.setQuery(query)
	sparql.setReturnFormat(SPARQLWrapper.JSON)

	for attempt in range(1, maxAttempts + 1):
		try:
			results = sparql.query().convert()
			break
		except urllib.error.HTTPError as e:
			if e.code not in (429, 503) or attempt == maxAttempts:
				raise
			try:
				wait = int(e.headers.get('Retry-After'))
			except (TypeError, ValueError):
				wait = 65
			print("  Wikidata returned HTTP %d (attempt %d/%d), retrying in %ds" % (e.code, attempt, maxAttempts, wait))
			time.sleep(wait)

	return results['results']['bindings']

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Tool to pull certain triple types from WikiData using SPARQL')
	parser.add_argument('--drugStopwords',required=True,type=str,help='Stopword file for drugs')
	parser.add_argument('--customAdditions', required=False, type=str, help='Some custom additions to the wordlist')
	parser.add_argument('--customDeletions', required=False, type=str, help='Some custom deletions from the wordlist')
	parser.add_argument('--outFile',type=str,required=True,help='File to output triples')
	args = parser.parse_args()

	mainterm = {}
	aliases = defaultdict(set)

	print("Loading stopwords...")
	with codecs.open(args.drugStopwords,'r','utf8') as f:
		stopwords = [ line.strip().lower() for line in f ]
		stopwords = set(stopwords)

	if args.customAdditions:
		print("Loading additions...")
		with codecs.open(args.customAdditions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				mainterm[termid] = singleterm
				aliases[termid].update(terms.split('|'))
	
	customDeletions = defaultdict(list)
	if args.customDeletions:
		print("Loading deletions...")
		with codecs.open(args.customDeletions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				customDeletions[termid] += terms.split('|')

	print("Gathering drugs and aliases from Wikidata")



	rowCount = 0

	medicationID = "Q12140"
	instanceOfID = "P31"
	subclassOfID = "P279"

	query = """
	SELECT ?item1 ?item1Label ?alias WHERE {
		SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
		?item1 wdt:%s wd:%s.
		OPTIONAL {?item1 skos:altLabel ?alias FILTER (LANG (?alias) = "en") .}
	} 
	""" % (instanceOfID,medicationID)

	for row in runQuery(query):
		#print(row)
		drugID = row['item1']['value']

		if 'xml:lang' in row['item1Label'] and row['item1Label']['xml:lang'] == 'en':
			mainterm[drugID] = row['item1Label']['value'].lower()

			if 'alias' in row:
				if row['alias']['xml:lang'] == 'en':
					aliases[drugID].add(row['alias']['value'].lower())

		rowCount += 1

	print ("  Got %d drugs (from %d rows)" % (len(mainterm),rowCount))

	with codecs.open(args.outFile,'w','utf-8') as f:
		keys = sorted(mainterm.keys())
		for k in keys:
			combined = aliases[k]
			combined.add(mainterm[k])
			combined = [ t for t in combined if not t in stopwords ]
			combined = [ t for t in combined if len(t) > 3 ]
			combined += [ t.replace('\N{REGISTERED SIGN}','').strip() for t in combined ]


			shortID = k.split('/')[-1]

			combined = [ t for t in combined if not t in customDeletions[shortID] ]

			combined = [ t.lower() for t in combined ]

			combined = sorted(list(set(combined)))

			if len(combined) > 0:
				data = [shortID,mainterm[k],"|".join(combined)]
				f.write("\t".join(data) + "\n")



