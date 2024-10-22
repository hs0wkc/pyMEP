# -*- coding: utf-8 -*-
import os
from csv import DictReader, reader

'''def ExtensionPath():
	# return module_path.replace('hs0wkc.extension\\lib\\pyCSV.py','')
	# return __file__.replace('pyCSV.py', '')
	return os.path.dirname(__file__)
 
def ConfigFile(configname = 'config.ini'):
	# return os.path.join(ExtensionPath(), 'config.ini')
	return os.path.join(os.path.dirname(__file__), configname)'''

def LibFile(libname = 'G17-2906204.ico'):
	# return os.path.join(ExtensionPath(), libname)
	return os.path.join(os.path.dirname(__file__), libname)

def read_ini(filepath, section, k):
	# https://discourse.pyrevitlabs.io/t/config-create-and-call-parameters/1981
	with open(filepath, "r") as f:
		lines = f.readlines()
	in_section = False
	for line in lines:
		line = line.strip()
		if line.startswith("[") and line.endswith("]"):
			if in_section: break
			in_section = line[1:-1] == section
		elif in_section and "=" in line:
			key, value = line.split("=")
			if k == key.strip():
				return value.strip()
			
def readall_ini(filepath, section):
	with open(filepath, "r") as f:
		lines = f.readlines()		
	return_dict = {}
	in_section = False
	for line in lines:
		line = line.strip()
		if line.startswith("[") and line.endswith("]"):
			if in_section: break
			in_section = line[1:-1] == section
		elif in_section and "=" in line:
			key, value = line.split("=")
			return_dict[key.strip()] = value.strip()
	return return_dict			

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
						
def LookupRange(key, value, data):
	"""
	INPUT            
	key : Key Range
	value : Value Range
	data : Interest key
	OUTPUT
	value in range
	EXAMPLE : 
	Determine the value that key equal 3 from table    
	┌────────┬───────┬───────┐
	│ <= 2.5 │ 2.5-5 │  >=5  │
	├────────┼───────┼───────┤
	│    2.5 │    4  │   6   │
	└────────┴───────┴───────┘
	LookupRange((2.5, 5),(2.5,4,6), 3)
	return 4
	"""
	for i in range(len(key)):
		if i == 0 and data <= key[i]:
			return value[0]        
		elif i > 0 and data > key[i-1] and data <= key[i]:
			return value[i]
		elif i == len(key)-1 and data > key[i]:
			return value[i+1]
		
def InterpolateRange(key, value, data):
	"""
	INPUT            
	key : Key Range
	value : Value Range
	data : Interest key
	OUTPUT
	value in range by interporate
	EXAMPLE : 
	Interporate the value that key equal 2.2 from table    
	┌───────┬───────┬───────┬───────┬───────┬────────┐
	│   1   │  1.5  │   2   │   3   │   4   │   6    │
	├───────┼───────┼───────┼───────┼───────┼────────┤
	│ 20-30 │ 30-40 │ 40-50 │ 50-60 │ 60-80 │ 80-100 │
	└───────┴───────┴───────┴───────┴───────┴────────┘
	InterpolateRange((1,1.5,2,3,4,6), (20,30,40,50,60,80,100), 2.2)
	return 47
	"""
	nkey = list(key)
	nkey.insert(0,key[0]-(key[1]-key[0])/2)
	nkey.append(key[-1] + (key[-1]-key[-2])/2)
	nvalue = [value[0]]
	for i in range(len(value)-1):
		nvalue.append((value[i]+value[i+1])/2)
	nvalue.append(value[-1])
	if data < nkey[0]: return nvalue[0]	
	if data in nkey: return nvalue[nkey.index(data)]	
	if data > nkey[-1]: return nvalue[-1]	
	for i in range(len(nkey)):
		if data > nkey[i] and data < nkey[i+1]:
			break
	keystep = (nkey[i+1] - nkey[i])/(nvalue[i+1] - nvalue[i])	
	for index, k in enumerate(range(int(nvalue[i]), int(nvalue[i+1]))):
		if nkey[i]+index*keystep >= data:
			break
	return k