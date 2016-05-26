#!/usr/bin/env python

SBATCH_options={
#davinci
('davinci','commons'):
{'max_time':8*60*60,
 'account':'commons'},
('davinci','ctbp-common'):
{'max_time':24*60*60,
 'account':'ctbp-common'},
('davinci','ctbp-wolynes'):
{'max_time':6*60*60,
 'account':'ctbp-wolynes'},
('davinci','interactive'):
{'max_time':30*60,
 'account':'commons'},
#nots
('nots','commons'):
{'max_time':15*60*60,
 'account':'ctbp-common'},
('nots','interactive'):
{'max_time':30*60,
 'account':'commons'},
#po
('po','commons'):
{'max_time':3*24*60*60,
 'account':'commons'},
#bioU
('biou','commons'):
{'max_time':24*60*60,
 'account':'commons'},
('biou','interactive'):
{'max_time':30*60,
 'account':'commons'}
} 

clusters=list(set([cluster for cluster,partition in SBATCH_options.keys()]))
partitions=list(set([partition for cluster,partition in SBATCH_options.keys()]))
clusters.sort()

import argparse
parser=argparse.ArgumentParser(description='Changes the slurm commands from a\
script file from one cluster configuration to another cluster configuration')
#Needed arguments
parser.add_argument('scripts',action='store',nargs='*',)
parser.add_argument('-c','--cluster',choices=clusters,required=True,
                    help='Cluster where the script(s) will run')
parser.add_argument('-p','--partition',default='commons',choices=partitions,
                    help='Partition where the script(s) will run')
parser.add_argument('--account',default=None,help=argparse.SUPPRESS)
#Optional multiprocess arguments
parser.add_argument('--nodes',default=None,type=int,
                    help='Number of nodes that will be used')
parser.add_argument('--ntasks',default=None,type=int,
                    help='Number of tasks that will be used (may be on separate nodes), used for MPI jobs')
parser.add_argument('--cpus-per-task',type=int,
                    help='Number of processes per task')
parser.add_argument('--ntasks-per-node',type=int,
                    help='Number of tasks per node')
parser.add_argument('--mem-per-cpu',type=str,
                    help='Maximum amount of physical memory used per process, ex:1024M')
parser.add_argument('--exclusive',action='store_true',
                    help='No other job will be able to run in the same node')
parser.add_argument('--export',default='None',
                    help='Exports the environment variables to the cluster')
#Other optional arguments
parser.add_argument('--job-name',default=None,type=str,
                    help='The name of the job, "WD" will give it the name of the folder it belongs')
parser.add_argument('--time',default=None,type=int,
                    help='The maximum amount of time that the job will run, if not specified will be automatically calculated')
parser.add_argument('--output',type=str,
                    help='The name of the file where the output will be writen')
parser.add_argument('--error',type=str,
                    help='The name of the file where the error will be writen')
parser.add_argument('--mail-user',type=str,
                    help='The e-mail where notifications of the job status will be sent')
parser.add_argument('--mail-type',choices=['ALL','BEGIN','END','FAIL','REQUEUE'],
                    help='Will notify when job reaches BEGIN, END, FAIL or REQUEUE.')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# Time manipulation
def stime(t):
    '''Convert slurm time format to seconds'''
    s=0    
    D=t.split('-')
    T=[int(i) for i in D[-1].split(':')]
    if len(D)==2:
        s+=int(D[0])*24*60*60
        if len(T)==1:#days-hours
            s+=T[0]*60*60
        elif len(T)==2:#days-hours:minutes
            s+=T[0]*60*60+T[1]*60
        elif len(T)==3:#days-hours:minutes:seconds
            s+=T[0]*60*60+T[1]*60+T[2]
    elif len(D)==1:
        if len(T)==1: #minutes
            s+=T[0]*60
        elif len(T)==2: #minutes:seconds
            s+=T[0]*60+T[1]
        elif len(T)==3: #hours:minutes:seconds
            s+=T[0]*60*60+T[1]*60+T[2]
    return s

def sformat(t):
    '''Convert from seconds to slurm time format'''
    t=int(t)
    s=t%60
    t-=s
    m=t%(60*60)/60
    t-=m*60
    h=t%(24*60*60)/60/60
    t-=h*60*60
    d=t/24/60/60
    if d>0:
        return '%i-%02i:%02i:%02i'%(d,h,m,s)
    elif h>0:
        return '%02i:%02i:%02i'%(h,m,s)
    else:
        return '%02i:%02i'%(m,s)

#os.path.abspath

print dir(parser)

args=parser.parse_args()
[arg for arg in dir(args) if (arg[0] <> '_' and vars(args)[arg]<>None and vars(args)[arg]<>False and arg<>'scripts')]
for script in args.scripts:
    print script
    #Try to read current configuration

    #Replace
    ##First take into account minimal values
    
    ##Replace and add with values from old file
    
    ##Replace and add from values from command line
    
    #Write new configuration
