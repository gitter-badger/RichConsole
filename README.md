RichConsole.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![TravisCI Build Status](https://travis-ci.org/KOLANICH/RichConsole.svg?branch=master)](https://travis-ci.org/KOLANICH/RichConsole)
[![PyPi Status](https://img.shields.io/pypi/v/RichConsole.svg)](https://pypi.python.org/pypi/RichConsole)
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/RichConsole.svg)](https://coveralls.io/r/KOLANICH/RichConsole)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/RichConsole.svg)](https://libraries.io/github/KOLANICH/RichConsole)

This is a tool to output "poor" (because it is limited by standardized control codes) rich text into console.

You create a tree structure where each piece of string has its own stylesheet. After you have finished forming the output message you convert it into a string. The library does the rest.

How does it work?
-----------------

The algorithm is damn simple: it just traverses the tree in depth-first way, determines exact style of each string, computes differences between them and emits control codes to apply them.


Requirements
------------
* [```Python 3```](https://www.python.org/downloads/). ```Python 2``` is dead, stop raping its corpse. Use ```2to3``` with manual postprocessing to migrate incompatible code to ```3```. It shouldn't take so much time. For unit-testing you need Python 3.6+ or PyPy3 because their ```dict``` is ordered.

Optional requirements
---------------------
This library automatically imports colors and other control codes from the following libraries:
* [```colorama```](https://github.com/tartley/colorama/)
  [![PyPi Status](https://img.shields.io/pypi/v/colorama.svg)](https://pypi.python.org/pypi/colorama)
  [![TravisCI Build Status](https://travis-ci.org/tartley/colorama.svg?branch=master)](https://travis-ci.org/tartley/colorama)
  ![License](https://img.shields.io/github/license/tartley/colorama.svg)

* [```plumbum.colorlib```](https://github.com/tomerfiliba/plumbum/)
  [![PyPi Status](https://img.shields.io/pypi/v/plumbum.svg)](https://pypi.python.org/pypi/plumbum)
  [![TravisCI Build Status](https://travis-ci.org/tomerfiliba/plumbum.svg?branch=master)](https://travis-ci.org/tomerfiliba/plumbum)
  ![License](https://img.shields.io/github/license/tomerfiliba/plumbum.svg)

* [```colored```](https://github.com/dslackw/colored/)
  [![PyPi Status](https://img.shields.io/pypi/v/colored.svg)](https://pypi.python.org/pypi/colored)
  [![TravisCI Build Status](https://travis-ci.org/dslackw/colored.svg?branch=master)](https://travis-ci.org/dslackw/colored)
  ![License](https://img.shields.io/github/license/dslackw/colored.svg)
