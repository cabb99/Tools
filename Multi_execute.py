#!/usr/bin/env python2.7
import argparse
import subprocess
import glob
import os
import time

if __name__=='__main__':
    
    parser=argparse.ArgumentParser(description='Executes a command multiple times, by entering in to the directory')
    parser.add_argument('Folders',help='The folder where the commands will be executed')
    parser.add_argument('-c','--command',help='The command you want to execute')
    parser.add_argument('-i','--condition', nargs=2, metavar='Cond',help='File_to_read line_to_find If it finds a line in the file, it will be executed')
    parser.add_argument('-p','--processes',help='Number of parallel processes to be executed', default=1,type=int)
    #parser.add_argument('Folders',help='The folder where the commands will be executed',nargs='*')
    args=parser.parse_args()
    
    #Remember original directory
    initial_dir=os.getcwd()
    Pool=[]
    for folder in glob.glob(args.Folders):
        #Enter the directory
        os.chdir(folder)
        try:        
            #Test condition
            Execute=False        
            with open(max(glob.iglob(args.condition[0]), key=os.path.getctime)) as handle:
                for line in handle:
                    if args.condition[1] in line:
                        Execute=True
        except ValueError:
            Execute=False
        except TypeError:
            Execute=True

        #Execute the command
        if Execute and args.processes==1:   
            subprocess.call(args.command, shell=True)
        elif Execute and args.processes>1:
            if len(Pool)<args.processes:
                Pool+=[subprocess.Popen(args.command, shell=True)]
            else:
                while True:
                    polls=[p.poll() for p in Pool]
                    np=len([p for p in polls if p is None])
                    #print len(polls),np
                    if np<args.processes:
                        Pool+=[subprocess.Popen(args.command, shell=True)]
                        break
                    time.sleep(1E-2)

            
        #Back to the original directory
        os.chdir(initial_dir)
