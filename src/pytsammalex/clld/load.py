import pathlib
import functools
import itertools

from clldutils import jsonlib
from clldutils.misc import nfilter
import pycldf

import pytsammalex
from pytsammalex.gbif import GBIF
from pytsammalex.clld.models import TaxonMixin, Biome, Ecoregion

try:
    from clld.cliutil import Data
except ImportError:
    Data = None


def iter_datasets(default_dir, filter=None, exclude=('bin', 'lib', 'share', 'include', 'man')):
    d = input('Directory containing the datasets [{}]:'.format(default_dir)) or default_dir
    for dd in pathlib.Path(d).iterdir():
        if dd.is_dir() and dd.name in exclude:
            continue
        for ds in pycldf.iter_datasets(dd):
            if (filter is None) or filter(ds):
                yield ds


def iter_taxa(cldf, language_tags, seen=None, enrich=False):
    """
    Iterate over a datasets' taxa, yielding a `dict` of taxon data for each `GBIF_ID` not yet in
    `seen`.

    :param cldf: `pycldf.Dataset` instance.
    :param language_tags: A `set` of ISO 639-2 language tags for which to retrieve vernacular \
    names for the taxon from GBIF.
    :param seen: `set` of already encountered `GBIF_ID`s
    :return: Generator of triples (parameter `dict`, vernacular names `dict`, taxon data `dict`).
    """
    seen = set() if seen is None else seen
    for param in cldf.iter_rows('ParameterTable', 'id', 'concepticonReference', 'name'):
        if (not param['GBIF_ID']) or param['GBIF_ID'] == '-':
            continue
        if param['GBIF_ID'] in seen:
            continue

        seen.add(param['GBIF_ID'])
        vnames = GBIF().get_vernacular_names(
            param['GBIF_ID'], param['rank'], language_tags=language_tags)
        taxon = {k: param.get(k) for k in dir(TaxonMixin) if not k.startswith('_')}
        if any(v is None for v in taxon.values()) and enrich:
            gbif_data = GBIF().usage(key=param['GBIF_ID'])
            taxon.update({k: gbif_data.get(k.replace('_', '')) for k in taxon})

        yield param, vnames, taxon


def get_center(arr):
    return functools.reduce(
        lambda x, y: [x[0] + y[0] / len(arr), x[1] + y[1] / len(arr)], arr, [0.0, 0.0])


def load_ecoregions(filter=None):
    """

    :param data:
    :param filter:
    :return:
    """
    ecoregions = jsonlib.load(
        pathlib.Path(pytsammalex.__file__).parent / 'ecoregions.json')['features']

    biome_map = {
        1: ('Tropical & Subtropical Moist Broadleaf Forests', '008001'),
        2: ('Tropical & Subtropical Dry Broadleaf Forests', '557715'),
        3: ('Tropical & Subtropical Coniferous Forests', ''),
        4: ('Temperate Broadleaf & Mixed Forests', ''),
        5: ('Temperate Conifer Forests', ''),
        6: ('Boreal Forests/Taiga', ''),
        7: ('Tropical & Subtropical Grasslands, Savannas & Shrublands', '98ff66'),
        8: ('Temperate Grasslands, Savannas & Shrublands', ''),
        9: ('Flooded Grasslands & Savannas', '0265fe'),
        10: ('Montane Grasslands & Shrublands', 'cdffcc'),
        11: ('Tundra', ''),
        12: ('Mediterranean Forests, Woodlands & Scrub', 'cc9900'),
        13: ('Deserts & Xeric Shrublands', 'feff99'),
        14: ('Mangroves', '870083'),
    }

    data = Data()
    for eco_code, features in itertools.groupby(
            sorted(ecoregions, key=lambda e: e['properties']['eco_code']),
            key=lambda e: e['properties']['eco_code']):
        features = list(features)
        props = features[0]['properties']
        if filter and not filter(eco_code, props):
            continue

        if int(props['BIOME']) not in biome_map:
            continue

        biome = data['Biome'].get(props['BIOME'])
        if not biome:
            name, color = biome_map[int(props['BIOME'])]
            biome = data.add(
                Biome, props['BIOME'],
                id=str(int(props['BIOME'])),
                name=name,
                description=color or 'ffffff')
        centroid = (None, None)
        f = sorted(features, key=lambda _f: _f['properties']['AREA'])[-1]
        if f['geometry']:
            coords = f['geometry']['coordinates'][0]
            if f['geometry']['type'] == 'MultiPolygon':
                coords = coords[0]
            centroid = get_center(coords)

        polygons = nfilter([_f['geometry'] for _f in features])
        data.add(
            Ecoregion, eco_code,
            id=eco_code,
            name=props['ECO_NAME'],
            description=props['G200_REGIO'],
            latitude=centroid[1],
            longitude=centroid[0],
            biome=biome,
            area=props['area_km2'],
            gbl_stat=Ecoregion.gbl_stat_map[int(props['GBL_STAT'])],
            realm=Ecoregion.realm_map[props['REALM']],
            jsondata=dict(polygons=polygons))
