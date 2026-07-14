import pytest
import openmc
from radial_build_tools import ToroidalModel,read_yaml,parse_args

def make_materials():

    RAFM = openmc.Material(name="RAFM")
    RAFM.add_element("Fe", 1.0)
    RAFM.set_density("g/cm3", 7.8)

    return openmc.Materials([RAFM])

def test_surfaces_created():

    data = read_yaml("examples/ExampleRadialBuild.yml")

    build = {
        "inboard": data["inboard"],
        "outboard": data["outboard"],
    }

    tm = ToroidalModel(
        build,
        800,
        300,
        100,
        make_materials(),
    )

    tm.get_openmc_model()
    assert "plasma_surface" in tm.surfaces
    assert "FW_ib" in tm.surfaces
    assert "FW_ob" in tm.surfaces
    assert "breeder_ib" in tm.surfaces
    assert "breeder_ob" in tm.surfaces