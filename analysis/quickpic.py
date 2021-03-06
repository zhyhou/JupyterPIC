import os
import re
import shutil
import subprocess
import IPython.display
import h5py
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact
from h5_utilities import *
from analysis import *
from scipy.optimize import fsolve

def execute(cmd):

    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def runqpic(rundir='',inputfile='qpinput.json'):

    if rundir == '' or not bool(re.match("^[A-Za-z0-9_-]*$", rundir)):
        print('''
        Error for quickpic.runqpic:
        rundir must be specified for the name of a runtime directory
        and rundir must be a string containing only numbers, letters, dashes, or underscores
        ''')
        return

    if os.path.isfile('qpic.e'):
        localexec = 'qpic.e'
    else:
        localexec = False
    sysexec = '/usr/local/quickpic/qpic.e'

    print(rundir)

    if(not os.path.isdir(rundir)):
        os.mkdir(rundir)
    else:
        shutil.rmtree(rundir)
        os.mkdir(rundir)

    shutil.copyfile(inputfile,rundir+'/qpinput.json')
    
    os.chdir(rundir)

    # run quickpic executable
    print('running qpic.e ...')
    waittick = 0
    if localexec:
        localexec = '../'+localexec
        for path in execute([localexec]):
            waittick += 1
            if(waittick == 100):
                IPython.display.clear_output(wait=True)
                waittick = 0
    else:
        for path in execute([sysexec]):
            waittick += 1
            if(waittick == 100):
                IPython.display.clear_output(wait=True)
                waittick = 0
    IPython.display.clear_output(wait=True)
    print('quickpic completed normally')

    os.chdir('../')

    return

def field(rundir='',dataset='e1',time=0,space=-1,
    xlim=[-1,-1],ylim=[-1,-1],zlim=[-1,-1],
    plotdata=[], **kwargs):

    if(space != -1):
        plot_or = 1
        PATH = gen_path(rundir, plot_or)
        hdf5_data = read_hdf(PATH)
        plt.figure(figsize=(8,5))
        #plotme(hdf5_data.data[:,space], **kwargs)
        plotme(hdf5_data,hdf5_data.data[space,:])
        plt.title('temporal evolution of e' + str(plot_or) + ' at cell ' + str(space))
        plt.xlabel('t')
        plt.show()
        return


    workdir = os.getcwd()
    workdir = os.path.join(workdir, rundir)

    odir = os.path.join(workdir, 'MS', 'FLD', dataset)
    files = sorted(os.listdir(odir))

    i = 0
    for j in range(len(files)):
        fhere = h5py.File(os.path.join(odir,files[j]), 'r')
        if(fhere.attrs['TIME'] >= time):
            i = j
            break

    fhere = h5py.File(os.path.join(odir,files[i]), 'r')

    plt.figure(figsize=(6, 3.2))
    plt.title(dataset+' at t = '+str(fhere.attrs['TIME']))
    plt.xlabel('$x_1 [c/\omega_p]$')
    plt.ylabel(dataset)

    xaxismin = fhere['AXIS']['AXIS1'][0]
    xaxismax = fhere['AXIS']['AXIS1'][1]

    nx = len(fhere[dataset][:])
    dx = (xaxismax-xaxismin)/nx

    plt.plot(np.arange(0,xaxismax,dx),fhere[dataset][:])

    if(xlim != [-1,-1]):
        plt.xlim(xlim)
    if(ylim != [-1,-1]):
        plt.ylim(ylim)
    if(zlim != [-1,-1]):
        plt.clim(zlim)

    plt.show()
