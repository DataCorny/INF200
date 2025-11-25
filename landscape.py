
"""

"""

__author__ = "Khalid Rashed  & Cornelius Birkelid Lekman"
__email__ = " Khalid.rashed@nmbu.no & cornelius.birkelid.lekman@nmbu.no"




from biosim.Animals import Herbivore, Carnivore
import random
from itertools import chain


class Cell:
    """
    Class representing a cell in the environment.
    """

    params = ({'f_max': None})

    def __init__(self):
        self.herbivore_list = []
        self.carnivore_list = []

    @staticmethod
    def _calc_len(calc_list):
        """
        Calculate the length of a list
        Parameters
        ----------
        calc_list : iterable
            The iterable for which the length needs to be calculated.

        Returns
        -------
        Length of the list given to this function
        """
        return len(calc_list)

    @staticmethod
    def sort_animal_by_high_fitness(sort_list):
        """
            Sort an iterable of animals by their fitness in descending order.

            Parameters
            ----------
            sort_list : iterable
                The iterable of animals to be sorted.

            Returns
            -------
            list
                The sorted list of animals, ordered by their fitness in descending order.

            """
        for animal in sort_list:
            animal._fitness_calc()

        sort_list.sort(key=lambda x: x.fitness, reverse=True)
        return sort_list

    @staticmethod
    def sort_animal_by_low_fitness(sort_list):
        """
           Sort an iterable of animals by their fitness in ascending order.

           Parameters
           ----------
           sort_list : iterable
               The iterable of animals to be sorted.

           Returns
           -------
           list
               The sorted list of animals, ordered by their fitness in ascending order.

           """
        for animal in sort_list:
            animal._fitness_calc()

        sort_list.sort(key=lambda x: x.fitness, reverse=False)
        return sort_list

    def put_animal_on_land(self, add_pop):
        """
           Add animals to the land by creating instances of the respective animal classes.

           Parameters
           ----------
           add_pop : list
               A list of dictionaries containing information about the animals to be added.
               Each dictionary should include 'species', 'age', and 'weight' keys.

           Returns
           -------
           None

           """
        population = add_pop
        for individual in population:
            animal_type = individual['species']
            animal_age = individual['age']
            animal_weight = individual['weight']

            if animal_type == 'Herbivore':
                to_class = Herbivore(animal_age, animal_weight)
                self.herbivore_list.append(to_class)

            elif animal_type == 'Carnivore':
                to_class = Carnivore(animal_age, animal_weight)
                self.carnivore_list.append(to_class)

    def age_animal(self):
        """
          Age all animals on the land by calling the `aging` method for each animal.

          Returns
          -------
          None

          """
        for animal in chain(self.herbivore_list, self.carnivore_list):
            animal.aging()

    def animal_eats(self):
        """
            Allow animals to eat by calling the `herbivore_eat` and `carnivore_eat` methods.

            Returns
            -------
            None

            """
        self.herbivore_eat()
        self.carnivore_eat()

    def herbivore_eat(self):
        """
         Allow herbivores to eat from the cell's food storage and update their weight.

         Raises:
             ValueError: If the food storage becomes less than 0 or is None.

         Returns:
             None

         """
        yearly_amount_food = self.params['f_max']
        self.sort_animal_by_high_fitness(self.herbivore_list)  # sort list by fitness
        for animal in self.herbivore_list:
            eaten = animal.eat(yearly_amount_food)
            yearly_amount_food -= eaten
            if yearly_amount_food == 0:
                break
            elif yearly_amount_food is None or yearly_amount_food < 0:
                raise ValueError('Food cant be less than 0 or be None')

    def carnivore_eat(self):

        """
            Allow carnivores to eat herbivores and update the list of surviving herbivores.

            Returns:
                None

            """
        random.shuffle(self.carnivore_list)
        carn_food = self.sort_animal_by_high_fitness(self.herbivore_list)  # sort list by fitness

        for animal in self.carnivore_list:
            survival = animal.feed(carn_food)
            self.herbivore_list = survival

    def lose_weight(self):
        """
           Make animals lose weight.

           Returns:
               None

           """
        for animal in chain(self.herbivore_list, self.carnivore_list):
            animal.weight_loss()

    def give_birth(self):
        """
           Allow animals to give birth and add newborn animals to the respective lists.

           Returns:
               None

           """
        new_born_herb = []
        new_born_carn = []
        length_of_list_herb = self._calc_len(self.herbivore_list)
        length_of_list_carn = self._calc_len(self.carnivore_list)

        # self.herbivore_list = [herb for herb in self.herbivore_list if not herb.birth()]

        for animal in self.herbivore_list:
            birth = animal.birth(length_of_list_herb)

            if birth is not None:
                new_born_herb.append(birth)
            elif birth is None:
                pass

        for animal in self.carnivore_list:
            birth = animal.birth(length_of_list_carn)

            if birth is not None:
                new_born_carn.append(birth)
            elif birth is None:
                pass

        self.add_newborn_to_herbivore_list(new_born_herb)
        self.add_newborn_to_carnivore_list(new_born_carn)

    def add_newborn_to_herbivore_list(self, baby):
        """
           Add newborn herbivore animals to the herbivore list.

           Parameters:
               baby (list): List of newborn herbivore animals.

           Returns:
               list: Updated herbivore list with newborn animals.

           """
        self.herbivore_list.extend(baby)
        return self.herbivore_list

    def add_newborn_to_carnivore_list(self, baby):
        """
            Add newborn carnivore animals to the carnivore list.

            Parameters:
                baby (list): List of newborn carnivore animals.

            Returns:
                list: Updated carnivore list with newborn animals.

            """
        self.carnivore_list.extend(baby)
        return self.carnivore_list

    def remove_dead(self):
        """
           Remove dead animals from the herbivore and carnivore lists.

           Returns:
               None

           """
        self.herbivore_list = [h for h in self.herbivore_list if not h.death()]
        self.carnivore_list = [c for c in self.carnivore_list if not c.death()]

    def check_migration(self):
        animals_moving = []
        for animals in chain(self.herbivore_list, self.carnivore_list):
            if animals.prob_to_move() is True:
                # if true remove from list and add to new list
                animals_moving.append(animals)
                if animals in self.carnivore_list:
                    self.carnivore_list.remove(animals)
                elif animals in self.herbivore_list:
                    self.herbivore_list.remove(animals)
        return animals_moving

    def put_migrating_animal_in_cell(self, animal):
        if type(animal) is Herbivore:
            self.herbivore_list.append(animal)
        elif type(animal) is Carnivore:
            self.carnivore_list.append(animal)


