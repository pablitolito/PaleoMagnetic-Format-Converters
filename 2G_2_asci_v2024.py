#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:12:28 2019

@author: pablitolito

Searches for all *.dat files from the 2G cryogenic system present in the folder
where this script is located.
Generates a *.asc file in 2G format for each file.
"""

import csv
from os import listdir
# from datetime import datetime


def filename():
    """
    Gets the name of .dat files present in the folder
    Output:
        List with the name of each *.dat file
    """
    
    files_name=[]
    for f in listdir("."):
        if f.endswith('.dat'):
            files_name.append(f)
    files_name.sort()
    print(len(files_name), '*.dat files found')
    
    return files_name


def conv(file_name):
    """
    Function to convert hexadecimal 2G files into text
    
    Input: name of the file to convert
    Output:
        header: Specimen info
        d_limpio: Raw data 
    """
        
    f=(open(file_name, 'rb'))
    f.seek(14)
    g=str(f.read(1))
    
    # Searching for the specimen name, which starts at position seek(15)
    i=0
    f.seek(15)
    g=str(f.read(1))
    name_spec=str()
    while len(g)==4:
        i+=1                
        name_spec=name_spec+g[2]
        f.seek(15+i)      
        g=str(f.read(1))
    # print('Name_specimen: ', name_spec)
    
    # Searching for the volume, which starts at position seek(24)
    i=0
    f.seek(24)
    g=str(f.read(1))
    vol=str()
    while len(g)==4:
        i+=1                
        vol=vol+g[2]
        f.seek(24+i)      
        g=str(f.read(1))
    # print('vol: ', vol)
    
    # Checking if it's mass or volume. Depends on the byte at seek(33)
    f.seek(33)
    g=f.read(1)
    if g!=b'\x01':
        gm=0
        cc=1
    else:
        gm=1
        cc=0
    
    # Searching for the file creation date. seek(37:53)
    f.seek(37)
    g=f.read(17)
    date=str(g)[2:-1]
    # print('Date: ', date)
    
    
    # Searching for the specimen azimuth. Starts at seek(111)
    i=0
    f.seek(111)
    g=str(f.read(1))
    az=str()
    while len(g)==4:
        i+=1                
        az=az+g[2]
        f.seek(111+i)      
        g=str(f.read(1))
    # print('Az: ', az)
    
    # Searching for the specimen plunge. Starts at seek(116)
    i=0
    f.seek(116)
    g=str(f.read(1))
    pl=str()
    while len(g)==4:
        i+=1                
        pl=pl+g[2]
        f.seek(116+i)      
        g=str(f.read(1))
    # print('Pl: ', pl)
    
    # Searching for the specimen dip direction. Starts at seek(120)
    i=0
    f.seek(120)
    g=str(f.read(1))
    dd=str()
    while len(g)==4:
        i+=1                
        dd=dd+g[2]
        f.seek(120+i)      
        g=str(f.read(1))
    # print('DD: ', dd)
    
    # Searching for the specimen dip. Starts at seek(125)
    i=0
    f.seek(125)
    g=str(f.read(1))
    dip=str()
    while len(g)==4:
        i+=1                
        dip=dip+g[2]
        f.seek(125+i)      
        g=str(f.read(1))
    # print('Dip: ', dip)
    
    # Checking if bedding is normal or inverted. Depends on the byte at seek(129)
    f.seek(129)
    over=f.read(1)
    if over!=b'\x01':
        over=0
    else: 
        over=1
        # print('Inverted!!!!!!!!!!!!')
                
    # Generates the header, which is in 2G_asci format
    # header=['NAME', 'SIZE', 'CC', 'GM', 'CA', 'CP', 'DA', 'DP', 'Overturned', 'FA', 'FP', 'MD', 'TIME','noCOMMENT']
    header=[name_spec, vol, cc, gm, az, pl, dd, dip, over, date]
    # print('Header: ', header)
        
    f=(open(file_name, 'rb'))
    input=str(f.read()).strip("b '")
    f.close()
    d=input.split('\\xcd')[1:]
                      
    d_limpio=[]
    for dato in d:
        out=dato.split('\\x00')
        out=list(filter(None, out))[0:26]
        # print('Len_out: ', len(out))
        d_limpio.append(out)
        
    # print('d_limpio: ', d_limpio)
    # print('len_d_limpio: ', len(d_limpio))
    
    return header, d_limpio


    
def format_asci(header, data):
    """
    Function to convert raw data from the conv function
    into the format output by the 2G program for ASCII conversion
 
    Input (from conv function)
    ----------
    Header: list with the header and related data
        output from the conv function
    Data: list of lists with data for each demagnetization step
        output from the conv function
        
    Returns
    -------
    out_format : list
        all data in 2G ASCII format

    """
        
    # Creating the first header
    out_format=[[len(data)]]
    out_l=['NAME', 'SIZE', 'CC', 'GM', 'CA', 'CP', 'DA', 'DP', 'Overturned', 'FA', 'FP', 'MD', 'TIME','noCOMMENT']
    out_format.append(out_l)
        
    # Collecting sample data from the first header
    name=header[0]
    vol=header[1]
    cc=header[2]
    gm=header[3]
    coreA=header[4]
    coreP=header[5]
    dipA=header[6]
    dipP=header[7]
    over=header[8]
    time=header[9]
    
    out_l=[name, vol, cc, gm, coreA, coreP, dipA, dipP, over, 0, 0, 0, time]
    out_format.append(out_l)
    
    # print('Out_format: ', out_format)
    
    # Creating the second header
    out_l=['#', 'DEMAG', 'CD', 'CI', 'ISD', 'ISI', 'RD', 'RI', 'M', 'J', 'X', 'SX', 
           'NX', 'EX', 'Y', 'SY', 'NY', 'EY', 'Z', 'SZ', 'NZ', 'EZ', 'S/N', 'S/D', 'S/H']
    out_format.append(out_l)
    # print('out_format: ', out_format)
    
    # Collecting data for each step (if any) and adding it to the list
    i=1
    if len(data)>1:
        for dato in data:
            dato.insert(0,i)            
            # print('Dato: ', dato)
            out_format.append(dato)
            i=i+1
    else: pass
    
    return out_format
    


files=filename()


print(len(files), 'files converted to *.asc')

for file in files:
    header, data=conv(file)
    out_asci=format_asci(header, data)
    name_asci=file[:-3]+'asc'
    file_out=open(name_asci, 'w')
    writer=csv.writer(file_out,delimiter='\t', lineterminator='\n')
    for row in out_asci:
        writer.writerow(row)
    del writer
    file_out.close()
    

        