#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-10 15:50
# @Author  : Guangjun
# @eMail   : gsu2@stanford.edu
# @File    : main.py
# @Software: PyCharm

from src.models.schedulor import *
from src.util.utils import *


if __name__ == '__main__':
    data_file = 'data/Staff Scheduling Model_Input Templates_v16.xlsx'  # path to input file

    # for loop to all staff types and scenarios
    # there are two staff types, which are 'circulator' and 'scrub'
    # currently, we have 4 different scenarios
    for staff_type in ['circulator', 'scrub']:
        for shift_scenario in [f'Shift_SC{i}' for i in range(1, 5)]:
            # call the
            X_skd, params, output = shift_assignment(data_file, staff_type, shift_scenario)

            # TODO: the output is not well developed, please help to develop it in the futuer!!

            #####################################
            ##  OUTPUT EXCEL FILE              ##
            ##  1. shift_assignment            ##
            ##  2. demand_supply               ##
            ##  3. supply_excess_analysis      ##
            ##  4. shift_time:                 ##
            #####################################
            excel = pd.ExcelWriter(f'result/v16_ot_avg/with_ot_shift_assignment_v16_{staff_type}_{shift_scenario}.xlsx')

            df = pd.DataFrame(output['records'])
            df.columns = ['Plan_Period', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours', 'Number',
                          'Total_Hours']
            df['Week'] = df['Plan_Period'].apply(lambda x: x.split('_')[1])
            df['Day'] = df['Plan_Period'].apply(lambda x: x.split('_')[0])
            df = df[['Plan_Period', 'Week', 'Day', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours',
                     'Number', 'Total_Hours']]
            df.to_excel(excel, sheet_name='shift_assignment', index=False)

            demand_supply_df = pd.DataFrame(output['demand_supply'])
            demand_supply_df.columns = ['Plan_Period', 'Skill_Group', 'Time_Bucket', 'Normal_Demand', 'Break_Demand',
                                        'Overtime_Demand', 'Total_Demand', 'Specific_Supply', 'Other_Supply']
            demand_supply_df['Start_Time'] = demand_supply_df['Time_Bucket'].apply(lambda x: TIME_BUCKET[x]['start'])
            demand_supply_df['End_Time'] = demand_supply_df['Time_Bucket'].apply(lambda x: TIME_BUCKET[x]['end'])
            demand_supply_df = demand_supply_df[['Plan_Period', 'Skill_Group', 'Time_Bucket', 'Start_Time', 'End_Time',
                                                 'Normal_Demand', 'Break_Demand', 'Overtime_Demand', 'Total_Demand',
                                                 'Specific_Supply', 'Other_Supply']]
            demand_supply_df['Total_Supply'] = demand_supply_df['Specific_Supply'] + demand_supply_df['Other_Supply']
            demand_supply_df['Excess'] = demand_supply_df['Total_Supply'] - demand_supply_df['Total_Demand']
            demand_supply_df.to_excel(excel, 'demand_supply', index=False)

            excess = demand_supply_df.groupby(['Skill_Group', 'Time_Bucket']).Excess.mean().reset_index()
            excess.to_excel(excel, 'supply_excess_analysis', index=False)

            shift_time_df = pd.DataFrame(output['shift_time'])
            shift_time_df.columns = ['Shift_Type', 'Shift_Start', 'Shift_End', 'Shift_Duration', 'Time_Bucket',
                                     'Available?']
            shift_time_df.to_excel(excel, 'shift_time', index=False)

            excel.save()

            ######################################################
            ##  OUTPUT TXT FILE                                 ##
            ##  - Some overall metrics of the shift assignment  ##
            ######################################################

            with open(f'result/v16_ot_avg/with_ot_shift_assignment_v16_{staff_type}_{shift_scenario}.txt', 'w') as f:
                f.write(print_head_block('Overall Metrics'))
                total_nurse_hours = df.Total_Hours.sum()
                total_nurse_numbers = df.Number.sum()
                f.write(f'({staff_type}) Total nurse hours is {total_nurse_hours}\n')
                f.write(f'({staff_type}) Total nurse number is {total_nurse_numbers}\n')
                f.write('\n')

                f.write(print_head_block('Skill Breakdown'))
                f.write(str(df.groupby(['Skill_Group']).Number.sum()/sum(df.groupby(['Skill_Group']).Number.sum())))
                f.write('\n')
                f.write(str(df.groupby(['Skill_Group']).Total_Hours.sum() / sum(df.groupby(['Skill_Group']).Total_Hours.sum())))
                f.write('\n')
                f.write('\n')

                f.write(print_head_block('Shift Breakdown'))
                f.write(str(df.groupby(['Shift']).Number.sum()/sum(df.groupby(['Shift']).Number.sum())))
                f.write('\n')
                f.write(str(df.groupby(['Shift']).Total_Hours.sum() / sum(df.groupby(['Shift']).Total_Hours.sum())))

