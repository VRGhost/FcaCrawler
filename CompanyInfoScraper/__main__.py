import argparse
import subprocess
import os
import sys
import sqlite3
import csv

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

def do_crawl(dbPath, query):
	subprocess.check_call(
		[
			sys.executable,
			"-m", "scrapy.cmdline",
			"crawl", "fca",
			"-a", "regNumber={}".format(query),
			"-o", os.path.abspath(dbPath),
			"-t", "sqlite",
		],
		cwd=THIS_DIR
	)

def do_query(dbPath, query):
	with sqlite3.connect(dbPath) as conn:
		cur = conn.cursor()
		cur.execute(query)
		colNames = [el[0] for el in cur.description]
		out = csv.writer(sys.stdout, delimiter="\t")

		out.writerow(colNames)
		for row in cur:
			row = [el if isinstance(el, basestring) else str(el) for el in row]
			out.writerow([el.encode("utf8") if el else "" for el in row])

DB_PATH = os.path.join(
	THIS_DIR, os.pardir,
	"data.sqlitedb"
)

def get_arg_parser():
	parser = argparse.ArgumentParser(description="register.fca.org crawler")
	parser.add_argument("--db_path", default=DB_PATH, help="Path to database to be used")

	subP = parser.add_subparsers(help="Execution mode")

	searchP = subP.add_parser("crawl", help="Crawl the website")
	searchP.set_defaults(mode="crawl")
	searchP.add_argument("query", help="search query")

	resultsP = subP.add_parser("results", help="Browse retreived results")
	resultsP.set_defaults(mode="results")
	resultsP.add_argument("--query", default="SELECT name,status,houseNumber FROM CompanyInfoItem ORDER BY name", nargs='+', required=False, help="Query to execute")

	return parser

if __name__ == "__main__":
	args = get_arg_parser().parse_args()
	if args.mode == "crawl":
		do_crawl(args.db_path, args.query)
	elif args.mode == "results":
		do_query(args.db_path, " ".join(args.query))