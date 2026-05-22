def find_max_feature(feature, dataframe, label=None):
    max_ftr = dataframe[feature].idxmax()
    max_ftr_value = dataframe.loc[max_ftr, feature]
    lga_name = dataframe.loc[max_ftr, 'LGA_NAME'] 
    display = label if label else feature 
    print(f"The LGA with the highest {display} is {lga_name} with a {display} of {max_ftr_value}")