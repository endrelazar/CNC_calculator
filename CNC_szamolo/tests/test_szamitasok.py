import pytest
import sys
import os
import szamitasok


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_atmero_melysegen():
    # Példa: alpha_fok=90, melyseg_mm=10
    assert szamitasok.atmero_melysegen(90, 10) == pytest.approx(20.0, rel=1e-2)

def test_forgacsolo_sebesseg():
    # Példa: atmero_mm=10, fordulat_rpm=1000
    assert szamitasok.forgacsolo_sebesseg(10, 1000) == pytest.approx(31.4159, rel=1e-2)

def test_elotolasi_sebesseg_furo():
    # Példa: fordulat_rpm=1000, elotolas_mm_per_rev=0.2
    assert szamitasok.elotolasi_sebesseg_furo(1000, 0.2) == pytest.approx(200, rel=1e-2)