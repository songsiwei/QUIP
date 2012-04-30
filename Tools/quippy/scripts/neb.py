#!/usr/bin/env python

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

from quippy import *
from ase.constraints import FixAtoms
from ase.neb import SingleCalculatorNEB
from ase.optimize import MDMin
from ase.optimize.fire import FIRE
import numpy as np
import sys
import os
import optparse

def write_band(neb, filename):
    out = AtomsWriter(filename)
    for image in neb.images:
        cp = image.copy()
        cp.params['energy'] = image.get_potential_energy()
        cp.add_property('force', image.get_forces().T, overwrite=True)
        out.write(cp)
    out.close()

p = optparse.OptionParser(usage='%prog [OPTIONS] INFILE')
p.add_option('-R', '--refine', action='store', type='int', help='Refine NEB pathway by this many steps')
p.add_option('-I', '--init-args', action='store', help='QUIP Potential init_args string', default="IP SW")
p.add_option('-p', '--param-file', action='store', help='Read QUIP potential XML from this file.', default='crack.xml')
p.add_option('-c', '--climb', action='store_true', help='If true, do climbing image NEB', default=False)
p.add_option('-k', action='store', type='float', help='Spring constant for NEB', default=1.0)
p.add_option('-O', '--optimizer', action='store', help='Optimizer to use: currently FIRE or MDMin', default="FIRE")
p.add_option('-w', '--write-traj', action='store', type='int', help='Write trajectory every this many steps')
p.add_option('-m', '--minim', action='store_true', help="Minimize start and end points before starting NEB")
p.add_option('--minim-method', action='store', help="Method to use for initial minimisations: sd, cg, cg_n or fire", default="cg_n")
p.add_option('--minim-tol', action='store', type='float', help="Tolerance for initial minimisations - df^2, (eV/A)^2", default=1e-3)
p.add_option('--minim-max-steps', action='store', type='int', help="Maximum number of steps for initial minimisations", default=100)
p.add_option('--minim-no-do-pos', action='store_true', help="If true, relax positions in initial minimisations")
p.add_option('--minim-do-lat', action='store_true', help="If true, relax lattice in initial minimisations")

opt, args = p.parse_args()

try:
    infile, = args
except:
    p.error('Exactly one input file must be given, got %r' % args)
    
basename = os.path.splitext(infile)[0]
images = AtomsList(infile)

if opt.minim:
    pot = Potential(opt.init_args, param_filename=opt.param_file)
    for at in (images[0], images[-1]):
        at.set_cutoff(pot.cutoff() + 1.0)
        pot.minim(at,
                  opt.minim_method,
                  opt.minim_tol,
                  opt.minim_max_steps,
                  do_pos=not opt.minim_no_do_pos,
                  do_lat=opt.minim_do_lat)


images = list(images) # FIXME -- unclear why we have to convert from AtomsList to list

have_constraint = hasattr(images[0], 'move_mask')
if have_constraint:
    constraint = FixAtoms(mask=np.logical_not(images[0].move_mask.view(np.ndarray)))

neb = SingleCalculatorNEB(images, climb=opt.climb, k=opt.k)

if opt.refine:
    neb.refine(opt.refine)

if have_constraint:
    for image in images:
        image.set_constraint(constraint)

calculators = [Potential(opt.init_args, param_filename=opt.param_file, inplace=False) for at in neb.images ]
neb.set_calculators(calculators)

print 'Starting NEB run with %d images' % len(neb.images)

# Optimize:
if opt.optimizer == 'FIRE':
    optimizer = FIRE(neb)
elif opt.optimizer == 'MDMin':
    optimizer = MDMin(neb)
else:
    p.error('Unknown optimizer %s' % opt.optimizer)

if opt.write_traj is not None:
    n = 0
    def write_traj():
        global neb, n
        write_band(neb, '%s-band-%d.xyz' % (basename, n))
        n += 1
    optimizer.attach(write_traj, interval=opt.write_traj)
    
optimizer.run(fmax=0.03)
write_band(neb, '%s-optimized.xyz' % basename)