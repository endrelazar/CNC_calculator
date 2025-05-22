import math

def atmero_melysegen(alpha_fok,melyseg_mm):
    alpha_rad = math.radians(alpha_fok/2)
    diameter = 2 * melyseg_mm *math.tan(alpha_rad)
    return diameter
def melyseg_valtozas(alpha_fok,diameter_mm):
    alpha_rad = math.radians(alpha_fok/2)
    melyseg_mm = diameter_mm/(2*math.tan(alpha_rad))
    return melyseg_mm
def melyseg_sugarbol(alpha_fok, sugar_mm):
    alpha_rad = math.radians(alpha_fok / 2)
    d = sugar_mm * math.tan(alpha_rad)
    return d
def sugar_melysegbol(alpha_fok, melyseg_mm):
    alpha_rad = math.radians(alpha_fok / 2)
    r = melyseg_mm / math.tan(alpha_rad)
    return r


def forgacsolo_sebesseg(atmero_mm, fordulat_rpm):
    return math.pi * atmero_mm * fordulat_rpm / 1000 

def elotolasi_sebesseg_furo(fordulat_rpm, elotolas_mm_per_rev):
    return fordulat_rpm * elotolas_mm_per_rev       

def elotolasi_sebesseg_maro(fordulat, fogelotol, fogsz):
    return fordulat * fogelotol * fogsz

def szeradatbol_fordulat(vagoseb, szeratmero,):
    return (1000 * vagoseb) / (szeratmero * math.pi)

def menet_parameter(fordulat, menetem):
    return (menetem * fordulat,2)
    