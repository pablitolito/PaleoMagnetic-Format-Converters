#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:12:28 2019

@author: pablitolito

Searches for all *.dat files from the 2G cryogenic system present in the folder
where this script is located.
Generates a *.th Utrecht format file with the information of the different specimens
"""

import csv
from os import listdir
from datetime import datetime


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


def format_utrecht(files):
    """
    Returns
    -------
    out : list
        Output file in Utrecht format
    """
    
    
    out=[['Robot','2G DC']]
    n=0
    end=[9999]
    
    for file in files:
        # Heading for each specimen
        n+=1
        # print(file)
        header, in_data=conv(file)
        # print('Input: ', in_data)
        # print('Over: ', over)
        name=header[0]
        print('Name: ', name)
        vol=header[1]
        coreA=header[4]
        coreP=header[5]
        dipA=(int(header[6])-90)%360
        
        if header[8]==0:
            dipP=header[7]
        else: 
            dipP=180-int(header[7])
        
        cab=[[name, n, coreA, coreP, vol, dipA, dipP]]
        
        # Initializes variables and takes all the steps of each sample, adding them to a list
        step=[]
        a=[]
        b=[]
        c=[]
        date=[]
        time=[]
        
        if len(in_data)>1:
            for dato in in_data:
                # print('Dato: ', dato)
                if dato[0]=='NRM': 
                    step=0
                elif dato[0][-1:]=='C':
                    step=dato[0][:-1]
                elif dato[0][-2:]=='mT':
                    step=dato[0][:-2]
                else: pass
                # print('Step: ', step)
                x=float(dato[9])
                y=float(dato[13])
                z=float(dato[17])
                # print(x)
                # print(y)
                # print(z)
                a=(-z)*10**9
                b=(-x)*10**9
                c=(y)*10**9
                date=dato[25].split(' ')
                date=date[0]+' '+date[1]+' '+date[2]
                time=date[3]
                # print("Time: ", time)
                date_f=datetime.strptime(date, "%b %d %Y")
                # print("date_f: ", date_f)
                date_out=datetime.strftime(date_f, "%d/%m/%Y")
                # print("Date_out: ", date_out)
                paso=[step,format(a,'e'),format(b,'e'),format(c,'e'),0.99,date_out,time]
                cab.append(paso)
            cab.append(end)
            # print('cab: ',cab)
            # print('cab[0]: ',cab[0])
            out.extend(cab)
        else: pass

    out.append(['END'])

    print( n, 'specimens added to "Utrecht_format.th')
    return out


files=filename()

file=format_utrecht(files)

file_out=open('Utrecht_format.th','w')
writer=csv.writer(file_out,delimiter=',',lineterminator='\r\n')
for row in file:
    writer.writerow(row)
del writer
file_out.close()
