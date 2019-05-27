#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-11 10:13
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : solution_parser.py
# @Software: PyCharm


def parse_solution(X_skd, params):
    records = []
    for d in params['P6_d']:
        for k in params['P4_k']:
            for s in params['P1_s']:
                _shift_start = params['P1_s_hours'][s][0]
                _shift_end = params['P1_s_hours'][s][1]
                _shift_length = params['P1_s_hours'][s][2]
                number = X_skd[(s, k, d)].x
                if number > 0:
                    records.append([d, k, s, _shift_start, _shift_end, _shift_length, number,  _shift_length * number])

    # output normal, break, and ot demand
    # output supply
    demand_supply = []
    for (k, t, d) in params['P7_ktd']:
        _supply = 0
        _other_supply = 0
        if k == 'Base':
            ks = ['Base_Ortho_Neuro', 'Base_Ortho', 'Base_Transplant']
        elif k == 'Base_Ortho':
            ks = ['Base_Ortho_Neuro']
        elif k == 'Base_Ortho_Neuro':
            ks = []
        elif k == 'Base_Transplant':
            ks = []

        for s in params['P1_s']:
            _supply += X_skd[(s, k, d)].x * params['P3_st'][(s, t)]

        for _k in ks:
            for s in params['P1_s']:
                _other_supply += X_skd[(s, _k, d)].x * params['P3_st'][(s, t)]
            _other_supply -= params['P10_ktd'][(_k, t, d)]

        demand_supply.append((d, k, t, params['P7_ktd'][(k, t, d)], params['P8_ktd'][(k, t, d)], params['P9_ktd'][(k, t, d)], params['P10_ktd'][(k, t, d)], _supply, _other_supply))

    # shift
    shift_time = []
    for s in params['P1_s']:
        _shift_start = params['P1_s_hours'][s][0]
        _shift_end = params['P1_s_hours'][s][1]
        _shift_length = params['P1_s_hours'][s][2]
        for t in params['P2_t']:
            shift_time.append((s, _shift_start, _shift_end, _shift_length, t, params['P3_st'][(s, t)]))

    output = {'records': records,
              'demand_supply': demand_supply,
              'shift_time': shift_time}

    return output

