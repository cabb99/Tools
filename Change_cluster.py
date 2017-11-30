#!/usr/bin/env python
import argparse,os,fileinput
cluster_configuration={
#davinci
('davinci','commons'):
{'time':8*60*60,
 'account':'commons'},
('davinci','ctbp-common'):
{'time':24*60*60,
 'account':'ctbp-common'},
('davinci','ctbp-wolynes'):
{'time':6*24*60*60,
 'account':'ctbp-wolynes'},
('davinci','interactive'):
{'time':30*60,
 'account':'commons'},
#nots
('nots','commons'):
{'time':15*24*60*60,
 'account':'ctbp-common'},
('nots','interactive'):
{'time':30*60,
 'account':'commons'},
#po
('po','commons'):
{'time':3*24*60*60,
 'account':'commons'},
#bioU
('biou','commons'):
{'time':24*60*60,
 'account':'commons'},
('biou','interactive'):
{'time':30*60,
 'account':'commons'}
} 

clusters=list(set([cluster for cluster,partition in cluster_configuration.keys()]))
partitions=list(set([partition for cluster,partition in cluster_configuration.keys()]))
clusters.sort()

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
parser.add_argument('--export',default='All',
                    help='Exports the environment variables to the cluster')
#Other optional arguments
parser.add_argument('--job-name',default=None,type=str,
                    help='The name of the job, "WD" will give it the name of the folder it belongs')
parser.add_argument('--time',default=None,type=str,
                    help='The maximum amount of time in slurm format that the job will run, if not specified will be automatically calculated')
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

args=parser.parse_args()
command_args={arg.replace('_','-'):vars(args)[arg] for arg in dir(args) if (arg[0] <> '_' and vars(args)[arg]<>None and vars(args)[arg]<>False and arg<>'scripts')}
try:
    default_args=cluster_configuration[(args.cluster,args.partition)]
except KeyError:
    print "The cluster/partition combination %s/%s is not defined on this program"%(args.cluster,args.partition)
    print "Only the following combinations are available:\n%s"%('\n'.join(['%s/%s'%(a,b) for a,b in cluster_configuration.keys()]))
    exit(2)
for script in args.scripts:
    
    #Try to read current configuration
    script_args={}
    print "Old Configuration:"
    with open(script) as S:
        for line in S:
            if len(line)>10 and line[:7]=='#SBATCH' and len(line.split('--'))==2:
                var,val=line.split('--')[1].split('=')
                print line[:-1]
                script_args.update({var:val.split('\n')[0]})
    #Replace
    #Time management
    if 'time' in script_args or 'time' in command_args:
        if 'time' in script_args:
            time=stime(script_args['time'])
            if 'cluster' in script_args and 'partition' in script_args and\
            (script_args['cluster'],script_args['partition']) in cluster_configuration and\
            time==cluster_configuration[(script_args['cluster'],script_args['partition'])]['time']:
                time=default_args['time']
                #Will conserve the time only if it is shown that is not the max 
                #time possible and if the time is less than that of the new cluster.
            else:
                time=default_args['time']
        if 'time' in command_args:
            time=stime(command_args['time'])
        if time>default_args['time']:
            time=default_args['time']
    else:
        time=default_args['time']
    ##Replace and add with values from old file
    new_args=script_args.copy()
    ##Replace and add from values from command line
    new_args.update(default_args)
    new_args.update(command_args)
    new_args.update({'time':sformat(time)})
    #Generate a new name:
    if 'job-name' in new_args and new_args['job-name']=='WD':
        new_args['job-name']=os.path.abspath(script).split('/')[-2]
    
    #Test and confirm new configuration
    keys=new_args.keys()
    keys.sort()
    print "New Configuration"
    new_configuration=''
    #print keys    
    for arg in keys:
	if arg<>'cluster':
        	new_configuration+='#SBATCH --%s=%s\n'%(arg,new_args[arg])
    print new_configuration
    #Replace with new configuration
    import fileinput
    for i,line in enumerate(fileinput.input(script, inplace=True)):
        if i==1:
            print new_configuration.rstrip('\n')
        if len(line)>10 and line[:7]=='#SBATCH' and len(line.split('--'))==2:
            continue
        print line.rstrip('\n')
        
    '''
    from shutil import move
    from os import remove
    #Move old file to backup
    move(script, script+'.backup')
    #Create temp file
    with open(script,'w') as new_file, open(script+'.backup') as old_file:
        for i,line in enumerate(old_file):
            if i==1:
                new_file.write(new_configuration)
            if len(line)>10 and line[:7]=='#SBATCH' and len(line.split('--'))==2:
                continue
            new_file.write(line)
    #Remove original file
    #remove(script+'.backup')
    '''
        
    
    
