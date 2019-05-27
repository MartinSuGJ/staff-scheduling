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

    return records

