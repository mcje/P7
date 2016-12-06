from module import SquareModule
from UPPAAL.uppaalAPI import get_best_time
import re

VERIFYTA = '/home/beta/uppaal64-4.1.19/bin-Linux/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.1.xml"


def tabu_search(recipes, modules, init_func, iters=50):
    """
    :param recipes:
    :param modules:
    :param init_func:
    :return:
    """
    def get_neighbours():
        """ Gets the neighbours of the current frontier.
        :return: A list of tuples, where the first element of the tuple is a string representing a configuration and
        the second element its evaluation.
        """
        return swap_neighbours(frontier, recipes)

    init_modules = init_func(recipes, modules, None)
    free_modules = [m for m in modules if m not in init_modules]
    
    init_time = get_best_time(recipes, init_modules, XML_TEMPLATE, VERIFYTA)

    current_best = (SquareModule.configuration_str(init_modules[0]), init_time)
    frontier = (SquareModule.configuration_str(init_modules[0]), init_time)

    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    for i in range(iters):
        neighbours = get_neighbours()
        short_term_memory += neighbours
        best = min(neighbours, key=(lambda x: x[1]))
        if best[1] < current_best[1]:
            current_best = best
        frontier = best

    return current_best


def swap_neighbours(frontier, recipes):
    """
    :param config_str:
    :return:
    """
    def eval_swap(old, new):
        """
        :param old: The modules you wish to swap out
        :param new: The module that you wish to swap in
        :return:
        """
        config_str = SquareModule.configuration_str(old)
        l = config_str.split(sep=':')
        for i, m_str in enumerate(l):
            m_str_id = re.search('(.*)(?=\{)', m_str).group(0)
            if str(old.m_id) == m_str_id:
                new_half = new.module_str().split('{')[0]
                old_half = old.module_str().split('{')[1]
                l[i] = new_half + '{' + old_half # Everything  old could do, new now can do
            else:
                split = m_str.find('[')
                s = m_str[:split]
                s += m_str[split:].replace(old.m_id, new.m_id)  # We replace all instances of the old mid with the new
                l[i] = s

        l.sort()    # TODO: I think text based sorting works, I am not sure.
        new_config_str = ':'.join(l)

        new_config_modules = SquareModule.modules_in_config(new_config_str)
        SquareModule.make_configuration(new_config_str) # We set up the new configuration in our module objects
        result = get_best_time(recipes, new_config_modules, XML_TEMPLATE, VERIFYTA)
        return (new_config_str, result)

    def swappable_modules(config_m, free_modules):
        """
        :param config_m:
        :param free_modules:
        :return:
        """
        L = []
        for fm in free_modules:
            if config_m.active_w_type <= fm.w_type:
                L.append(fm)
        return L

    config_str = frontier[0]
    config_modules = SquareModule.modules_in_config(config_str)
    free_modules = SquareModule.modules_not_in_config(config_str)

    neighbours = []

    for config_m in config_modules:
        swappable = swappable_modules(config_m, free_modules)
        for free_m in swappable:
            neighbours.append(eval_swap(config_m, free_m))

    return neighbours

