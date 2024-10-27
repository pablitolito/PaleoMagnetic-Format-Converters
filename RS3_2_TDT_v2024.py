#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:56:45 2024

@author: pablo
"""

import csv
import numpy as np
from os import listdir
import sys



def filename():
    """
    Gets the name of .rs3 files present in the folder
    Output:
        List with the name of each *.rs3 file
    """
    
    files_name=[]
    for f in listdir("."):
        if f.endswith('.rs3'):
            files_name.append(f)
    files_name.sort()
    print(f'\n{len(files_name)} *.rs3 files found\n')
    
    return files_name

def getRS3(filename):
    '''
    Gets the data from the rs3 file without the header, and only selects the necessary columns
    Output:
        List with the data from each file used in to_TDT
    '''
    
    # Data is saved in "data", without the header and without the NRM measurement
    # If you want to keep the NRM, change 4 to 3 in skip_header
    data=np.genfromtxt(filename, dtype='str', skip_header=4, encoding="cp1252")
    data2=np.delete(data, (0, -1), axis=1)
    
    return data2
    
def to_TDT(file_name, checks_pos, lab_field):
    '''
    Function to generate the file in TDT format
    '''
    
    data=getRS3(file_name)
    name=file_name[:-4]
      
    
    # Informing the user of the number of records per file
    print(f'{name} has {str(len(data))} records')
    
        
    # Collecting checks (ending in 2) and removing them from the main data list
    i=0
    checks_data=[]
    for dato in data:
        if dato[0][-1]=='2':
            data=np.delete(data, i, axis=0)
            checks_data.append(dato)
            i-=1
        i+=1
    
    # Inserting the checks in the corresponding positions
    if len(checks_data)!=len(checks_pos):
        print(f'\nThe file {file_name} contains {len(checks_data)} checks but {len(checks_pos)} was/were expected')
        print('The number of checks (steps ending in 2) and the number of indicated positions should be the same\n')
        if len(checks_data)>0:
            for check in checks_data:
                data=np.insert(data, len(data), check, axis=0)
        else: pass
    else:
        try: 
            for check, pos in zip(checks_data, checks_pos):
                data=np.insert(data, int(pos)-1, check, axis=0)
        except (IndexError, ValueError):      
                data=np.insert(data, len(data), check, axis=0)
                print(f'\nWarning!!! Problems adding the check {check[0]} in {name}')
                print('It is added at the end of the file\n')
                
                
    # Adding the code to each step depending on the type of measurement
    for dato in data:
        dato[0]=f'{dato[0][:2]}0.{dato[0][2:]}0'
    
    
    # Inserting the specimen name as the first column
    name_l=[]
    for i in range (len(data)):
        name_l.append(name)
        
    data=np.insert(data, 0, name_l, axis=1)

    
    # Adding header according to TDT files
    header=[['Thellier-tdt','' ,'' ,'' ,''], [lab_field, '0.0', '0.0', '0.0', '0.0']]
    tdt_out=np.insert(data, 0, header, axis=0)
        
    return tdt_out



checks = input("Indicate the measurement number(s) corresponding to the checks (excluding the NRM), separated by commas: ")
checks_l = checks.split(',') if checks !='' else []
input_lab_field = input("\nIndicate the laboratory field used for experiments (µT): ")
try: 
    lab_field = f'{float(input_lab_field):.1f}'
except:
    print('Please input a valid laboratory field (e.g., 40)')
    sys.exit()
print(f'\nLab_field: {lab_field}')
    

files=filename()


for file in files:
    out_tdt=to_TDT(file, checks_l, lab_field)
    name_tdt=file[:-3]+'tdt'
    file_out=open(name_tdt, 'w')
    writer=csv.writer(file_out,delimiter='\t', lineterminator='\n')
    for row in out_tdt:
        writer.writerow(row)
    del writer
    file_out.close()