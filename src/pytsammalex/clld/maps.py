try:
    from clld.web.maps import Layer
except ImportError:
    from unittest import mock
    Layer = mock.Mock

from pytsammalex.clld.adapters import ECOREGIONS_TITLE


def gbif_occurrence_overlay(taxon):
    return {
        "name": "Occurrences of {} according to GBIF".format(taxon),
        "url": "https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png?"
               "style=classic.poly&bin=hex&hexPerTile=30&taxonKey=" + str(taxon.id),
        "options": {
            "attribution": "Occurrence data from <a href=\"https://www.gbif.org/\">GBIF</a>"},
    }


def get_layers(req):
    return Layer('ecoregions', ECOREGIONS_TITLE, req.route_url('ecoregions_alt', ext='geojson'))
