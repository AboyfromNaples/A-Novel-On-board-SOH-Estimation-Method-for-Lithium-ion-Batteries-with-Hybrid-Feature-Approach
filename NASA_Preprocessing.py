# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 11:20:12 2024

@author: yigit
"""

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import glob 
import os
import scipy

from scipy import signal

path = r"C:\Users\YİĞİT\Desktop\cleaned_dataset\Cells\B5" #This line should be modified by desired cell type 

data_list = glob.glob(path+"/*.csv")
sub_list = []
guide = pd.read_csv(r"C:\Users\YİĞİT\Desktop\cleaned_dataset\metadata.csv")

for file in data_list:
    filename = os.path.basename(file)  # Extract filename from the file path
    df_name = "df_"+os.path.splitext(filename)[0]  # Remove file extension from the filename
    ov = pd.read_csv(file)
    if len(ov.columns) == 6 and len(ov) > 5 and ov["Current_measured"].iloc[5] <= 0:
            locals()[df_name] = ov
            sub_list.append(df_name)
            
cycle = 1
total = pd.DataFrame()
total2 = pd.DataFrame()
capacity_cycle = 1963 #This line must be modified regarding to discharge data from cell & guide file
cap = guide["Capacity"].dropna().reset_index(drop=True).to_frame()
columns = ["Temperature Factor","ICA"]
ds = pd.DataFrame(columns = columns)
row_counter = 0
for name in sub_list:
    df = locals()[name]  # Access the actual dataframe using locals()
    df["Counter"] = range(0,len(df))
    index = df["Voltage_measured"].idxmin()
    time = df.loc[index, "Time"]  # Access the "Time" column of the dataframe
    delta_time = time - df.loc[2,"Time"]
    capacity = cap.iloc[capacity_cycle, 0]
    capacity_cycle = capacity_cycle + 1
    SOH = (float(capacity)/2.0)*100
    if SOH > 100:
        SOH = 100
        
    ICA_values = []
    temperature_values = []
    voltage_values = []
    temp_values = []
    
    for i in range(2,index-1):
        
        if df.loc[i, "Voltage_measured"] > 3.4:
            voltage_diff = df.loc[i, "Voltage_measured"] - df.loc[i + 1, "Voltage_measured"] 
            time_diff = df.loc[i + 1, "Time"] - df.loc[i, "Time"]  # Calculate time difference correctly
            ICA = (df.loc[i, "Current_measured"] * time_diff/3600)/(voltage_diff) 
            ICA_values.append(ICA)
        else:
            Temp_diff = df.loc[i, "Temperature_measured"] - df.loc[i + 1, "Temperature_measured"]
            time2 = df.loc[i + 1, "Time"] - df.loc[i, "Time"]
            Temperature_Factor = (Temp_diff) / ((df.loc[i, "Current_measured"])  * time2)
            temperature_values.append(Temperature_Factor)
            
        voltage = df.loc[i, "Voltage_measured"]
        voltage_values.append(voltage)
        temp_values.append(df.loc[i, "Temperature_measured"])
        

    temp_values = temp_values[temp_values != 0]
    df.loc[:, "SOH"] = SOH
    
    ds.loc[row_counter, "SOH"] = SOH
    ds.loc[row_counter, "ICA"] = np.mean(ICA_values)
    ds.loc[row_counter, "Temperature Factor"] = np.mean(temperature_values) 
    
    cycle += 1
    total = pd.concat([total,df])
    total2 = pd.concat([total2,ds])
    kantır = 1;

        
    """y = signal.savgol_filter(ICA_values,5,3)
    plt.plot(voltage_values,y,lw = 3)

plt.xlabel("Voltage(V)")
plt.ylabel("ICA(dQ/dV)")"""


corr = total2.corr()
    
total2 = total2[total2['SOH'] != 0]
total2.to_csv("Final_B5.csv", index = True)
