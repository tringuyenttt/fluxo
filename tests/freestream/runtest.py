#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import sys
import math
import shutil
import tempfile
import time
import argparse
import subprocess
import re

########################################################################################################
# use ../helpers.py
sys.path.append('../')

from helpers import copy2temporary, execute, modify_prm, read_prm

########################################################################################################

# MAIN PROGRAM

########################################################################################################
parser = argparse.ArgumentParser(description='Tool to run fluxo tests')
parser.add_argument('-p','--procs', type=int, default=1, help='number of processors used for the run')
parser.add_argument('-ntail', type=int, default=10, help='number of last line output of screenlog')
parser.add_argument('exe', help='path to executable')
parser.add_argument('prm',   help='path to parameter file')

args = parser.parse_args()

if not os.path.exists(args.prm) :
    print "parameter-file '%s' not found" % args.prm 
    sys.exit(1)


# copy executable and parameter file to a temporary directory
tmp_dir = tempfile.mkdtemp()
args.exe = copy2temporary(tmp_dir, args.exe)
args.prm = copy2temporary(tmp_dir, args.prm)
args.ntail = 10
args.procs = 1


# this generates 3 meshes
Degree = ['3'] #  ['5','6']
Meshes = glob.glob('../meshes/*_mesh.h5') 
projectname = read_prm(args.prm,'ProjectName')

# loop over meshes
for i in range(0,len(Degree)) :
  for m in range(0,len(Meshes)) :
    print "               "
    print "%03.0i %03.0i === >  %s %s " % (i,m,Degree[i],Meshes[m])
    print "               "
    meshname = re.sub('\_mesh\.h5','',os.path.basename(Meshes[m]))

    projectnameX = projectname+'_Degree_'+Degree[i]+'_Mesh_'+meshname 
    modify_prm(args.prm, {'ProjectName' : projectnameX})
    print "               "
    print "%03.0i === > ProjectName: %s" % (i,projectnameX)
    print "               "
    # modify parameters by replacing string
    #    args.prm = [w.replace('NEX',nElemsX[i] ) for w in args.prm] 
    modify_prm(args.prm, {'N' : Degree[i]})
    modify_prm(args.prm, {'MeshFile' : Meshes[m]})


    # execute fluxo
    start_time = time.time()
    try :
        execute(args.exe, args.prm, projectnameX, log = True, ntail = args.ntail ,\
                mpi_procs = args.procs)
    except :
        shutil.rmtree(tmp_dir)
        exit(1)
    end_time = time.time()


    #print end_time - start_time
    sys.stdout.flush()


 
shutil.rmtree(tmp_dir)
