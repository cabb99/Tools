#!/usr/bin/python
#SBATCH --export=ALL
#SBATCH --job-name=Lysozime
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --account=ctbp-common
#SBATCH --partition=ctbp-common
#SBATCH --time=1-00:00:00

#Modules
import time,subprocess, os, glob

#Parameters
import os
PDB_name=os.getcwd().split('/')[-1][:os.getcwd().split('/')[-1].find('_All')]
lmp_serial="./lmp_serial_552_mod_frust_elec"
input_file="%s.in"%PDB_name
seq_file="%s.seq"%PDB_name

#Functions
def write_dump(read_file,write_file,initial_ts,final_ts):
    ts_line=False
    write=False
    a=open(read_file)
    o=open(write_file,'w+')
    for line in a:
        if ts_line:
            ts_line=False
            ts=int(line)
            if ts>=initial_ts and ts<final_ts:
                write=True
                o.write('ITEM: TIMESTEP\n%s'%line)
                continue
        if line=='ITEM: TIMESTEP\n':
            ts_line=True
            write=False
            continue
        if write:
            o.write(line)
    a.close()
    o.close()

def write_energy(read_file,write_file,initial_ts,final_ts):
    a=open(read_file)
    o=open(write_file,'w+')
    for line in a:
        s=line.split()
        if len(s)>1 and s[0]<>'#' and s[0]<>'Step':
            if int(s[0])>=initial_ts and int(s[0])<final_ts:
                o.write(line)
    a.close()
    o.close()


#Read the input file to find some variables
handle=open(input_file)
for line in handle:
    c=line.split()
    if len(c)>0 and len(c[0])>0 and c[0][0]<>'#': #Filter only valid commands
        comm=c[0]
        if comm=='run':
            run_iter=c[1]
        if comm=='restart':
            restart_freq=c[1]
            restart_name=c[2]
        if comm=='reset_timestep':
            first_ts=int(c[1])
        if comm=='dump':
            dump_freq=c[4]
            dump_name=c[5]
handle.close()

### This script can be used to run long lammps simulations and 
### then does some post-processing

#Print the date it starts and ends
print "The job starts at", time.ctime()
import atexit
def exit_handler():
    print "The job ends at", time.ctime()
atexit.register(exit_handler)

#print the node it works on
import socket

print "The job ran on: ",socket.gethostname()
subprocess.call("echo $SLURM_JOB_NODELIST",shell=True)

#Check if a restart file exist
restart_files=[(os.stat(f).st_mtime,f) for f in glob.glob('%s.*'%restart_name)]
restart_files.sort(reverse=True)
restart_files=[b for a,b in restart_files]
restart_sizes=[os.stat(f).st_size for f in restart_files]

if len(restart_files)<4: #If there are less than 4 restart files, run lammps normally
    print "Starting the simulation"
    subprocess.call([lmp_serial],stdin=open(input_file))
else:
    #All restart_files should have the same size
    for restart,size in zip(restart_files,restart_sizes):
        if size==restart_sizes[0]:
            break
    restart_iter=int(restart.split('.')[-1])
    if restart_iter<=int(run_iter)-int(restart_freq):
        print "Restarting the simulation"
        ########################
        #Restart the simulation#
        ########################
        r=len(glob.glob('*_dump'))+1
        print "Restart number: ",r
        print "Restart iteration: ",restart_iter
        #Locate first iteration of last restart:
        if r>1:
            handle=open(input_file+'.r%02i'%(r-1))
            for line in handle:
                c=line.split()
                if len(c)>0 and len(c[0])>0 and c[0][0]<>'#': #Filter only valid commands
                    comm=c[0]
                    if comm=='reset_timestep':
                        first_ts=int(c[1])
            handle.close()
        #Copy the trajectory
        write_dump(dump_name,"%02i_dump"%r,first_ts,restart_iter)
        subprocess.call("mv %s %02i_dump.backup"%(dump_name,r),shell=True)
        #Copy the energies
        write_energy('energy',"%02i_energy1"%r,first_ts,restart_iter)
        write_energy('energy.log',"%02i_energy2"%r,first_ts,restart_iter+1)
        subprocess.call("mv %s %02i_energy1.backup"%('energy',r),shell=True)
        subprocess.call("mv %s %02i_energy2.backup"%('energy.log',r),shell=True)
        #Copy the log
        subprocess.call("mv %s %02i_log"%('log.lammps',r),shell=True)
        #Create a restart script
        input_restart=input_file+'.r%02i'%r
        handle=open(input_file)
        rhandle=open(input_restart,'w+')
        for line in handle:
            c=line.split()
            if len(c)>0 and len(c[0])>0 and c[0][0]<>'#': #Filter only valid commands
                comm=c[0]
                if comm=='run':
                    rhandle.write('run %i\n'%(int(run_iter)-int(restart_iter)))
                elif comm=='read_data':
                    rhandle.write('read_restart %s\n'%restart)  
                elif comm=='reset_timestep':
                    rhandle.write('reset_timestep %i\n'%int(restart_iter))  
                else:
                    rhandle.write(' '.join(c)+'\n')
        handle.close()
        rhandle.close()
        #Run the restart script
        subprocess.call([lmp_serial],stdin=open(input_restart))

###################
# Post-processing #
###################
import fileinput
#Join the trayectories
Files=fileinput.input(sorted(glob.glob('*[1234567890]_dump'), key=lambda l: int(l.split('_')[0]))+[dump_name])
with open('All_dump', 'w') as fout:
    for line in Files:
        fout.write(line)

#Join the energies
Files=fileinput.input(sorted(glob.glob('*[1234567890]_energy1'), key=lambda l: int(l.split('_')[0]))+['energy'])
with open('All_energy1', 'w') as fout:
    for line in Files:
        fout.write(line)
        
Files=fileinput.input(sorted(glob.glob('*[1234567890]_energy2'), key=lambda l: int(l.split('_')[0]))+['energy.log'])
with open('All_energy2', 'w') as fout:
    for line in Files:
        fout.write(line)

#Join the logs
Files=fileinput.input(sorted(glob.glob('*[1234567890]_log'), key=lambda l: int(l.split('_')[0]))+['log.lammps'])
with open('All_log', 'w') as fout:
    for line in Files:
        fout.write(line)

#Calculate the q_value
subprocess.call("python ~/opt/script/CalcQValue_multi.py $PDB All_dump All_qo 1",shell=True) ##Modify the path to your own path

subprocess.call("cat fix_backbone_coeff.data >> All_log",shell=True)

subprocess.call("BuildAllAtomsFromLammps.py All_dump VMD_tray -seq %s"%seq_file,shell=True)

#Print the date it finishes
print "The job ends at", time.ctime()


