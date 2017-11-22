# -*- coding: utf-8 -*-
import socket
import sys
import threading
import time
import collections
import re
import os

def checkFile():
    list = os.listdir('.')
    for iterm in list:
        if iterm == '1.txt':
            os.remove(iterm)
            print 'remove'
        else:
            pass

def transfile(sock, addr, dic):
    #use loop to recv data from client
    try:
        while True:
            data = sock.recv(1024)
            #check the size of dic
            if len(dic) >= 2:
                sock.send("please connect another time")
                sock.close()
                break
            else:
                #split the data from client
                splitData = re.split(r'[\s\,]+',data)
                #append the key and value to the dic
                dic[splitData[0]] = splitData[1]
                print dic
                while True:
                    #check if the client is the first client in the dic
                    if splitData[0] == dic.keys()[0]:
                        sock.send("Now you can trans file now")
                        while True:
                            #recv the file from client
                            data = sock.recv(1024)
                            #finish the recv, exit
                            if not data :
                                print 'reach the end of file'
                                print "Client %s exit." % addr[0]
                                dic.pop(dic.keys()[0])
                                return
                            #begin to recv, create the file,and check if the file exist
                            elif data == 'begin to send':
                                print 'create file'
                                checkFile()
                                with open('./1.txt', 'wb') as f:
                                    pass
                            #trans the data in file
                            else:
                                with open('./1.txt', 'ab') as f:
                                    f.write(data)

        sock.close()
    except socket.errno, e:
        print "Socket error: %s" % str(e)
    except Exception as e:
        print "Other exception: %s" % str(e)
    finally:
        sock.close()
    pass



def test_server(Port, dic):
    #create the Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #set up the adress reuse
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #bind the adress and Port
    srv_addr = ("",port)
    sock.bind(srv_addr)
    #listen the Socket
    sock.listen(5)
    #loop to connect
    while True:
        conn, addr = sock.accept()
        t = threading.Thread(target = transfile, args = (conn, addr, dic))
        t.start()
    pass

if __name__ == '__main__':
    port = 8900
    dic = collections.OrderedDict()
    test_server(port,dic)
