# -*- coding: utf-8 -*-
import time
import os
import shutil

from scapy.all import *
from scapy.utils import PcapWriter

filename = ""
filepath = "/home/kelvin/Desktop/PythonProj/Proj1/pcaps/"
toUploadPath = "/home/kelvin/Desktop/PythonProj/Proj1/pcaps_upload/"

def _change_filename(filepath,filename):
    ISOTIMEFORMAT = "%Y-%m-%d-%H-%M-%S"
    filename = str(time.strftime(ISOTIMEFORMAT))+".pcap"
    #with open(filepath+filename) as f:
    #    pass
    return filename


def _is_need_change(filepath,filename):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    if len(os.listdir(filepath)) == 0:
        return True
    if not os.path.isfile(filepath+filename):
        return True
    if os.path.exists(filepath+filename):
        size = os.path.getsize(filepath+filename)
        if int(size) > 1048576:
            return True
        else:
            return False

def save(p):
    global filepath
    global filename
    if _is_need_change(filepath,filename):
        filename = _change_filename(filepath,filename)
        print "modifying filename: {}".format(filename)
    writer = PcapWriter(filepath+filename,append=True)
    writer.write(p)
    writer.flush()
    writer.close()
    if _is_need_change(filepath,filename):
        shutil.move(filepath+filename,toUploadPath+filename)

def collect_pcaps():
    sniff(prn=lambda i:save(i))


if __name__=='__main__':
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    if not os.path.exists(toUploadPath):
        os.makedirs(toUploadPath)

    collect_pcaps()
