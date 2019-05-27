#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 15:50
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : main.py
# @Software: PyCharm

from src.models.schedulor import *


if __name__ == '__main__':
    X_skd, params, records = shift_assignment('/Users/gsu2/Desktop/git/StanfordProject/staff-scheduling/data/Staff Scheduling Model_Input Templates_v11.xlsx')
    df = pd.DataFrame(records)
    df.columns = ['Plan_Period', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours', 'Number', 'Total_Hours']
    df['Week'] = df['Plan_Period'].apply(lambda x: x.split('_')[1])
    df['Day'] = df['Plan_Period'].apply(lambda x: x.split('_')[0])
    df = df[['Plan_Period', 'Week', 'Day', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours', 'Number', 'Total_Hours']]
    df.to_excel('data/shift_assignment_v11.xlsx', index=False)
