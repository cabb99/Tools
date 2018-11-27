#!/usr/bin/python

#Mathematica to python

#Parse text
text=""
t = input("Insert mathematica text here: (end with new line)\n")
while t!="":
    text+=t
    t = input()


#Replace new line with space
text=text.replace("\n"," ")
#Merge extra spaces
while "  " in text:
    text=text.replace("  "," ")
#Replace ", " with new line
text=text.replace(", ","\n")
#Other replacements
text=text.replace(" -> ","=")
text=text.replace("( ","(")
text=text.replace(" )",")")
text=text.replace(" + ","+")
text=text.replace(" - ","-")
text=text.replace(" ","*")
text=text.replace("^","**")
#Output
print ("Python equations\n")
print (text+"\n")
