# H0 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# H0 X
# H0 X   libAtoms+QUIP: atomistic simulation library
# H0 X
# H0 X   Portions of this code were written by
# H0 X     Albert Bartok-Partay, Silvia Cereda, Gabor Csanyi, James Kermode,
# H0 X     Ivan Solt, Wojciech Szlachta, Csilla Varnai, Steven Winfield.
# H0 X
# H0 X   Copyright 2006-2010.
# H0 X
# H0 X   These portions of the source code are released under the GNU General
# H0 X   Public License, version 2, http://www.gnu.org/copyleft/gpl.html
# H0 X
# H0 X   If you would like to license the source code under different terms,
# H0 X   please contact Gabor Csanyi, gabor@csanyi.net
# H0 X
# H0 X   Portions of this code were written by Noam Bernstein as part of
# H0 X   his employment for the U.S. Government, and are not subject
# H0 X   to copyright in the USA.
# H0 X
# H0 X
# H0 X   When using this software, please cite the following reference:
# H0 X
# H0 X   http://www.libatoms.org
# H0 X
# H0 X  Additional contributions by
# H0 X    Alessio Comisso, Chiara Gattinoni, and Gianpietro Moras
# H0 X
# H0 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

ifneq (${QUIP_ARCH},)
	export BUILDDIR=build.${QUIP_ARCH}
	export QUIP_ARCH
	include ${BUILDDIR}/Makefile.inc
	include Makefile.rules
	include Makefile.config
	include Makefiles/Makefile.${QUIP_ARCH}
else
	BUILDDIR=crap
endif


ifeq (${HAVE_GP},1)
MODULES = libAtoms gp QUIP_Core QUIP_Utils GAProgs QUIP_Programs # Tests
else
MODULES = libAtoms QUIP_Core QUIP_Utils QUIP_Programs # Tests
endif
FOX = FoX-4.0.3
EXTRA_CLEAN_DIRS = Tools/quippy

default: ${MODULES}

EXTRA_ALL_DIRS = Tools
all: default
	@for f in ${MODULES} ${EXTRA_ALL_DIRS}; do ${MAKE} $$f/all; done

.PHONY: arch ${MODULES} doc

arch: 
ifeq (${QUIP_ARCH},)
	@echo
	@echo "You need to define the architecture using the QUIP_ARCH variable"
	@echo
	@exit 1
endif

${FOX}: ${FOX}/objs.${QUIP_ARCH}/lib/libFoX_common.a
${FOX}/objs.${QUIP_ARCH}/lib/libFoX_common.a:
	make -C ${FOX} -I${PWD} -I${PWD}/Makefiles -I${PWD}/${BUILDDIR} -f Makefile.QUIP 


${MODULES}: ${BUILDDIR}
	ln -sf ${PWD}/$@/Makefile ${BUILDDIR}/Makefile
	${MAKE} -C ${BUILDDIR} VPATH=${PWD}/$@ -I${PWD} -I${PWD}/Makefiles
	rm ${BUILDDIR}/Makefile

ifeq (${HAVE_GP},1)
gp: libAtoms
QUIP_Core: libAtoms gp ${FOX}
GAProgs: libAtoms gp ${FOX} QUIP_Core QUIP_Utils
else
QUIP_Core: libAtoms ${FOX}
endif
QUIP_Util: libAtoms ${FOX} QUIP_Core
QUIP_Programs: libAtoms ${FOX} QUIP_Core QUIP_Utils 
Tests: libAtoms ${FOX} QUIP_Core QUIP_Utils

