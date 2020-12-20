from pathlib import Path
import glob
import os
import pandas as pd

list_filename = []
list_filesize = []
for y in glob.glob(os.path.join('*.gz')):
    list_filename.append(y)
    list_filesize.append(Path(y).stat().st_size)
df = pd.DataFrame(columns=['name', 'size', 'status'])
df['name'] = list_filename
df['size'] = list_filesize
df.sort_values("size", axis = 0, ascending = True, inplace = True, na_position ='first') 
print(df)
df.to_csv('linkedin_data.csv', index=False)