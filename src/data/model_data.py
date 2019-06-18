#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 20:08
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : model_data.py
# @Software: PyCharm

import pandas as pd
import re
from config import *


def construct_model_data(data_file, staff_type, shift_scenario):
    excel = pd.ExcelFile(data_file)
    block = excel.parse('Block')
    shift = excel.parse(shift_scenario)
    period = excel.parse('Plan_Period')
    skill = excel.parse('Service_Skills')
    overtime = excel.parse('OT_Demand_75')


    ##################
    ##  PARAMETERS  ##
    ##################
    # set of shifts
    P1_s = set(shift.loc[shift.Shift_Length > 0].Shift_Type.unique())
    P1_s_hours = _construct_shift_hours(shift, P1_s)

    # set of time buckets
    P2_t = set(range(len(TIME_BUCKET)))

    # 1 if shift s is available at time bucket t; 0 otherwise
    # dictionary type: (s, t): 1/0
    P3_st = _construct_shift_time_param(shift, P1_s, P2_t)

    # set of skills
    P4_k, service_skill_mapping = _construct_skill(skill)

    # cost of staffing per nurse with skill k
    # TODO: need to use the right cost for each skill
    P5_sk = _compute_nurse_cost_by_skill_and_shift(shift, P1_s, P4_k)

    # set of plan period
    P6_d = set(period.Plan_Period.unique())

    # number of nurses with skill k at time bucket t on day d are needed for normal block
    P7_ktd = _construct_block_demand(block, P4_k, P2_t, P6_d, staff_type)

    # number of nurses with skill k at time bucket t on day d are needed for break schedule
    P8_ktd = _construct_break_demand(P7_ktd)

    # number of nurses with skill k at time bucket t on day d are needed for overtime
    P9_ktd = _construct_overtime_demand(overtime, P7_ktd)

    # sum of the total demand
    P10_ktd = _sum_total_demand(P7_ktd, P8_ktd, P9_ktd)

    # total number of nurses with skill k
    # TODO:
    P11_k = None

    # maximum weekly working hours of nurses with skill k
    # TODO:
    P12_k = None

    # list of list of days d for each week
    P13_w = {'W1': {'Mon_W1', 'Tue_W1', 'Wed_W1', 'Thur_W1', 'Fri_W1', 'Sat_W1', 'Sun_W1'},
             'W2': {'Mon_W2', 'Tue_W2', 'Wed_W2', 'Thur_W2', 'Fri_W2', 'Sat_W2', 'Sun_W2'},
             'W3': {'Mon_W3', 'Tue_W3', 'Wed_W3', 'Thur_W3', 'Fri_W3', 'Sat_W3', 'Sun_W3'},
             'W4': {'Mon_W4', 'Tue_W4', 'Wed_W4', 'Thur_W4', 'Fri_W4', 'Sat_W4', 'Sun_W4'},
             'W5': {'Mon_W5', 'Tue_W5', 'Wed_W5', 'Thur_W5', 'Fri_W5', 'Sat_W5', 'Sun_W5'}}

    params = {'P1_s':       P1_s,
              'P1_s_hours': P1_s_hours,
              'P2_t':       P2_t,
              'P3_st':      P3_st,
              'P4_k':       P4_k,
              'P5_sk':      P5_sk,
              'P6_d':       P6_d,
              'P7_ktd':     P7_ktd,
              'P8_ktd':     P8_ktd,
              'P9_ktd':     P9_ktd,
              'P10_ktd':    P10_ktd,
              'P11_k':      P11_k,
              'P12_k':      P12_k,
              'P13_w':      P13_w}

    return params


def _construct_shift_time_param(shift, P1_s, P2_t):
    """
    Construct a dictionary to specify availability of each shift at each time bucket, e.g. 'F' starts from 7 to 19,
    then res[('F', 0)] to res[('F', 11)] equals to 1; res[('F', 12)] to res[('F', 16)] equals to 0

    :param shift: pd.DataFrame of shift
    :param P1_s: set of shifts
    :param P2_t: set of time bucket
    :return: a dictionary with key of shift and time bucket to specify availability of each shit at each time bucket
    """
    res = dict()
    for s in P1_s:
        start = shift.loc[shift.Shift_Type == s, "Shift_Start_Time"].values[0]
        end = shift.loc[shift.Shift_Type == s, "Shift_End_Time"].values[0]
        for t in P2_t:
            _t_start = TIME_BUCKET[t]['start']
            _t_end = TIME_BUCKET[t]['end']
            if (start <= _t_start <= end) and (start <= _t_end <= end):
                res[(s, t)] = 1
            elif (s == 'G') and (start <= _t_start):
                res[(s, t)] = 1
            else:
                res[(s, t)] = 0

    return res


