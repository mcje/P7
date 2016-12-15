import re
import random
import bisect
from random import choice
from module import SquareModule
from UPPAAL.uppaalAPI import get_best_time
from configuration.config_string_handler import ConfigStringHandler
from configuration.initial_config import initial_configuration_generator
from configuration.path_placers import connect_module_list, push_around, push_underneath
from configuration.neighbour_functions.anti_serialize import neighbours_anti_serialized
from configuration.neighbour_functions.parallelize import neighbours_parallelize
from configuration.neighbour_functions.swap import neighbours_swap


VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"

WEIGHT_START = 100
WEIGHT_STRENGTH = 1
WEIGHT_X = 3
WEIGHT_Y = 1

weighted_funcs = [(neighbours_anti_serialized, WEIGHT_START), (neighbours_parallelize, 0), (neighbours_swap, 0)]

def tabu_search(recipes, modules, transport_module, iters=50):
    """ Tabu Search
    :param recipes: A list of Recipe objects
    :param modules: A list of module objects
    :param init_func: A function that creates the initial configuration
    :param iters: How many iterations of Tabu search
    :return: The best configuration found by the search
    """

    def evaluate_config(config):
        """ Evaluates a configuration
        :param config: A string representing a configuration
        :return: An integer representing the evaluation of the config.
        """

        if config in config_fitness:
            return config_fitness[config]
        else:
            csh.make_configuration(config)  # SIDE EFFECT: Makes loads of changes to modules
            modules_in_config = csh.modules_in_config(config)
            fitness, worked, transported = get_best_time(recipes, modules_in_config, XML_TEMPLATE, VERIFYTA)

            config_fitness[config] = fitness
            config_worked[config] = worked
            return fitness

    def get_neighbour_func():
        global weighted_funcs
        result = weighted_choice(weighted_funcs)
        funcs, weights = zip(*weighted_funcs)
        new_weights = [w for w in weights]
        x = WEIGHT_X * WEIGHT_STRENGTH
        if new_weights[0] < x:
            new_weights[1] += new_weights[0]
            new_weights[0] = 0
        else:
            new_weights[1] += x
            new_weights[0] -= x

        y = WEIGHT_Y * WEIGHT_STRENGTH
        if new_weights[1] < y:
            new_weights[2] += new_weights[1]
            new_weights[1] = 0
        else:
            new_weights[2] += y
            new_weights[1] -= y

        temp = list(zip(funcs, new_weights))
        weighted_funcs = temp
        return result

    csh = ConfigStringHandler(recipes, modules, transport_module)
    generator = initial_configuration_generator(recipes, modules, csh)

    # Memory used for remembering evalutations, used so we dont have to evaluate the same configuration twice.
    config_fitness = {}
    config_worked = {}

    # Tabu Search specific memories
    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    for config in generator:
        evaluate_config(config)  # Updates dynamic memory
        long_term_memory.append(config)

    # Creating the initial configuration and evalutates it
    long_term_memory.sort(key=(lambda x: config_fitness[x]))
    overall_best = long_term_memory[0]
    frontier = long_term_memory[0]


    # Here begins the actual search
    for _ in range(iters):  # TODO: Maybe have stopping criteria instead of iterations, or allow for both.
        neighbour_func = get_neighbour_func()

        if neighbour_func is neighbours_anti_serialized:
            args = [frontier, csh, config_worked[frontier]]
        else:
            args = [frontier, csh]

        results = []
        for n in neighbour_func(*args):
            results.append((n, evaluate_config(n)))

        results.sort(key=lambda x: x[1])
        for r in results:
            if r[0] in short_term_memory:
                continue
            else:
                frontier = r[0]
                break

        if config_fitness[frontier] < config_fitness[overall_best]:
            overall_best = frontier

        short_term_memory.append(frontier)
        long_term_memory.append(frontier)


    return config_fitness


def weighted_choice(choices):
    """ Randomly picks a choices based on weights
    :param choices: A list of tuples, where the first element of the tuple is a potential choice and the second element
    is the weight with which the choice can be picked
    :return: A randomly weighted selection of a choice, along with its weight and the index it had.
    """
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect_left(cum_weights, x)
    return values[i]




