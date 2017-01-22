#!/usr/bin/env python3
__all__ = ["ControlCodes", "Style", "Color", "BasicColor", "IndexedColor", "RGBColor", "StyleGroup", "groups", "Sheet", "RichStr", "Styler", "rsjoin"]
__author__="KOLANICH"
__license__="Unlicense"
__copyright__=r"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
"""

import re, itertools
from collections import MutableMapping

groups=None

class ControlCodes():
	"""Represents a sequence of control codes"""
	def __init__(self, codes:tuple):
		if not isinstance(codes, tuple):
			codes = (codes,)
	def __str__(self):
		return "".join(("\x1b[",";".join(map(str, self.codes)),"m"))
	def __repr__(self):
		return "".join((self.__class__.name(), ", ", repr(self.codes), ")"))

	def __add__(self, other):
		return __class__(self.codes, other.codes)
	def __iadd__(self, other):
		if type(self) is type(other):
			self.codes+=other.codes
		else:
			return self+other

class Style(ControlCodes):
	"""Represents a style of a string. Its groups contain groups of active styles"""
	def __init__(self, name:str, codes:tuple, group=None):
		super().__init__(codes)
		self.name=name
		self.group=group
		self.codes=codes
	def __repr__(self):
		return "".join(
			[
				str(self),
				((self.group.name+":") if self.group and self.group.name else ""),
				self.name,
				(str(self.group.reset) if self.group and self.group.reset else "\x1b[0m")
			]
		)
	def __iadd__(self, other):
		if self.group is other.group:
			self.codes+=other.codes

class Color(Style):
	def __init__(self, name:str, codes:tuple):
		super().__init__(name, codes)
	
	def setPlane(self, code, bg):
		self.codes=((40 if bg else 30)+code,)
		self.group=(groups["Back"] if bg else groups["Fore"])


class _BasicColor(Color):
	def __init__(self, code, name=None):
		super().__init__(name, (code,))
	
	@property
	def code(self):
		return self.codes[0]
	
	@code.setter
	def code(self, code):
		self.codes=(code,)

	@property
	def index(self):
		return self.code%30
	
	@index.setter
	def index(self, index):
		self.code+=(-self.index+index)
	
	def setNumeric(self, name, val, magic):
		self.code+=(int(bool(val)) - int(getattr(self, name)))*60
	
	@property
	def bg(self):
		return self.index>=10
	
	@bg.setter
	def bg(self, index):
		self.setNumeric("bg", index, 1)
	
	@property
	def intensive(self):
		return self.code>90

	@intensive.setter
	def intensive(self, val:bool):
		self.setNumeric("intensive", val, 60)

class BasicColor(_BasicColor):
	def __init__(self, name, index, intensive=False, bg=False):
		assert(index > 0 and index%10!=8)
		self.setPlane(index, bg)
		if intensive:
			self.codes=(self.codes[0]+60,)
		super().super().__init__(name, self.codes)
	
	def parse(code, name=None):
		a = _BasicColor(code, name)
		a.__class__=__class__
		return a

class IndexedColor(Color):
	def __init__(self, name, index, bg=False):
		assert(index >= 0 and index <= 255)
		self.setPlane(8, bg)
		super().__init__(name, (*self.codes, 5, index))

class _RGBColor(Color):
	def __init__(self, r=0, g=0, b=0, name=None):
		super().__init__(name, (*self.codes, 2, r, g, b))
	
	@property
	def r(self):
		return self.codes[2]
	@r.setter
	def r(self, col):
		self.codes=(self.codes[0], self.codes[1], col, self.codes[3], self.codes[4])

	@property
	def g(self):
		return self.codes[3]
	@g.setter
	def g(self, col):
		self.codes=(self.codes[0], self.codes[1], self.codes[2], col, self.codes[4])
	
	@property
	def b(self):
		return self.codes[3]
	@b.setter
	def b(self, col):
		self.codes=(self.codes[0], self.codes[1], self.codes[2], self.codes[3], col)

class RGBColor(_RGBColor):
	def __init__(self, name, r=0, g=0, b=0, bg=False):
		self.setPlane(8, bg)
		super().__init__(r, g, b, name)

class StyleGroup():
	"""Represent a group of mutually exclusive styles. ```reset``` is dedicated style returning style to default"""
	def __init__(self, name: str, styles, reset=None):
		if reset is not None and not isinstance(reset, Style):
			raise TypeError("Must be either ", type(None), " or compatible with ", Style, " but ", type(reset), " was given")
		self.stylesSet=set()
		self.stylesDict={}
		for style in styles:
			self.addStyle(style)
		self.reset=reset
		self.name=name
	def addStyle(self, style: Style):
		self.stylesSet.add(style)
		self.stylesDict[style.name]=style
		style.group=self
	def __str__(self):
		return str(self.stylesSet)
	def __repr__(self):
		return "".join((
			self.__class__.__name__,"(",
			", ".join(( repr(self.name), repr(self.stylesSet), "reset="+repr(self.reset) )),
			")"
		))


under_score2camelCaseRx=re.compile(r"""_(\w)""")
def under_score2camelCase(str):
	i=0
	res=[]
	for token in under_score2camelCaseRx.split(str):
		if i%2==1:
			res.append(token.upper())
		else:
			res.append(token.lower())
		i+=1
	return "".join(res)

class Storage(MutableMapping):
	"""Represents a storage allowing access by both . and [] notation"""
	def __init__(self, new={}):
		if isinstance(new, MutableMapping):
			self.__dict__=type(self.__dict__)(new)
	
	def __iter__(self):
		return self.__dict__
		
	def __getitem__(self, key):
		return self.__dict__[key]
	
	def __setitem__(self, key, val):
		self.__dict__[key]=val
	def __delitem__(self, key):
		del(self.__dict__[key])
	
	def __contains__(self, item):
		return item in self.__dict__
	
	def __len__(self):
		return len(self.__dict__)
	
	def values(self):
		return self.__dict__.values()
	
	def keys(self):
		return self.__dict__.keys()
	
	def __repr__(self):
		return self.__class__.__name__+"("+repr(self.__dict__)+")"

def initGroups():
	global groups
	reset     =Style("reset", (0 ,))
	blinkReset=Style("reset", (25,))
	foreReset =Style("reset", (39,))
	backReset =Style("reset", (49,))
	
	
	"""This is our global storage of styles"""
	groups={
		"Back"   : StyleGroup("Back" , [backReset], backReset),
		"Fore"   : StyleGroup("Fore" , [foreReset], foreReset),
		"Style"  : StyleGroup("Style", [reset], reset),
		"Blink"  : StyleGroup("Blink", [Style("slow", (5,)), Style("rapid", (6,)), blinkReset], blinkReset)
	}
	
	try:
		import plumbum.colors
		def importPlumbumColors():
			for st in plumbum.colors:
				col=st.full.fg
				colorName=under_score2camelCase(col.name)
				groups["Fore"].addStyle(RGBColor(colorName, *col.rgb, bg=False))
				groups["Back"].addStyle(RGBColor(colorName, *col.rgb, bg=True))
		importPlumbumColors()
	except ImportError as err:
		pass
	
	try:
		import colored
		indexed=colored.colored("A").paint
		for (colorName, index) in indexed.items():
			colorName=under_score2camelCase(colorName)
			index=int(index)
			groups["Fore"].addStyle(IndexedColor(colorName, index, bg=False))
			groups["Back"].addStyle(IndexedColor(colorName, index, bg=True))
	except ImportError as err:
		pass
	
	try:
		import colorama
		coloramaColRx=re.compile("^[A-Z_]+$")
		
		def importColoramaGroup(groupName):
			"""Converts control codes from colorama to our styles"""
			coloramaGroup=getattr(colorama.ansi, "Ansi"+groupName)
			for colorName in dir(coloramaGroup):
				if coloramaColRx.match(colorName): #colorama color names are written in UPPERCASE
					newName=under_score2camelCase(colorName)
					groups[groupName].addStyle(BasicColor.parse(code=getattr(coloramaGroup, colorName), name=newName))
		for groupName in ["Back", "Fore", "Style"]:
			importColoramaGroup(groupName)
	except ImportError as err:
		pass

initGroups()

class Sheet(Storage):
	"""Represents the set of string's styles at any moiment of time"""
	def __init__(self, new={}):
		if new is None:
			for gr in groups:
				self[gr]=groups[gr].reset
		if isinstance(new, Sheet):
			self.__dict__=type(self.__dict__)(new.__dict__)
		if isinstance(new, Style):
			new={new.group.name:new}
		if isinstance(new, list):
			new={n.group.name:n for n in new}
		super().__init__(new)
	
	def diff(old, new):
		patch=Sheet({})
		for gr in groups:
			o=old[gr] if gr in old else groups[gr].reset
			n=new[gr] if gr in new else groups[gr].reset
			if o!=n:
				patch[gr]=n
		return patch
	
	def __sub__(self, other):
		return other.diff(self)
	
	def __add__(self, other):
		return self|other
	
	def __or__(self, other):
		return Sheet({**self.__dict__, **other.__dict__})
	
	def __iadd__(self, other):
		self|=other
	
	def __ior__(self, other):
		self.__dict__={**self.__dict__, **other.__dict__}
	

