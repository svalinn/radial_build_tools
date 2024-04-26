import numpy as np
import plot_radial_build


def plot_parastell_build(build, phi, theta, title, colors=None,
                         max_characters=35, max_thickness=1e6, size=(8, 4),
                         unit='cm', write_yml = True):
    """
    Use the plot_radial_build script to generate a png plot and yml definition
    from a parastell build dict.

    Arguments:
    build (dict): dictionary of list of toroidal and poloidal angles, as
            well as dictionary of component names with corresponding thickness
            matrix and optional material tag to use in H5M neutronics model.
            The thickness matrix specifies component thickness at specified
            (polidal angle, toroidal angle) pairs. This dictionary takes the
            form
            {
                'phi_list': toroidal angles at which radial build is specified.
                'theta_list': poloidal angles at which radial build is
                    specified.
                'wall_s': closed flux surface label extrapolation at wall
                    (float),
                'radial_build': {
                    'component': {
                        'thickness_matrix': list of list of float (cm),
                        'h5m_tag': h5m_tag (str)
                    }
                }
            }
    phi (float): torodial angle in degrees. Must be in the phi_list of the
        build dict.
    theta (float): poloidal angle in degrees. Must be in the theta_list of the
        build dict.
    title (string): title for plot and filename to save to
    colors (list of str): list of matplotlib color strings. 
        If specific colors are desired for each layer they can be added here
    max_characters (float): maximum length of a line before wrapping the 
        text
    max_thickness (float): maximum thickness of layer to display, useful
        for reducing the total size of the figure.
    size (iter of float): figure size, inches. (width, height)
    unit (str): Unit of thickness values
    """
    # access the thickness values at given theta phi
    phi_list = build['phi_list']
    theta_list = build['theta_list']
    radial_build = build['radial_build']

    phi_index = np.where(phi_list == phi)[0]
    theta_index = np.where(theta_list == theta)[0]

    plotter_build = {}
    #build the dictionary for plotting
    for layer_name, layer in radial_build.items():
        thickness = float(layer['thickness_matrix'][phi_index, theta_index][0])
        material = layer['h5m_tag']
        plotter_build[layer_name] = {"thickness": thickness,
                                     "composition":{material: 1}
                                     }
    plot_radial_build.plot_radial_build(plotter_build, title, colors,
                                        max_characters, max_thickness, size,
                                        unit)

