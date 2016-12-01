from framework.module import SquareModule
from framework.recipe import Recipe
from copy import deepcopy, copy
from Generation.xml_generator import generate_xml
from UPPAAL.verifytaAPI import run_verifyta, pprint
import networkx as nx
import random


def create_transporters(amount, time, queue_size):

    transporters = []
    for i in range(amount):
        t = SquareModule('trans_' + str(i), [], {}, time, queue_size, allow_passthrough= True)
        transporters.append(t)
    return transporters


def get_factorial_list(nodes):
    n = []
    for i in range(1, len(nodes) + 1):
        n.append({x for j, x in enumerate(nodes) if j < i})

    return n

def initial_configuration(recipes, modules, transporters=None):
    G = Recipe.get_flow_graph(recipes)
    G.reverse()
    Recipe.plot(G)
    G_copy = nx.topological_sort(G)

    conf = []
    while G_copy:
        size = 0
        current = None
        for i, n in enumerate(get_factorial_list(G_copy)):
            l = [m for m in modules if m.w_type >= n]
            if l:
                current = l
                size = i + 1
                continue
            else:
                break

        smallest_len = len(G)
        candidate = None
        for m in current:
            if len(m.w_type) <= smallest_len:
                smallest_len = len(m.w_type)
                candidate = m

        candidate.active_w_type = set(G_copy[:size])
        conf.append(candidate)
        G_copy = G_copy[size:]

    for i, m in enumerate(conf):
        if i < len(conf) - 1:
            m.right = conf[i + 1]

    return conf

def tabu_search(recipes, modules, transporters, init_func):
    initial_configuration = init_func(modules, recipes, transporters)
    free_modules = [m for m in modules if m not in initial_configuration]


    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []
    try:
        while True:
            pass

    except KeyboardInterrupt:
        pass


def get_neighbours(conf, recipes, free_modules, free_transporters):
    return get_swap_neighbours(conf, recipes, free_modules, free_transporters)

def get_swap_neighbours(conf, recipes, free_modules, free_transporters):
    L = []
    for m in conf:
        for fm in free_modules:
            if m.active_w_type <= fm.w_type:
                L.append((m, fm))

    m, fm = random.choice(L)
    m.swap(fm)


t0 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m0 = SquareModule(0, {0, 9}, {0: 60, 9: 0},  t0, 3)

t1 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m1 = SquareModule(1, {1}, {1: 106},  t1, 3)

t2 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m2 = SquareModule(2, {2}, {2: 582},  t2, 3, allow_passthrough=True)

t3 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m3 = SquareModule(3, {3}, {3: 20}, t3, 3)

t4 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m4 = SquareModule(4, {4}, {4: 68},  t4, 3, allow_passthrough=True)

t5 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m5 = SquareModule(5, {5}, {5: 68},  t5, 3, allow_passthrough=True)

t6 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m6 = SquareModule(6, {6}, {6: 68},  t6, 3, allow_passthrough=True)


t7 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m7 = SquareModule(7, {7}, {7: 68},  t7, 3, allow_passthrough=True)


modules = [m0, m1, m2, m3, m4, m5, m6, m7]

# Transporter
t = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]


func_deps1 = {0: set(), 9: {0}, 1: {9}, 4: {1}, 6: {4}, 7: {6}}
func_deps2 = {2: set(), 3: {2}, 6: {3}, 7: {6}}
func_deps3 = {0: set(), 2: {0}, 5: {2}, 6: {5}, 7: {6}}

r0 = Recipe(func_deps1, 0, 3)
r1 = Recipe(func_deps2, 2, 3)
r2 = Recipe(func_deps3, 0, 3)

x = initial_configuration([r0, r1], modules)
map = generate_xml("../../Modeler/iter3.4.1.xml", x, [r0, r1])
res, trace = run_verifyta("../../Code/Configuration/test.xml",
             "../../Code/Configuration/test.q", "-t 2 -o 3 -u",
             verifyta='/home/alexander/uppaal64-4.1.19/bin-Linux/verifyta')

pprint(res)