#!/usr/bin/env python3
import os, sys
import unittest
import itertools
import colorama
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..')))

from collections import OrderedDict
dict=OrderedDict

from RichConsole import *

red=Sheet()
red.Fore=groups["Fore"].stylesDict["red"]

green=Sheet()
green.Back=groups["Back"].stylesDict["green"]

cyan=Sheet()
cyan.Fore=groups["Fore"].stylesDict["cyan"]

class Tests(unittest.TestCase):
	reference=(
		(
			RichStr( "DDD",            RichStr("RRR",              RichStr("GGG", sheet=green),        "rrr", sheet=red),          "ddd" ),
			"".join(["DDD", colorama.Fore.RED, "RRR", colorama.Back.GREEN, "GGG", colorama.Back.RESET, "rrr", colorama.Fore.RESET, "ddd"])
		),
	)
	def testReferenceCases(self):
		for case in self.reference:
			self.assertEqual(str(case[0]), case[1])
	
	def testSideEffects(self):
		order=[]
		order.append(RichStr("GGG", sheet=green))
		order.append(RichStr("CCC", sheet=cyan))
		order.append(RichStr("RRR", order[0], "rrr", order[1], "RRR", sheet=red))
		order.append(RichStr("DDD", order[2], "ddd"))
		
		perms=list(itertools.permutations(range(len(order))))[1:]
		reference=[str(rs) for rs in order]
		
		for perm in perms:
			self.assertEqual([str(rs) for rs in (order[pos] for pos in perm)], [reference[pos] for pos in perm])
		

if __name__ == '__main__':
	unittest.main()
