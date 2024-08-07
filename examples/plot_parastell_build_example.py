import numpy as np
from radial_build_tools import RadialBuildPlot

num_phi = 80
num_theta = 90

phi_list = np.linspace(0, 90, num_phi)
theta_list = np.linspace(0, 360, num_theta)
ones = np.ones((len(phi_list), len(theta_list)))

build = {
    "phi_list": phi_list,
    "theta_list": theta_list,
    "wall_s": 1.2,
    "radial_build": {
        "fw": {"thickness_matrix": ones * 4, "h5m_tag": "FNSFFW"},  # cell 3
        "breeder": {
            "thickness_matrix": ones * 50,  # cell 4
            "h5m_tag": "FNSFDCLL",
        },
        "BW": {"thickness_matrix": ones * 2, "h5m_tag": "FNSFBW"},  # cell 5
        "manifolds": {
            "thickness_matrix": ones * 6,  # cell 6
            "h5m_tag": "FNSFHeManifolds",
        },
        "HTS": {"thickness_matrix": ones * 20, "h5m_tag": "FNSFIBSR"},  # cell 7
        "Gap_1": {"thickness_matrix": ones * 1, "h5m_tag": "Vacuum"},  # cell 8
        "vvfrontplate": {
            "thickness_matrix": ones * 2,  # cell 9
            "h5m_tag": "SS316L",
        },
        "VVFill": {
            "thickness_matrix": ones * 6,  # cell 10
            "h5m_tag": "VVFill",
        },
        "VVBackPlate": {
            "thickness_matrix": ones * 2,  # cell 11
            "h5m_tag": "SS316L",
        },
        "Gap_2": {"thickness_matrix": ones * 2, "h5m_tag": "AirSTP"},  # cell 12
        "LTS": {"thickness_matrix": ones * 23, "h5m_tag": "LTS"},  # cell 13
        "Thermal_Insulator": {
            "thickness_matrix": ones * 10,  # cell 14
            "h5m_tag": "AirSTP",
        },
        "coilfrontplate": {
            "thickness_matrix": ones * 2,  # cell 15
            "h5m_tag": "coils",
        },
        "coils": {
            "thickness_matrix": ones * 50.5,  # cell 16
            "h5m_tag": "coils",
        },
    },
}

rbp = RadialBuildPlot.from_parastell_build(build, phi_list[-1], theta_list[-1])

# create the radial build plot png
rbp.title = "Example Parastell Build"
rbp.plot_radial_build()
rbp.to_png()

# save the plot configuration as a yml file
rbp.write_yml()
