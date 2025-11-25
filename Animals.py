"""jh"""
import math
import numpy as np
import random

class Animal():
    """jhh"""
    params = ({'w_birth': None,
               'sigma_birth': None,

               'beta': None,
               'eta': None,

               'a_half': None,
               'phi_age': None,

               'w_half': None,
               'phi_weight': None,

               'mu': None,
               'gamma': None,
               'zeta': None,
               'xi': None,
               'omega': None,
               'F': None,
               'delta_phi_max': None})

    def __init__(self, age, weight):

        if age is None:
            self.age = 0

        elif age < 0:
            raise ValueError('age cannot be less than 0')
        else:
            self.age = age

        if weight is None:
            self.weight = 0
        elif weight < 0:
            raise ValueError('weigth cannot be less than 0')
        else:
            self.weight = weight

        self.weight = weight
        self.age = age
        self.fitness = self._fitness_calc()

    def _fitness_calc(self):
        """
        Calculate the fitness based on age, weight, and hunger
        Implementation of fitness calculation depends on your specific formula
        Returns
        -------

        """
        q_plus = 1 / (1 + math.exp((self.params['phi_age'] * self.age - self.params['a_half'])))
        q_negative = 1 / (1 + math.exp(-self.params['phi_weight'] *
                                       (self.weight - self.params['w_half'])))
        phi = q_plus * q_negative
        if 0 <= phi <= 1:
            return phi
        elif self.weight <= 0:
            return 0
        else:
            raise Exception('Phi is less than 0 or more than 1')

    def birth(self, N):
        """
        checks if an animal can i give birth and if so creates a new object animal
        Parameters
        ----------
        N  = the population of the herd

        Returns
        -------
        type(self)
        The class type of the newborn animal.

        """
        offspring_threshold = self.params['zeta'] * (self.params['w_birth']
                                                     + self.params['sigma_birth'])
        if self.weight > offspring_threshold and self.age > 0:
            birth_probability = (self.params['gamma'] * self._fitness_calc() * N)
            if min(1, birth_probability) > random.random():
                mean = np.log(math.pow(self.params['w_birth'], 2) / (
                    np.sqrt(math.pow(self.params['w_birth'], 2) +
                            math.pow(self.params['sigma_birth'], 2))))
                std = np.sqrt(
                    np.log(1 + (math.pow(self.params['sigma_birth'], 2)
                                / math.pow(self.params['w_birth'], 2))))
                baby_weight = np.random.lognormal(mean, std)
                if baby_weight < self.weight:
                    self.weight -= (self.params['xi'] * baby_weight)
                    return type(self)(0, baby_weight)

    def aging(self):
        """
        Ages the animal.

        Returns:
            int: The updated age of the animal.

        """
        self.age += 1
        return self.age

    def weight_loss(self):
        """
        Decrease the weight of the animal each year
        Returns
        -------

        """
        weight_loss = self.params['eta'] * self.weight  # w for weight not the omega param
        self.weight -= weight_loss
        return self.weight

    def death(self):
        """
        Check if the animal dies this year.

        Returns:
            bool: True if the animal dies, False otherwise.

        """
        prob_death = self.params['omega'] * (1 - self._fitness_calc())
        if random.random() < prob_death or self.weight <= 0:
            return True
        else:
            return False

    def prob_to_move(self):
        """

        Returns
        -------
        Returns True if animal moves
        """
        move_prob = self.params['mu'] * self._fitness_calc()
        if random.random() < move_prob:
            return True
        else:
            return False


class Herbivore(Animal):

    params = ({'w_birth': 8.0,
               'sigma_birth': 1.5,

               'beta': 0.9,
               'eta': 0.05,

               'a_half': 40.0,
               'phi_age': 0.6,

               'w_half': 10.0,
               'phi_weight': 0.1,

               'mu': 0.25,
               'gamma': 0.2,
               'zeta': 3.5,
               'xi': 1.2,
               'omega': 0.4,
               'F': 10.0})

    def __init__(self, age=None, weight=None):
        super().__init__(age, weight)
        """this makes it to a subclass of Animal class
        it will then use its own params (age, weight) and put into Animal class
        if no herbivores then the age weight is None and it wont go further
        """

    _info = "This is class herbivore"

    @classmethod
    def set_herbivore_params(cls, new_params):
        """
        Update the herbivore parameters with the provided values.

        Parameters:
             new_params (dict): Dictionary containing the new parameter values.

         Raises:
             AttributeError: If a parameter key in new_params is not found in the class parameters.

         Returns:
            None

        """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')

    def eat(self, food):

        """
       Checks the amount of food available in the cell and,
        allows the animal to eat a certain amount of food.
       For herbivores, it calculates their weight gain after eating,
        and adjusts their fitness.

       Parameters:
           food (float): Amount of food available in the cell.

       Returns:
           float: Amount of food eaten by the animal.

       """
        if food >= self.params['F']:
            eaten = min(food, self.params['F'])
            weight_gain = eaten * self.params['beta']  # increase weigth
            self.weight += weight_gain
            self._fitness_calc()
            return eaten

        elif food <= self.params['F']:
            weight_gain = food * self.params['beta']
            food_eaten = 0
            self.weight += weight_gain
            self._fitness_calc()
            return food_eaten


class Carnivore(Animal):
    params = ({'w_birth': 6.0,
               'sigma_birth': 1.0,

               'beta': 0.75,
               'eta': 0.125,

               'a_half': 40.0,
               'phi_age': 0.3,

               'w_half': 4.0,
               'phi_weight': 0.4,

               'mu': 0.4,
               'gamma': 0.8,
               'zeta': 3.5,
               'xi': 1.1,
               'omega': 0.8,
               'F': 50.0,
               'DeltaPhiMax': 10.0})

    def __init__(self, age=None, weight=None):
        super().__init__(age, weight)

    @classmethod
    def set_carnivore_params(cls, new_params):
        """
       Update the carnivore parameters with the provided values.

       Parameters:
           new_params (dict): Dictionary containing the new parameter values.

       Raises:
           AttributeError: If a parameter key in new_params is not found in the class parameters.

       Returns:
           None

       """
        for key, value in new_params.items():
            if key in cls.params:
                cls.params[key] = value
            else:
                raise AttributeError(f'this class has no key/params {key}')



    def feed(self, herbivores):
        """
        Checks if the carnivore can kill and eat a herbivore,
         based on their respective fitness levels.

        Parameters:
            herbivores (list): Herbivore list sorted by fitness (increasing, low to high).

        Returns:
            list: List of surviving herbivores.
        """
        hunger = self.params['F']
        survival = []
        for herb in herbivores:
            if hunger <= 0:
                survival.append(herb)
            elif self._fitness_calc() < herb._fitness_calc():
                survival.append(herb)
            else:
                fitness = self._fitness_calc()
                kill_prob = (fitness - herb._fitness_calc()) / self.params['DeltaPhiMax']
                if random.random() > kill_prob:  # if herb survive
                    survival.append(herb)
                else:  # herb is eaten
                    eaten = min(hunger, herb.weight)
                    herb.weight -= eaten
                    hunger -= eaten
                    herb.death()
                    self.weight += eaten * self.params['beta']
                    self._fitness_calc()
        return survival
