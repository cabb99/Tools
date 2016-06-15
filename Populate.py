#!/usr/bin/env python2.7
import shutil
import sys
import random
import numpy

def main(source,Changes,ask=True):
    """Inputs:
           source: A source folder, the folder that you want to use as a template
           Changes: A list of changes that you want to make to the folder. Each change
           should contain 4 parameters.
                filemod: The file you want to use as a template
                linemod: The line you want to modify in the file
                lvalues: The list of values wich you want to modify the original line
                alias: A short name used to name the new folders"""

    #Evaluate if the changes are as expected
    Folders=[source]
    zchanges=[[]]
    nfolders=1
    
    for filemod,linemod,lvalues,alias in Changes:
        #find name of the changing variable:
        found=False
        lvalues=[str(v) for v in lvalues]
        for l in range(len(lvalues[0])):
            for v in lvalues[1:]:
                if lvalues[0][:l]<>v[:l]:
                    found=True
                if found:
                    break  
            if found:
                break
            max_l=l
        common_pattern=lvalues[0][:max_l]
        new_folders=[]
        new_changes=[]
        for v in lvalues:
            for F in Folders:
                #print '%s_%s'%(F,v.replace(common_pattern,alias))
                if len(common_pattern)>0:
                    new_folders+=['%s_%s'%(F,v.replace(common_pattern,alias))]
                else:
                    new_folders+=['%s_%s%s'%(F,alias,v)]
            for c in zchanges:
                new_changes+=[c+[(filemod,linemod,v)]]
                #print new_folders
        nfolders*=len(lvalues)
        Folders=new_folders
        zchanges=new_changes
    print '\nThe folder %s will be used to create the following new %i folders:'%(source,nfolders)
    for i in range(len(Folders)/3+1):
        print '\t'.join(Folders[i*3:i*3+3])
        
    print '\nThe modifications on each folder will be similar to this one:'
    for filemod,linemod,v in zchanges[0]:
        filename=filemod.split('/')[-1]
        original=open(filemod)
        instances=0
        for line in original:
            if line.find(linemod)>=0:
                instances+=1
        original.close()
        new='%s/%s'%(Folders[0],filename)
        print '%s: %s --> %s: %s (replaced %i time(s))'%(filemod, linemod, new, v, instances) 
    
    if ask:
        proceed=query_yes_no('\nContinue with the creation of folders?')
    else:
        proceed=True
        
    if proceed:
        #Change the parameters       
        for folder,changes in zip(Folders,zchanges):
            shutil.copytree(source,folder)
            filemods=set([filemod for filemod,linemod,v in changes])
            for filemod in filemods:            
                original=open(filemod)
                filename=filemod.split('/')[-1]
                new=open('%s/%s'%(folder,filename),'w+')
                for line in original:
                    for filemod_compare,linemod,v in changes:
                        if filemod_compare==filemod:
                            line=line.replace(linemod,v)
                    new.write(line)
                original.close()
                new.close()
    else:
        print "No changes made"
        exit(0)      



#Yes or No recipe
def query_yes_no(question, default=True):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True, "y":True,  "Y":True,  "Yes":True, "YES":True,
             "no":False, "n":False, "N":False, "No":False, "NO":False}
    if default == None:
        prompt = " [y/n] "
    elif default == True:
        prompt = " [Y/n] "
    elif default == False:
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Make copies of one folder changing some parameters in specified files')
    parser.add_argument('Source',help='The folder you want to copy',type=str)
    parser.add_argument('-c','--change',nargs=4,help='The changes you want to make on the files. The change should be defined as: File_to_change line_to_change final_values Alias',action='append')
    parser.add_argument('-y',help='Continue without asking',action='store_true')
    args=parser.parse_args()
    source=args.Source
    if source[-1]=='/':
        source=source[:-1]
    Changes=[]
    for change in args.change:
        filemod=change[0]
        linemod=change[1]
        values=change[2]
        alias=change[3]
        
        try:
            F=open(filemod)
            instances=0
            for line in F:
                if line.find(linemod)>=0:
                    instances+=1
            if instances==0:
                #The line to change should exist in the document
                print 'The line to change: %s does not exist within the file to change %s'%(linemod,filemod)
                exit(2)
        except IOError:
            #The file mod should be a file in the folder
            print 'The file %s does not exist'%filemod
            exit(2)
        
        #The values should be a python expresion
        try:
            lvalues=eval(values)
            if type(lvalues)<>list:
                if type(lvalues)==tuple:
                    lvalues=list(values)
                else:
                    print 'The indicated values are not a list: %s'%values
                    exit(2)
        except SyntaxError:
            print 'The indicated values are not a valid python expression: %s'%values
            exit(2)
        Changes+=[[filemod,linemod,lvalues,alias]]
    #Execute main function
    main(source,Changes,not args.y)
    
    

