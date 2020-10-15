try:
    from clld.web.adapters.geojson import GeoJson
except ImportError:
    GeoJson = object

ECOREGIONS_TITLE = "WWF's Terrestrial Ecoregions"


class GeoJsonEcoregions(GeoJson):
    def featurecollection_properties(self, ctx, req):
        return {'name': ECOREGIONS_TITLE}

    def get_features(self, ctx, req):
        for ecoregion in ctx.get_query():
            for polygon in ecoregion.jsondata['polygons']:
                yield {
                    'type': 'Feature',
                    'properties': {
                        'id': ecoregion.id,
                        'label': '%s %s' % (ecoregion.id, ecoregion.name),
                        'color': ecoregion.biome.description,
                        'language': {'id': ecoregion.id},
                        'latlng': [ecoregion.latitude, ecoregion.longitude],
                    },
                    'geometry': polygon,
                }
