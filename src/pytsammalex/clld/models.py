try:
    from zope.interface import implementer, Interface
    from sqlalchemy import Column, Unicode, Integer, Float, ForeignKey
    from sqlalchemy.orm import relationship, backref

    from clld import interfaces
    from clld.db.meta import CustomModelMixin, Base
    from clld.db.models import common


    class IEcoregion(Interface):
        """marker
        """

    class TaxonMixin(object):
        genus = Column(Unicode)
        family = Column(Unicode)
        order = Column(Unicode)
        class_ = Column(Unicode)
        phylum = Column(Unicode)
        kingdom = Column(Unicode)
        genusKey = Column(Integer)
        familyKey = Column(Integer)
        orderKey = Column(Integer)
        classKey = Column(Integer)
        phylumKey = Column(Integer)
        kingdomKey = Column(Integer)
        rank = Column(Unicode, default='species')


    class Biome(Base, common.IdNameDescriptionMixin):
        """
        description holds a RGB color to use in maps.
        """


    @implementer(IEcoregion)
    class Ecoregion(Base, common.IdNameDescriptionMixin):
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
        realm = Column(Unicode, doc='Biogeographical realm')
        gbl_stat = Column(
            Unicode,
            doc='A 30-year prediction of future conservation status given current '
                'conservation status and trajectories.')
        latitude = Column(Float)
        longitude = Column(Float)
        area = Column(Integer, doc='Area of the Ecoregion (km2)')
        biome_pk = Column(Integer, ForeignKey('biome.pk'))
        biome = relationship(
            Biome, backref=backref('ecoregions', order_by=str('Ecoregion.id')))

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
except ImportError:
    pass
