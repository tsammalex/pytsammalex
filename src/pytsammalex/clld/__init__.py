try:
    from clld.interfaces import IIndex

    from pytsammalex.clld.models import Ecoregion, IEcoregion
    from pytsammalex.clld.adapters import GeoJsonEcoregions

    def includeme(config):
        config.register_resource('ecoregion', Ecoregion, IEcoregion, with_index=True)
        config.registry.settings['mako.directories'].append(
            'pytsammalex:clld/templates')

        #config.register_adapters([[IFamily] + spec for spec in specs])
        #config.register_map('family', Map)
        #config.register_datatable('familys', Familys)
        config.register_adapter(GeoJsonEcoregions, IEcoregion, IIndex)

except ImportError:
    pass
