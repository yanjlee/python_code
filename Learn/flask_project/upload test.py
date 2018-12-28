# coding=utf-8
import os,sys
import shutil
import struct

file_list = []

def listdir(folder, file_list):
    fileNum = 0
    new_file_list = os.listdir(folder) 
    for line in new_file_list:
        #print line
        filepath = os.path.join(folder,line)
        if os.path.isfile(filepath):
            print(line)
            file_list.append(line)
            fileNum = fileNum + 1
            #if fileNum > 10:
            #   return


#change .jpg.txt to .txt
def ChangeFileName(folder, file_list):
    for file_line in file_list:
        old_file_name = file_line
        new_file_name = file_line.replace(".jpg.txt", ".txt")
        print("new: " + new_file_name)
        print("old: " + old_file_name)
        if new_file_name != old_file_name:
            print("file_name:" + old_file_name)
            print ("new_file_name:" + new_file_name)
            os.rename(os.path.join(folder, file_line), os.path.join(folder, new_file_name))

folder = sys.argv[1]
print(folder)
listdir(folder, file_list)
# ChangeFileName(folder, file_list)