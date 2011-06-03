# HQ XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# HQ X
# HQ X   quippy: Python interface to QUIP atomistic simulation library
# HQ X
# HQ X   Copyright James Kermode 2010
# HQ X
# HQ X   These portions of the source code are released under the GNU General
# HQ X   Public License, version 2, http://www.gnu.org/copyleft/gpl.html
# HQ X
# HQ X   If you would like to license the source code under different terms,
# HQ X   please contact James Kermode, james.kermode@gmail.com
# HQ X
# HQ X   When using this software, please cite the following reference:
# HQ X
# HQ X   http://www.jrkermode.co.uk/quippy
# HQ X
# HQ XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

"""quippy package

James Kermode <james.kermode@kcl.ac.uk>

Contains python bindings to the libAtoms/QUIP Fortran 95 codes
<http://www.libatoms.org>. """

import sys
assert sys.version_info >= (2,4,0)

import atexit, os, numpy, logging
from ConfigParser import ConfigParser

# Read ${HOME}/.quippyrc config file if it exists
cfg = ConfigParser()
quippyrc = os.path.join(os.environ['HOME'],'.quippyrc')
if os.path.exists(quippyrc):
   cfg.read(quippyrc)

# Read config file given in ${QUIPPY_CFG} if it exists
if 'QUIPPY_CFG' in os.environ and os.path.exists(os.environ['QUIPPY_CFG']):
   cfg.read(os.environ['QUIPPY_CFG'])

if 'logging' in cfg.sections():
   if 'level' in cfg.options('logging'):
      logging.root.setLevel(getattr(logging, cfg.get('logging', 'level')))

disabled_modules = []
if 'modules' in cfg.sections():
   for name, value in cfg.items('modules'):
      if not int(value):
         disabled_modules.append(name)

# External dependencies
available_modules = []
unavailable_modules = []
for mod in ['netCDF4', 'pylab', 'scipy', 'ase', 'atomeye', 'enthought.mayavi']:
   if mod in disabled_modules: continue
   try:
      __import__(mod)
      available_modules.append(mod)
   except ImportError:
      unavailable_modules.append(mod)

logging.debug('disabled_modules %r' % disabled_modules)
logging.debug('available_modules %r' % available_modules)
logging.debug('unavailable_modules %r' % unavailable_modules)

if 'netCDF4' in available_modules:
   from netCDF4 import Dataset
   netcdf_file = Dataset
else:
   from pupynere import netcdf_file

AtomsReaders = {}
AtomsWriters = {}

def atoms_reader(source, lazy=True):
   """Decorator to add a new reader"""
   def decorate(func):
      from quippy import AtomsReaders
      func.lazy = lazy
      if not source in AtomsReaders:
         AtomsReaders[source] = func
      return func
   return decorate

import _quippy

# Reference values of .true. and .false. from Fortran
QUIPPY_TRUE = _quippy.qp_reference_true()
QUIPPY_FALSE = _quippy.qp_reference_false()

from oo_fortran import FortranDerivedType, FortranDerivedTypes, FortranRoutines, fortran_class_prefix, wrap_all

# Read spec file generated by f90doc and construct wrappers for classes
# and routines found therein.

def quippy_cleanup():
   try:
      _quippy.qp_verbosity_pop()
      _quippy.qp_system_finalise()
   except AttributeError:
      pass

_quippy.qp_system_initialise(-1, qp_quippy_running=QUIPPY_TRUE)
_quippy.qp_verbosity_push(0)
atexit.register(quippy_cleanup)

from spec import spec
wrap_modules = spec['wrap_modules']
# Jointly wrap atoms_types, atoms and connection into the respective classes
del wrap_modules[wrap_modules.index('atoms_types')]
del wrap_modules[wrap_modules.index('atoms')]
del wrap_modules[wrap_modules.index('connection')]
del wrap_modules[wrap_modules.index('domaindecomposition')]
wrap_modules += [ [ 'atoms_types', 'atoms', 'connection', 'domaindecomposition' ] ]
###
classes, routines, params = wrap_all(_quippy, spec, wrap_modules, spec['short_names'], prefix='qp_')

QUIP_ROOT = spec['quip_root']
QUIP_ARCH = spec['quip_arch']
QUIP_MAKEFILE = spec['quip_makefile']

for name, cls in classes:
   setattr(sys.modules[__name__], name, cls)

for name, routine in routines:
   setattr(sys.modules[__name__], name, routine)

sys.modules[__name__].__dict__.update(params)

# Import custom sub classes
import atoms;           from atoms import Atoms, make_lattice, get_lattice_params, get_bulk_params
import dictionary;      from dictionary import Dictionary
import cinoutput;       from cinoutput import CInOutput, CInOutputReader, CInOutputWriter
import dynamicalsystem; from dynamicalsystem import DynamicalSystem
import potential;       from potential import Potential
import table;           from table import Table
import extendable_str;  from extendable_str import Extendable_str

for name, cls in classes:
   try:
      # For some Fortran types, we have customised subclasses written in Python
      new_cls = getattr(sys.modules[__name__], name[len(fortran_class_prefix):])
   except AttributeError:
      # For the rest, we make a dummy subclass which is equivalent to Fortran base class
      new_cls = type(object)(name[len(fortran_class_prefix):], (cls,), {})
      setattr(sys.modules[__name__], name[len(fortran_class_prefix):], new_cls)

   FortranDerivedTypes['type(%s)' % name[len(fortran_class_prefix):].lower()] = new_cls

del classes
del routines
del params
del wrap_all
del fortran_class_prefix
del spec

import fortranio;   from fortranio import *
import farray;      from farray import *
import atomslist;   from atomslist import *
import periodic;    from periodic import *
import util;        from util import *

import sio2, povray, cube, xyz, netcdf

if 'ase' in available_modules:
   import aseinterface

try:
   import castep
except ImportError:
   logging.warning('quippy.castep import failed.')

if is_interactive_shell():
   if 'atomeye' in available_modules:
      import atomeye
      import atomeyewriter

   if 'enthought.mayavi' in available_modules:
      import plot3d

   if 'pylab' in available_modules:
      import plot2d

   import elastic
   from elastic import *

   import surface
   from surface import *

   import crack
   from crack import *
   
   
