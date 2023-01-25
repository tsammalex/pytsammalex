import json
import logging
import pathlib
import sqlite3
import contextlib

from pygbif import species
from appdirs import user_cache_dir

import pytsammalex

__all__ = ['RANKS', 'GBIF']

RANKS = [
    'KINGDOM',
    'PHYLUM',
    'CLASS',
    'ORDER',
    'FAMILY',
    'GENUS',
    'SPECIES',
    'SUBSPECIES',
    'VARIETY',
    'FORM',
    None,
]


class Cache:
    def __init__(self):
        d = pathlib.Path(user_cache_dir(appname=pytsammalex.__name__))
        if not d.exists():
            d.mkdir(parents=True)
        self.dbpath = d / 'gbif.sqlite'

    def __enter__(self):
        with self.cursor() as cu:
            cu.execute(
                "CREATE TABLE IF NOT EXISTS requests (method TEXT, query TEXT, result TEXT);")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @contextlib.contextmanager
    def cursor(self):
        with contextlib.closing(sqlite3.connect(str(self.dbpath))) as conn:
            yield conn.cursor()
            conn.commit()

    def get(self, method, **kw):
        query = json.dumps(list(sorted(kw.items())))
        with self.cursor() as cu:
            cu.execute(
                "select result from requests where method = ? and query = ?", (method, query))
            res = cu.fetchone()
            if res:
                logging.getLogger('tsammalex').debug('cache hit: {} {}'.format(method, query))
                return json.loads(res[0])
            res = getattr(species, 'name_' + method)(**kw)
            cu.execute(
                "insert into requests (method, query, result) values (?,?,?)",
                (method, query, json.dumps(res)))
            return res


class GBIF:
    def __call__(self, method, no_cache=False, **kw):
        op = getattr(species, 'name_' + method)
        if no_cache:
            return op(**kw)
        with Cache() as cache:
            return cache.get(method, **kw)

    def clear_cache(self):
        Cache().dbpath.unlink()

    def suggest(self, **kw):
        return self('suggest', **kw)

    def lookup(self, **kw):
        return self('lookup', **kw)

    def usage(self, **kw):
        return self('usage', **kw)

    def get_vernacular_names(self, key, rank='species', language_tags=['eng']):
        langs = set(tag for tag in language_tags or [])
        names = {k: None for k in langs}

        def _get_names(k):
            for res in self.usage(key=k, data='vernacularNames')['results']:
                tag = res.get('language')
                if (tag in langs) or language_tags is None:
                    names[tag] = res['vernacularName']
                    if tag in langs:
                        langs.remove(tag)  # We take the first matching name, then clear the tag.

        _get_names(key)
        if langs and rank and (rank.lower() == 'subspecies'):
            # For subspecies we try to supplement names for the species.
            _get_names(self.usage(key=key)['speciesKey'])
        return {k: v for k, v in names.items() if v}
