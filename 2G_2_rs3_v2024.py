#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:12:28 2019

@author: pablitolito

Searches for all *.dat files from the 2G cryogenic system in the folder
where the script is located.
Generates a *.asc file in 2G format for each file.
"""

import csv
from os import listdir
import numpy as np
# from datetime import datetime


def filename():
    """
    Gets the name of .dat files present in the folder.
    Output:
        List with the name of each *.dat file.
    """
    
    files_name=[]
    for f in listdir("."):
        if f.endswith('.dat'):
            files_name.append(f)
    files_name.sort()
    print(len(files_name), '*.dat files found')
    
    return files_name

def dir2car(dir): 
    """
    being 'dir' a list of lists, with pairs of Dec, Inc in degrees
    converts from geographic to cartesian coordinates
    """
	
    dec=np.radians(dir[0])
    inc=np.radians(dir[1])
    
    x=np.cos(dec)*np.cos(inc) 
    y=np.sin(dec)*np.cos(inc) 
    z=np.sin(inc)                 
    
    cart=[x,y,z]
    
    modulo=np.sqrt(x*x+y*y+z*z)
    print('Module: ', modulo)
    
    # print('Cart: ', cart)
    return cart

def car2dir(cart): 
    """
    being 'cart' a list of lists, with x, y, z
    converts from cartesian to geographic coordinates
    """
	
	
    dec=round(np.degrees(np.arctan2(cart[1],cart[0])),1)
    inc=round(np.degrees(np.arcsin(cart[2])), 1)
    dir=[dec%360,inc]
	
    # print('Dir: ', dir)
    return dir

def spe2geo(dec, inc, az, pl): 
    """
    converts from specimen to geographic coordinates
    """
    
    
    car=dir2car([dec, inc])
        
    # A1=dir2car([az, pl])
    # A2=dir2car([az + 90., 0])
    # A3=dir2car([az - 180, 90. - pl])
    
    A1=dir2car([az, pl - 90.])
    A2=dir2car([az + 90., 0])
    A3=dir2car([az, pl])

    x_rot = A1[0] * car[0] + A2[0] * car[1] + A3[0] * car[2]
    y_rot = A1[1] * car[0] + A2[1] * car[1] + A3[1] * car[2]
    z_rot = A1[2] * car[0] + A2[2] * car[1] + A3[2] * car[2]
    
    
    
    dir_geo=car2dir([x_rot, y_rot, z_rot])
    
    return dir_geo


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


    
def format_RS3(header, data):
    """
    Function to convert raw data from the conv function into the RS3 format
 
    Input (output of the conv program)
    ----------
    Header: list with the header and its relevant data
    Data: list of lists with data related to each demagnetization step
        
    Returns
    -------
    out_format: data in RS3 format

    """
    
    out=[]
        
    header_1=['Name'.ljust(10)+ 'Site'.ljust(10)+ 'Latitude'.ljust(10)+ 'Longitude'.ljust(11)+
          'Height'.ljust(10)+ 'Rock'.ljust(15)+ 'Age'.ljust(5)+ 'Fm'.ljust(3)+
          'SDec'.ljust(6)+ 'SInc'.ljust(6)+ 'BDec'.ljust(6)+ 'BInc'.ljust(6)+
          'FDec'.ljust(6)+'FInc'.ljust(6)+ 'P1'.ljust(3)+ 'P2'.ljust(3)+ 'P3'.ljust(3)+
          'P4'.ljust(3)+ 'Note'.ljust(4)]

    name=header[0]
    az=header[4]
    pl=header[5]
    dipdir=header[6]
    if header[8]==0:
        dip=header[7]
    else:
        dip=str(180-int(header[7]))

    datos_muestra=[name.ljust(74)+az.ljust(6)+ pl.ljust(6)+ dipdir.ljust(6)+ dip.ljust(18)+
                  '12'.ljust(3)+ '90'.ljust(3)+ '12'.ljust(3)+ '0'.ljust(7)]

    # print('Len_data: ', len(data))
    if len(data)>0:
        if data[-1][0][-1:]=='C':
            treat='T'
            unidades='Step[°C]'
        else:
            treat='A'
            unidades='Step[mT]'
    else: unidades='Step[°C]'


    header_2=['ID'.ljust(3)+ unidades.ljust(17)+'M[A/m]'.ljust(9)+'Dsp'.ljust(6)+'Isp'.ljust(6)+
             'Dge'.ljust(6)+'Ige'.ljust(6)+'Dtc'.ljust(6)+'Itc'.ljust(6)+'Dfc'.ljust(6)+'Ifc'.ljust(6)+
             'Prec'.ljust(8)+'K[e-06 SI]'.ljust(11)+'Limit1'.ljust(10)+'Limit2'.ljust(10)+'Note'.ljust(10)]
    
    out.append(header_1)
    out.append(datos_muestra)
    out.append(header_2)
    
                
    if len(data)>0:            
        for dato in data:
            if dato[0]=='NRM':
                id='N'
                step=0
            else:
                if treat=='T':
                    id='T'
                    step=dato[0][:-1]
                else:
                    id='A'
                    step=dato[0][:-4]
        

            mag=format(float(dato[8])*1000, "1e")
            dsp=dato[1]
            isp=dato[2]
            dge=dato[3]
            ige=dato[4]
            dtc=dato[5]
            itc=dato[6]
            prec='1.0'
        
            data=[id.ljust(3)+ str(step).ljust(3)+ str(mag).rjust(21)+ str(dsp).rjust(6)+ str(isp).rjust(6)+
                  str(dge).rjust(6)+ str(ige).rjust(6)+ str(dtc).rjust(6)+ str(itc).rjust(6)+ 
                  str(prec).rjust(18)+ ' '.rjust(45)]
            
            out.append(data)


    return out
    


files=filename()


print(len(files), 'files converted to *.rs3')

for file in files:
    header, data=conv(file)
    out_RS3=format_RS3(header, data)
    name_RS3=file[:-3]+'rs3'
        
    file_out=open(name_RS3, 'w', encoding="cp1252")
    writer=csv.writer(file_out, lineterminator='\r\n')
    for row in out_RS3:
        writer.writerow(row)
    del writer
    file_out.close()
    

        