#!/usr/bin/env python2.7
import argparse
import subprocess
import glob
import os

if __name__=='__main__':
    
    parser=argparse.ArgumentParser(description='Executes a command multiple times, by entering in to the directory')
    parser.add_argument('Folders',help='The folder where the commands will be executed')
    parser.add_argument('-c','--command',help='The command you want to execute')
    args=parser.parse_args()
    
    #Remember original directory
    initial_dir=os.getcwd()
    for folder in glob.glob(args.Folders):
        #Enter the directory
        os.chdir(folder)
        #Execute the command
        subprocess.call(args.command, shell=True)
        #Back to the original directory
        os.chdir(initial_dir)
