import attr
from csvw.metadata import URITemplate

from pytsammalex.gbif import GBIF

try:
    import pylexibank
except ImportError:
    import mock
    pylexibank = mock.Mock()


@attr.s
class Taxon(pylexibank.Concept):
    GBIF_ID = attr.ib(default=None)
    GBIF_NAME = attr.ib(default=None)
    canonicalName = attr.ib(default=None)
    rank = attr.ib(default=None)
    kingdom = attr.ib(default=None)
    kingdomKey = attr.ib(default=None)
    phylum = attr.ib(default=None)
    phylumKey = attr.ib(default=None)
    class_ = attr.ib(default=None)
    classKey = attr.ib(default=None)
    order = attr.ib(default=None)
    orderKey = attr.ib(default=None)
    family = attr.ib(default=None)
    familyKey = attr.ib(default=None)
    genus = attr.ib(default=None)
    genusKey = attr.ib(default=None)

    @classmethod
    def dict_from_gbif(cls, gbif_id, **kw):
        res = {}
        data = GBIF().usage(key=gbif_id, **kw)
        for k in attr.fields_dict(cls):
            target = {'GBIF_ID': 'key', 'GBIF_NAME': 'scientificName', 'class_': 'class'}.get(k, k)
            if target in data:
                res[k] = data[target]
        return res


class Dataset(pylexibank.Dataset):
    concept_class = Taxon
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,",  # characters that split forms e.g. "a, b".
        missing_data=('?', '-'),  # characters that denote missing data.
        strip_inside_brackets=True   # do you want data removed in brackets or not?
    )

    @staticmethod
    def add_image_schema(writer):
        writer.cldf.add_table(
            'images.csv',
            {
                'name': 'ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id',
            },
            'Taxon_ID',
            'objid',
            'bitstreamid',
            {"name": "tags", "separator": ";"},
            'mime_type',
            'creator',
            'date',
            'place',
            'permission',
            'source',
            'Comment',
        )
        writer.cldf['images.csv', 'ID'].valueUrl = URITemplate(
            'https://cdstar.shh.mpg.de/bitstreams/{objid}/{bitstreamid}')
        writer.cldf.add_foreign_key('images.csv', 'Taxon_ID', 'ParameterTable', 'ID')
