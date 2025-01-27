import clr
clr.AddReference(r"wpf\\PresentationFramework")
from io import StringIO
from System import Object
from System.Collections.Generic import List, IEnumerable
from System.IO import StreamReader
from System.Windows import Window, LogicalTreeHelper
from System.Windows.Markup import XamlReader
from winsound import Beep
from xml.etree.ElementTree import parse

def ErrorBeep(frequency=440, duration=550):
	Beep(frequency, duration)

def GetIEnumerable(inlist):
	ListIEnumerable = List[Object]()
	for i in inlist:
		ListIEnumerable.Add(i)
	return IEnumerable[Object](ListIEnumerable)

class Wpf(Window):
	def _LoadComponent(self, xaml_file:str|None=None, xaml_str:str|None=None):
		# Define namespaces
		namespaces = {'x': 'http://schemas.microsoft.com/winfx/2006/xaml',
					   '': 'http://schemas.microsoft.com/winfx/2006/xaml/presentation'}
		# Parse the XAML file
		root = parse(xaml_file).getroot() if xaml_file is not None else parse(StringIO(xaml_str))
		
		# Find all elements with the x:Name attribute
		named_elements = root.findall(".//*[@x:Name]", namespaces)
		
		# Extract and print element name and x:Name value
		for elem in named_elements:
			# element_name = elem.tag.split('}')[-1]  # Remove namespace prefix
			name_value = elem.attrib[f"{{{namespaces['x']}}}Name"]
			# print(f"Element: {element_name}, x:Name: {name_value}")
			exec('self.' + name_value + '= LogicalTreeHelper.FindLogicalNode(self.window,'+ '"' + name_value + '")')
			
	def __init__(self, xaml_file:str|None=None, xaml_str:str|None=None):
		self.window = XamlReader.Load(StreamReader(xaml_file).BaseStream) if xaml_file is not None else XamlReader.Parse(xaml_str)
		self._LoadComponent(xaml_file=xaml_file, xaml_str=xaml_str)
