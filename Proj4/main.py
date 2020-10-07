import sys
import os
import time
import threading
import termios
import tty
import cv2
import pyprind

class CharFrame:
    accii_char = "$@B%*&WM#*oahkbdqwmZO0QLCJUYXzcvunxrjft/\|()l{}[]?-_+~<>i!lI;:,\"^`'. "

    def pixelToChar(self, luminance):
        return self.accii_char[int(luminance/256*len(self.accii_char))]

    def convert(self, img, limitSize = -1, fill = False, wrap = False):
        if limitSize != -1 and (img.shape[0] > limitSize[1] or img.shape[1] > limitSize[0]):
            img = cv2.resize(img, limitSize, interpolation = cv2.INTER_AREA)
            ascii_frame = ''
            blank = ''
            if fill:
                blank += ' ' * (limitSize[0] - img.shape[1])
            if wrap:
                blank += '\n'
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    ascii_frame += self.pixelToChar(img[i, j])
                
                ascii_frame += blank
            
            return ascii_frame


class I2Char(CharFrame):
    result = None
    
    def __init__(self, path, limitSize = -1, fill = False, wrap = False):
        self.genCharImage(path, limitSize, fill, wrap)
    
    def genCharImage(self, path, limitSize = -1, fill = False, wrap = False):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return
        self.result = self.convert(img, limitSize, fill, wrap)
    
    def show(self, stream = 2):
        if self.result is None:
            return
        if stream == 1 and os.isatty(sys.stdout.fileno()):
            self.streamOut = sys.stdout.write
            self.streamFlush = sys.stdout.flush
        elif stream == 2 and os.isatty(sys.stderr.fileno()):
            self.streamOut = sys.stderr.write
            self.streamFlush = sys.stderr.flush
        elif hasattr(stream, 'write'):
            self.streamOut = stream.write
            self.streamFlush = stream.flush
        
        self.streamOut(self.result)
        self.streamFlush()
        self.streamOut('\n')

class V2Char(CharFrame):
    charVideo = []
    timeInterval = 0.033

    def __init__(self, path):
        if path.endswith('txt'):
            self.load(path)
        else:
            self.getCharVideo(path)
    
    def getCharVideo(self, filepath):
        self.charVideo = []
        cap = cv2.VideoCapture(filepath)
        self.timeInterval = round(1 / cap.get(5), 3)
        nf = int(cap.get(7))
        print('Generate char video, please wait...')
        for i in pyprind.prog_bar(range(nf)):
            rawFrame = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
            frame = self.convert(rawFrame, os.get_terminal_size(), fill = True)
            self.charVideo.append(frame)
        cap.release()
    
    def export(self, filepath):
        if not self.charVideo:
            return
        with open(filepath, 'w') as f:
            for frame in self.charVideo:
                f.write(frame + '\n')
    
    def load(self, filepath):
        self.charVideo = []
        for i in open(filepath):
            self.charVideo.append(i[:-1])
    
    def play(self, stream = 1):
        if not self.charVideo:
            return
        if stream == 1 and os.isatty(sys.stdout.fileno()):
            self.streamOut = sys.stdout.write
            self.streamFlush = sys.stdout.flush
        elif stream == 2 and os.isatty(sys.stderr.fileno()):
            self.streamOut = sys.stderr.write
            self.streamFlush = sys.stderr.flush
        elif hasattr(stream, 'write'):
            self.streamOut = stream.write
            self.streamFlush = stream.flush
        
        old_settings = None
        breakflag = None
        fd = sys.stdin.fileno()

        def getChar():
            nonlocal breakflag
            nonlocal old_settings

            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            breakflag = True if ch else False
        
        getchar = threading.Thread(target = getChar)
        getchar.daemon = True
        getchar.start()

        rows = len(self.charVideo[0]) // os.get_terminal_size()[0]
        for frame in self.charVideo:
            if breakflag is True:
                break
            self.streamOut(frame)
            self.streamFlush()
            time.sleep(self.timeInterval)
            self.streamOut('\033[{}A\r'.format(rows-1))
        
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        self.streamOut('\033[{}B\033[K'.format(rows-1))

        for i in range(rows-1):
            self.streamOut('\033[1A')
            self.streamOut('\r\033[K')
        info = 'User interupt!\n' if breakflag else 'Finished!\n'
        self.streamOut(info)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file', help = 'Video file or charvideo file')
    parser.add_argument('-e', '--export', nargs = '?', const = 'charvideo.txt', help = 'Export charvideo file')

    args = parser.parse_args()
    v2char = V2Char(args.file)
    if args.export:
        v2char.export(args.export)
    v2char.play()
