#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 15:51
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : config.py
# @Software: PyCharm

TIME_BUCKET = {
    0:  {'start': 7, 'end': 8},
    1:  {'start': 8, 'end': 9},
    2:  {'start': 9, 'end': 10},
    3:  {'start': 10, 'end': 11},
    4:  {'start': 11, 'end': 12},
    5:  {'start': 12, 'end': 13},
    6:  {'start': 13, 'end': 14},
    7:  {'start': 14, 'end': 15},
    8:  {'start': 15, 'end': 16},
    9:  {'start': 16, 'end': 17},
    10: {'start': 17, 'end': 18},
    11: {'start': 18, 'end': 19},
    12: {'start': 19, 'end': 20},
    13: {'start': 20, 'end': 21},
    14: {'start': 21, 'end': 22},
    15: {'start': 22, 'end': 23},
    16: {'start': 23, 'end': 24},
}


BREAK_CONVERSION = {
    0:  0.,
    1:  0.,
    2:  1/3.,  # Morning Break (2 hours)
    3:  1/3.,  # Morning Break (2 hours)
    4:  1/2.,  # Lunch Break
    5:  1/2.,  # Lunch Break
    6:  0.,
    7:  1/3.,  # Afternoon Break
    8:  1/3.,  # Afternoon Break
    9:  0.,
    10: 1/3.,  # Evening Break
    11: 1/3.,  # Evening Break
    12: 0.,
    13: 0.,
    14: 0.,
    15: 0.,
    16: 0.
}

# TODO: construct a OT ratio dictionary
# OT_RATIO = {
#     'Base': {},
#     'Ortho': {},
#     ''
# }

# OT Time Bucket
# [0, 1, 2, 3, 4, 5, 6, 7, 17, 18, 19, 20, 21, 22, 23]


COST_BY_SKILL_PER_HOUR = {'Base':               1,
                          'Base_Ortho':         3,
                          'Base_Ortho_Neuro':   5,
                          'Base_Transplant':    7}
