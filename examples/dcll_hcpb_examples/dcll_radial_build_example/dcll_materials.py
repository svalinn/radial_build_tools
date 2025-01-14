import openmc
import json
import material_db_tools as mdbt


def mix_material_data():
    """
    Returns material dictionary with composition and citation information
    """
    material_dict = {
        "sol": {"composition": {"Void": 1.0}, "citation": "DavisFusEngDes_2018"},
        "fw_armor": {
            "composition": {"W": 1.0},
            "density_factor": 0.91,
            "citation": "ZhouEUDEMOHCPB_2023",
        },
        "fw": {
            "composition": {"MF82H": 0.34, "HeNIST": 0.66},
            "citation": "ZhouEUDEMOHCPB_2023",
        },
        "be_multiplier": {
            "composition": {"Be": 1.0},
            "citation": "DavisFusEngDes_2018",
        },
        "breeder": {
            "composition": {
                "Pb157Li90": 0.737,
                "SiC": 0.039,
                "HeNIST": 0.149,
                "MF82H": 0.075,
            },
            "citation": "ZhouEUDEMOHCPB_2023",
        },  # fix this
        "bw": {
            "composition": {"MF82H": 0.8, "HeNIST": 0.2},
            "citation": "DavisFusEngDes_2018",
        },
        "manifold": {
            "composition": {"MF82H": 0.3, "HeNIST": 0.7},
            "citation": "DavisFusEngDes_2018",
        },
        "hts": {
            "composition": {"HeNIST": 0.2, "MF82H": 0.28, "BMF82H": 0.52},
            "citation": "DavisFusEngDes_2018",
        },
        "gap_1": {"composition": {"Void": 1.0}, "citation": "DavisFusEngDes_2018"},
        "vv_front_plate": {
            "composition": {"SS316L": 1.0},
            "citation": "DavisFusEngDes_2018",
        },
        "vv_fill": {
            "composition": {"HeNIST": 0.4, "Cr3FS": 0.6},
            "citation": "DavisFusEngDes_2018",
        },
        "vv_back_plate": {
            "composition": {"SS316LN": 1.0},
            "citation": "DavisFusEngDes_2018",
        },
        "gap_2": {"composition": {"AirSTP": 1.0}, "citation": "ZhouEUDEMOHCPB_2023"},
        "lts": {
            "composition": {"Cr3FS": 0.39, "BMF82H": 0.29, "Water": 0.32},
            "citation": "DavisFusEngDes_2018",
        },
        "thermal_insulator": {
            "composition": {"AirSTP": 1.0},
            "citation": "ZhouEUDEMOHCPB_2023",
        },
        "coil_pack": {
            "composition": {"SS316LN": 1.0},
            "citation": "DavisFusEngDes_2018",
        },
    }
    return material_dict


def mix_materials(material_dict):
    """
    Uses material dictionary and material_db_tools to create a PyNE material library
    """
    # Load pure material library
    mat_lib = mdbt.MaterialLibrary()
    mat_lib.from_json("PureFusionMaterials_libv1.json")

    # create material library object
    mixmat_lib = mdbt.MaterialLibrary()
    for mat_name, mat_data in material_dict.items():
        if "Void" in mat_data["composition"].keys():
            continue
        mixmat_lib[mat_name] = mdbt.mix_by_volume(
            mat_lib,
            mat_data["composition"],
            mat_data["citation"],
            density_factor=mat_data.get("density_factor", 1),
        )
    return mixmat_lib


# write DCLL material library
def main():
    """
    Writes OpenMC materials object file
    """
    material_dict = mix_material_data()
    mixmat_lib = mix_materials(material_dict)
    mixmat_lib.write_openmc("mixedMaterialsDCLL_libv1.xml")


if __name__ == "__main__":
    main()
