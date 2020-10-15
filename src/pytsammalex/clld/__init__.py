try:
    from clld.interfaces import IIndex
except ImportError:
    IIndex = None

from pytsammalex.clld.models import Ecoregion, IEcoregion
from pytsammalex.clld.adapters import GeoJsonEcoregions


def includeme(config):
    config.registry.settings['mako.directories'].append('pytsammalex:clld/templates')
    config.register_resource('ecoregion', Ecoregion, IEcoregion, with_index=True)
    config.register_adapter(GeoJsonEcoregions, IEcoregion, IIndex)
