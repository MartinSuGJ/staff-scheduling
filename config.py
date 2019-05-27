#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 15:51
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : config.py
# @Software: PyCharm

TIME_BUCKET = {
    0:  {'start': 7, 'end': 9},
    1:  {'start': 9, 'end': 11},
    2:  {'start': 11, 'end': 13},
    3:  {'start': 13, 'end': 14},
    4:  {'start': 14, 'end': 15},
    5:  {'start': 15, 'end': 16},
    6:  {'start': 16, 'end': 17},
    7:  {'start': 17, 'end': 18},
    8:  {'start': 18, 'end': 19},
    9:  {'start': 19, 'end': 20},
    10: {'start': 20, 'end': 21},
    11: {'start': 21, 'end': 23},
    12: {'start': 23, 'end': 7}
}

BREAK_CONVERSION = {
    0:  0.,
    1:  1/3.,  # Morning Break (2 hours)
    2:  1/2.,  # Lunch Break
    3:  0.,
    4:  1/3.,  # Afternoon Break
    5:  1/3.,  # Afternoon Break
    6:  0.,
    7:  1/3.,  # Evening Break
    8:  1/3.,  # Evening Break
    9:  0.,
    10: 0.,
    11: 0.,
    12: 0.
}

# TODO: construct a OT ratio dictionary
# OT_RATIO = {
#     'Base': {},
#     'Ortho': {},
#     ''
# }


COST_BY_SKILL_PER_HOUR = {'Base':               1,
                          'Base_Ortho':         2,
                          'Base_Ortho_Neuro':   3,
                          'Base_Transplant':    4}
