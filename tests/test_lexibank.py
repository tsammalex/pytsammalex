from pytsammalex.lexibank import *


def test_Dataset():
    class DS(Dataset):
        id = 'x'
    ds = DS()
    try:
        assert ds.concept_class == Taxon
    except AttributeError:  # run with no pylexibank installed
        pass

