#import sparql
import SPARQLWrapper
import argparse
import codecs
import six
from collections import defaultdict

def runQuery(query):
	endpoint = 'https://query.wikidata.org/sparql'
	sparql = SPARQLWrapper.SPARQLWrapper(endpoint)
	sparql.setQuery(query)
	sparql.setReturnFormat(SPARQLWrapper.JSON)
	results = sparql.query().convert()

	return results['results']['bindings']

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Tool for exploring Wikipedia')
	parser.add_argument('--property',required=True,type=str,help='Property ID, e.g. P31 for "instance of"')
	parser.add_argument('--target',required=True,type=str,help='ID for target, e.g. Q12140 for medication')
	args = parser.parse_args()

	query = """
	SELECT ?item1 ?item1Label ?alias WHERE {
		SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
		?item1 wdt:%s wd:%s.
		OPTIONAL {?item1 skos:altLabel ?alias FILTER (LANG (?alias) = "en") .}
	} 
	""" % (args.property,args.target)
	#?item1 wdt:P31 wd:Q12140.
	#LIMIT 100000

	mainTerms = {}
	aliases = defaultdict(set)
	for row in runQuery(query):
		pageID = row['item1']['value']

		if 'xml:lang' in row['item1Label'] and row['item1Label']['xml:lang'] == 'en':
			mainTerm = row['item1Label']['value'].lower()

			mainTerms[pageID] = mainTerm

			if 'alias' in row:
				if row['alias']['xml:lang'] == 'en':
					aliases[pageID].add(row['alias']['value'].lower())


	for pageID in sorted(mainTerms.keys()):
		t = mainTerms[pageID]
		a = sorted(list(aliases[pageID]) + [t])

		print("%s\t%s\t%s" % (pageID, t, "|".join(a).lower()))