def optimizeSheetsToOpCodes(buf):
	"""Removes unneeded control codes. To do it computes diffs between initial state and final state """
	initialState=Sheet()
	state=type(initialState)(initialState)
	prevState=type(state)(state)
	
	for it in buf:
		if isinstance(it, Sheet):
			state=type(state)(it)
		else:
			for st in (state-prevState).values():
				yield st
			prevState=type(state)(state)
			yield it
	
	for st in (initialState-prevState).values():
		yield st

def mergeAdjacentOpCodes(buf):
	"""Merges adjacent opcodes into a single opcode"""
	accum=None
	for it in buf:
		if isinstance(it, ControlCodes):
			if accum is None:
				accum=it
			else:
				accum+=it
		else:
			if accum is not None:
				yield accum
				accum=None
			yield it
	if accum is not None:
		yield accum

mergeOpcodes=False

class RichStr():
	"""Represents a string with rich formating. Makes a tree of strings and builds a string from that tree in the end"""
	def __init__(self, *args, sheet=None):
		sheet = sheet if sheet is not None else Sheet()
		self.subStrs=list(args)
		self.sheet=sheet
	
	def __add__(*args):
		return __class__(*args)
	
	def __radd__(self, other):
		return __class__(other, self)
	
	def __iadd__(self, other):
		if isinstance(other, (str, RichStr)):
			self.subStrs.append(other)
		elif isinstance(other, list):
			self.subStrs+=other
	
	def dfs(self, sheet):
		"""Transforms the directed acyclic graph of styles into an iterator of styles-applying operations and strings. It's your responsibility to ensure that the graph is acyclic, if it has a cycle you will have infinity recursion."""
		sheet=Sheet(sheet)+self.sheet
		for subStr in self.subStrs:
			if isinstance(subStr, RichStr):
				for item in subStr.dfs(sheet):
					yield item
			else:
				yield sheet
				yield str(subStr)
	
	def sheetRepr(self):
		"""Returns flat representation of RichString - an array of (Sheet)s and (str)ings"""
		sheet=Sheet(None)
		buf=list(self.dfs(sheet))
		buf.append(sheet)
		return buf
	
	def optimizedOpcodeRepr(self):
		"""Returns optimized representation of RichString where all the styles are replaced with control codes"""
		buf = self.sheetRepr()
		if mergeOpcodes:
			return list(mergeAdjacentOpCodes(optimizeSheetsToOpCodes(buf)))
		else:
			return list(optimizeSheetsToOpCodes(buf))
	
	def __str__(self):
		buf=self.optimizedOpcodeRepr()
		buf=(str(it) for it in buf)
		return "".join(buf)
	
	def __repr__(self):
		return self.__class__.__name__+"("+repr(self.sheetRepr())


