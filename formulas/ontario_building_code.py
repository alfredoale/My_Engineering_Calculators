def specifiedsnowload_part9(Cb, Ss, Sr):
    S = max((Cb * Ss) + Sr, 1)
    return S


def basicsnowloadrooffactor_part9(roof_width):
    # Basic snow load roof factor, as per OBC Part 9
    # Roof width in meters
    if roof_width <= 4.3:
        Cb = 0.45
    else:
        Cb = 0.55
    return Cb


specifiedsnowload_part9_notes = """
    **Equation**
        
    S = C<sub>b</sub> * S<sub>s</sub> + S<sub>r</sub>

    **Notes**

    - Refer to O. Reg. 332/12: Building Code (2012), article 9.4.2.2. Specified Snow Loads.
    - The specified snow load must be at least 1 kPa. For bow string, arch, or semi-circular roof trusses with an unsupported span greater than 6 m, the design must comply with the snow load requirements in Subsection 4.1.6.
    - The basic snow load roof factor **C<sub>b</sub>**, is 0.45 for roofs with a width of 4.3 m or less and 0.55 for wider roofs.
    - [Find clossest location to an address.](https://www.google.com/maps/d/viewer?mid=1rOmkZ8IGp56MVXm2q9rcsw5Rxq8ErC0&femb=1&ll=48.278889463158336%2C-84.54679069999999&z=5)
"""