def _process_skill_group(skill):
    """
    Mapping specific skillset into skillset group.

    :param skill: string, name of any specific skillset
    :return: string, name of its belonging skillset group
    """
    if skill == 'Transplant':
        return skill
    elif skill == 'Orthopedics':
        return 'Ortho'
    elif skill == 'Nephrology' or skill == 'Neurosurgery':
        return 'Neuro'
    else:
        return 'Base'


def _construct_block_demand(block, P4_k, P2_t, P6_d, staff_type):
    """
    Construct a dictionary, res[(k, t, d)], to specify minimum number of nurses with skill k at time bucket t on day d
    in order to meet the block demand. Now, we assume 100% utilization of block hours. Also, we have already considered
    the special requirement for block with 'OSC' tag. For a block with 'OSC' tag, two circulators and 1 scrub techs are
    required to be staffed for that block

    :param block: pd.DataFrame, block schedule dataframe
    :param P4_k: set of skillset group
    :param P2_t: set of time bucket
    :param P6_d: set of plan periods (day)
    :param staff_type: string to specify staff_type, e.g. 'circulator', or 'scrub'
    :return: a dictionary, res[(k, t, d)]
    """
    res = dict()
    for k in P4_k:
        for t in P2_t:
            for d in P6_d:
                res[(k, t, d)] = 0

    len_df = len(block)
    for i in range(len_df):
        _record = block.iloc[i]
        start = _record.Demand_Start_Time_Rounded
        end = _record.Demand_End_Time_Rounded
        k = _record.Skill
        d = _record.Plan_Period
        is_OSC = _record['OSC?']
        for t in P2_t:
            _t_start = TIME_BUCKET[t]['start']
            _t_end = TIME_BUCKET[t]['end']
            if (start <= _t_start <= end) and (start <= _t_end <= end):
                if is_OSC == 'Yes' and staff_type == 'circulator':
                    res[(k, t, d)] += 2
                else:
                    res[(k, t, d)] += 1

    return res


def _construct_break_demand(P7_ktd):
    """
    Construct a dictionary, res[(k, t, d)], to specify minimum number of nurses with skill k at time bucket t on day d
    in order to meet the breaker demand. Now, we assume the breaker schedule (time) and ratio are fixed. You can play
    around with different schedule or ratio in the configuration file. Note, the breaker demand is proportional to the
    normal block demand, so we calculate the breakder demand based on the normal block demand.

    :param P7_ktd: dictionary, normal block demand.
    :return: a dictionary, res[(k, t, d)]
    """
    res = dict()
    for (k, t, d) in P7_ktd:
        if t == 3 or t == 5 or t == 8 or t == 11:
            continue
        else:
            if t == 2 or t == 4 or t == 7 or t == 10:
                conversion = BREAK_CONVERSION[t]
                num_breakers = max(P7_ktd[(k, t, d)], P7_ktd[(k, t, d)]) * conversion
                int_num_breakers = int(num_breakers)
                decimal_num_breakers = num_breakers - int_num_breakers
                res[(k, t, d)] = int_num_breakers + ((1/conversion)/2.) * decimal_num_breakers
                res[(k, t+1, d)] = int_num_breakers
            else:
                res[(k, t, d)] = 0

    return res


def _construct_overtime_demand(overtime, P7_ktd):
    """
    Construct a dictionary, res[(k, t, d)], to specify minimum number of nurses with skill k at time bucket t on day d
    in order to meet the over-block/OT demand. Now, we use summer 2018 data to summarize the over-block demand by day of
    week and by types of skillset group. Now, we use R to process the historical data and input into this model.

    :param overtime: pd.DataFrame, overtime schedule dataframe
    :param P7_ktd: dictionary, normal block demand
    :return: a dictionary, res[(k, t, d)]
    """
    res = dict()
    # Initialize the overtime demand
    for (k, t, d) in P7_ktd:
        res[(k, t, d)] = 0.

    skills = ['Base', 'Base_Ortho', 'Base_Ortho_Neuro', 'Base_Transplant']
    for i in range(len(overtime)):
        _row = overtime.iloc[i]
        _d = _row.Plan_Period
        for k in skills:
            _ot_demand = _row[k]
            _ot_demand = [float(it) for it in re.findall(r'[-+]?([0-9]*\.[0-9]+|[0-9]+)', _ot_demand)]
            _ot_demand = _ot_demand[8:]
            for _t, _ot_d in enumerate(_ot_demand):
                t = _t + 10
                if _t >= 1:
                    res[(k, t, _d)] += max(_ot_d - P7_ktd[(k, t, _d)], 0)

    # modify the late night demand to ensure we assign the night shift for each day
    for (k, t, d) in P7_ktd:
        if t >= 12 and res[(k, t, d)] == 0 and k == 'Base':
            res[(k, t, d)] += 0.01

    return res


