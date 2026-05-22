import pandas as pd
from helpers.py import find_max_feature

biggerdf = pd.read_csv('bigger_df_clean', index_col='LGA_CODE_2021')

print("What feature would you like to find the maximum of (must be a column name from the dfs")
feature = input()
print("Would you like to give it a name (makes it nicer to read)? If you would respond with the name here, if not just press enter")
label = input()


if label:
    find_max_feature(feature, biggerdf, label)
else:
    find_max_feature(feature, biggerdf)