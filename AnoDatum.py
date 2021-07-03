import os
import colorsys
import time
import cv2
import json
from tkinter import *
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk

class AnoDatum:
    def __init__(self, root):
        self.root = root
        self.root.title('AnoDatum')
        self.root.resizable(False, False)
        
        self.currentTheme = 'light'
        self.style = ttk.Style(self.root)
        self.bg = '#ffffff'
        self.fg = '#000000'
        
        self.directoryPath = StringVar()
        self.fileIndex = -1
        
        self.numClasses = IntVar()
        self.numClasses.set(1)
        self.classList = list()
        self.colorDict = dict()
        self.currentClass = StringVar()
        
        self.availModes = ['Bounding Box', 'Landmark']
        self.drawDict = {'Bounding Box': self.drawBB, 'Landmark': self.drawLM}
        self.currentMode = StringVar()
        
        self.data = {'annotation-type': str(), 'labels': list(), 'annotations': dict()}
        
        self.clicked = False
        self.sx = 0
        self.sy = 0
        
        self.saveOrNot = IntVar()
        
        self.Theming()
        self.style.theme_use('azure')
        self.MainFrame()
        
    def Theming(self):
        self.root.tk.call('source', 'Azure/azure/azure.tcl')
        self.root.tk.call('source', 'Azure/azure-dark/azure-dark.tcl')
        
    def MainFrame(self):
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(row = 0, column = 0)
        
        self.canvframe = ttk.Frame(self.mainframe, width = 640, height = 480)
        self.canvframe.grid(row = 0, column = 0, rowspan = 2, columnspan = 2, padx = (20, 10), pady = (20, 10), sticky = W)
        self.logframe = ttk.LabelFrame(self.mainframe, text = 'Log')
        self.logframe.grid(row = 0, column = 2, columnspan = 2, padx = (10, 20), pady = (20, 10), sticky = W)
        self.fileframe = ttk.LabelFrame(self.mainframe, text = 'Files')
        self.fileframe.grid(row = 2, column = 1, columnspan = 3, padx = (10, 20), pady = (10, 20), sticky = W)
        self.detailframe = ttk.LabelFrame(self.mainframe, text = 'Details')
        self.detailframe.grid(row = 2, column = 0, padx = (20, 10), pady = (10, 20), sticky = W)
        self.configframe = ttk.LabelFrame(self.mainframe, text = 'Configuration')
        self.configframe.grid(row = 1, column = 2, padx = (10, 20), pady = 10, sticky = W)
        
        self.LogFrame()
        self.FileFrame()
        self.DetailFrame()
        self.ConfigFrame()
        
    def CanvasFrame(self):
        master = self.canvframe
        try: self.canCanvas.destroy()
        except: pass
        try: filepath = self.directoryPath.get()+'/'+self.currentFile()
        except: return
        self.data['annotations'][self.currentFile()] = []
        self.stuffLog = []
        self.clearLog(self.logBox)
        img = Image.open(filepath).resize((640, 480))
        img = ImageTk.PhotoImage(img)
        master.image = img
        self.canvCanvas = Canvas(master, width = 640, height = 480, relief = 'flat', bd = 0, bg = self.bg)
        self.canvCanvas.grid(row = 0, column = 0, sticky = W)
        self.curImg = self.canvCanvas.create_image(0, 0, anchor = NW, image = img)
        
    def LogFrame(self):
        master = self.logframe
        ttk.Label(master, text = '>').grid(row = 0, column = 0, padx = (20, 0), pady = 10, sticky = N)
        self.logBox = Text(master, width = 30, height = 10, relief = 'flat', state = 'disabled', bg = self.bg, highlightthickness = 0)
        self.logBox.grid(row = 0, column = 1, padx = 20, pady = 10, rowspan = 2, sticky = (N, E, W, S))
        
    def FileFrame(self):
        master = self.fileframe
        self.direLabel = ttk.Label(master, text = 'Current Directory :')
        self.direLabel.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = W)
        self.sldiLabel = ttk.Label(master, text = 'None')
        self.sldiLabel.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = E)
        self.fileLabel = ttk.Label(master, text = 'Current File :')
        self.fileLabel.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = W)
        self.slfiLabel = ttk.Label(master, text = 'None')
        self.slfiLabel.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = E)
        self.chfiButton = ttk.Button(master, text = 'Choose Directory', command = self.chooseDirectory)
        self.chfiButton.grid(row = 0, column = 2, padx = 20, pady = 10, columnspan = 2, sticky = (N, E, W, S))
        
    def DetailFrame(self):
        master = self.detailframe
        self.modeLabel = ttk.Label(master, text = 'Selected Mode :')
        self.modeLabel.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = W)
        self.slmoLabel = ttk.Label(master, text = self.currentMode.get())
        self.slmoLabel.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = E)
        self.clasLabel = ttk.Label(master, text = 'Current Label :')
        self.clasLabel.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = W)
        self.clasBox = ttk.Combobox(master, state = 'readonly', textvariable = self.currentClass, values = self.getValues(self.classList))
        self.clasBox.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = W)
        self.clasBox.bind('<<ComboboxSelected>>', lambda event: self.putColorPatch())
            
    def ConfigFrame(self):
        master = self.configframe
        self.saveButton = ttk.Button(master, text = 'Save', command = self.save)
        self.saveButton.grid(row = 0, column = 0, padx = 25, pady = 10, sticky = (N, E, W, S))
        self.darkSwitch = ttk.Checkbutton(master, text = 'Switch Mode', style = 'Switch', command = self.switchMode)
        self.darkSwitch.grid(row = 0, column = 1, padx = 25, pady = 10, sticky = (N, E, W, S))
        commands = [self.nextFile, self.CanvasFrame, self.bindCanvas]
        self.nextButton = ttk.Button(master, text = 'Next', command = self.commit(commands), style = 'AccentButton')
        self.nextButton.grid(row = 1, column = 0, padx = 25, pady = 10,  sticky = (N, E, W, S))
        self.settButton = ttk.Button(master, text = 'Settings', command = self.SettingsFrame)
        self.settButton.grid(row = 2, column = 0, padx = 25, pady = 10, columnspan = 2, sticky = (N, E, W, S))
        
    def SettingsFrame(self):
        try: self.settings.lift()
        except:
            self.settings = Toplevel(self.root, background = self.bg)
            self.settings.title('AnoDatum - Settings')
            self.settings.resizable(False, False)
            
            self.saveOrNot.set(1)
        
            self.ModeFrame()
            self.LoadSaveFrame()
        
    def ClassLandmarkFrame(self):
        self.cllaFrame = ttk.LabelFrame(self.settings, text = 'Labels')
        self.cllaFrame.grid(row = 1, column = 0, padx = 20, pady = 20, sticky = W)
        
        master = self.cllaFrame
        self.nuclLabel = ttk.Label(master, text = 'Number of Labels :')
        self.nuclLabel.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = W)
        self.nuclEntry = ttk.Entry(master, width = 5, textvariable = self.numClasses)
        self.nuclEntry.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = W)
        commands = [self.setUpClassList, self.DefineFrame]
        self.conuButton = ttk.Button(master, text = 'Set', style = 'AccentButton', command = self.commit(commands))
        self.conuButton.grid(row = 1, column = 0, columnspan = 2, padx = 20, pady = 10, sticky = (N, E, W, S))
        
    def DefineFrame(self):
        self.defineFrame = ttk.LabelFrame(self.settings, text = 'Define Labels')
        self.defineFrame.grid(row = 0, column = 1, padx = 20, pady = 20, rowspan = 3, sticky = W)
        
        def edit(event):
            temp = Toplevel(self.root, background = self.bg)
            temp.title('Edit Label Name')
            temp.resizable(False, False)
            clicked_index = int(self.declTree.focus().replace('I',''), 16) - 1
            temp_entry = ttk.Entry(temp, textvariable = self.classList[clicked_index])
            temp_entry.grid(row = 0, column = 0, padx = 20, pady = (20, 10))
            change = lambda: self.declTree.item(self.declTree.focus(), value = self.classList[clicked_index].get())
            commands = [change, temp.destroy]
            conf_button = ttk.Button(temp, text = 'Confirm', command = self.commit(commands))
            conf_button.grid(row = 1, column = 0, padx = 20, pady = (10, 20), sticky = (N, E, W, S))
        
        master = self.defineFrame
        self.declTree = ttk.Treeview(master, columns = ['Name'], height = 17)
        self.declTree.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = (N, E, W, S))
        self.declTree.column('#0', width = 20, anchor = 'center')
        self.declTree.column('Name', width = 200, anchor = 'center')
        self.declTree.heading('#0', text = 'Id')
        self.declTree.heading('Name', text = 'Name')
        for i in range(self.numClasses.get()):
            self.declTree.insert('', i, text = str(i), values = self.classList[i].get())
        self.declTree.bind('<<TreeviewSelect>>', edit)
        
    def ModeFrame(self):
        self.modeFrame = ttk.LabelFrame(self.settings, text = 'Mode')
        self.modeFrame.grid(row = 0, column = 0, padx = 20, pady = 20, sticky = W)
        
        master = self.modeFrame
        self.modeLabel = ttk.Label(master, text = 'Choose Mode :')
        self.modeLabel.grid(row = 0, column = 0, padx = 20, pady = 10)
        self.modeBox = ttk.Combobox(master, state = 'readonly', textvariable = self.currentMode, values = self.availModes)
        self.modeBox.set(self.availModes[0])
        self.modeBox.grid(row = 0, column = 1, padx = 20, pady = 10)
        commands = [self.ClassLandmarkFrame]
        self.comoButton = ttk.Button(master, text = 'Set', style = 'AccentButton', command = self.commit(commands))
        self.comoButton.grid(row = 1, column = 0, padx = 20, pady = 10, columnspan = 2, sticky = (N, E, W, S))
        
    def LoadSaveFrame(self):
        self.losaFrame = ttk.LabelFrame(self.settings, text = 'Configuration')
        self.losaFrame.grid(row = 2, column = 0, padx = 20, pady = 20, sticky = W)
        
        master = self.losaFrame
        self.loadButton = ttk.Button(master, text = 'Load Settings', command = self.loadSettings)
        self.loadButton.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = (N, E, W, S))
        self.saveCheck = ttk.Checkbutton(master, text = 'Remember settings', variable = self.saveOrNot, onvalue = 1, offvalue = 0)
        self.saveCheck.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = (N, E, W, S))
        commands = [self.submit, self.settings.destroy]
        self.confButton = ttk.Button(master, text = 'Confirm', style = 'AccentButton', command = self.commit(commands))
        self.confButton.grid(row = 2, column = 0, padx = 20, pady = 10, columnspan = 2, sticky = (N, E, W, S))
    
    def drawPoint(self, event):
        color = self.colorDict[self.currentClass.get()]
        point = (event.x-3, event.y-3, event.x+3, event.y+3)
        self.canvCanvas.create_oval(point, fill = color, outline = 'black', width = 2)
        
    def drawBB(self, event):
        max_h = int(self.canvCanvas['height'])
        max_w = int(self.canvCanvas['width'])
        ex = (0 <= event.x < max_w) * event.x + (event.x >= max_w) * (max_w-1)
        ey = event.y
        if 'Control' in str(event):
            if self.sy < event.y: ey = self.sy + abs(self.sx - ex)
            else: ey = self.sy - abs(self.sx - ex)
        ey = (0 <= ey < max_h) * ey + (ey >= max_h) * (max_h-1)
        try: color = self.colorDict[self.currentClass.get()]
        except: return
        box = (self.sx, self.sy, ex, ey)
        if 'ButtonPress' in str(event):
            if event.num == 1:
                if self.clicked:
                    self.clicked = False
                    centre = ((self.sx+ex)//2, (self.sy+ey)//2)
                    width = abs(self.sx-ex)
                    height = abs(self.sy-ey)
                    classId = self.data['labels'].index(self.currentClass.get())
                    to_put = [classId, centre[0], centre[1], width, height]
                    self.data['annotations'][self.currentFile()].append(to_put)
                    self.updateLog(str(to_put), 'a')
                else:
                    self.clicked = True
                    self.sx, self.sy = event.x, event.y
                    rect = self.canvCanvas.create_rectangle(self.sx, self.sy, self.sx+1, self.sy+1, outline = color, width = 3)
                    self.stuffLog.append(rect)
        elif 'Motion' in str(event) and self.clicked:
            self.canvCanvas.coords(self.stuffLog[-1], box)
    
    def drawLM(self, event):
        max_h = int(self.canvCanvas['height'])
        max_w = int(self.canvCanvas['width'])
        ex = (0 <= event.x < max_w) * event.x + (event.x >= max_w) * (max_w-1)
        ey = (0 <= event.y < max_h) * event.y + (event.y >= max_h) * (max_h-1)
        try: color = self.colorDict[self.currentClass.get()]
        except: return
        classId = self.data['labels'].index(self.currentClass.get())
        if 'ButtonPress' in str(event):
            if event.num == 1:
                point = self.canvCanvas.create_oval(ex-3, ey-3, ex+3, ey+3, fill = color, outline = 'black', width = 2)
                self.stuffLog.append(point)
                to_put = [classId, ex, ey]
                self.data['annotations'][self.currentFile()].append(to_put)
                self.updateLog(str(to_put), 'a')
                self.currentClass.set(self.data['labels'][(classId+1)%self.numClasses.get()])
                self.putColorPatch()
            if event.num == 3:
                self.currentClass.set(self.data['labels'][(classId-1)%self.numClasses.get()])
                self.putColorPatch()
    
    def drawSS(self, event):
        pass
    
    def drawPS(self, event):
        pass
    
    def undo(self, event):
        try: 
            self.canvCanvas.delete(self.stuffLog[-1])
            self.updateLog(str(self.data['annotations'][self.currentFile()][-1]), 'r')
            self.stuffLog.pop()
            self.data['annotations'][self.currentFile()].pop()
        except: pass
    
    def hue2hex(self, degree):
        rgb = colorsys.hsv_to_rgb(degree/360, 1, 1)
        r, g, b = int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def giveColors(self):
        one_part = 360//self.numClasses.get()
        degrees = [one_part*i for i in range(self.numClasses.get())]
        for clas, deg in zip(self.getValues(self.classList), degrees):
            self.colorDict[clas] = self.hue2hex(deg)
        
    def bindCanvas(self):
        try:
            self.canvCanvas.bind('<Button-1>', self.drawDict[self.currentMode.get()])
            if self.currentMode.get() == 'Bounding Box':
                self.canvCanvas.bind('<Motion>', self.drawDict[self.currentMode.get()])
                self.canvCanvas.bind('<Control>', self.drawDict[self.currentMode.get()])
                self.canvCanvas.bind('<ButtonRelease-1>', self.drawDict[self.currentMode.get()])
            elif self.currentMode.get() == 'Landmark':
                self.canvCanvas.bind('<Button-3>', self.drawDict[self.currentMode.get()])
            self.root.bind_all('<Control-z>', self.undo)
        except: pass
        
    def submit(self):
        self.slmoLabel.config(text = self.currentMode.get())
        self.clasBox.config(values = self.getValues(self.classList))
        self.clasBox.set(self.classList[0].get())
        self.giveColors()
        self.putColorPatch()
        self.data['annotation-type'] = self.currentMode.get()
        self.data['labels'] = self.getValues(self.classList)
        try: self.bindCanvas()
        except: pass
        if self.saveOrNot.get():
            self.saveSettings()
    
    def save(self):
        try:
            string = json.dumps(self.data, sort_keys=True, indent = 4)
            f = open(self.directoryPath.get()+'data{}.json'.format(time.strftime('@%H-%M-%S_%d-%m-%Y')), 'w')
            f.write(string)
            f.close()
            msg.configure(text = 'Saved.')
        except:
            a = Toplevel(self.root)
            msg = ttk.Label(a, text = 'Couldn\'t save.', font = (None, 20))
            msg.grid(row = 0, column = 0, padx = 20, pady = 20)
            
    def saveSettings(self):
        try:
            settings = {'mode': self.currentMode.get(), 'num_labels': self.numClasses.get(), 'labels': self.getValues(self.classList)}
            string = json.dumps(settings, indent = 4)
            f = open(self.directoryPath.get()+'setting{}.json'.format(time.strftime('@%H-%M-%S_%d-%m-%Y')), 'w')
            f.write(string)
            f.close()
        except: 
            a = Toplevel(self.settings)
            msg = ttk.Label(a, text = 'Couldn\'t save', font = (None, 20))
            msg.grid(row = 0, column = 0, padx = 20, pady = 20)
        
    def loadSettings(self):
        settingsPath = filedialog.askopenfilename()
        try:
            settingsDict = json.load(open(settingsPath))
            self.currentMode.set(settingsDict['mode'])
            self.numClasses.set(settingsDict['num_labels'])
            self.classList = [StringVar() for _ in range(self.numClasses.get())]
            for i in range(self.numClasses.get()):
                self.classList[i].set(settingsDict['labels'][i])
        except: 
            a = Toplevel(self.settings)
            ttk.Label(a, text = 'Couldn\'t load.', font = (None, 20)).grid(row = 0, column = 0, padx = 20, pady = 20)
    
    def setUpClassList(self):
        for i in range(self.numClasses.get()):
            try:
                if self.classList[i].get() == '':
                    self.classList[i].set('unamed-'+str(i))
            except:
                self.classList.append(StringVar())
                self.classList[i].set('unamed-'+str(i))
    
    def updateLog(self, string, mode):
        self.logBox.configure(state = 'normal')
        if mode == 'a':
            self.logBox.insert('1.0', 'added : '+string+'\n')
        if mode == 'r':
            self.logBox.insert('1.0', 'removed : '+string+'\n')
        self.logBox.configure(state = 'disabled')
        
    def clearLog(self, pointer):
        self.logBox.configure(state = 'normal')
        self.logBox.delete('1.0', END)
        self.logBox.configure(state = 'disabled')
    
    def colorImg(self, color):
        img = Image.new('RGB', (10, 80), color)
        img = ImageTk.PhotoImage(img)
        return img
    
    def putColorPatch(self):
        try: self.colPatch.destroy()
        except: pass
        finally:
            color = self.colorDict[self.currentClass.get()]
            colr = self.colorImg(color)
            self.colPatch = ttk.Label(self.logframe, image = colr)
            self.colPatch.image = colr
            self.colPatch.grid(row = 1, column = 0, padx = (20, 0), pady = 10, sticky = (N, E, W, S))
    
    def isImage(self, filename):
        extension = filename.split('.')[-1]
        extensions = ['jpg', 'jpeg', 'png']
        return extension in extensions
    
    def chooseDirectory(self):
        self.directoryPath.set(filedialog.askdirectory())
        self.sldiLabel.config(text = self.directoryPath.get().split('/')[-1])
        
    def directoryList(self):
        try: return [filename for filename in os.listdir(self.directoryPath.get()) if self.isImage(filename)]
        except FileNotFoundError: return None
    
    def currentFile(self):
        try: return self.directoryList()[self.fileIndex]
        except: return None
        
    def nextFile(self):
        if self.currentFile():
            self.fileIndex += 1
            self.slfiLabel.config(text = self.currentFile())
    
    def switchMode(self):
        if self.currentTheme == 'light':
            self.style.theme_use('azure-dark')
            self.currentTheme = 'dark'
            self.bg = '#333333'
            self.fg = '#ffffff'
        elif self.currentTheme == 'dark':
            self.style.theme_use('azure')
            self.currentTheme = 'light'
            self.bg = '#ffffff'
            self.fg = '#000000'
        self.changeBgFg(self.root)
    
    def changeBgFg(self, root):
        for _, wid in root.children.items():
            tw = type(wid)
            if tw in [Toplevel, ttk.Frame, ttk.LabelFrame]:
                try:
                    wid.configure(background = self.bg)
                    wid.configure(foreground = self.fg)
                except: pass
                finally: self.changeBgFg(wid)
            elif tw in [Text, Canvas, ttk.Combobox]:
                try: 
                    wid.configure(highlightthickness = 0)
                    wid.configure(background = self.bg)
                    wid.configure(foreground = self.fg)
                except: pass
        
    def commit(self, commands):
        return lambda: [func() for func in commands]
    
    def getValues(self, list_):
        return [item.get() for item in list_]

root = Tk()
app = AnoDatum(root)
root.mainloop()
