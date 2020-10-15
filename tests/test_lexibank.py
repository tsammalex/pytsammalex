from pytsammalex.lexibank import *


def test_Dataset():
    class DS(Dataset):
        id = 'x'
    ds = DS()
    assert ds.concept_class == Taxon
