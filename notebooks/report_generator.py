import pandas as pd
import os
import pathlib

percentile = ['avg', '75', '95']
for pct in percentile:
    folder = f'../result/has_neuro_buffer/v16_ot_{pct}/'
    output_folder = f'../result/has_neuro_buffer/v16_ot_{pct}_result_new/'
    files = os.listdir(folder)

    for staff_type in ['scrub', 'circulator']:
        # staff_type = 'scrub'
        # staff_type = 'circulator'

        circulator_format = 'with_ot_shift_assignment_v16_circulator_Shift_SC{}.xlsx'
        scrub_format = 'with_ot_shift_assignment_v16_scrub_Shift_SC{}.xlsx'


        shift_assignment = pd.DataFrame()
        demand_supply = pd.DataFrame()
        shift_df = pd.DataFrame()
        number_scenarios = 4
        for i in range(1, number_scenarios + 1):
            if staff_type == 'circulator':
                excel = pd.ExcelFile(os.path.join(folder, circulator_format.format(i)))
            else:
                excel = pd.ExcelFile(os.path.join(folder, scrub_format.format(i)))
            _shift_assignment_temp = excel.parse('shift_assignment')
            _demand_supply_temp = excel.parse('demand_supply')
            _shift_df = excel.parse('shift_time')[['Shift_Type', 'Shift_Duration']]
            _shift_assignment_temp['scenario'] = f'SC{i}'
            _demand_supply_temp['scenario'] = f'SC{i}'  
            shift_assignment = pd.concat([shift_assignment, _shift_assignment_temp])
            demand_supply = pd.concat([demand_supply, _demand_supply_temp])    
            shift_df = pd.concat([shift_df, _shift_df])
        shift_df = shift_df.drop_duplicates()

        # Demand Summary
        temp = demand_supply.groupby(['Skill_Group']).agg({'Normal_Demand': sum, 'Break_Demand': sum, 'Overtime_Demand': sum, 'Total_Demand': sum})/number_scenarios
        temp.to_excel(f'{output_folder}{staff_type}_demand_summary.xlsx')

        # Supply Summary
        temp = demand_supply.groupby(['Skill_Group']).agg({'Specific_Supply': sum, 'Other_Supply': sum, 'Total_Supply': sum})/number_scenarios
        temp.to_excel(f'{output_folder}{staff_type}_supply_summary.xlsx')

        temp = demand_supply.groupby(['scenario']).agg({'Total_Supply': sum})
        temp.to_excel(f'{output_folder}{staff_type}_total_supply_by_scenario.xlsx')

        def cal_ot_shift(shift):
            if shift == 'A6':
                return 1
            elif shift == 'A7':
                return 2
            elif shift == 'A8':
                return 3
            elif shift == 'A9':
                return 4
            else:
                return 0

        # overtime summary    
        shift_assignment['overtime'] = shift_assignment.Shift.apply(lambda x: cal_ot_shift(x))
        temp = shift_assignment.groupby(['scenario']).overtime.sum()
        temp.to_excel(f'{output_folder}{staff_type}_overtime_by_scenario.xlsx')

        # shift assignment by day of week
        temp = shift_assignment.loc[shift_assignment.scenario=='SC1'].groupby(['Day', 'Skill_Group']).Number.sum().unstack('Day')/5
        temp.to_excel(f'{output_folder}{staff_type}_shift_assignment_by_day_of_week.xlsx')

        # excess supply
        temp = demand_supply.groupby(['scenario', 'Skill_Group']).Excess.sum().unstack('scenario')
        temp.to_excel(f'{output_folder}{staff_type}_excess_summary_by_scenario.xlsx')

        temp = demand_supply.groupby(['scenario', 'Skill_Group']).Excess.sum().unstack('scenario')/40.
        temp.to_excel(f'{output_folder}{staff_type}_excess_summary_by_scenario_fte_1.xlsx')

        # Number of Nurse (FTE=1)
        nn_df = shift_assignment.groupby(['scenario', 'Shift']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Shift']).Number_Nurse.sum().unstack('scenario')
        temp.to_excel(f'{output_folder}{staff_type}_number_of_nurses_fte_1.xlsx')

        # Number of Nurse (FTE=weighted)
        scale = 0.8 if staff_type == 'circulator' else 0.9
        nn_df = shift_assignment.groupby(['scenario', 'Shift']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(scale*40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Shift']).Number_Nurse.sum().unstack('scenario')
        temp.to_excel(f'{output_folder}{staff_type}_number_of_nurses_fte_weighted.xlsx')


        # Skill Breakdown
        # base of number of shift
        temp = shift_assignment.groupby(['scenario', 'Skill_Group']).Number.sum().unstack('scenario')/shift_assignment.groupby(['scenario', 'Skill_Group']).Number.sum().unstack('scenario').sum()
        temp.to_excel(f'{output_folder}{staff_type}_skill_breakdown_number_of_shifts.xlsx')


        # base of numer of nurses FTE = 1
        nn_df = shift_assignment.groupby(['scenario', 'Shift', 'Skill_Group']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario')/nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario').sum()
        temp.to_excel(f'{output_folder}{staff_type}_skill_breakdown_number_of_nurses_fte_1.xlsx')

        # base of numer of nurses FTE = 0.8
        nn_df = shift_assignment.groupby(['scenario', 'Shift', 'Skill_Group']).Number.sum().reset_index()
        nn_df = pd.merge(nn_df, shift_df[['Shift_Type', 'Shift_Duration']], left_on='Shift', right_on='Shift_Type')
        nn_df['Number_Nurse'] = nn_df['Number']/(0.8*40/nn_df['Shift_Duration']*5)
        temp = nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario')/nn_df.groupby(['scenario', 'Skill_Group']).Number_Nurse.sum().unstack('scenario').sum()
        temp.to_excel(f'{output_folder}{staff_type}_skill_breakdown_number_of_nurses_fte_weighted.xlsx')

        # Shifts breakdown in % (based on the number of shifts)
        temp = shift_assignment.groupby(['scenario', 'Shift']).Number.sum().unstack('scenario')/shift_assignment.groupby(['scenario', 'Shift']).Number.sum().unstack('scenario').sum()
        temp.to_excel(f'{output_folder}{staff_type}_shift_breakdown.xlsx')

