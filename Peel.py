import os
import cv2
from tkinter import *
from tkinter import ttk, filedialog

class Peel:
    '''
    App to turn video files into images.
    '''
    def __init__(self, root):
        '''
        Takes in root and builds app stack.
        '''
        self.root = root
        self.root.title('Peel')
        self.root.resizable(False, False)
        
        # control variables
        self.fps = IntVar()
        self.fileName = StringVar()

        # styling
        self.style = ttk.Style()
        try:
            self.root.tk.call('source', 'Azure/azure/azure.tcl')
            self.style.theme_use('azure')
        except: pass
        
        self.MainFrame()
    
    def MainFrame(self):
        '''
        Manages the main frame.
        '''
        self.configFrame = ttk.Frame(self.root)
        self.processFrame = ttk.Frame(self.root)
        
        # positioning
        self.configFrame.grid(row = 0, column = 0, padx = 20, pady = (20, 10))
        self.processFrame.grid(row = 1, column = 0, padx = 20, pady = (10, 20))
        
        self.ConfigFrame()
    
    def ConfigFrame(self):
        '''
        Places necessary interactions.
        '''
        master = self.configFrame
        self.fpsLabel = ttk.Label(master, text = 'FPS :')
        self.fpsEntry = ttk.Entry(master, textvariable = self.fps, width = 4)
        self.direLabel = ttk.Label(master, text = 'Directory :')
        self.direLabel1 = ttk.Label(master, text = 'None')
        self.fileLabel = ttk.Label(master, text = 'File :')
        self.fileLabel1 = ttk.Label(master, text = 'None')
        self.fileButton = ttk.Button(master, text = 'Choose File', command = self.getFile)
        
        # posiioning
        self.fpsLabel.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = W)
        self.fpsEntry.grid(row = 0, column = 1, padx = 10, pady = 10, sticky = E)
        self.direLabel.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = W)
        self.direLabel1.grid(row = 1, column = 1, padx = 10, pady = 10, sticky = W)
        self.fileLabel.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = W)
        self.fileLabel1.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = W)
        self.fileButton.grid(row = 3, column = 0, padx = 10, pady = 10, columnspan = 2, sticky = (N, E, W, S))
        
    def ProcessFrame(self):
        '''
        Shows progress.
        '''
        master = self.processFrame
        self.fileButton = ttk.Button(master, text = 'Peel this file', style = 'AccentButton', command = self.peel)
        self.progBar = ttk.Progressbar(master, mode = 'determinate')
        
        self.fileButton.grid(row = 0, column = 0, padx = 10, pady = 10)
        self.progBar.grid(row = 0, column = 1, padx = 10, pady = 10)
        
    def getFile(self):
        '''
        Manages file.
        '''
        name = filedialog.askopenfilename(filetypes = [('MPEG4', '.mp4'), ('AVI', '.avi')])
        try:
            fragments = name.split('/')
            directory = '.../'+fragments[::-1][1]
            filename = fragments[-1]
            self.fileName.set(name)
            self.direLabel.config(text = directory)
            self.fileLabel.config(text = filename)
            self.ProcessFrame()
        except: pass

    def peel(self):
        '''
        Peels the video like an apple.
        Peeled images are stored in a folder of
        the same name as the file.
        '''
        try: os.mkdir(self.fileName.get().split('.')[0])
        except: pass
        dire = self.fileName.get().split('.')[0]
        self.progBar.config(value = 0)
        vid = cv2.VideoCapture(self.fileName.get())
        nframe = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        curfps = int(vid.get(cv2.CAP_PROP_FPS))
        n = 1
        for i in range(nframe):
            success, frame = vid.read()
            if not success:
                break
            if i%round(curfps/self.fps.get()) == 0:
                cv2.imwrite(dire+'/image{}.jpg'.format(n), frame)
                if i != nframe-1:
                    newpoint = i/nframe*100
                else:
                    newpoint = 100
                self.progBar.config(value = newpoint)
                self.progBar.update()
                n += 1

root = Tk()
app = Peel(root)
root.mainloop()
