import openmc
from radial_build_tools import ToroidalModel, RadialBuildPlot
from dcll_materials import mix_material_data
import argparse


def make_build_dict():
    """
    Returns a build dictionary for use with radial_build_tools, includes material name,
    composition and layer thickness
    """
    build_dict = {
        "sol": {"thickness": 5, "composition": {"Void": 1.0}},
        "fw_armor": {
            "thickness": 0.2,
        },
        "fw": {
            "thickness": 3.8,
        },
        "be_multiplier": {
            "thickness": 0,
        },
        "breeder": {"thickness": 50, "scores": ["flux", "H3-production"]},
        "bw": {
            "thickness": 2,
        },
        "manifold": {
            "thickness": 6,
        },
        "hts": {"thickness": 10},
        "gap_1": {"thickness": 1, "composition": {"Void": 1.0}},
        "vv_front_plate": {
            "thickness": 2,
        },
        "vv_fill": {
            "thickness": 6,
        },
        "vv_back_plate": {
            "thickness": 2,
        },
        "gap_2": {
            "thickness": 2,
        },
        "lts": {"thickness": 10},
        "thermal_insulator": {
            "thickness": 10,
        },
        "coil_pack": {
            "thickness": 52,
        },
    }
    material_dict = mix_material_data()
    for layer_name, properties in build_dict.items():
        if "composition" not in properties.keys():
            properties["material_name"] = layer_name
            properties["composition"] = material_dict[layer_name][
                "composition"
            ]
    return build_dict


def plot_dcll_radial_build(build_dict):
    """
    Makes a radial build plot of the model from the build dictionary
    """
    rbp = RadialBuildPlot(build_dict, title="Toroidal Model DCLL", size=(9, 4))
    rbp.plot_radial_build()
    rbp.to_png()


def main():
    """
    Writes model XML from ToroidalModel
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Call the plotting function if this flag is provided.",
    )
    args = parser.parse_args()

    major_radius = 800
    minor_radius_z = 114
    minor_radius_xy = 114
    materials = openmc.Materials.from_xml("mixedMaterialsDCLL_libv1.xml")

    build_dict = make_build_dict()

    toroidal_model = ToroidalModel(
        build_dict, major_radius, minor_radius_z, minor_radius_xy, materials
    )

    model, cells = toroidal_model.get_openmc_model()
    model.export_to_model_xml()
    build_dict = make_build_dict()
    if args.plot:
        plot_dcll_radial_build(build_dict)


if __name__ == "__main__":
    main()
