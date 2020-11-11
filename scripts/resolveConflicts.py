import argparse
from collections import defaultdict

def main():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('--wordlist',required=True,type=str,help='Wordlist to help resolve conflicts')
	parser.add_argument('--conflicts',required=True,type=str,help='File with conflicting terms (separated by ;)')
	parser.add_argument('--nowarn', action='store_true', help='Do not check for missing conflicts where one is expected')
	parser.add_argument('--outFile',required=True,type=str,help='Output file with resolution options (for deletions file)')
	args = parser.parse_args()

	print("Loading wordlist...")
	main_terms = {}
	synonym_to_identifier = defaultdict(list)
	with open(args.wordlist) as f:
		for line in f:
			split = line.strip('\n').split('\t')
			identifier,main,synonyms = split[:3]
			
			main_terms[identifier] = main
			for s in synonyms.lower().split('|'):
				synonym_to_identifier[s].append(identifier)

	print("Processing conflicts...")
	with open(args.conflicts) as f, open(args.outFile,'w') as outF:
		conflicting_terms = sorted(set([ line.strip().lower() for line in f ]))
		for ct in conflicting_terms:
			identifiers = synonym_to_identifier[ct]

			if not args.nowarn:
				assert len(identifiers) > 1, "Couldn't find conflict for term: %s" % ct

			if len(identifiers) > 1:
				for identifier in identifiers:
					outData = [ identifier, main_terms[identifier], ct ]
					outF.write("\t".join(outData) + "\n")

	print("Done")
			

if __name__ == '__main__':
	main()
