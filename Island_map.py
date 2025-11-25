"""jh"""
import random
import textwrap
import pandas as pd

from biosim.landscape import Lowland, Highland, Desert


class Map:
    """jhh"""
    def __init__(self, geography):
        """
        Initializes a Map object with the given geography.

        Parameters:
            geography (str): The string representation of the map's geography.

        Raises:
            Exception: If no map data was given.

        """
        self.geo = geography
        self.herbivore_list_object = []
        self.carnivore_list_object = []
        self.df_of_island = pd.DataFrame(columns=['Rows', 'Columns', 'Herbivore', 'Carnivore'])
        self.matrix_map = None

        if self.geo is None:
            raise Exception('No Map data was given')

        if self.matrix_map is None:
            self.make_matrix_for_land()

    def get_loc_and_send_animal(self, new_animals):
        """
        Takes the given population list, extracts the location and population,
        and places the animals in their designated cells on the map.

        Parameters:
            new_animals: A list containing the location and population of new animals.

        """
        for loop in new_animals:
            location = loop['loc']  # gets the location of the animals

            population = loop['pop']  # gets the population

            # so that it starts on index 0 in the matrix
            x_location = location[0] - 1
            y_location = location[1] - 1
            targeted_cell = self.matrix_map[x_location][y_location]

            if isinstance(targeted_cell, Lowland):
                targeted_cell.put_animal_on_land(population)
            elif type(targeted_cell) == Highland:
                targeted_cell.put_animal_on_land(population)
            elif isinstance(targeted_cell, Desert):
                targeted_cell.put_animal_on_land(population)
            elif targeted_cell == 'W':
                raise Exception('choose between Low/High-land or Desert')
            else:
                raise Exception('Cell must be W/H/L/D class ')

    def make_matrix_for_land(self):
        """
        Converts the text representation of the map into a matrix.
        Also checks if the map is equal length, before sending it to other functions

        Returns
        -------

        """

        lines = self.geo.strip().split('\n')

        first_bracket_length = len(lines[0])
        for line in lines[1:]:
            if len(line) is not first_bracket_length:
                raise ValueError('Map string is not equal in length')

        wrapped_lines = [list(textwrap.wrap(line, 1)) for line in lines]

        matrix = wrapped_lines
        self.matrix_map = matrix
        self.check_border_of_matrix()
        self.cycle_through_matrix()

    def cycle_through_matrix(self):
        """
        Replaces the letters in the matrix with classes, creating a simulated map.

        Examples:
        Matrix now looks like: [['W', 'W', 'W'], ['W', class object, 'W'], ['W', 'W', 'W']]
        Where all land types except for water (W) is made to a class

        Returns:
            None

        Raises:
            ValueError: If the geography contains something other than W/H/L/D.

        """

        replacement_dict = {'L': Lowland, 'H': Highland, 'D': Desert}

        for row in range(len(self.matrix_map)):
            for col in range(len(self.matrix_map[row])):
                if self.matrix_map[row][col] not in ['W', 'L', 'H', 'D']:
                    raise ValueError('geography contains something else than W/H/L/D')

                if self.matrix_map[row][col] in replacement_dict:
                    self.matrix_map[row][col] = replacement_dict[self.matrix_map[row][col]]()

    def check_border_of_matrix(self):
        """
        Checks that the island has water all around it.
        Additionally, checks that each row starts and ends with 'W'.

        Returns:
            None

        Raises
        ----------
            ValueError: If the first row does not contain 'W'.
            ValueError: If the last row does not contain 'W'.
            ValueError: If any row does not start and end with 'W'.

        """
        for check in self.matrix_map[0]:
            if check != 'W':
                raise ValueError('First row must contain W')

        for check in self.matrix_map[-1]:
            if check != 'W':
                raise ValueError('Last row must contain W')

        for inner_list in self.matrix_map:
            if inner_list[0] != 'W' or inner_list[-1] != 'W':
                raise ValueError('Each row must start with W and end in W')

    def cycle_map(self):
        """
        Cycles through all the cells on the island,
        and creates a dataframe with the coordinates and population.

        Returns:
            None

        """
        data = []
        object_herb = []
        object_carn = []
        for row in range(len(self.matrix_map)):
            for col in range(len(self.matrix_map[row])):
                run_cell = self.matrix_map[row][col]
                if run_cell == 'W':
                    location = [row, col]
                    data.append([location[0], location[1], 0, 0])

                elif run_cell != 'W':
                    run_cell.give_birth()
                    run_cell.animal_eats()
                    self.migration(run_cell, row, col)
                    run_cell.age_animal()
                    run_cell.lose_weight()
                    run_cell.remove_dead()

                    location = [row, col]
                    length_of_herb = len(run_cell.herbivore_list)
                    length_of_carn = len(run_cell.carnivore_list)

                    object_herb.extend(run_cell.herbivore_list)
                    object_carn.extend(run_cell.carnivore_list)
                    self.herbivore_list_object = object_herb
                    self.carnivore_list_object = object_carn

                    data.append([location[0], location[1], length_of_herb, length_of_carn])

        df = pd.DataFrame(data=data, columns=['Rows', 'Columns', 'Herbivore', 'Carnivore'])
        self.df_of_island = df

    def make_list_of_herb(self):
        """
        make a list of all the herbivore objects
        Returns
        -------

        """
        herb_list = []
        herb_list = herb_list.append(self.df_of_island)

    def make_list_of_carn(self):
        carn_list = []
        carn_list = carn_list.extend(self.df_of_island['Carnivore'].sum())
    def calc_total_amount_of_animals(self):
        """
        Calculates the total number of animals on the island.

        Returns:
            int: Total number of animals

        """

        herb_column = self.df_of_island['Herbivore']
        carn_column = self.df_of_island['Carnivore']
        total_animals = sum(carn_column + herb_column)
        return total_animals

    def migration(self, landscape_type, rows, columns):
        """
        This function gets a list of animals that are migrating from,
         the check_migration function in landscape
        It then checks if the cell type is not water then,
        it makes a random choice out of the 4 surrounding cells
        Then it takes each animal in the cell and randomly puts that single animal in a new cell,
        then it starts on the next animal and again chooses randomly the new cell
        The probability of each random cell is 25%

        Parameters
        ----------
        landscape_type: class/W
            defines if the cell is an L/H/D type or water type
        rows: int
            defines which row in the matrix the cell is (landscape_type)
        columns: int
            defines which bracket of the matrix that is to be chosen

        Returns
        -------

        """
        list_of_moving_animals = landscape_type.check_migration()

        if landscape_type != 'W':

            north = self.matrix_map[rows][columns - 1]
            south = self.matrix_map[rows][columns + 1]
            east = self.matrix_map[rows + 1][columns]
            west = self.matrix_map[rows - 1][columns]

            new_cells = [north, south, east, west]
            prob_move_to_cell = [0.25, 0.25, 0.25, 0.25]

            for animal in list_of_moving_animals:
                random_new_cell = random.choices(new_cells, prob_move_to_cell)
                get_obj_cell = random_new_cell[0]

                if get_obj_cell == 'W':
                    landscape_type.put_migrating_animal_in_cell(animal)
                else:
                    get_obj_cell.put_migrating_animal_in_cell(animal)