ifeq (${HAVE_GP},1)
GAProgs/%: libAtoms gp ${FOX} QUIP_Core QUIP_Utils
	ln -sf ${PWD}/GAProgs/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/GAProgs -I${PWD} -I${PWD}/Makefiles $${targ#GAProgs/}
	rm ${BUILDDIR}/Makefile
endif

QUIP_Programs/Examples/%: libAtoms ${FOX} QUIP_Core QUIP_Utils
	ln -sf ${PWD}/QUIP_Programs/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/QUIP_Programs/Examples -I${PWD} -I${PWD}/Makefiles $${targ#QUIP_Programs/Examples/}
	rm ${BUILDDIR}/Makefile

QUIP_Programs/%: libAtoms ${FOX} QUIP_Core QUIP_Utils
	ln -sf ${PWD}/QUIP_Programs/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/QUIP_Programs -I${PWD} -I${PWD}/Makefiles $${targ#QUIP_Programs/}
	rm ${BUILDDIR}/Makefile

QUIP_Core/%: libAtoms ${FOX} QUIP_Core QUIP_Utils
	ln -sf ${PWD}/QUIP_Core/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/QUIP_Core -I${PWD} -I${PWD}/Makefiles $${targ#QUIP_Core/}
	rm ${BUILDDIR}/Makefile

libAtoms/%: libAtoms 
	ln -sf ${PWD}/libAtoms/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/libAtoms -I${PWD} -I${PWD}/Makefiles $${targ#libAtoms/}
	rm ${BUILDDIR}/Makefile

Tools/%: libAtoms ${FOX} QUIP_Core QUIP_Utils
	ln -sf ${PWD}/Tools/Makefile ${BUILDDIR}/Makefile
	targ=$@ ; ${MAKE} -C ${BUILDDIR} VPATH=${PWD}/Tools -I${PWD} -I${PWD}/Makefiles $${targ#Tools/}
	rm ${BUILDDIR}/Makefile


${BUILDDIR}: arch
	@if [ ! -d build.${QUIP_ARCH} ] ; then mkdir build.${QUIP_ARCH} ; fi


clean:
	for mods in  ${MODULES} ; do \
	  ln -sf ${PWD}/$$mods/Makefile ${BUILDDIR}/Makefile ; \
	  ${MAKE} -C ${BUILDDIR} -I${PWD} -I${PWD}/Makefiles clean ; \
	done ; \

deepclean: clean
	for dir in ${EXTRA_CLEAN_DIRS}; do \
	  cd $$dir; make clean; \
	done

install:
	@if [ "x${QUIP_INSTDIR}" == "x" ]; then \
	  echo "make install needs QUIP_INSTDIR defined"; \
	  exit 1; \
	fi; \
	if [ ! -d ${QUIP_INSTDIR} ]; then \
	  echo "make install QUIP_INSTDIR '${QUIP_INSTDIR}' doesn't exist or isn't a directory"; \
	  exit 1; \
	fi
	${MAKE} install-build.QUIP_ARCH install-Tools install-structures

install-build.QUIP_ARCH:
	@echo "installing from build.${QUIP_ARCH}"; \
	for f in `/bin/ls build.${QUIP_ARCH} | egrep -v '\.o|\.a|\.mod|Makefile*'`; do \
	  if [ -x build.${QUIP_ARCH}/$$f ]; then \
	    echo "copying f $$f to ${QUIP_INSTDIR}"; \
	    cp build.${QUIP_ARCH}/$$f ${QUIP_INSTDIR}; \
	  fi; \
	done

install-Tools:
	@echo "installing from Tools"; \
	for f in `/bin/ls Tools | egrep -v '\.f95|Makefile*'`; do \
	  if [ -f Tools/$$f ] && [ -x Tools/$$f ]; then \
	    echo "copying f $$f to ${QUIP_INSTDIR}"; \
	    cp Tools/$$f ${QUIP_INSTDIR}; \
	  fi; \
	done

install-structures:
	@if [ "x${QUIP_STRUCTS_DIR}" == "x" ]; then \
	  if [ "x${QUIP_DIR}" == "x" ]; then \
	    if [ -d ${HOME}/share/quip_structures ]; then \
	      echo "QUIP_STRUCTURS_DIR, QUIP_DIR not defined, copying structures into HOME/share/quip_structures"; \
	      cp structures/*xyz ${HOME}/share/quip_structures; \
	    else \
	      echo "No QUIP_STRUCTS_DIR or QUIP_DIR defined, and HOME/share/quip_structures is not a directory"; \
	    fi; \
	  else \
	    if [ -d ${QUIP_DIR}/structures ]; then \
	      echo "QUIP_STRUCTURS_DIR not defined, copying structures into QUIP_DIR/structures"; \
	      cp structures/*xyz ${QUIP_DIR}/structures; \
	    else \
	      echo "QUIP_DIR defined as ${QUIP_DIR}, but ${QUIP_DIR}/structures is not a directory"; \
	    fi; \
	  fi; \
	else \
	  if [ -d ${QUIP_STRUCTS_DIR}/structures ]; then \
	    echo "copying structures into QUIP_STRUCTS_DIR"; \
	    cp structures/*xyz ${QUIP_STRUCTS_DIR}/structures; \
	  else \
	    echo "QUIP_STRUCTS_DIR defined as ${QUIP_STRUCTS_DIR}, but it is not a directory"; \
	  fi; \
	fi

doc: quip-reference-manual.pdf

quip-reference-manual.pdf:
	./Tools/mkdoc

atomeye:
	if [[ ! -d Tools/AtomEye ]]; then svn co svn+ssh://cvs.tcm.phy.cam.ac.uk/home/jrk33/repo/trunk/AtomEye Tools/AtomEye; fi
	make -C Tools/AtomEye QUIP_ROOT=${PWD}

quippy:
	make -C Tools/quippy install QUIP_ROOT=${PWD}

test:
	${MAKE} -C Tests -I${PWD} -I${PWD}/Makefiles -I${PWD}/${BUILDDIR}
