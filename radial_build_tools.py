import yaml
import argparse
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors
import numpy as np
import openmc
import textwrap
import random


class RadialBuildPlot(object):
    """
    Uses a radial build definition to generate radial build plots.

    Parameters
        build (dict): {"layer name": {
                            "thickness": (float),
                            "composition": {
                                "material name": fraction (float)
                                },
                            "description": (str),
                            "color": (str): Optional matplotlib color string 
                                          or hex code to specify the layer's color.
                    }
                }
            The dict corresponding to each "layer_name" key may be empty,
            or have any combination of entries.
    Optional attributes:
        title (string): title for plot and filename to save to
        colors (list of str): list of matplotlib color strings.
            If specific colors are desired for each layer they can be added
            here.
        max_characters (float): maximum length of a line before wrapping the
            text
        max_thickness (float): maximum thickness of layer to display, useful
            for reducing the total size of the figure.
        size (iter of float): figure size, inches. (width, height)
        unit (str): Unit of thickness values
    """

    def __init__(self, build, **kwargs):
        self.build = build
        self.title = "radial_build"
        self.max_characters = 35
        self.max_thickness = 1e6
        self.size = (8, 4)
        self.unit = "cm"
        for name in kwargs.keys() & (
            "title",
            "colors",
            "max_characters",
            "max_thickness",
            "size",
            "unit",
        ):
            self.__setattr__(name, kwargs[name])

        self.used_colors = set()
        self.available_colors = set(matplotlib.colors.XKCD_COLORS.values())
        self.colors = self.assign_colors()

    def assign_colors(self):
        """
        Assign colors to each layer in the build definition using a two-phase approach:

        Phase 1: Handle Pre-specified Colors
            - Loop 1 iterates through the build dictionary and checks for the 'color' key.
            - If a pre-specified color is found, it is added to the `used_colors` set.
            - The color is also removed from the `available_colors` set to avoid random reassignment.
            - Layers with pre-specified colors will always use those colors, even if they duplicate others.

        Phase 2: Assign Unique Colors to Unspecified Layers
            - Loop 2 iterates through layers that do not have a pre-specified color.
            - For these layers, a random color is chosen from the `available_colors` set.
            - This ensures that auto-assigned colors are unique and do not duplicate either user-specified or previously assigned colors.
            - Once a color is assigned, it is removed from `available_colors` and added to `used_colors`.

        Returns:
            list of str: A list of color strings corresponding to each layer in the build.
        """
        colors = []
        for layer in self.build.values():
            # Check for user-specified colors
            if "color" in layer:
                color = layer["color"]
                self.used_colors.add(color)  # Mark as used
                self.available_colors.discard(color)  # Remove from available pool
            else:
                # Assign a unique random color
                color = self.generate_unique_color()
                layer["color"] = color  # Store the color in the layer

            colors.append(color)  # Add the color to the list for this layer

        return colors

    def generate_unique_color(self):
        """
        Generate a random color that has not been used yet. Ensures a color
        isn't randomly selected that has already been used.
        """
        color = random.choice(list(self.available_colors))
        self.available_colors.remove(color)  # Remove chosen color
        self.used_colors.add(color)  # Add to used colors
        return color
    
    def build_composition_string(self, composition):
        """
        Assembles string from composition dict for use in radial build plot

        Arguments:
            composition (dict): "material name (str)":volume_fraction (float)

        Returns:
            comp_string (string): formatted string with composition definition
        """

        mat_strings = [
            f"{mat}: {round(frac*100,3)}%" for mat, frac in composition.items()
        ]

        comp_string = (
            textwrap.fill(", ".join(mat_strings), width=self.max_characters)
            + "\n"
        )

        return comp_string

    def write_yml(self):
        """
        Writes yml file defining radial build plot. File will be called
        title.yml
        """

        data_dict = self.__dict__

        del data_dict["figure"]

        filename = self.title.replace(" ", "") + ".yml"

        with open(filename, "w") as file:
            yaml.safe_dump(
                data_dict, file, default_flow_style=False, sort_keys=False
            )

    def get_layer_string(self, name, layer):
        """
        Processes a layer in the radial build dict to get formatted text for
        the plot

        Returns:
            text (str): formatted text for layer
            visual_thickness (float): width of the rectangle for the layer
        """
        min_line_height = 9
        visual_thickness = min_line_height

        thickness_str = ""
        if "thickness" in layer:
            thickness_str = f': {layer["thickness"]} {self.unit}'
            visual_thickness = layer["thickness"]

        comp_string = ""
        if "composition" in layer:
            comp_string = self.build_composition_string(layer["composition"])

        description_str = ""
        if "description" in layer:
            description_str = textwrap.fill(
                f'{layer["description"]}',
                self.max_characters,
                drop_whitespace=False,
            )

        # ensure sensible line breaks, this is the simplest way I have
        # found due to how the above fields can be combined
        text = f"{name}{thickness_str}\n{comp_string}{description_str}".rstrip()

        newlines = text.count("\n")

        min_thickness = (newlines + 1) * min_line_height

        visual_thickness = min(
            max(visual_thickness, min_thickness), self.max_thickness
        )

        return text, visual_thickness

    def plot_radial_build(self):
        """
        Creates a radial build plot, with layers scaled between a minimum and
        maximum pixel width to preserve readability.

        Returns:
            fig (matplotlib figure): figure containing radial build plot
        """

        char_to_height = 1.15
        height = char_to_height * self.max_characters

        # initialize list for lower left corner of each layer rectangle
        ll = [0, 0]
        fig = plt.figure(figsize=self.size)
        plt.tight_layout()
        ax = plt.gca()
        ax.set_ylim(0, height + 1)

        total_thickness = 0
        for (name, layer), color in zip(self.build.items(), self.colors):

            if layer.get("thickness") == 0:
                continue

            layer_str, visual_thickness = self.get_layer_string(name, layer)

            ax.add_patch(
                Rectangle(
                    ll,
                    visual_thickness,
                    height,
                    facecolor=color,
                    edgecolor="black",
                )
            )

            centerx = ll[0] + visual_thickness / 2 + 1
            centery = height / 2
            plt.text(
                centerx,
                centery,
                layer_str,
                rotation="vertical",
                ha="center",
                va="center",
            )

            ll[0] += float(visual_thickness)

            total_thickness += visual_thickness

        ax.set_xlim(-1, total_thickness + 1)
        ax.set_axis_off()
        plt.title(self.title)
        self.figure = fig

    def to_png(self, filename=None):
        """
        Write the plot to a png file.

        Arguments:
            filename (str): Optional, file name to write the plot to. If None,
                file name will be the same as the plot title
        """
        if filename is None:
            filename = self.title.replace(" ", "")

        self.figure.savefig(f"{filename}.png", dpi=200)

    @classmethod
    def from_parastell_build(cls, parastell_build_dict, phi, theta):

        # access the thickness values at given theta phi
        phi_list = parastell_build_dict["phi_list"]
        theta_list = parastell_build_dict["theta_list"]
        radial_build = parastell_build_dict["radial_build"]

        phi_index = np.where(phi_list == phi)[0]
        theta_index = np.where(theta_list == theta)[0]
        build = {}
        # build the dictionary for plotting
        for layer_name, layer in radial_build.items():
            thickness = float(
                layer["thickness_matrix"][phi_index, theta_index][0]
            )
            material = layer["h5m_tag"]
            build[layer_name] = {
                "thickness": thickness,
                "description": material,
            }

        radial_build = cls(build)

        return radial_build


