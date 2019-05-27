#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 21:20
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : schedulor.py
# @Software: PyCharm

from src.data.model_data import *
from src.models.solution_parser import *
from gurobipy import *
import itertools


def shift_assignment(data_file, staff_type, shift_scenario):
    # TODO: maximum number of available nurses by skill
    # TODO: maximum number of nurse working hours groupby week (FTE)

    ####################################################
    ##  PREPARE PARAMETERS OF SHIFT SCHEDULING MODEL  ##
    ####################################################
    params = construct_model_data(data_file, staff_type, shift_scenario)

    m = Model("shift-scheduling")

    ##################################
    ##  DECLARE DECISION VARIABLES  ##
    ##################################
    skd_tuples = tuple(itertools.product(params['P1_s'], params['P4_k'], params['P6_d']))
    X_skd = m.addVars(skd_tuples, vtype=GRB.INTEGER, name='shift_assignment')

    ############################
    ##  BUILD UP CONSTRAINTS  ##
    ############################

    # Neuro Demand
    m.addConstrs(((quicksum([X_skd[(s, k, d)] * params['P3_st'][(s, t)] for s in params['P1_s'] for k in ['Base_Ortho_Neuro']]) >=
                  quicksum([params['P10_ktd'][(k, t, d)] for k in ['Base_Ortho_Neuro']]))
                  for t in params['P2_t'] for d in params['P6_d']),
                 name='neuro_demand')

    # Ortho Demand
    m.addConstrs(((quicksum([X_skd[(s, k, d)] * params['P3_st'][(s, t)] for s in params['P1_s'] for k in ['Base_Ortho_Neuro', 'Base_Ortho']]) >=
                  quicksum([params['P10_ktd'][(k, t, d)] for k in ['Base_Ortho_Neuro', 'Base_Ortho']]))
                  for t in params['P2_t'] for d in params['P6_d']),
                 name='ortho_demand')

    # Transplant Demand
    m.addConstrs(((quicksum([X_skd[(s, k, d)] * params['P3_st'][(s, t)] for s in params['P1_s'] for k in ['Base_Transplant']]) >=
                  quicksum([params['P10_ktd'][(k, t, d)] for k in ['Base_Transplant']]))
                  for t in params['P2_t'] for d in params['P6_d']),
                 name='transplant_demand')

    # Base Demand
    m.addConstrs(((quicksum([X_skd[(s, k, d)] * params['P3_st'][(s, t)] for s in params['P1_s'] for k in ['Base_Ortho_Neuro', 'Base_Ortho', 'Base_Transplant', 'Base']]) >=
                  quicksum([params['P10_ktd'][(k, t, d)] for k in ['Base_Ortho_Neuro', 'Base_Ortho', 'Base_Transplant', 'Base']]))
                  for t in params['P2_t'] for d in params['P6_d']),
                 name='base_demand')

    #####################
    ##  SET OBJECTIVE  ##
    #####################
    m.setObjective(quicksum([X_skd[(s, k, d)] * params['P5_sk'][(s, k)] for s in params['P1_s'] for k in params['P4_k'] for d in params['P6_d']]))

    m.optimize()

    for d in params['P6_d']:
        print('========================')
        print(f'Scheduling {d}...')
        for k in params['P4_k']:
            for s in params['P1_s']:
                x = X_skd[(s, k, d)].x
                if x > 0:
                    print(f'{k}-{s} => {x}')

    ######################
    ##  PARSE SOLUTION  ##
    ######################
    output = parse_solution(X_skd, params)

    return X_skd, params, output




