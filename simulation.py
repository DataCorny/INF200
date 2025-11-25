"""
Template for BioSim class.
"""
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Hans Ekkehard Plesser / NMBU
from .Island_map import Map
from .Animals import Herbivore, Carnivore
from .landscape import Lowland, Highland, Desert, Water

# Update these variables to point to your ffmpeg and convert binaries
# If you installed ffmpeg using conda or installed both softwares in
# standard ways on your computer, no changes should be required.
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files

_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class BioSim:
    """
    Top-level interface to BioSim package.
    """

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_years=None, img_dir=None, img_base=None, img_fmt='png',
                 log_file=None, img_name=None):


        if img_base is None:
            img_base = img_name

        if img_name is None:
            img_name = _DEFAULT_GRAPHICS_NAME

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None

        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self.population = ini_pop
        self.map = island_map
        self.seed = seed
        self.island_map = Map(island_map)
        self.add_population(ini_pop)
        self.vis_years = vis_years
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals
        self.hist_specs = hist_specs
        self._img_years = img_years
        self._img_dir = img_dir
        self._img_fmt = img_fmt
        self._img_ctr = 0
        self.log_file = log_file

        self.amount_years_simulated = 0
        self.final_year_simulated = None

        # the following will be used in setup function and plot function
        self._fig = None
        self._map_ax = None
        self._img_axis = None

        self._pop_graph_ax = None
        self._pop_graph_herb = None
        self._pop_graph_carn = None

        self._heat_map_herb_ax = None
        self._img_herb_axis = None

        self._heat_map_carn_ax = None
        self._img_carn_axis = None

        self._weight_ax = None
        self._age_ax = None
        self._fit_ax = None
        self._year_ax = None


        if cmax_animals is None:
            self.cmax_animals = {'Herbivore': 300, 'Carnivore': 80}

        """
        Parameters
        ----------
        island_map : str
            Multi-line string specifying island geography
        ini_pop : list
            List of dictionaries specifying initial population
        seed : int
            Integer used as random number seed
        vis_years : int
            Years between visualization updates (if 0, disable graphics)
        ymax_animals : int
            Number specifying y-axis limit for graph showing animal numbers
        cmax_animals : dict
            Color-scale limits for animal densities, see below
        hist_specs : dict
            Specifications for histograms, see below
        img_years : int
            Years between visualizations saved to files (default: `vis_years`)
        img_dir : str
            Path to directory for figures
        img_base : str
            Beginning of file name for figures
        img_fmt : str
            File type for figures, e.g. 'png' or 'pdf'
        log_file : str
            If given, write animal counts to this file

        Notes
        -----
        - If `ymax_animals` is None, the y-axis limit should be adjusted automatically.
        - If `cmax_animals` is None, sensible, fixed default values should be used.
        - `cmax_animals` is a dict mapping species names to numbers, e.g.,

          .. code:: python

             {'Herbivore': 50, 'Carnivore': 20}

        - `hist_specs` is a dictionary with one entry per property for which a histogram
          shall be shown. For each property, a dictionary providing the maximum value
          and the bin width must be given, e.g.,

          .. code:: python

             {'weight': {'max': 80, 'delta': 2},
              'fitness': {'max': 1.0, 'delta': 0.05}}

          Permitted properties are 'weight', 'age', 'fitness'.
        - If `img_dir` is None, no figures are written to file.
        - Filenames are formed as

          .. code:: python

             Path(img_dir) / f'{img_base}_{img_number:05d}.{img_fmt}'

          where `img_number` are consecutive image numbers starting from 0.

        - `img_dir` and `img_base` must either be both None or both strings.
        """

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            Name of species for which parameters shall be set.
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """

        if species == 'Herbivore':
            herb = Herbivore
            herb.set_herbivore_params(params)
        elif species == 'Carnivore':
            carn = Carnivore
            carn.set_carnivore_params(params)
        else:
            raise ValueError('Invalid parameter values')

    @staticmethod
    def set_landscape_parameters(landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ----------
        landscape : str
            Code letter for landscape
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """
        if isinstance(params, dict):
            if landscape == 'L':
                low = Lowland
                low.set_landscape_params(params)
            elif landscape == 'H':
                high = Highland
                high.set_landscape_params(params)
            elif landscape == 'D':
                desert = Desert
                desert.set_landscape_params(params)
            elif landscape == 'W':
                water = Water
                water.set_landscape_params(params)
            else:
                raise ValueError('invalid values for parameter or not a dictionary')

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            Number of years to simulate.

        Returns
        -------
        None
        """
        self.final_year_simulated = self.amount_years_simulated + num_years
        self.make_figure()

        while self.amount_years_simulated < self.final_year_simulated:
            self.island_map.cycle_map()
            self.update_all_graphics()
            self.amount_years_simulated += 1

    def add_population(self, population):
        """
        Adds a population of animals to the island, by sending it to next function

        Parameters
        ----------
        population : list of dictionaries
        A list of dictionaries representing the population to be put on the island.
        Each dictionary should have the following keys:
        - 'loc': A tuple specifying the (row, column) coordinates.
        - 'pop': A list of dictionaries representing the animals in the population.
                 Each dictionary should have the following keys:
                 - 'species': A string indicating the species ('Herbivore' or 'Carnivore').
                 - 'age': An integer indicating the age of the animal.
                 - 'weight': An integer indicating the weight of the animal.

        Returns
        -------
        None
        """

        self.island_map.get_loc_and_send_animal(population)

    def update_all_graphics(self):
        """
        Updates the plot for the simulation
        Each year/sim this function:
            Updates the total population
            Updates the heatmaps of both carnivore and herbivore distribution on the island
        Returns
        -------

        """
        self.update_all_animals()
        self.update_heatmap_herbivore()
        self.update_heatmap_carnivore()


        self.update_fit(self.island_map, self.hist_specs)
        self.update_age(self.island_map, self.hist_specs)
        self.update_weight(self.island_map, self.hist_specs)

        self._fig.canvas.flush_events()  # ensure every thing is drawn
        plt.pause(1e-6)  # pause required to pass control to GUI

        self._save_graphics()

    def make_figure(self):
        """
        Creates the main figure for visualizing the simulation.
        Also, setup all the subplots and updates the plots

        Returns
        -------

        """
        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(12, 7))
            self._fig.subplots_adjust(wspace=0.4, hspace=0.4)

        if self._map_ax is None:
            self._map_ax = self._fig.add_subplot(3, 3, 1)
            self._img_axis = None
            self.make_map()

        if self._pop_graph_ax is None:
            self._pop_graph_ax = self._fig.add_subplot(3, 3, 3)

        self._pop_graph_ax.set_xlim(0, self.final_year_simulated + 1)

        if self._pop_graph_herb is None:
            herb_plot = self._pop_graph_ax.plot(np.arange(0, self.final_year_simulated + 1),
                                                np.full(self.final_year_simulated + 1, np.nan))
            self._pop_graph_herb = herb_plot[0]
        else:
            x_data, y_data = self._pop_graph_herb.get_data()
            x_new = np.arange(x_data[-1] + 1, self.final_year_simulated + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._pop_graph_herb.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data, y_new)))

        if self._pop_graph_carn is None:
            carn_plot = self._pop_graph_ax.plot(np.arange(0, self.final_year_simulated + 1),
                                                np.full(self.final_year_simulated + 1, np.nan))
            self._pop_graph_carn = carn_plot[0]
        else:
            x_data, y_data = self._pop_graph_carn.get_data()
            x_new = np.arange(x_data[-1] + 1, self.final_year_simulated + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._pop_graph_carn.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data, y_new)))

        self._pop_graph_ax.yaxis.tick_right()
        self._pop_graph_ax.legend(['Herbivore', 'Carnivore'], loc='best')
        self._pop_graph_ax.set_ylabel('Population')
        self._pop_graph_ax.set_xlabel('Years')

        if self._heat_map_herb_ax is None:
            self._heat_map_herb_ax = self._fig.add_subplot(3, 3, 4)
            self._img_herb_axis = None

        # Features for herbivore heat map
        self._heat_map_herb_ax.title.set_text('Herbivore distribution')
        self._heat_map_herb_ax.set_ylabel('y ')
        self._heat_map_herb_ax.set_xlabel('x ')

        if self._heat_map_carn_ax is None:
            self._heat_map_carn_ax = self._fig.add_subplot(3, 3, 6)
            self._img_carn_axis = None

        # Features for carnivore heat map
        self._heat_map_carn_ax.title.set_text('Carnivore distribution')
        self._heat_map_carn_ax.set_ylabel('y')
        self._heat_map_carn_ax.set_xlabel('x')

        if self._fit_ax is None:
            self._fit_ax = self._fig.add_subplot(3,3,7)
            self._fit_ax.set_title('Fitness distribution')
            self._img_fit_axis = None

        if self._age_ax is None:
            self._age_ax = self._fig.add_subplot(3,3,8)
            self._age_ax.set_title('Age distribution')
            self._img_age_axis = None

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_subplot(3,3,9)
            self._weight_ax.set_title('Weight distribution')
            self._img_weight_axis = None


    def make_map(self):
        """
        Creates the island map visualization.

        """

        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row]
                   for row in self.map.splitlines()]

        ax_im = self._map_ax

        ax_im.imshow(map_rgb)
        ax_im.set_xticks(range(len(map_rgb[0])))
        ax_im.set_xticklabels(range(1, 1 + len(map_rgb[0])))
        ax_im.set_yticks(range(len(map_rgb)))
        ax_im.set_yticklabels(range(1, 1 + len(map_rgb)))

        ax_lg = self._fig.add_subplot(3, 3, 2)  # self._legend
        ax_lg.axis('off')
        for ix, name in enumerate(('Water', 'Lowland',
                                   'Highland', 'Desert')):
            ax_lg.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                          edgecolor='none',
                                          facecolor=rgb_value[name[0]]))
            ax_lg.text(0.35, ix * 0.2, name, transform=ax_lg.transAxes)

        plt.show()

    def herb_to_heatmap(self):
        """
        Converts the Herbivore population data into a heatmap array.

        Returns:
            numpy.ndarray: Heatmap array for the Herbivore population.

        """
        df = self.island_map.df_of_island
        num_rows = df["Rows"].iloc[-1] + 1
        num_cols = df["Columns"].iloc[-1] + 1
        index = 0
        array_herbs = np.zeros(shape=(num_rows, num_cols))
        for row in range(num_rows):
            for col in range(num_cols):
                if index < len(df['Herbivore']):
                    array_herbs[row, col] = df["Herbivore"].iloc[index]
                    index += 1
                else:
                    raise Exception('Index is longer than dataframe')
        return array_herbs

    def carn_to_heatmap(self):
        """
        Converts the carnivore population data into a heatmap array.

        Returns:
            numpy.ndarray: Heatmap array for the carnivore population.

        """
        df = self.island_map.df_of_island
        num_rows = df["Rows"].iloc[-1] + 1
        num_cols = df["Columns"].iloc[-1] + 1

        index = 0
        array_herbs = np.zeros(shape=(num_rows, num_cols))
        for row in range(num_rows):
            for col in range(num_cols):
                if index < len(df['Carnivore']):
                    array_herbs[row, col] = df["Carnivore"].iloc[index]
                    index += 1
                else:
                    raise Exception('Index is longer than dataframe')
        return array_herbs

    def update_heatmap_herbivore(self):
        """
        Updates the Herbivores heatmap based on the current population distribution.

        Returns:
            None

        """
        if self._img_herb_axis is not None:
            self._img_herb_axis.set_data(self.herb_to_heatmap())
        else:
            self._img_herb_axis = self._heat_map_herb_ax.imshow(self.herb_to_heatmap(),
                                                                interpolation='nearest',
                                                                vmin=0,
                                                                vmax=self.cmax_animals['Herbivore'])
            plt.colorbar(self._img_herb_axis, ax=self._heat_map_herb_ax,
                         orientation='vertical', location='right')  # change to vertical

    def update_heatmap_carnivore(self):
        """
        Updates the carnivore heatmap based on the current population distribution.

        Returns:
            None

        """
        if self._img_carn_axis is not None:
            self._img_carn_axis.set_data(self.carn_to_heatmap())
        else:
            self._img_carn_axis = self._heat_map_carn_ax.imshow(self.carn_to_heatmap(),
                                                                interpolation='nearest',
                                                                vmin=0,
                                                                vmax=self.cmax_animals['Carnivore'])
            plt.colorbar(self._img_carn_axis, ax=self._heat_map_carn_ax,
                         orientation='vertical', location='right')  # change to vertical

    def update_all_animals(self):
        """
        Updates the data for the population graph with,
         the current number of herbivores and carnivores.

        Returns:
            None

        """
        animal_dict = self.num_animals_per_species
        total_carn = animal_dict['Carnivore']
        total_herbs = animal_dict['Herbivore']

        # update the graph
        y_data_herb = self._pop_graph_herb.get_ydata()
        y_data_carn = self._pop_graph_carn.get_ydata()
        y_data_herb[self.amount_years_simulated] = total_herbs
        y_data_carn[self.amount_years_simulated] = total_carn
        self._pop_graph_herb.set_ydata(y_data_herb)
        self._pop_graph_carn.set_ydata(y_data_carn)

        if self.ymax_animals is None:
            self._pop_graph_ax.set_ylim(0, self.num_animals * 1.1)

    def update_fit(self, island, hist_specs):
        """Updates the histogram with fitness for Herbivores and Carnivores."""
        if hist_specs is not None:
            fit_specs = hist_specs['fitness']
            bins = int(fit_specs['max'] / fit_specs['delta'])
            x_max = fit_specs['max']
        else:
            bins = 20
            x_max = 1

        fitness_herb = np.array([herb.fitness for herb in island.herbivore_list_object])
        fitness_carn = np.array([carn.fitness for carn in island.carnivore_list_object])

        if self._img_fit_axis is not None:
            self._fit_ax.clear()
            self._fit_ax.set_title('Fitness distribution')
            self._fit_ax.hist(fitness_herb, edgecolor='blue',
                              color='white', bins=bins, histtype='step')
            self._fit_ax.hist(fitness_carn, edgecolor='red',
                              color='white', bins=bins, histtype='step')
            self._fit_ax.set_xlim(0, x_max)

        else:
            self._img_fit_axis = self._fit_ax.hist(fitness_herb, edgecolor='blue',
                                                   color='white', bins=bins, histtype='step')[0]
            self._img_fit_axis = self._fit_ax.hist(fitness_carn, edgecolor='red',
                                                   color='white', bins=bins, histtype='step')[0]

    def update_age(self, island, hist_specs):
        """Updates the histogram with age for Herbivores and Carnivores."""
        if hist_specs is not None:
            age_specs = hist_specs['age']
            bins = int(age_specs['max'] / age_specs['delta'])
            x_max = age_specs['max']
        else:
            bins = 20
            x_max = 60

        age_herb = np.array([herb.age for herb in island.herbivore_list_object])
        age_carn = np.array([carn.age for carn in island.carnivore_list_object])

        if self._img_age_axis is not None:
            self._age_ax.clear()
            self._age_ax.set_title('Age distribution')
            self._age_ax.hist(age_herb, edgecolor='blue', color='white', bins=bins, histtype='step')
            self._age_ax.hist(age_carn, edgecolor='red', color='white', bins=bins, histtype='step')
            self._age_ax.set_xlim(0, x_max)

        else:
            self._img_age_axis = self._age_ax.hist(age_herb, edgecolor='blue', color='white',
                                                   bins=bins, histtype='step')[0]
            self._img_age_axis = self._age_ax.hist(age_carn, edgecolor='red', color='white',
                                                   bins=bins, histtype='step')[0]

    def update_weight(self, island, hist_specs):
        """Updates the histogram with weight for Herbivores and Carnivores."""
        if hist_specs is not None:
            weight_specs = hist_specs['weight']
            bins = int(weight_specs['max'] / weight_specs['delta'])
            x_max = weight_specs['max']
        else:
            bins = 20
            x_max = 60

        weight_herb = np.array([herb.weight for herb in island.herbivore_list_object])
        weight_carn = np.array([carn.weight for carn in island.carnivore_list_object])
        if self._img_weight_axis is not None:
            self._weight_ax.clear()
            self._weight_ax.set_title('Weight distribution')
            self._weight_ax.hist(weight_herb, edgecolor='blue',
                                 color='white', bins=bins, histtype='step')
            self._weight_ax.hist(weight_carn, edgecolor='red',
                                 color='white', bins=bins, histtype='step')
            self._weight_ax.set_xlim(0, x_max)

        else:
            self._img_weight_axis = self._age_ax.hist(weight_herb, edgecolor='blue', color='white',
                                                      bins=bins, histtype='step')[0]
            self._img_weight_axis = self._age_ax.hist(weight_carn, edgecolor='red', color='white',
                                                      bins=bins, histtype='step')[0]

    # rewrite
    def _save_graphics(self):
        """Saves graphics to file if file name given."""

        if self._img_base is None:  # or self.amount_years_simulated % self._img_years != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)

    @property
    def year(self):
        """
        Last year simulated.

        Returns:
            int: The last year simulated.

        """
        return self.final_year_simulated

    @property
    def num_animals(self):
        """
        Total number of animals on the island.

        Returns:
           int: Total number of animals.

        """
        final_num_animals = self.island_map.calc_total_amount_of_animals()
        return final_num_animals

    @property
    def num_animals_per_species(self):
        """
        Number of animals per species on the island, as a dictionary.

        Returns:
            dict: Number of animals per species, with keys 'Herbivore' and 'Carnivore'.

        """
        num_animals_per_species = {'Herbivore': self.island_map.df_of_island['Herbivore'].sum(),
                                   'Carnivore': self.island_map.df_of_island['Carnivore'].sum()}
        return num_animals_per_species

    @staticmethod
    def calc_mean(mean_list):
        return np.mean(mean_list)
