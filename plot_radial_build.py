import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors
import yaml
import argparse
import numpy as np

class radial_build(object):

    """
    A representation of a radial build for plotting

    Parameters
        `build (dict): {"layer name": {"thickness": (float),
                                "composition": {
                                "material name": fraction (float)
                        }
                    }
        `        }
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

    def __init__(
            self,
            build,
            title,
            colors=None,
            max_characters = 35,
            max_thickness = 1e6,
            size = (8,4),
            unit = 'cm'
    ):
        self.build = build
        self.title = title
        if colors == None:
            self.colors = list(matplotlib.colors.XKCD_COLORS.values())[0:len(build)]
        else:
            self.colors = colors
        self.max_characters = max_characters
        self.max_thickness = max_thickness
        self.size = size
        self.unit = unit

    def wrap_text(self, text):
        """
        loop thru text, if line length is too long, go back and replace the 
        previous space with a linebreak

        Arguments: 
            text (str): text to wrap

        returns:
            text (str): wrapped text
        """

        character_counter = 0
        for index, character in enumerate(text):
            
            character_counter += 1
            if character == ' ':
                space_index = index
            elif character == '\n':
                character_counter = 0

            if character_counter > self.max_characters:
                text = text[:space_index]+'\n'+text[space_index+1:]
                character_counter = 0

        return text

    def build_composition_string(self, composition):
        """
        Assembles string from composition dict for use in radial build plot

        Arguments:
            composition (dict): "material name (str)":volume_fraction (float)

        Returns:
            comp_string (string): formatted string with material definition
        """

        comp_string = ''
        for material, fraction in composition.items():
            
            mat_string = f'{material}: {round(fraction*100,3)}%, '
            comp_string += mat_string
            
        comp_string = self.wrap_text(comp_string)

        return comp_string[0:-2]+'\n'
    
    def write_yml(self):
        """
        Writes yml file defining radial build object. File will be called
        self.title.yml
        """
        
        data_dict = {}
        data_dict['build'] = self.build
        data_dict['title'] = self.title
        data_dict['colors'] = self.colors
        data_dict['max_characters'] = self.max_characters
        data_dict['max_thickness'] = self.max_thickness
        data_dict['size'] = self.size
        data_dict['unit'] = self.unit

        filename = self.title.replace(' ',"") + '.yml'

        with open(filename, 'w') as file:
            yaml.safe_dump(data_dict, file, default_flow_style=False)

    def plot_radial_build(self):
        """
        Creates a radial build plot, with layers scaled between a minimum and
            maximum pixel width to preserve readability
        """

        char_to_height = 1.15
        min_line_height = 8
        min_lines = 2
        height = char_to_height*self.max_characters

        #initialize list for lower left corner of each layer rectangle
        ll = [0,0]
        plt.figure(1, figsize=self.size)
        plt.tight_layout()
        ax = plt.gca()
        ax.set_ylim(0,height+1)

        total_thickness = 0
        for (name, layer), color in zip(self.build.items(), self.colors):
            
            if 'thickness' not in layer:
                layer['thickness'] = min_line_height
                thickness_str = ''
            else:
                thickness_str = f': {layer["thickness"]} {self.unit}'

            if 'composition' not in layer:
                comp_string = ''
            else:
                comp_string = self.build_composition_string(layer['composition'])
                
            if 'description' not in layer:
                description_str = ''
            else:
                description_str = self.wrap_text(f'{layer["description"]}')
            
            text = f'{name}{thickness_str}\n{comp_string}{description_str}'
            text = self.wrap_text(text)
            if text[-1] == '\n':
                text = text[0:-1]

            newlines = text.count('\n')

            min_thickness = (min_lines + newlines) * min_line_height

            thickness = min(max(layer['thickness'], min_thickness),
                            self.max_thickness)
                
            ax.add_patch(Rectangle(ll,thickness, height, facecolor = color, 
                                edgecolor = "black"))

            #put the text in
            centerx = ll[0] + thickness/2 + 1
            centery = height/2
                    
            plt.text(centerx, centery, text, rotation = "vertical", 
                     ha = "center", va = "center")

            ll[0] += float(thickness)

            total_thickness += thickness

        ax.set_xlim(-1, total_thickness+1)
        ax.set_axis_off()
        plt.title(self.title)
        plt.savefig(self.title.replace(' ',"") + '.png',dpi=200)
        plt.close()

    @classmethod
    def from_parastell_build(cls, parastell_build_dict, title, phi, theta,
                             colors = None, max_characters=35, max_thickness=1e6,
                             size=(8,4), unit='cm'):

        # access the thickness values at given theta phi
        phi_list = parastell_build_dict['phi_list']
        theta_list = parastell_build_dict['theta_list']
        radial_build= parastell_build_dict['radial_build']

        phi_index = np.where(phi_list == phi)[0]
        theta_index = np.where(theta_list == theta)[0]
        plotter_build = {}
        #build the dictionary for plotting
        for layer_name, layer in radial_build.items():
            thickness = float(layer['thickness_matrix'][phi_index, theta_index][0])
            material = layer['h5m_tag']
            plotter_build[layer_name] = {"thickness": thickness,
                                        "description":material}
            
        radial_build = cls(plotter_build, title, colors, max_characters,
                           max_thickness, size, unit)
        
        return radial_build
    
def parse_args():
    """Parser for running as a script
    """
    parser = argparse.ArgumentParser(prog='plot_radial_build')

    parser.add_argument(
        'filename', help='YAML file defining radial build'
    )

    return parser.parse_args()

def read_yaml(filename):
    """Reads yaml file to extract title and build variables
    """
    with open(filename) as file:
        data = yaml.safe_load(file)
    
    return data

def main():

    #default data for running from command line
    data_default = {
        'title':'Radial Build',
        'colors':None,
        'max_characters':35,
        'max_thickness':1e6,
        'size':(8,4),
        'unit': 'cm'
    }

    args = parse_args()
    data = read_yaml(args.filename)

    data_dict = data_default.copy()
    data_dict.update(data)
    
    rb = radial_build(data_dict['build'], data_dict['title'], 
                      data_dict['colors'], data_dict['max_characters'],
                      data_dict['max_thickness'], data_dict['size'],
                      data_dict['unit'])
    
    rb.plot_radial_build()

if __name__ == "__main__":
    main()