class Styler():
	def __init__(self, sheet):
		if isinstance(sheet, Sheet):
			self.sheet=sheet
		else:
			self.sheet=Sheet(sheet)
	def __call__(self, *strs):
		return RichStr(*strs, sheet=self.sheet)

def interleavedChain(delim, *iters):
	"""str.join for iterators """
	iters=iter(iters)
	yield(next(iters))
	for item in iters:
		yield(delim)
		yield(item)

def rsjoin(delim, iter, sheet=None):
	"""Joins (RichStr)ings into a (RichStr)ing"""
	if delim:
		substrs=list(interleavedChain(delim, *iter))
	else:
		substrs=list(iter)
	return RichStr(*substrs, sheet=sheet)

"""Neutral stuff doing nothing for the cases where styles are required"""
neutral=Style("neutral", ())
neutralGroup=StyleGroup("Neutral", [neutral], neutral)
neutralSheet=Sheet({name:neutral for name in groups})
neutralStyler=Styler(neutralSheet)

if __name__ == "__main__":
	import os, random
	from pprint import pprint
	thisLibName=os.path.splitext(os.path.basename(__file__))[0]
	
	wordDelimiter=re.compile("([\\W]+)")
	wordsStylers=itertools.cycle((Styler(groups["Back"].stylesDict["red"]), Styler(groups["Back"].stylesDict["green"]), Styler(groups["Back"].stylesDict["blue"])))
	#wordsStylers=itertools.cycle((Styler(random.choice(list(groups["Back"].stylesSet))) for st in range(5)))
	def decorateWords(sent):
		"""Here we use Stylers"""
		i=0
		for token in wordDelimiter.split(sent):
			if i%2==0:
				yield (next(wordsStylers))(token)
			else:
				yield token
			i+=1
	
	sentDelimiter=re.compile("([\\.?!])")
	sentenceStyles=itertools.cycle((Sheet({"Fore":groups["Fore"].stylesDict["black"], "Blink":groups["Blink"].stylesDict["slow"]}), Sheet({"Fore":groups["Fore"].stylesDict["yellow"]})))
	
	def decoratedSentences(par):
		"""Here we create RichString from iterator over substrings"""
		i=0
		st=next(sentenceStyles)
		for token in sentDelimiter.split(par):
			if i%2==1:
				st=next(sentenceStyles)
				yield RichStr(*decorateWords(token), sheet=st)
			else:
				yield RichStr(*decorateWords(token), sheet=st)
	
	def decorateSentences(par):
		return rsjoin("", decoratedSentences(par))
	
	paragraphDelimiter="\n\n"
	paragraphsStylers=itertools.cycle((Styler(groups["Back"].stylesDict["lightblackEx"]), Styler(groups["Back"].stylesDict["white"])))
	def demo(text:str):
		"""Returns a string with paragraphs formatted"""
		return rsjoin(
			paragraphDelimiter,
			(
				(next(paragraphsStylers))(
					decorateSentences(par)
				)
				for par in text.split(paragraphDelimiter)
			)
		)

	print(demo(thisLibName))
	print(demo("https://github.com/"+__author__+"/"+thisLibName))
	print(demo(__copyright__))