def _sum_total_demand(P7_ktd, P8_ktd, P9_ktd):
    """
    Construct a dictionary, res[(k, t, d)], to specify minimum number of nurses with skill k at time bucket t on day d
    in order to meet the block, breaker, and overtime demand. We sum up the demand from normal block demand, breakder
    demand and overtime demand.

    Also, we consider the 'Neuro Buffer' constraint, i.e. staffing one more 'Neuro' nurse and one less 'Base' nurse if
    there is any demand for 'Neuro' on that day.

    Note: The way that we deal with 'Neuro Buffer' is stupid but effective for current block schedule. This could be
    coded in a smarter way.

    :param P7_ktd: dictionary, block demand
    :param P8_ktd: dictionary, breaker demand
    :param P9_ktd: dictionary, overtime demand
    :return: a dictionary, res[(k, t, d)]
    """
    res = dict()
    for (k, t, d) in P7_ktd:
        res[(k, t, d)] = P7_ktd[(k, t, d)] + P8_ktd[(k, t, d)] + P9_ktd[(k, t, d)]

    for (k, t, d) in P7_ktd:
        # Add Neuro Buffer
        if k == 'Base_Ortho_Neuro' and res[(k, 1, d)] > 0 and t >= 0 and t <= 9:
            res[(k, t, d)] += 1
            res[('Base', t, d)] -= 1

    return res


def _compute_nurse_cost_by_skill_and_shift(shift, P1_s, P4_k):
    """
    Construct a dictionary, res[(s, k)], to specify cost of staffing per nurse with skill k to shift s.

    The cost is equal to hourly_cost_by_skill * length_of_shift. The hourly_cost_by_skill is specified in config.py, see
    'COST_BY_SKILL_PER_HOUR'.

    :param shift: pd.DataFrame, shift dataframe
    :param P1_s: set of shift
    :param P4_k: set of skillset group
    :return: a dictionary, res[(s, k)]
    """
    res = dict()
    for s in P1_s:
        _shift_length = shift.loc[shift.Shift_Type == s, 'Shift_Length'].values[0]
        # TODO: add start time preference
        _start = shift.loc[shift.Shift_Type == s, 'Shift_Start_Time'].values[0]
        _additional_cost = 0
        if _start == 7:
            _additional_cost = 5
        for k in P4_k:
            res[(s, k)] = COST_BY_SKILL_PER_HOUR[k] * _shift_length + _additional_cost

    return res


def _construct_shift_hours(shift, P1_s):
    """
    Construct a dictionary, res[(s)], to specify hours of each shift, and it includes shift start time, shift end time,
    and shift length.

    :param shift: pd.DataFrame, shift dataframe
    :param P1_s: set of shift
    :return: a dictionary, res[(s)]
    """
    res = dict()
    for s in P1_s:
        _shift_length = shift.loc[shift.Shift_Type == s, 'Shift_Length'].values[0]
        _shift_start = shift.loc[shift.Shift_Type == s, 'Shift_Start_Time'].values[0]
        _shift_end = shift.loc[shift.Shift_Type == s, 'Shift_End_Time'].values[0]
        res[s] = (_shift_start, _shift_end, _shift_length)

    return res


def _construct_skill(skill):
    """
    Return set of skillset group, and mapping from service to skillset group.

    :param skill: pd.DataFrame, skill dataframe
    :return: skills_set (set of skillset group), and service_skill_mapping (mapping from service to skillset group)
    """
    skills_set = set(skill.Skill.unique().tolist())
    service_skill_mapping = dict()
    for i in range(len(skill)):
        _service = skill.iloc[i].Service
        _skill = skill.iloc[i].Skill
        service_skill_mapping[_service] = _skill

    return skills_set, service_skill_mapping
