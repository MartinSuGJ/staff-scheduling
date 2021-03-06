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
        fte_weight = 0.8 if staff_type == 'circulator' else 0.9
        num_of_scenarios = 4
        assignment_all_scenarios = pd.DataFrame()
        demand_all_scenarios = pd.DataFrame()
        excess_all_scenarios = pd.DataFrame()
        shift_df = pd.DataFrame()
        for shift_scenario in [f'Shift_SC{i}' for i in range(1, num_of_scenarios + 1)]:
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
            excel = pd.ExcelWriter(f'result/v16_ot_75/with_ot_shift_assignment_v16_{staff_type}_{shift_scenario}.xlsx')

            df = pd.DataFrame(output['records'])
            df.columns = ['Plan_Period', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours', 'Number',
                          'Total_Hours']
            df['Week'] = df['Plan_Period'].apply(lambda x: x.split('_')[1])
            df['Day'] = df['Plan_Period'].apply(lambda x: x.split('_')[0])
            df = df[['Plan_Period', 'Week', 'Day', 'Skill_Group', 'Shift', 'Shift_Start', 'Shitf_End', 'Shift_Hours',
                     'Number', 'Total_Hours']]
            df.to_excel(excel, sheet_name='shift_assignment', index=False)

            df_with_scenario = df.copy()
            df_with_scenario['scenario'] = shift_scenario
            assignment_all_scenarios = pd.concat([assignment_all_scenarios, df_with_scenario])

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

            demand_supply_df_all_scenarios = demand_supply_df.copy()
            demand_supply_df_all_scenarios['scenario'] = shift_scenario
            demand_all_scenarios = pd.concat([demand_all_scenarios, demand_supply_df_all_scenarios])

            excess = demand_supply_df.groupby(['Skill_Group', 'Time_Bucket']).Excess.mean().reset_index()
            excess.to_excel(excel, 'supply_excess_analysis', index=False)

            excess_by_scenario = excess.copy()
            excess_by_scenario['scenario'] = shift_scenario
            excess_all_scenarios = pd.concat([excess_all_scenarios, excess_by_scenario])

            shift_time_df = pd.DataFrame(output['shift_time'])
            shift_time_df.columns = ['Shift_Type', 'Shift_Start', 'Shift_End', 'Shift_Duration', 'Time_Bucket',
                                     'Available?']
            # shift_time_df.to_excel(excel, 'shift_time', index=False)

            shift_df = pd.concat([shift_df, shift_time_df])

            excel.save()

        shift_df = shift_df.drop_duplicates()


        ######################################################
        ##  OUTPUT EXCEL FILE                               ##
        ##  - Some overall metrics of the shift assignment  ##
        ######################################################
        metrics_xlsx = pd.ExcelWriter(f'result/v16_ot_75/with_ot_shift_assignment_v16_{staff_type}_metrics.xlsx')

        # Demand Summary
        temp = demand_all_scenarios.groupby(['Skill_Group', 'scenario']).agg({'Total_Demand': sum}).unstack('scenario')
        print(temp)
        temp.to_excel(metrics_xlsx, 'Demand Summary')

        # Supply Summary
        temp = demand_all_scenarios.groupby(['Skill_Group', 'scenario']).agg({'Total_Supply': sum}).unstack('scenario')
        temp.to_excel(metrics_xlsx, 'Supply Summary')

        # Excess Summary
        temp = excess_all_scenarios.groupby(['Skill_Group', 'scenario']).agg({'Excess': sum}).unstack('scenario') * 5 * 5
        temp.to_excel(metrics_xlsx, 'Excess Summary')

        # Excess supply FTE=1 by skillset
        temp = excess_all_scenarios.groupby(['Skill_Group', 'scenario']).agg({'Excess': sum}).unstack('scenario') * 5 * 5 / (40 * 5)
        temp.to_excel(metrics_xlsx, 'Excess Supply by Skill (FTE=1)')

        # Number of Nurses (FTE = 1)
        nn_df = assignment_all_scenarios.groupby(['scenario', 'Shift', 'Skill_Group']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Shift']).Number_Nurse.sum().unstack('scenario') / 25 #/nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario').sum()
        temp.to_excel(metrics_xlsx, '# of Nurse by Shift (FTE = 1)')

        # Number of Nurses (FTE = weighted average)
        nn_df = assignment_all_scenarios.groupby(['scenario', 'Shift', 'Skill_Group']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(fte_weight * 40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Shift']).Number_Nurse.sum().unstack('scenario') / 25 #/nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario').sum()
        temp.to_excel(metrics_xlsx, f'# by Shift (FTE = {fte_weight})')

        # Shifts breakdown in % (based on the number of shifts)
        temp = assignment_all_scenarios.groupby(['scenario', 'Shift']).Number.sum().unstack(
            'scenario') / assignment_all_scenarios.groupby(['scenario', 'Shift']).Number.sum().unstack('scenario').sum()
        temp.to_excel(metrics_xlsx, 'Shift Breakdown')

        # Skills breakdown (based on number of shifts)
        temp = assignment_all_scenarios.groupby(['scenario', 'Skill_Group']).Number.sum().unstack(
            'scenario') / assignment_all_scenarios.groupby(['scenario', 'Skill_Group']).Number.sum().unstack('scenario').sum()
        temp.to_excel(metrics_xlsx, 'Skill Breakdown')

        # Skills breakdown by Number: hours of supply per skill group / 40*weighted FTE*5_ weeks
        temp = assignment_all_scenarios.groupby(['scenario', 'Skill_Group']).Total_Hours.sum().unstack('scenario')/(40*fte_weight*5)
        temp.to_excel(metrics_xlsx, f'Skill Breakdown (FTE={fte_weight})')

        # Skills breakdown by Number: hours of supply per skill group / 40*5
        temp = assignment_all_scenarios.groupby(['scenario', 'Skill_Group']).Total_Hours.sum().unstack('scenario') / (40 * 5)
        temp.to_excel(metrics_xlsx, f'Skill Breakdown (FTE=1)')

        metrics_xlsx.save()