class ToroidalModel(object):
    """
    An object that uses a radial build definition generate OpenMC models
    with toroidal geometry.

    Parameters
        build (dict): {"layer name": {
                            "thickness": (float),
                            "composition": {
                                "material name": fraction (float)
                                },
                            "material_name": (str) name of material in
                                associated OpenMC material library. To have a
                                layer with vacuum/void do not include the
                                'material_name' key.
                            "color": (str): Optional matplotlib color string 
                                          or hex code to specify the layer's color.
                    }
                }
            The dict corresponding to each "layer_name" key may be empty,
            or have any combination of entries.
        major_rad (float): major radius of the torus
        minor_rad_z (float): minor radius of the plasma region parallel to the
            z axis
        minor_rad_xy (float): minor radius of the plasma region perpendicular
            to the z axis
        materials (str or OpenMC Materials object): path to the OpenMC materials
            xml file for this model, or the corresponding Materials OpenMC
            object
    """

    def __init__(self, build, major_rad, minor_rad_z, minor_rad_xy, materials):
        self.build = build
        self.major_rad = major_rad
        self.minor_rad_z = minor_rad_z
        self.minor_rad_xy = minor_rad_xy
        if isinstance(materials, str):
            self.input_materials = openmc.Materials.from_xml(materials)
        else:
            self.input_materials = materials

        self.assign_materials()

    def assign_materials(self):
        """
        Assign OpenMC material objects to each layer in the build dict
        """
        for layer_name, layer_data in self.build.items():
            if "material_name" in layer_data:
                layer_data["material"] = self.get_material_by_name(
                    layer_data["material_name"]
                )
            else:
                layer_data["material"] = None

    def get_material_by_name(self, material_name):
        """
        Search the materials object for a material with a matching name. Openmc
        allows duplicate names, and names are not required, be advised.

        Arguments:
            materials (OpenMC Materials Object): material library to search
            material (string): name of material to be returned

        Returns:
            mat (OpenMC material object): material object with matching name
        """
        for mat in self.input_materials:
            if mat.name == material_name:
                return mat
        # if this returns none, openmc will just assign vacuum to any cell
        # using this material
        raise ValueError(
            f"no material name {material_name} was found in the library"
        )

    def build_surfaces(self):
        """
        Build the surfaces representing the radial build using OpenMC CSG.
        """
        major_rad = self.major_rad
        minor_rad_z = self.minor_rad_z
        minor_rad_xy = self.minor_rad_xy
        # build surfaces
        surfaces = {}

        surfaces["plasma_surface"] = openmc.ZTorus(
            a=major_rad, b=minor_rad_z, c=minor_rad_xy
        )

        for surface, surface_dict in self.build.items():
            if surface_dict["thickness"] != 0:
                minor_rad_z += surface_dict["thickness"]
                minor_rad_xy += surface_dict["thickness"]
                surfaces[surface] = openmc.ZTorus(
                    a=major_rad, b=minor_rad_z, c=minor_rad_xy
                )

        self.surfaces = surfaces

    def build_regions(self):
        """
        Build OpenMC regions from the surfaces defined by the build dict
        """
        # build regions
        regions = {}

        regions["plasma"] = -self.surfaces["plasma_surface"]

        surf_list = list(self.surfaces.keys())

        for inner_surf, outer_surf in zip(surf_list[0:-1], surf_list[1:]):
            regions[outer_surf] = (
                -self.surfaces[outer_surf] & +self.surfaces[inner_surf]
            )

        self.regions = regions
        self.surf_list = surf_list

    def build_cells(self):
        """
        Build OpenMC cells from the regions defined by the build dict
        """
        # build cells
        cell_dict = {}
        materials = set()

        cell_dict["plasma_cell"] = openmc.Cell(
            region=self.regions["plasma"], name="plasma_cell"
        )

        for layer, layer_def in self.build.items():
            if layer_def["thickness"] != 0:
                cell_dict[layer] = openmc.Cell(
                    region=self.regions[layer],
                    name=layer,
                    fill=layer_def["material"],
                )
                materials.add(layer_def["material"])

        self.cell_list = list(cell_dict.values())
        self.cell_dict = cell_dict
        self.materials = materials.discard(None)

    def get_bounded_geometry(self):
        """
        Get an OpenMC geometry instances containing all cells, plus a bounding
        vacuum cell
        """
        unbounded_geometry = openmc.Geometry(self.cell_list)

        bounding_box = unbounded_geometry.bounding_box

        vac_surf = openmc.Sphere(
            r=np.sum(
                np.multiply(
                    (bounding_box[1] - bounding_box[0]),
                    (bounding_box[1] - bounding_box[0]),
                )
            )
            ** 0.5,
            boundary_type="vacuum",
        )

        vac_region = -vac_surf & +self.surfaces[self.surf_list[-1]]
        vac_cell = openmc.Cell(region=vac_region, name="vac_cell")

        self.cell_list.append(vac_cell)
        self.cell_dict["vac_cell"] = vac_cell

        self.geometry = openmc.Geometry(self.cell_list)

    def build_openmc_model(self):
        """
        Builds openmc model using the build definition
        """
        self.build_surfaces()
        self.build_regions()
        self.build_cells()
        self.get_bounded_geometry()

    def get_openmc_model(self):
        """
        Return toroidal model built using the build definition, contains
        geometry and material information

        Returns:
            model (openmc model): Model containing materials and geometry
                from the build dict.
            cells (dict): dict mapping layer names to openmc cell instances in
                the model object returned by this function.
        """
        self.build_openmc_model()
        model = openmc.Model(geometry=self.geometry, materials=self.materials)
        return model, self.cell_dict
    

def parse_args():
    """Parser for running as a script"""
    parser = argparse.ArgumentParser(prog="plot_radial_build")

    parser.add_argument("filename", help="YAML file defining radial build")

    return parser.parse_args()


def read_yaml(filename):
    """Reads yaml file to extract title and build variables"""
    with open(filename) as file:
        data = yaml.safe_load(file)

    return data


def main():
    args = parse_args()
    data = read_yaml(args.filename)

    rbp = RadialBuildPlot(**data)
    rbp.plot_radial_build()
    rbp.to_png()


if __name__ == "__main__":
    main()
