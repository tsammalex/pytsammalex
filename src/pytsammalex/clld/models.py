try:
    import zope.interface
    import sqlalchemy as sa
    import sqlalchemy.orm as orm

    from clld import interfaces
    from clld.db import meta
    from clld.db.models import common
except ImportError:
    from unittest import mock
    zope = mock.Mock()
    sa = mock.Mock()
    orm = mock.Mock()
    interfaces = mock.Mock()
    class _TMP1(mock.Mock): pass
    class _TMP2(mock.Mock): pass
    meta = mock.Mock(Base=_TMP1)
    common = mock.Mock(IdNameDescriptionMixin=_TMP2)


class IEcoregion(zope.interface.Interface):
    """marker
    """


class TaxonMixin(object):
    genus = sa.Column(sa.Unicode)
    family = sa.Column(sa.Unicode)
    order = sa.Column(sa.Unicode)
    class_ = sa.Column(sa.Unicode)
    phylum = sa.Column(sa.Unicode)
    kingdom = sa.Column(sa.Unicode)
    genusKey = sa.Column(sa.Integer)
    familyKey = sa.Column(sa.Integer)
    orderKey = sa.Column(sa.Integer)
    classKey = sa.Column(sa.Integer)
    phylumKey = sa.Column(sa.Integer)
    kingdomKey = sa.Column(sa.Integer)
    rank = sa.Column(sa.Unicode, default='species')


class Biome(meta.Base, common.IdNameDescriptionMixin):
    """
    description holds a RGB color to use in maps.
    """


@zope.interface.implementer(IEcoregion)
class Ecoregion(meta.Base, common.IdNameDescriptionMixin):
    """
    Attribute_Label: ECO_NAME -> name
    Attribute_Definition: Ecoregion Name

    Attribute_Label: BIOME

    Attribute_Label: eco_code -> id
    Attribute_Definition:
        This is an alphanumeric code that is similar to eco_ID but a little easier to
        interpret. The first 2 characters (letters) are the realm the ecoregion is in.
        The 2nd 2 characters are the biome and the last 2 characters are the ecoregion
        number.

    Attribute_Label: GBL_STAT
    Attribute_Definition: Global Status
    Attribute_Definition_Source:
        A 30-year prediction of future conservation status given current conservation
        status and trajectories.

    Attribute_Label: area_km2
    Attribute_Definition: Area of the Ecoregion (km2)

    Attribute_Label: G200_REGIO -> description
    Attribute_Definition: Global 200 Name
    """
    realm = sa.Column(sa.Unicode, doc='Biogeographical realm')
    gbl_stat = sa.Column(
        sa.Unicode,
        doc='A 30-year prediction of future conservation status given current '
            'conservation status and trajectories.')
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    area = sa.Column(sa.Integer, doc='Area of the Ecoregion (km2)')
    biome_pk = sa.Column(sa.Integer, sa.ForeignKey('biome.pk'))
    biome = orm.relationship(
        Biome, backref=orm.backref('ecoregions', order_by=str('Ecoregion.id')))

    gbl_stat_map = {
        1: 'CRITICAL OR ENDANGERED'.lower(),
        2: 'VULNERABLE'.lower(),
        3: 'RELATIVELY STABLE OR INTACT'.lower(),
    }
    realm_map = dict(
        AA='Australasia',
        AN='Antarctic',
        AT='Afrotropics',
        IM='IndoMalay',
        NA='Nearctic',
        NT='Neotropics',
        OC='Oceania',
        PA='Palearctic',
    )

    def wwf_url(self):
        return 'http://www.worldwildlife.org/ecoregions/' + self.id.lower()
