# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 18:35:48 2024

@author: yigit
"""

import pandas as pd
import numpy as np 
import seaborn as sns
import glob 
import os
from scipy import signal 

path = r"C:\Users\YİĞİT\Desktop\cleaned_dataset\Cells\B5"

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
cap = guide["Capacity"].dropna().reset_index(drop=True).to_frame()
columns = ["Voltage_window","Temperature_difference","Temperature Factor","Voltage Factor"]
ds = pd.DataFrame(columns = columns)
row_counter = 0

capacity_cycle = 1963

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
    temp = df.loc[index,"Temperature_measured"] -df.loc[2,"Temperature_measured"] 
    df.loc[:, "Capacity"] = capacity
    df.loc[:, "Cycle"] = cycle
    window = df["Voltage_measured"].max() - df["Voltage_measured"].min()
    voltage_factor =  ((2*delta_time)/window)
    DTV = temp/window
    temperature_factor = temp/ (delta_time*2)
     
    ICA_values = []
    tempo_values = []
    current_values = []
    temperature_values = []
    voltage_values = []
    
    for i in range(2,index):
        voltage_diff = df.loc[i, "Voltage_measured"] - df.loc[i + 1, "Voltage_measured"] 
        Temp_diff = df.loc[i, "Temperature_measured"] - df.loc[i + 1, "Temperature_measured"] 
        time_diff = df.loc[i + 1, "Time"] - df.loc[i, "Time"]  # Calculate time difference correctly
    
        ICA = (df.loc[i, "Current_measured"] * time_diff)/voltage_diff
        
        current = df.loc[i, "Current_measured"]
        tempo = Temp_diff / current
        
        ICA_values.append(ICA)
        tempo_values.append(tempo)
        current_values.append(current)
        temperature_values.append(Temp_diff/voltage_diff)
        voltage_values.append(voltage_diff)
        
    ft = np.fft.fft(ICA_values)
    ft2 = np.fft.fft(voltage_values)
    ft3 = np.fft.fft(tempo_values)
    tempo_values_np = np.array(tempo_values)
    ICA_values_np = np.array(ICA_values)
    current_values_np = np.array(current_values)
    y = signal.savgol_filter(tempo_values,25,5)
    
    Sxx = 2 * time_diff.mean() ** 2 / (ft2 * np.conj(ft2))
    Sxx_np = np.array(Sxx)
    
    df.loc[:, "Voltage_window"] = window
    df.loc[:, "SOH"] = SOH
    df.loc[:, "Temperature_difference"] = temp
    df.loc[:, "Temperature Factor"] = temperature_factor
    df.loc[:, "Voltage Factor"] = voltage_factor
    df.loc[:,"DTV"] = DTV
    
    ds.loc[row_counter, "Voltage_window"] = window
    ds.loc[row_counter, "SOH"] = SOH
    ds.loc[row_counter, "Temperature_difference"] = temp
    ds.loc[row_counter, "Temperature Factor"] = y.mean() / current_values_np.mean()
    ds.loc[row_counter, "Voltage Factor"] = ICA_values_np.mean()
    ds.loc[row_counter, "DTV"] =  DTV
    
    cycle += 1
    total = pd.concat([total,df])
    
    total2 = pd.concat([total2,ds])