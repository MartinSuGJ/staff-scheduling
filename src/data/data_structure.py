#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 16:06
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : data_structure.py
# @Software: PyCharm


class Shift:

    def __init__(self, ID, shift_type, start_time, end_time, shift_length):
        self.ID = ID
        self.shift_type = shift_type
        self.start_time = start_time
        self.end_time = end_time
        self.shift_length = shift_length


class Nurse:

    def __init__(self, ID, first_name, last_name, position, seniority, FTE, max_hours, min_hours, empl_type,
                 shift_preference, day_preference, skill_proficiency, PTO_or_EDU):
        self.ID = ID
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.seniority = seniority
        self.FTE = FTE
        self.max_hours = max_hours
        self.min_hours = min_hours
        self.empl_type = empl_type
        self.shift_preference = shift_preference
        self.day_preference = day_preference
        self.skill_proficiency = skill_proficiency
        self.PTO_or_EDU = PTO_or_EDU


class PlanPeriod:

    def __init__(self, ID, plan_period):
        self.ID = ID
        self.plan_period = plan_period


class Block:

    def __init__(self, ID, plan_period, OR, service, hours, start_time, end_time, staff_start_time, staff_end_time,
                 circulator_demand, scrub_demand):
        self.ID = ID
        self.plan_period = plan_period
        self.OR = OR
        self.service = service
        self.hours = hours
        self.start_time = start_time
        self.end_time = end_time
        self.staff_start_time = staff_start_time
        self.staff_end_time = staff_end_time
        self.circulator_demand = circulator_demand
        self.scrub_demand = scrub_demand


class Break:
    # TODO: need to modify the attributes of Break class
    def __init__(self, ID, plan_period, OR, service, hours, start_time, end_time, staff_start_time, staff_end_time,
                 circulator_demand, scrub_demand):
        self.ID = ID
        self.plan_period = plan_period
        self.OR = OR
        self.service = service
        self.hours = hours
        self.start_time = start_time
        self.end_time = end_time
        self.staff_start_time = staff_start_time
        self.staff_end_time = staff_end_time
        self.circulator_demand = circulator_demand
        self.scrub_demand = scrub_demand


class ModelParameters:

    def __init__(self):
        pass
