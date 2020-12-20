import glob
import os
import pandas as pd



path = input("Please enter a path:\n")

result = []

for x in os.walk(path):
    for y in glob.glob(os.path.join(x[0], '*.xls')):
        result.append(y)
list_of_dfs = [pd.read_excel(filename) for filename in result]
field = os.path.basename(path)
city = os.path.basename(os.path.dirname(path))
print('city: {}, field: {}'.format(city, field))

for dataframe, filename in zip(list_of_dfs, result):
    dataframe['filename'] = os.path.basename(filename)
    dataframe['field'] = field
    dataframe['city'] = city

if len(list_of_dfs) > 0:
    combined_df1 = pd.concat(list_of_dfs, ignore_index=True)
else:
    combined_df1 = pd.DataFrame()

for x in os.walk(path):
    for y in glob.glob(os.path.join(x[0], '*.xlsx')):
        result.append(y)
list_of_dfs = [pd.read_excel(filename) for filename in result]
for dataframe, filename in zip(list_of_dfs, result):
    dataframe['filename'] = os.path.basename(filename)
    dataframe['field'] = field
    dataframe['city'] = city

if len(list_of_dfs) > 0:
    combined_df2 = pd.concat(list_of_dfs, ignore_index=True)
else:
    combined_df2 = pd.DataFrame()

combined_df =  pd.concat([combined_df1, combined_df2], ignore_index=True)
print(combined_df.head(5))
combined_df.to_excel(os.getcwd()+'/datanew/{}_{}.xlsx'.format(city, field),index=False, engine='xlsxwriter')

