# -*- coding: utf-8 -*-
import os
from csv import DictReader, reader

def ExtensionPath():
    #return module_path.replace('hs0wkc.extension\\lib\\pyCSV.py','')
    return __file__.replace('pyCSV.py', '')

def LibFile(libname = 'G17-2906204.ico'):
    return os.path.join(ExtensionPath(), libname)

def ConfigFile():
    return os.path.join(ExtensionPath(), 'config.ini')

# https://discourse.pyrevitlabs.io/t/config-create-and-call-parameters/1981
def read_ini(filepath, section, k):
    with open(filepath, "r") as f:
        lines = f.readlines()

    in_section = False
    for line in lines:
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_section = line[1:-1] == section
        elif in_section and "=" in line:
            key, value = line.split("=")
            if k == key.strip():
                return value.strip()

def write_ini(filepath, section, k, v):
    with open(filepath, "r") as f:
        lines = f.readlines()

    in_section = False
    outlines = []
    for line in lines:
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_section = line[1:-1] == section
        elif in_section and "=" in line:
            key, value = line.split("=")
            if k == key.strip():
                line = line.replace(value.strip(), v)
        outlines.append(line)

    with open(filepath, "w") as f:
        for line in outlines:
            f.write(str(line))
            f.write("\n")
        f.close()

def csvlist(csvstr):
    return [i.strip() for i in csvstr.split(',')]

def read_csv(csvfile, k, v, e=None):
    """
	INPUT            
	csvfile : CSV Filename
	k : KEY
	v : VALUE
	e : VALUE or list of dicionary
	OUTPUT
	value corresponding with return KEY or list of dicionary
	EXAMPLE : Find Steam Condensate(sc_thk) Insualtion Thickness of 50mm pipe sch40 from 'PipeInsulation.csv' file.
	read_csv('PipeInsulation.csv', 'nps', '50 mm', 'sc_thk')    
	return 2
    or
    read_csv('PipeInsulation.csv', 'nps', '50 mm')
	"""
    with open(csvfile) as f:
        csvdata = DictReader(f)
        for row in csvdata:
            if row[k] == v:
                return (row if e == None else row[e])

def read_csv2(csvfile, k, v, e):
    """
	INPUT            
	csvfile : CSV Filename
	k : list of KEY               -> [k1, k2, ...]
	v : list of specific VALUE    -> [v1, v2, ...]
	e : list of return KEY        -> [e1, e2, ...]
	OUTPUT
	list of value corresponding with return KEY 
	EXAMPLE : Find Outside Diameter and thickness of 15mm pipe sch40 from 'PipeTable.csv' file.
	read_csv2('PipeTable.csv', ['nps','Para'],['15 mm','t'],['OD','40'])    
	return [21.3, 2.77]
	"""
    with open(csvfile) as f:
        csvdata = DictReader(f)
        for row in csvdata:
            key = True
            for i in range(len(k)):
                key = key and (row[k[i]] == v[i])
            if key:
                outvalue = []
                for i in range(len(e)):
                    outvalue.append(row[e[i]])
                return outvalue

def readall_csv(csvfile, mainlist, k, v, e):
    """
	INPUT
	csvfile : CSV Filename
	mainllist : list of specific VALUE fo MainKey   -> [v1, v2, ...]
	k : list of KEY                                 -> [MainKey, SubKey]
	v : specific VALUE of SubKey
	e : VALUE
	OUTPUT
	list of value corresponding with return KEY
	EXAMPLE : Find oustside diameter of 15mm, 20mm, 25mm pipe from 'PipeTable.csv' file.
	readall_csv('PipeTable.csv', ['15 mm','20 mm', '25mm'], ['nps', 'Para'], 't', 'OD')
	return [21.3, 26.7, 33.4]
	"""
    with open(csvfile) as f:
        csvdata = DictReader(f)
        outvalue = []
        for mainkey in range(len(mainlist)):
            f.seek(0)
            for row in csvdata:
                if row[k[0]] == mainlist[mainkey] and row[k[1]] == v:
                    outvalue.append(row[e])
        return outvalue

def readall_csv2(csvfile, mainlist, k, e):
    """
    INPUT            
	csvfile : CSV Filename
	mainllist : list of specific VALUE fo MainKey   -> [v1, v2, ...]
	k : KEY
	v : specific VALUE of Key        
	e : VALUE   
    OUTPUT
	list of value corresponding with return KEY
    EXAMPLE : Find oustside diameter of 15mm, 20mm, 25mm pipe from 'PipeTable.csv' file.
	readall_csv('PipeThickness.csv', ['15 mm','20 mm', '25mm'], 'nps', 'OD')
	return [21.3, 26.7, 33.4]
    """
    with open(csvfile) as f:
        csvdata = DictReader(f)
        outvalue = []
        for mainkey in range(len(mainlist)):
            f.seek(0)
            outvalue.append([row[e] for row in csvdata if row[k] == mainlist[mainkey]][0])
        return outvalue

def LookupTable(csvfile, k, v, e, Maximize=True):
    """
    INPUT            
	csvfile : CSV Filename
	k : The data which is being looked up. The input is the number of the column, counted from the left
	v : Vertical Lookup value on k column
	e : Horizon Lookup value on v row
    OUTPUT
	Header value 
    EXAMPLE : 
	Determine the required pipe size with the length is 320ft delivery 5000 BTU/hr.
	Using the Longest Length Method table LPG10-1 file
	vlookup('LPG10-1.csv', 0, 320, 5000)
	return '40 mm'
    """
    with open(csvfile, mode='r') as f:
        header = list(f.readline().strip().split(','))
        csvdata = reader(f)
        vt = [lines[k] for lines in csvdata]
        for i in range(len(vt)):
            if Maximize:
                if float(vt[i]) >= v:
                    v = float(vt[i])
                    break
            else:
                if float(vt[i]) >= v:
                    v = float(vt[i - 1])
                    break
        f.seek(0)
        f.readline()  # skip header line
        for lines in csvdata:
            if float(lines[k]) == v:
                for i in range(1, len(lines)):
                    if Maximize:
                        if float(lines[i]) >= e:
                            return header[i]
                    else:
                        if float(lines[i]) >= e:
                            return header[i - 1]