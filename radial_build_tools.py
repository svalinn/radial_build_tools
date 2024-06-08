import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors
import yaml
import argparse
import numpy as np
import openmc
import textwrap


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
                    }
                }
            The dict corresponding to each "layer_name" key may be empty,
            or have any combination of entries.
                title (string): title for plot and filename to save to
        colors (list of str): list of matplotlib color strings.
            If specific colors are desired for each layer they can be added
            here
        max_characters (float): maximum length of a line before wrapping the
            text
        max_thickness (float): maximum thickness of layer to display, useful
            for reducing the total size of the figure.
        size (iter of float): figure size, inches. (width, height)
        unit (str): Unit of thickness values
    """

    def __init__(
        self,
        build,
        title="radial_build",
        colors=None,
        max_characters=35,
        max_thickness=1e6,
        size=(8, 4),
        unit="cm",
    ):
        self.build = build
        self.title = title
        if colors is None:
            self.colors = list(matplotlib.colors.XKCD_COLORS.values())[
                0 : len(self.build)
            ]
        self.max_characters = max_characters
        self.max_thickness = max_thickness
        self.size = size
        self.unit = unit

    def build_composition_string(self, composition):
        """
        Assembles string from composition dict for use in radial build plot

        Arguments:
            composition (dict): "material name (str)":volume_fraction (float)

        Returns:
            comp_string (string): formatted string with material definition
        """

        comp_string = ""
        for material, fraction in composition.items():

            mat_string = f"{material}: {round(fraction*100, 3)}%, "
            comp_string += mat_string
        comp_string = textwrap.fill(
            comp_string, width=self.max_characters, drop_whitespace=False
        )

        return comp_string[0:-2] + "\n"

    def write_yml(self):
        """
        Writes yml file defining radial build plot. File will be called
        title.yml
        """

        data_dict = self.__dict__

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
        min_line_height = 8
        min_lines = 2

        visual_thickness = layer.get("thickness", min_line_height)
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

        min_thickness = (min_lines + newlines) * min_line_height

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
        return fig

    def to_png(self, filename=None):
        """
        Write the plot to a png file.

        Arguments:
            filename (str): Optional, file name to write the plot to. If None,
                file name will be the same as the plot title
        """
        if filename is None:
            filename = self.title.replace(" ", "")

        fig = self.plot_radial_build()
        fig.savefig(f"{filename}.png", dpi=200)

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
                            "material": OpenMC material
                    }
                }
            The dict corresponding to each "layer_name" key may be empty,
            or have any combination of entries.

    """

    def __init__(self, build, a, b, c):
        self.build = build
        self.a = a
        self.b = b
        self.c = c
        self.build_surfaces()
        self.build_regions()
        self.build_cells()
        self.get_bounded_geometry()

    def build_surfaces(self):
        """
        Build the surfaces representing the radial build using OpenMC CSG.
        """
        a = self.a
        b = self.b
        c = self.c
        # build surfaces
        surfaces = {}

        surfaces["plasma_surface"] = openmc.ZTorus(a=a, b=b, c=c)

        for surface, surface_dict in self.build.items():
            if surface_dict["thickness"] != 0:
                b += surface_dict["thickness"]
                c += surface_dict["thickness"]
                surfaces[surface] = openmc.ZTorus(a=a, b=b, c=c)

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
            ** 0.5
            + 100,
            boundary_type="vacuum",
        )

        vac_region = -vac_surf & +self.surfaces[self.surf_list[-1]]
        vac_cell = openmc.Cell(region=vac_region, name="vac_cell")

        self.cell_list.append(vac_cell)
        self.cell_dict["vac_cell"] = vac_cell

        self.geometry = openmc.Geometry(self.cell_list)

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

    # default data for running from command line
    data_default = {
        "title": "Radial Build",
        "colors": None,
        "max_characters": 35,
        "max_thickness": 1e6,
        "size": (8, 4),
        "unit": "cm",
    }

    args = parse_args()
    data = read_yaml(args.filename)

    data_dict = data_default.copy()
    data_dict.update(data)

    rb = radial_build(data_dict["build"])

    rb.plot_radial_build(
        title=data_dict["title"],
        colors=data_dict["colors"],
        max_characters=data_dict["max_characters"],
        max_thickness=data_dict["max_thickness"],
        size=data_dict["size"],
        unit=data_dict["unit"],
    )


if __name__ == "__main__":
    main()
