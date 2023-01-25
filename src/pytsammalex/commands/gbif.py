"""
Search taxa in GBIF's backbone taxonomy.

Typically yo will want to use "lookup" - because this will provide fuzzy search, i.e. typos
and partial names might work:

$ tsammalex gbif lookup "Pantera leo"
      key  scientificName                 rank     taxonomicStatus
---------  -----------------------------  -------  -----------------
104061133  Panthera leo                   SPECIES  ACCEPTED
  5219404  Panthera leo (Linnaeus, 1758)  SPECIES  ACCEPTED

If you are certain about the spelling, try "suggest" - which is quicker.


https://www.gbif.org/tools/species-lookup

"""
import json

from clldutils.clilib import Table, add_format

from pytsammalex.gbif import GBIF


def register(parser):
    # FIXME: no-cache option!
    parser.add_argument('service')
    parser.add_argument('query')
    add_format(parser, default='simple')


def run(args):
    kw = {'key' if args.service == 'usage' else 'q': args.query}
    res = GBIF()(args.service, **kw)
    if args.service == 'suggest':
        cols = ['key', 'scientificName', 'rank', 'status']
        with Table(args, *cols) as table:
            for row in res:
                if not row['synonym']:
                    table.append([row.get(col) for col in cols])
    elif args.service == 'lookup':
        cols = ['key', 'scientificName', 'rank', 'taxonomicStatus']
        with Table(args, *cols) as table:
            for row in res['results']:
                if 1:#not row['synonym'] and 'nubKey' not in row and 'kingdom' in row:
                    table.append([row.get(col) for col in cols])
    elif args.service == 'usage':
        print(json.dumps(res, indent=4))

