# -*- coding: utf-8 -*-
import socket
import threading
import time
import random

def test_client(Host, Port):
    #create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect server
    srv_addr = (Host,Port)
    sock.connect(srv_addr)

    #use random num as a ip adress
    ipAdress = random.randint(0,99)
    filenum = 1

    #send the ip adress and filenum
    sock.send("%s, %d" % (ipAdress,filenum))
    #recv the data from the server
    data = sock.recv(1024)
    if 'another' in data:
        print "%s" % data
        return
    else:
        #trans the file
        try:
            sock.send('begin to send')
            print 'sending, please wait for a second ...'
            #open the file and send data to server
            with open('./1.txt', 'rb') as f:
                for data in f:
                    sock.send(data)
            print 'sended !'

            sock.close()
        except socket.errno, e:
            print "Socket error: %s" % str(e)
        except Exception as e:
            print "Other exception: %s" % str(e)
        finally:
            sock.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8900
    test_client(host,port)
