#!/usr/bin/env python2.7
import argparse
import subprocess
import glob
import os

if __name__=='__main__':
    
    parser=argparse.ArgumentParser(description='Executes a command multiple times, by entering in to the directory')
    parser.add_argument('Folders',help='The folder where the commands will be executed')
    parser.add_argument('-c','--command',help='The command you want to execute')
    parser.add_argument('-i','--condition', nargs=2, metavar='Cond',help='File_to_read line_to_find If it finds a line in the file, it will be executed')
    args=parser.parse_args()
    
    #Remember original directory
    initial_dir=os.getcwd()
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
        if Execute:        
            subprocess.call(args.command, shell=True)
        #Back to the original directory
        os.chdir(initial_dir)