class Lowland(Cell):
    _info = 'Information specific to Lowland'
    params = ({'f_max': 800})

    def __init__(self):
        super().__init__()
        """this makes it to a subclass of Cell class
        it will then use its own params and put into Cell class
        """

    @classmethod
    def set_landscape_params(cls, new_params):
        """
           Update the landscape parameters with the provided values.

           Parameters:
               new_params (dict): Dictionary containing the new parameter values.

           Raises:
               AttributeError: If a parameter key in new_params is not found,
                in the class parameters.

           Returns:
               None

           """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')


class Highland(Cell):
    _info = 'Information specific to Highland'
    params = ({'f_max': 300})

    @classmethod
    def set_landscape_params(cls, new_params):
        """
           Update the landscape parameters with the provided values.

           Parameters:
               new_params (dict): Dictionary containing the new parameter values.

           Raises:
               AttributeError: If a parameter key in new_params,
                is not found in the class parameters.

           Returns:
               None

           """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')


class Desert(Cell):
    _info = 'Information specific to Desert, animals can go here but no food'
    params = ({'f_max': 0})

    @classmethod
    def set_landscape_params(cls, new_params):
        """
           Update the landscape parameters with the provided values.

           Parameters:
               new_params (dict): Dictionary containing the new parameter values.

           Raises:
               AttributeError: If a parameter key in new_params is not found,
                in the class parameters.

           Returns:
               None

           """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')


class Water(Cell):
    _info = 'animals cant be on water and food is 0 '
    params = ({'f_max': 0})

    @classmethod
    def set_landscape_params(cls, new_params):
        """
           Update the landscape parameters with the provided values.

           Parameters:
               new_params (dict): Dictionary containing the new parameter values.

           Raises:
               AttributeError: If a parameter key in new_params is not found,
                in the class parameters.

           Returns:
               None

           """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')
