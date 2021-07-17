import os
import colorsys
import time
import cv2
import json
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class AnoDatum:
    '''
    The whole app...
    '''
    class Box:
        '''
        Creates a bounding box with specified:
        - vertices
        - label
        - color
        '''
        def __init__(self, master, sx, sy, ex, ey, label, color):
            '''
            Constructs the box, label and box bounding the label on the canvas.
            master : (tkinter.Canvas)
            sx, sy : starting vertix (int)
            ex, ey : ending vertix (int)
            label  : label for the box (string)
            color  : hex color code (string)
            '''
            self.__master = master
            self.start = self.get_real(sx, sy)
            end = self.get_real(ex, ey)
            self.id = master.create_rectangle(self.start + end, outline = color, width = 3)
            x, y = master.bbox(self.id)[:2]
            self.__text = master.create_text(x+2, y+2, text = label, fill = '#ffffff', anchor = 'nw')
            self.__bound = master.create_rectangle(master.bbox(self.__text), fill = color, width = 0)
            master.lift(self.__text)
        
        def destroy(self):
            '''
            Destroys the box, the label and box bounding 
            the label from the canvas.
            '''
            for item in (self.id, self.__text, self.__bound):
                self.__master.delete(item)
        
        def get_real(self, x, y):
            '''
            Translates the coordinates from space with canvas' size
            onto absolute space and force not to go beyond the
            absolute lower and upper bounds.
            x : x-coordinate on the canvas space (int)
            y : y-coordinate on the canvas space (int)
            
            Returns -
            Tuple of corrected coordinates (x, y) (int)
            
            (With larger images fitted on the fixed canvas,
            and the behaviour of Tk canvas that coordinates
            are drawn relative to the canvas space, doing stuffs
            can be (are) quite drunkening. The function was made
            to save the doer from hell like that.)
            '''
            max_w = self.__master.bbox('image')[2]
            max_h = self.__master.bbox('image')[3]
            
            abs_x = int(self.__master.xview()[0] * max_w + x)
            abs_y = int(self.__master.yview()[0] * max_h + y)
            
            abs_y = (0 <= abs_y < max_h) * abs_y + (abs_y >= max_h) * (max_h-1)
            abs_x = (0 <= abs_x < max_w) * abs_x + (abs_x >= max_w) * (max_w-1)
        
            return abs_x, abs_y
            
        def info(self):
            '''
            Constructs information about the bounding box
            on the correct space.
            
            Returns - 
            List of:
            - centre on x direction (float)
            - centre on y direction (float)
            - width (float)
            - height (float)
            with relative to the actual image space
            in [0, 1] to adapt various sizes.
            '''
            max_w = self.__master.bbox('image')[2]
            max_h = self.__master.bbox('image')[3]
            x1, y1, x2, y2 = self.__master.bbox(self.id)
            width = abs(x1 - x2) / max_w
            height = abs(y1 - y2) / max_h
            centerx = ((x1 + x2) // 2) / max_w
            centery = ((y1 + y2) // 2) / max_h
            return [round(i,4) for i in (centerx, centery, width, height)]
        
        def update(self, new_end_x, new_end_y, make_square = False):
            '''
            Updates the ending coordinates (current cursor position)
            onto the correct space.
            new_end_x   : x part of new ending vertix (int)
            new_end_y   : y part of new ending vertix (int)
            make_square : flag to let the function know to force draw square (boolean)
            '''
            sx, sy = self.start
            ex, ey = self.get_real(new_end_x, new_end_y)
            if make_square:
                if sx < ex: ex = sx + abs(sy - ey)
                else: ex = sx - abs(sy - ey)
            self.__master.coords(self.id, (sx, sy, ex, ey))
            
            x, y = self.__master.bbox(self.id)[:2]
            self.__master.coords(self.__text, x+2, y+2)
            self.__master.coords(self.__bound, self.__master.bbox(self.__text))
        
    class Point:
        '''
        Creates a point with specified :
        - x, y coordinate
        - label
        - color
        '''
        def __init__(self, master, x, y, name, color):
            '''
            Constructs the point, label and box bounding the label on the canvas.
            master : (tkinter.Canvas)
            x, y   : point (int)
            label  : label for the box (string)
            color  : hex color code (string)
            '''
            self.__master = master
            x, y = self.get_real(x, y)
            self.id = master.create_oval(x, y, x+4, y+4, fill = color, outline = '#ffffff', width = 1)
            x, y = master.bbox(self.id)[:2]
            self.__text = master.create_text(x, y+8, text = name, fill = '#ffffff', anchor = 'ne')
            self.__bound = master.create_rectangle(master.bbox(self.__text), fill = color, width = 0)
            master.lift(self.__text)
            
        def destroy(self):
            '''
            Destroys the box, the label and box bounding 
            the label from the canvas.
            '''
            for item in (self.id, self.__text, self.__bound):
                self.__master.delete(item)
                
        def get_real(self, x, y):
            '''
            Translates the coordinates from space with canvas' size
            onto absolute space and force not to go beyond the
            absolute lower and upper bounds.
            x : x-coordinate on the canvas space (int)
            y : y-coordinate on the canvas space (int)
            
            Returns -
            Tuple of corrected coordinates (x, y) (int)
            
            (With larger images fitted on the fixed canvas,
            and the behaviour of Tk canvas that coordinates
            are drawn relative to the canvas space, doing stuffs
            can be (are) quite drunkening. The function was made
            to save the doer from hell like that.)
            '''
            max_w = self.__master.bbox('image')[2]
            max_h = self.__master.bbox('image')[3]
            
            abs_x = int(self.__master.xview()[0] * max_w + x)
            abs_y = int(self.__master.yview()[0] * max_h + y)
        
            return abs_x, abs_y
        
        def info(self):
            '''
            Constructs information about the point
            on the space.
            
            Returns - 
            List of:
            - coordinate on x direction (float)
            - coordinate on y direction (float)
            with relative to the actual image space
            in [0, 1] to adapt various sizes.
            '''
            x, y, _, _ = self.__master.bbox(self.id)
            max_w = self.__master.bbox('image')[2]
            max_h = self.__master.bbox('image')[3]
            x = x / max_w
            y = y / max_h
            return [round(x, 4), round(y, 4)]
        
    def __init__(self, root):
        '''
        Take in the root and builds the app up on that.
        '''
        # Configures the root.
        self.root = root
        self.root.title('AnoDatum')
        self.root.resizable(False, False)
        
        # Configures style.
        self.currentTheme = 'light'
        self.style = ttk.Style(self.root)
        try:
            self.root.tk.call('source', 'Azure/azure/azure.tcl')
            self.root.tk.call('source', 'Azure/azure-dark/azure-dark.tcl')
            self.styleDict = {'light': 'azure',
                              'dark' : 'azure-dark'}
            self.bg = {'light': '#ffffff', 'dark': '#333333'}
            self.fg = {'light': '#000000', 'dark': '#ffffff'}
        except: 
            self.styleDict = {'light': 'default',
                              'dark' : 'default'}
            self.bg = {'light': '#ffffff', 'dark': '#000000'}
            self.fg = {'light': '#000000', 'dark': '#ffffff'}
        self.style.theme_use(self.styleDict[self.currentTheme])
        
        # Sets up file communication system.
        self.directoryPath = StringVar()
        self.fileIndex = -1
        
        # Sets up class/label and color system
        self.numClasses = 0
        self.classList = list()
        self.colorDict = dict()
        self.currentClass = StringVar()
        
        # Sets up labelling modes
        self.availModes = ['Bounding Box', 'Landmark']
        self.drawDict = {'Bounding Box': self.drawBB, 'Landmark': self.drawLM}
        self.currentMode = StringVar()
        
        # Sets up labelling schemes
        self.availSchemes = ['Classic', 'Extended', 'Hierarchical']
        self.relationGraph = dict() # required in Hierarchical scheme
        self.currentScheme = StringVar()
        
        # Declare data
        self.data = {'annotation-type': str(), 
                     'annotation-scheme': str(), 
                     'labels': list(), 
                     'annotations': dict()}
        
        # Sets up drawing system
        self.clicked = False # click marker required in Bounding Box mode
        
        # Load/Save part
        self.saveOrNot = IntVar(value = 0)
        
        # Start constructing the app stack
        self.MainFrame()
        
    def MainFrame(self):
        '''
        Creates individual parts and position them.
        '''
        self.mainframe = ttk.Frame(self.root) # main frame
                
        self.canvframe = ttk.Frame(self.mainframe) # drawing area
        self.logframe = ttk.LabelFrame(self.mainframe, text = 'Log') # log
        self.detailframe = ttk.LabelFrame(self.mainframe, text = 'Details') # label choosing area
        self.configframe = ttk.LabelFrame(self.mainframe, text = 'Configuration') # settings area
        self.fileframe = ttk.LabelFrame(self.mainframe, text = 'Files') # file system area
                
        # Positioning
        self.mainframe.grid(row = 0, column = 0)
        self.canvframe.grid(row = 0, column = 1, rowspan = 3, pady = 20, sticky = W)
        self.logframe.grid(row = 0, column = 2, padx = 20, pady = (20, 10), sticky = W)
        self.detailframe.grid(row = 0, column = 0, rowspan = 3, padx = 20, pady = 20, sticky = W)
        self.configframe.grid(row = 2, column = 2, padx = 20, pady = (10, 20), sticky = W)
        self.fileframe.grid(row = 1, column = 2, padx = 20, pady = 10, sticky = W)
        
        self.LogFrame()
        self.FileFrame()
        self.PrepareCanvas()
        self.DetailFrame()
        self.ConfigFrame()
        
    def PrepareCanvas(self):
        '''
        Prepares the drawing area.
        '''
        master = self.canvframe
        
        self.currentLabel = ttk.Label(master, text = '', font = ('Courier', 11)) # shows current label string
        self.colorPatch = Canvas(master, width = 100, height = 5, relief = 'flat', bg = self.bg[self.currentTheme], highlightthickness = 0, bd = 0) # color idicator
        self.canvCanvas = Canvas(master, width = 640, height = 480, relief = 'flat', bg = self.bg[self.currentTheme], highlightthickness = 0, bd = 0) # the actual drawing canvas
        
        # Scrollbars
        self.sby = ttk.Scrollbar(master, orient = VERTICAL) # y scrollbar
        self.sbx = ttk.Scrollbar(master, orient = HORIZONTAL) # x scrollbar
        
        # Key bindings
        self.canvCanvas.bind('<Button-5>', lambda _: self.canvCanvas.yview_scroll(1, 'units')) # wheel-down to go down y view
        self.canvCanvas.bind('<Button-4>', lambda _: self.canvCanvas.yview_scroll(-1, 'units')) # wheel-up to go up y view
        self.canvCanvas.bind('<Control-5>', lambda _: self.canvCanvas.xview_scroll(1, 'units')) # Ctrl+wheel-down to go down x view
        self.canvCanvas.bind('<Control-4>', lambda _: self.canvCanvas.xview_scroll(-1, 'units')) # Ctrl+wheel-up to go up x view
        
        # Positioning
        self.currentLabel.grid(row = 0, column = 0, pady = 10, sticky = W)
        self.colorPatch.grid(row = 1, column = 0, pady = 10, sticky = (N, E, W, S))
        self.canvCanvas.grid(row = 2, column = 0, pady = (10, 0), sticky = (N, E, W, S))
        self.sby.grid(row = 2, column = 1, sticky = 'ns')
        self.sbx.grid(row = 3, column = 0, sticky = 'ew')
        
    def CanvasFrame(self):
        '''
        Manages the actual drawing canvas.
        Called as every change in file.
        '''
        master = self.canvframe
        try: self.clearFrame(self.canvCanvas) # to avoid confusing view and memory leak
        except: pass
        try: filepath = self.directoryPath.get()+'/'+self.currentFile() # to ensure a file is called
        except: return
        self.data['annotations'][self.currentFile()] = []
        self.stuffLog = [] # container for every drawings on the current canvas
        self.clearLog(self.logBox) # to avoid confusing
        img = Image.open(filepath)
        img = ImageTk.PhotoImage(img)
        master.image = img # don't know why this has to be done - just don't touch
        self.curImg = self.canvCanvas.create_image(0, 0, anchor = 'nw', image = img, tags = 'image') # fits the image on the canvas
        self.sbx.config(command = self.canvCanvas.xview)
        self.sby.config(command = self.canvCanvas.yview)
        self.canvCanvas.config(xscrollcommand = self.sbx.set, yscrollcommand = self.sby.set, scrollregion = self.canvCanvas.bbox('all'))
        
    def LogFrame(self):
        '''
        Briefly reports the user that what they have done.
        '''
        master = self.logframe
        
        indiLabel = ttk.Label(master, text = '>') # to look cool
        self.logBox = Text(master, font = ('Courier', 10),
                           width = 32, height = 10, 
                           relief = 'flat', state = 'disabled', 
                           background = self.bg[self.currentTheme], foreground = self.fg[self.currentTheme],
                           highlightthickness = 0)
        
        indiLabel.grid(row = 0, column = 0, padx = (20, 0), pady = 10, sticky = N)
        self.logBox.grid(row = 0, column = 1, padx = 20, pady = 10, rowspan = 2, sticky = (N, E, W, S))
        
    def FileFrame(self):
        '''
        Creates actions points to help user
        play with the files.
        '''
        master = self.fileframe
        
        direLabel = ttk.Label(master, text = 'Current Directory :')
        self.sldiLabel = ttk.Label(master, text = 'None')
        fileLabel = ttk.Label(master, text = 'Current File :')
        self.slfiLabel = ttk.Label(master, text = 'None')
        chfiButton = ttk.Button(master, text = 'Choose Directory', command = self.chooseDirectory)
        commands = [self.prevFile, self.CanvasFrame, self.bindCanvas]
        prevButton = ttk.Button(master, text = 'Previous', command = self.commit(commands))
        commands = [self.nextFile, self.CanvasFrame, self.bindCanvas]
        nextButton = ttk.Button(master, text = 'Next', command = self.commit(commands), style = 'AccentButton')
        
        # positioning
        direLabel.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = W)
        self.sldiLabel.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = E)
        fileLabel.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = W)
        self.slfiLabel.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = E)             
        chfiButton.grid(row = 2, column = 0, columnspan = 2, padx = 20, pady = 10, sticky = (N, E, W, S))
        prevButton.grid(row = 3, column = 0, padx = 20, pady = 10,  sticky = (N, E, W, S))
        nextButton.grid(row = 3, column = 1, padx = 20, pady = 10,  sticky = (N, E, W, S))
        
    def DetailFrame(self):
        '''
        Creates choice points (radio-buttons/check_buttons)
        to help the user choose a label string to work.
        '''
        # ------ Local helper functions down here ------
        def processChoice(index):
            '''
            After the user makes a choice, 
            - actual label (single label in Classic
              and multi labels in non-Classic) need to be 
              carefully fetched.
            - respective color need to be shown.
            The function takes care.
            '''
            # Assemble actual label
            if self.currentScheme.get() != 'Classic':
                label = []
                for i in range(index+1):
                    if self.labelarr[i].get():
                        self.currentClass.set(self.classList[i].get())
                        label.append(self.classList[i].get())
                label = '-'.join(label)
                
                # Enable/Disable buttons in Hierarchical scheme
                if self.currentScheme.get() == 'Hierarchical':
                    guide_buttons(index)
                
            else:
                label = self.currentClass.get()
            
            try: # Ensures a valid label is chosen
                self.currentLabel.configure(text = label)
                self.colorPatch.configure(background = self.colorDict[self.currentClass.get()])
            except: # If not, invisiblise the label and color penel
                self.currentLabel.configure(text = '')
                self.colorPatch.configure(background = self.bg[self.currentTheme])
                
        def find_parent(node_index):
            '''Finds parent of given node index in the relationGraph.'''
            for parent, kids in self.relationGraph.items():
                if node_index in kids: 
                    return str(parent) if parent != 'root' else parent
                    
        def find_siblings(node_index):
            '''Finds siblings of given node index in the relationGraph.'''
            return self.relationGraph[find_parent(node_index)]
        
        def find_children(node_index):
            '''Finds children of given node index in the relationGraph.'''
            try: return self.relationGraph[str(node_index)]
            except: return []
                
        def switch_state(button):
            '''Switches the state of buttons.'''
            if str(button['state']) == 'normal':
                button.configure(state = 'disabled')
            else: button.configure(state = 'normal')
                
        def guide_buttons(node_index):
            '''Manages buttons -
            if clicked buttton is checked
                - shuts down parent and siblings
                - turns on children
            else
                - does the opposite'''
            parent = find_parent(node_index)
            if parent != 'root':
                switch_state(self.buttons[int(parent)])
            for i in find_siblings(node_index):
                if i == node_index: continue
                switch_state(self.buttons[i])
            for i in find_children(node_index):
                switch_state(self.buttons[i])
        # ------ Local helper functions end here -----
        
        master = self.detailframe
        self.clearFrame(master)
        
        self.slscLabel = ttk.Label(master, text = 'Scheme\t: '+self.currentScheme.get())
        self.slmoLabel = ttk.Label(master, text = 'Mode\t: '+self.currentMode.get())
        
        labelselectCanvas = Canvas(master, width = 200, height = 450, relief = 'flat', bd = 0, highlightthickness = 0, bg = self.bg[self.currentTheme])
        labels = self.getValues(self.classList)
        
        if self.currentScheme.get() == 'Classic': # ensures only ONE label is chosen in Classic
            self.buttons = [ttk.Radiobutton(labelselectCanvas,
                                       text = labels[i],
                                       variable = self.currentClass,
                                       value = labels[i]) for i in range(self.numClasses)]
        else: # allows multiple label choices in non-Classic
            self.labelarr = [IntVar(value = 0) for _ in range(self.numClasses)]
            self.buttons = [ttk.Checkbutton(labelselectCanvas,
                                       text = labels[i],
                                       variable = self.labelarr[i],
                                       onvalue = 1, 
                                       offvalue = 0) for i in range(self.numClasses)]
            
            if self.currentScheme.get() == 'Hierarchical': # shuts down non-root buttons
                for key, item in self.relationGraph.items():
                    if key != 'root':
                        for i in item:
                            self.buttons[i]['state'] = 'disabled'
                            
        for i in range(self.numClasses): # positions the buttons and binds with action functions
            self.buttons[i].configure(command = lambda index = i: processChoice(index))
            labelselectCanvas.create_window((0, i*35), window = self.buttons[i], anchor = NW)
        
        # Scrollbars
        sby = ttk.Scrollbar(master, orient = VERTICAL, command = labelselectCanvas.yview)
        sbx = ttk.Scrollbar(master, orient = HORIZONTAL, command = labelselectCanvas.xview)
        labelselectCanvas.config(xscrollcommand = sbx.set, yscrollcommand = sby.set, scrollregion = labelselectCanvas.bbox('all'))
        
        # Key bindings
        labelselectCanvas.bind('<Button-4>', lambda _: labelselectCanvas.yview_scroll(1, 'units'))
        labelselectCanvas.bind('<Button-5>', lambda _: labelselectCanvas.yview_scroll(-1, 'units'))
        
        # Positioning
        labelselectCanvas.grid(row = 2, column = 0, padx = (20, 10), pady = 10, sticky = (N, E, W, S))
        self.slscLabel.grid(row = 0, column = 0, padx = (20, 10), pady = 10, sticky = W)
        self.slmoLabel.grid(row = 1, column = 0, padx = (20, 10), pady = 10, sticky = W)
        sby.grid(row = 2, column = 1, pady = 20, sticky = (N, S))
        sbx.grid(row = 3, column = 0, padx = 20, sticky = (E, W))
            
    def ConfigFrame(self):
        '''
        Creates configurative buttons to help
        the user configure.
        '''
        master = self.configframe
        
        saveButton = ttk.Button(master, text = 'Save', command = self.save, style = 'AccentButton')
        darkSwitch = ttk.Checkbutton(master, text = 'Switch Mode', style = 'Switch', command = self.switchMode)
        settButton = ttk.Button(master, text = 'Settings', command = self.SettingsFrame)
        
        # Positioning
        saveButton.grid(row = 0, column = 0, padx = 25, pady = 10, sticky = (N, E, W, S))
        darkSwitch.grid(row = 0, column = 1, padx = 25, pady = 10, sticky = (N, E, W, S))
        settButton.grid(row = 1, column = 0, columnspan = 2, padx = 25, pady = 10, sticky = (N, E, W, S))
        
    def SettingsFrame(self):
        '''
        Creates panels that navigate the user to do set-ups for their work.
        '''
        try: self.settings.lift() # ensures not to be called more than ONCE
        except:
            self.settings = Toplevel(self.root, background = self.bg[self.currentTheme])
            self.settings.title('AnoDatum - Settings')
            self.settings.resizable(False, False)
            
            self.modeFrame = ttk.LabelFrame(self.settings, text = 'Mode')
            self.defineFrame = ttk.LabelFrame(self.settings, text = 'Define Labels')
            self.losaFrame = ttk.LabelFrame(self.settings, text = 'Configuration')
            
            # Positioning
            self.modeFrame.grid(row = 0, column = 0, padx = 20, pady = 20, sticky = W)
            self.defineFrame.grid(row = 0, column = 1, padx = 20, pady = 20, rowspan = 3, sticky = W)
            self.losaFrame.grid(row = 2, column = 0, padx = 20, pady = 20, sticky = W)

            self.ModeFrame()
            self.LoadSaveFrame()
            
    def ModeFrame(self):
        '''
        Panel that helps the user choose mode and scheme.
        Currently supports:
        - Bounding Box
        - Landmark
        '''
        master = self.modeFrame
        modeLabel = ttk.Label(master, text = 'Choose Mode :')
        modeBox = ttk.Combobox(master, state = 'readonly', textvariable = self.currentMode, values = self.availModes)
        schemeLabel = ttk.Label(master, text = 'Choose Scheme :')
        schemeBox = ttk.Combobox(master, state = 'readonly', textvariable = self.currentScheme, values = self.availSchemes)
        comoButton = ttk.Button(master, text = 'Set', style = 'AccentButton', command = self.DefineFrame)
        
        modeBox.set(self.availModes[0])
        schemeBox.set(self.availSchemes[0])

        # Positioning
        modeLabel.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = W)
        modeBox.grid(row = 0, column = 1, padx = 20, pady = 10)
        schemeLabel.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = W)
        schemeBox.grid(row = 1, column = 1, padx = 20, pady = 10)
        comoButton.grid(row = 2, column = 0, padx = 20, pady = 10, columnspan = 2, sticky = (N, E, W, S))
        
    def DefineFrame(self):
        '''
        Creates a treeview that helps the user
        add, define/name, remove labels.
        '''
        # ----- Local helper functions down here -----
        def add_node(tree):
            '''
            Adds a new label to the classList and shows in the treeview.
            '''
            self.numClasses += 1 # gives the guy a place
            self.setUpClassList()
            index = self.numClasses-1 # gets the index of last item
            declTree.insert('', END, text = self.classList[index].get())
            
        def add_sibling(tree):
            '''
            Adds a new sibling label of clicked item to the classList and shows in the treeview.
            '''
            self.numClasses += 1 # gives the guy a place
            self.setUpClassList()
            index = self.numClasses - 1 # gets the index of last item in classList
            parent = tree.parent(tree.focus()) # gets the parent of focused item in the tree
            declTree.insert(parent, END, text = str(self.classList[index].get()))
            self.buildGraph(parent, self.relationGraph, tree)
            
        def add_child(tree):
            '''
            Adds a new child label of clicked item to the classList and shows in the treeview.
            '''
            self.numClasses += 1 # gives the guy a place
            self.setUpClassList()
            index = self.numClasses - 1 # gets the index of last item in classList
            parent = tree.focus() # parent is the clicked item
            tree.insert(parent, END, text = str(self.classList[index].get())) # new child is added under clicked item
            self.buildGraph(parent, self.relationGraph, tree)
            
        def delete_node(tree):
            '''
            Deletes a label node from the tree and classList.
            Deleteing a node with children will also delete
            its children. {Implement this!}
            '''
            try: # ensures to take action only when something is selected
                index = int(tree.focus().replace('I',''), 16)-1 # retrives decimal index from hexadecimal return of tree's focus to be used in classList
                parent = tree.parent(tree.focus()) # keeps the parent of focused item for later use
                self.classList.pop(index) # deletes the label and its children from the classList
                tree.delete(tree.focus()) # deletes the item from the tree
                self.numClasses = len(self.classList) # retrives the classList length controller
                self.buildGraph(parent, self.relationGraph, tree) # uses the parent here
            except: pass
            
        def edit(tree):
            '''
            Creates a Toplevel and allow the user rename the label they clicked.
            + Press Enter to finish +
            '''
            try: clicked_index = int(tree.focus().replace('I',''), 16) - 1
            except: return
            temp = Toplevel(self.root, background = self.bg[self.currentTheme])
            temp.title('Edit Label Name')
            temp.resizable(False, False)
            
            temp_entry = ttk.Entry(temp, textvariable = self.classList[clicked_index])
            # replaces the label corresponding to the item in treeview is currently on focus with vale of entry
            change = lambda: tree.item(tree.focus(), text = self.classList[clicked_index].get())
            commands = [change, temp.destroy]
            conf_button = ttk.Button(temp, text = 'Confirm', command = self.commit(commands))
            
            temp_entry.bind('<Return>', lambda _: self.commit(commands)())
            
            # Positioning
            temp_entry.grid(row = 0, column = 0, padx = 20, pady = (20, 10))
            conf_button.grid(row = 1, column = 0, padx = 20, pady = (10, 20), sticky = (N, E, W, S))
            
        def index_to_item(index):
            '''
            Converts integer indices into
            hex string indices used by treeview.
            '''
            num = hex(index+1).replace('0x', '').upper()
            return 'I'+'0'*(3-len(num))+num
        # ----- Local helper functions ends here -----
        
        master = self.defineFrame
        self.clearFrame(master)
        
        declTree = ttk.Treeview(master, selectmode = 'browse', height = 8)   
        declTree.column('#0', width = 300, stretch = False)
        declTree.heading('#0', text = 'Labels')
            
        # tries to build treeview from the classList if exists
        if self.currentScheme.get() in ['Classic', 'Extended']:
            for item in self.getValues(self.classList):
                declTree.insert('', END, text = item)
            labelButton = ttk.Button(master, text = 'Add Label', command = lambda : add_node(declTree))
        else:
            self.buildGraph('', self.relationGraph, declTree)
            for key, indices in self.relationGraph.items():
                if key == 'root': key = ''
                else: key = index_to_item(int(key))
                for index in indices:
                    declTree.insert(key, index, text = self.classList[index].get())
            siblingButton = ttk.Button(master, text = 'Add Sibling', command = lambda : add_sibling(declTree))
            childButton = ttk.Button(master, text = 'Add Child', command = lambda : add_child(declTree))
        
        deleteButton = ttk.Button(master, text = 'Delete', command = lambda : delete_node(declTree))
        
        # Scrollbars
        sby = ttk.Scrollbar(master, orient = VERTICAL, command=declTree.yview)
        sbx = ttk.Scrollbar(master, orient = HORIZONTAL, command=declTree.xview)
        
        declTree.config(xscrollcommand = sbx.set, yscrollcommand = sby.set)
                    
        # Positioning
        declTree.grid(row = 0, column = 0, columnspan = 3, padx = (20, 0), pady = 10, sticky = (N, E, W, S))
        if self.currentScheme.get() in ['Classic', 'Extended']:
            labelButton.grid(row = 2, column = 1, padx = 10, pady = (10, 20))
        else:
            siblingButton.grid(row = 2, column = 0, padx = (20, 10), pady = (10, 20))
            childButton.grid(row = 2, column = 1, padx = 10, pady = (10, 20))
        deleteButton.grid(row = 2, column = 2, padx = (10, 20), pady = (10, 20))
        sby.grid(row=0, column=3, padx = 10, pady = 20, sticky = 'ns')
        sbx.grid(row=1, column=0, columnspan = 3, padx = 20, sticky = 'ew')
        
        # Key bindings
        declTree.bind('<Double-1>', lambda _: edit(declTree))

    def LoadSaveFrame(self):
        '''
        Creates buttons to help load/submit existing settings.
        '''
        master = self.losaFrame
        loadButton = ttk.Button(master, text = 'Load Settings', command = self.loadSettings)
        saveCheck = ttk.Checkbutton(master, text = 'Remember settings', variable = self.saveOrNot, onvalue = 1, offvalue = 0)
        commands = [self.setUp, self.settings.destroy]
        confButton = ttk.Button(master, text = 'Confirm', style = 'AccentButton', command = self.commit(commands))
        
        # Positioning
        loadButton.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = (N, E, W, S))
        saveCheck.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = (N, E, W, S))
        confButton.grid(row = 2, column = 0, padx = 20, pady = 10, columnspan = 2, sticky = (N, E, W, S))
    
    def bindCanvas(self):
        '''
        Binds drawing canvas with required key bindings.
        '''
        try: # ensures existence of canvas to be binded
            to_bind = self.canvCanvas
            draw = self.drawDict[self.currentMode.get()]
            to_bind.bind('<Button-1>', draw)
            if self.currentMode.get() == 'Bounding Box':
                to_bind.bind('<Motion>', draw)
                to_bind.bind('<Control-1>', draw)
                to_bind.bind('<ButtonRelease-1>', draw)
            elif self.currentMode.get() == 'Landmark':
                to_bind.bind('<Button-3>', draw)
            self.root.bind_all('<Control-z>', self.undo)
        except: pass
        
    def buildGraph(self, node, placeholder, tree):
        '''
        Builds a relational graph from the tree.
        Recursively called but the graph is LINEAR.
        '''
        try: index = str(int(node.replace('I',''), 16) - 1) # checks if node passed is root or not
        except: index = 'root'
        literal_classList = self.getValues(self.classList)
        children = tree.get_children(node) # gets children of node
        if children != (): # if there are any children
            placeholder[index] = [] # gives the node's family a place in graph
            for child in children: # for each child of node
                placeholder[index].append(literal_classList.index(tree.item(child)['text'])) # they goes into the node's family
                self.buildGraph(child, placeholder, tree) # goes find thier children again

    def clearFrame(self, frame):
        '''
        Clears the frame by destroying its children.
        '''
        for wid in frame.winfo_children():
            wid.destroy()
    
    def clearLog(self, pointer):
        '''
        Clears the log (pointer) by deleting every line.
        '''
        pointer.configure(state = 'normal')
        pointer.delete('1.0', END)
        pointer.configure(state = 'disabled')

    def commit(self, commands):
        '''
        Runs each function pointer in the commands list.
        '''
        return lambda: [func() for func in commands]
        
    def chooseDirectory(self):
        '''
        Let the user choose a directory to work.
        '''
        self.directoryPath.set(filedialog.askdirectory())
        self.sldiLabel.config(text = self.directoryPath.get().split('/')[-1])
        
    def currentFile(self):
        '''
        Gets current file.
        '''
        try: return self.directoryList()[self.fileIndex] # ensures to avoid IndexError
        except: return None

    def directoryList(self):
        '''
        Gets the directory as a list.
        '''
        # ensures correct directory path.
        try: return [filename for filename in os.listdir(self.directoryPath.get()) if self.isImage(filename)]
        except FileNotFoundError: return None
        
    def drawBB(self, event):
        '''
        Instantiate Box class and draw bounding boxes
        in accordance to mouse event.
        + Left click to create a raw box. +
        + Hover to adjust. +
        + Left click again to finalise the box. +
        + Press Ctrl while hovering to force shape square. +
        '''
        try: # ensures a label is selected
            color = self.colorDict[self.currentClass.get()]
            master = self.canvCanvas
        except: return
        if 'ButtonPress' in str(event):
            if event.num == 1: # second click to finalise the box
                if self.clicked:
                    self.clicked = False
                    self.submit()
                else: # first click to create a raw box
                    self.clicked = True
                    self.stuffLog.append(self.Box(master, 
                                                  event.x, event.y, 
                                                  event.x+1, event.y+1, 
                                                  self.currentLabel['text'], color))
        elif 'Motion' in str(event) and self.clicked: # hover to adjust the size
            square = 'Control' in str(event) # press Ctrl to force draw square
            self.stuffLog[-1].update(event.x, event.y, square)
    
    def drawLM(self, event):
        '''
        Instantiate Point class and draw points
        in accordance to mouse click.
        + Left click to mark a point. +
        '''
        try: # ensures a label is selected
            color = self.colorDict[self.currentClass.get()]
            master = self.canvCanvas
            # reterives upperbounds
            max_h = master.bbox('image')[2]
            max_w = master.bbox('image')[3]
        except: return
        # ensures the click event happen only on the image
        if event.x < 0 or event.x > max_w: return
        if event.y < 0 or event.y > max_h: return
        if 'ButtonPress' in str(event):
            if event.num == 1: # left click to create a point
                self.stuffLog.append(self.Point(master, event.x, event.y, self.currentLabel['text'], color))
                self.submit()
            if event.num == 3 or self.currentScheme.get() == 'Classic': # right click to switch to another label automatically
                classId = self.getValues(self.classList).index(self.currentClass.get())
                self.currentClass.set(self.data['labels'][(classId+1)%self.numClasses])
                self.currentLabel.configure(text = self.currentClass.get())
                self.colorPatch.configure(background = self.colorDict[self.currentClass.get()])
    
    def drawSS(self, event):
        pass
    
    def drawPS(self, event):
        pass

    def getValues(self, list_):
        '''
        Returns a value-only list of list of tk variables.
        '''
        return [item.get() for item in list_]
        #except: return []

    def giveColors(self):
        '''
        Assigns hex color codes to each of unique labels.
        (If there are 3 unique labels, 1st label gets hue of 0 degree,
        2nd label gets hue of 120 degree, and 3rd label gets hue of 240 degree.
        Then hue space is mapped to hex space.)
        '''
        one_part = 360//self.numClasses
        degrees = [one_part*i for i in range(self.numClasses)]
        for clas, deg in zip(self.getValues(self.classList), degrees):
            self.colorDict[clas] = self.hue2hex(deg)
            
    def hue2hex(self, degree):
        '''
        Converts hue degrees into hex codes.
        '''
        rgb = colorsys.hsv_to_rgb(degree/360, 1, 1)
        r, g, b = int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def isImage(self, filename):
        '''
        Checks if a file is valid image.
        '''
        extension = filename.split('.')[-1]
        extensions = ['jpg', 'jpeg', 'png']
        return extension in extensions
    
    def loadSettings(self):
        '''
        Loads control variables from valid file containing past settings.
        '''
        settingsPath = filedialog.askopenfilename(filetypes = [('JSON', '.json')])
        try: # ensures settings get loaded correctly
            settingsDict = json.load(open(settingsPath)) # json to dict
            self.currentMode.set(settingsDict['mode'])
            self.currentScheme.set(settingsDict['scheme'])
            self.numClasses = settingsDict['num-labels']
            self.relationGraph = settingsDict['relation-graph']
            self.classList = [StringVar() for _ in range(self.numClasses)]
            for i in range(self.numClasses):
                self.classList[i].set(settingsDict['labels'][i])
        except: # if not, show message
            a = Toplevel(self.settings, background = self.bg[self.currentTheme])
            ttk.Label(a, text = 'Couldn\'t load.', font = (None, 20)).grid(row = 0, column = 0, padx = 20, pady = 20)
            
    def nextFile(self):
        '''
        Increments fileIndex so that self.currentFile can fetch next file.
        '''
        if self.currentFile(): # ensures a directory is selected
            self.fileIndex += 1
            self.slfiLabel.config(text = self.currentFile())
        
    def prevFile(self):
        '''
        Decrements fileIndex so that self.currentFile can fetch previous file.
        '''
        if self.currentFile(): # ensures a directory is selected
            self.fileIndex -= 1
            self.slfiLabel.config(text = self.currentFile())
    
    def save(self):
        '''
        Saves worked data to a file.
        Saved file names are -
        'data(dd)-(mm)-(yyyy)_(hh)-(mm)-(ss).json'
        -by default.
        '''
        try: # ensures data get saved correctly
            string = json.dumps(self.data, sort_keys=True, indent = 4)
            f = open(self.directoryPath.get()+'data{}.json'.format(time.strftime('@%d-%m-%Y_%H-%M-%S')), 'w')
            f.write(string)
            f.close()
        except: # if not, show message
            a = Toplevel(self.root, background = self.bg[self.currentTheme])
            ttk.Label(a, text = 'Couldn\'t save.', font = (None, 20)).grid(row = 0, column = 0, padx = 20, pady = 20)
            
    def saveSettings(self):
        '''
        Saves current settings to a file.
        Saved file names are -
        'settings(dd)-(mm)-(yyyy)_(hh)-(mm)-(ss).json'
        -by default.
        '''
        try: # ensures settings get saved correctly
            settings = {'mode': self.currentMode.get(),
                        'scheme': self.currentScheme.get(),
                        'num-labels': self.numClasses,
                        'labels': self.getValues(self.classList),
                        'relation-graph': self.relationGraph} # constructs settings dict
            string = json.dumps(settings, indent = 4)
            f = open(self.directoryPath.get()+'setting{}.json'.format(time.strftime('@%d-%m-%Y_%H-%M-%S')), 'w')
            f.write(string)
            f.close()
        except: # if not, show message
            a = Toplevel(self.settings, background = self.bg[self.currentTheme])
            msg = ttk.Label(a, text = 'Couldn\'t save', font = (None, 20)).grid(row = 0, column = 0, padx = 20, pady = 20)
    
    def setUp(self):
        '''
        Sets up control vaiables and do actions 
        according to settings.
        '''
        self.giveColors()
        self.data['annotation-type'] = self.currentMode.get()
        self.data['annotation-scheme'] = self.currentScheme.get()
        self.data['labels'] = self.getValues(self.classList)
        self.data['relation-graph'] = self.relationGraph
        self.DetailFrame()
        try: self.bindCanvas()
        except: pass
        if self.saveOrNot.get():
            self.saveSettings()
            
    def setUpClassList(self):
        '''
        Updates classList depending on numClasses.
        '''
        for i in range(self.numClasses):
            try: # if classList has members but not initiated
                if self.classList[i].get() == '':
                    self.classList[i].set('unamed-'+str(i))
            except: # if desired member doesn't exist (i.e. len(classList) < numClasses, and raises IndexError in above block
                self.classList.append(StringVar())
                self.classList[i].set('unamed-'+str(i))
        
    def submit(self):
        '''
        Submits th information of drawn objects when user finalises.
        i.e. label indicator, x centre, y centre, width, height
        '''
        # ---- Local helper functions down here -----
        def prefix():
            '''
            Label indicator must be a readable string when shown in log,
            and a numeric array/list when actually used. The function returns 
            'numeric' and 'string' versions of label indicator.
            '''
            pf = dict()
            if self.currentScheme.get() == 'Classic': # just fetching index from classList is enough in Classic
                pf['numeric'] = [self.data['labels'].index(self.currentClass.get())]
            else: # multiple labels could be used in non-Classic
                pf['numeric'] = self.getValues(self.labelarr)
            pf['string'] = [self.currentLabel['text']]
            return pf
        # ---- Local helper functions end here -----
        
        prefixes = prefix() # reterives label indicator
        to_put = prefixes['numeric'] + self.stuffLog[-1].info() # for actual use
        self.data['annotations'][self.currentFile()].append(to_put)
        to_put = prefixes['string'] + self.stuffLog[-1].info() # for visual in log
        self.updateLog(str(to_put), self.logBox, 'a')
                    
    def switchMode(self):
        '''
        Switches light and dark themes.
        '''
        # ----- Local helper functions down here -----
        def changeBgFg(root):
            '''
            Changes bg and fg of widgets if okay.
            '''
            for _, wid in root.children.items():
                tw = type(wid)
                if tw in [Toplevel, ttk.Frame, ttk.LabelFrame]:
                    try:
                        wid.configure(background = self.bg[self.currentTheme])
                        wid.configure(foreground = self.fg[self.currentTheme])
                    except: pass
                    finally: changeBgFg(wid)
                elif tw in [Text, Canvas, ttk.Combobox]:
                    try: 
                        wid.configure(highlightthickness = 0)
                        wid.configure(background = self.bg[self.currentTheme])
                        wid.configure(foreground = self.fg[self.currentTheme])
                    except: pass
        # ----- Local helper functions end here -----
        
        if self.currentTheme == 'light':
            self.currentTheme = 'dark'
        elif self.currentTheme == 'dark':
            self.currentTheme = 'light'
        self.style.theme_use(self.styleDict[self.currentTheme])
        changeBgFg(self.root)
    
    def undo(self, event):
        '''
        Undoes an unwanted action done on the drawing area.
        i.e. removes last drawn object.
        '''
        try: # ensures at least one object is drawn
            self.stuffLog[-1].destroy() # deletes the object leaving a placeholder in stuffLog
            self.updateLog(str(self.data['annotations'][self.currentFile()][-1]), self.logBox, 'r') # removes its message line from log
            self.stuffLog.pop() # removes its placeholder from collection of objects for current file
            self.data['annotations'][self.currentFile()].pop() # removes from data record
        except: pass
        
    def updateLog(self, string, pointer, mode):
        '''
        Updates content of 'pointer' with 'string'.
        modes: 
        - a : add
        - r : remove
        '''
        pointer.configure(state = 'normal')
        if mode == 'a':
            pointer.insert('1.0', 'added : '+string+'\n')
        if mode == 'r':
            pointer.delete('1.0', '2.0')
        pointer.configure(state = 'disabled')

root = Tk()
app = AnoDatum(root)
root.mainloop()
