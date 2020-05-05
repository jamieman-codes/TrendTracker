#Importing stuff
import tkinter as tk
from tkinter import ttk
from processing import *
import pickle
from datetime import datetime
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
auth = tweepy.OAuthHandler('xuyLXNxuVF2vrQoOGp6HTJaRz', 'st2jaeoTE4nKdBHU5YQAQQaMdDojKkWizw2bZyK4n2XeyEnKBn')
auth.set_access_token('2799784460-HATeAT02qGcgjLb91NNy4wlpzqSDhJzCj2hNHHW', 'Fioy5vc9H0oKS4SzggnlVxql7cfGR6fO2cZavMbMgiffk')
api = tweepy.API(auth)
COUNTRYCODES = pickle.load(open("countryCodes.p", "rb")) #Loads the country codes dictionary from an external pickle file
style.use('ggplot') #Styles the matplotlib graphs to make them look nicer

class TrendTracker(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self) #Create root for tkinter
        tk.Tk.wm_title(self, "Trend Tracker Client")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, TwitterPage, GooglePageLoc, GooglePageTime): #Create the different pages of the program
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage) 

    def show_frame(self, cont):
        '''
        Changes which is currently being shown to the user
        '''
        frame = self.frames[cont]
        frame.tkraise()        

class StartPage(tk.Frame):
    '''
    Homepage of the application
    The user can navigate to the different pages from here
    '''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = ttk.Label(self, text="Trend Tracker", font='Helvetica 12 bold')
        label.grid(row=0,column=0, columnspan = 2)
        button = ttk.Button(self, text="Twitter", command=lambda: controller.show_frame(TwitterPage)) #A lambda has to be used in a ttk Button as otherwise the command will be ran as soon as the frame is loaded
        button.grid(row=1, column = 0)
        button2 = ttk.Button(self, text="Google", command=lambda: controller.show_frame(GooglePageLoc))
        button2.grid(row=1, column = 1)
        
class TwitterPage(tk.Frame):
    '''
    Twitter trends page
    Here the user can choose what location they want to track the twitter key words for
    '''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.label = ttk.Label(self, text="Twitter Trends", font='Helvetica 12 bold')
        self.label.grid(row=1,column=0,padx = 10, columnspan = 2)
        self.button = ttk.Button(self, text="Return", command=lambda: controller.show_frame(StartPage))
        self.button.grid(row=0, column = 0)
        self.label2 = ttk.Label(self, text= "Enter Location:", font = 'Helvetica 10')
        self.label2.grid(row=2, column= 0)
        self.e1 = ttk.Entry(self)
        self.e1.grid(row=2, column = 1)
        self.button2 = ttk.Button(self, text="Create Graph", command = lambda: self.createGraph(self.e1.get()))
        self.button2.grid(row=3, column=0, columnspan = 2)
    
    def checkComplete(self):
        '''
        Checks if the form has been completed correctly
        '''
        if self.e1.get() == '': #Checks if text entry box is empty
            self.createErrorMessage('No location entered')
            return False
        elif getWOEID(self.e1.get()) == False: #If the getWOEID function cannot find the location after 3 attempts the location is named invalid
            self.createErrorMessage('Invalid location entered')
            return False
        return True
    
    def createErrorMessage(self, message):
        '''
        Creates a popup window to tell the user when they have not entered a value into the form
        '''
        errorWindow = tk.Toplevel(self)
        label1 = ttk.Label(errorWindow, text = 'ERROR : ' + message, font = 'Helvetica 10 bold')
        label1.pack()
        button1 = ttk.Button(errorWindow, text = 'Close', command=lambda :errorWindow.destroy())
        button1.pack()
        errorWindow.grab_set()#Freezes the other open windows whilst the error window is open
        self.wait_window(errorWindow) #Pauses the code here until the window is closed
        errorWindow.grab_release() #Unfreezes the other windows    
        
    def createGraph(self, location):
        '''
        Creates the twitter trends graph in a new popout window
        '''
        if self.checkComplete() == True:
                graphWindow = tk.Toplevel(self) #Create a popup window linked to the main window
                graph = TwitterGraph(graphWindow, location) #Creates the graph object
                graph.pack()
         
class GooglePageLoc(tk.Frame):
    '''
    Google Location Trends page
    Here the user chooses a Location and 1 keyword and can then view a graph of the populairty of that keyword within that location
    '''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label4 = None
        self.label = ttk.Label(self, text="Google Trends\nLocation", font='Helvetica 12 bold')
        self.label.grid(row=1,column=0,padx = 10, columnspan = 2)
        self.button = ttk.Button(self, text="Return", command=lambda: controller.show_frame(StartPage))
        self.button.grid(row=0, column = 0)   
        self.button = ttk.Button(self, text="Location", command=lambda: controller.show_frame(GooglePageLoc))
        self.button.grid(row=2, column = 0)
        self.button2 = ttk.Button(self, text="Time", command=lambda: controller.show_frame(GooglePageTime))
        self.button2.grid(row=2, column = 1)
        self.label2 = ttk.Label(self, text= "Choose Location:", font = 'Helvetica 10')
        self.label2.grid(row=3, column = 0)
        self.tkvar = tk.StringVar(self) #TkVars are used to change what is being displayed in a Tk object without having to redefine it 
        self.choices = COUNTRYCODES.keys()
        self.tkvar.set('')
        self.popupMenu = ttk.OptionMenu(self, self.tkvar, *self.choices) #Creates drop down menu
        self.popupMenu.grid(row=3, column = 1)
        self.label3 = ttk.Label(self, text= "Enter Keyword:", font = 'Helvetica 10')
        self.label3.grid(row=4, column = 0)
        self.e2 = ttk.Entry(self)
        self.e2.grid(row=4, column = 1)
        self.button3 = ttk.Button(self, text="Create Graph", command = lambda: self.createGraph(self.e2.get(), COUNTRYCODES[self.tkvar.get()]))
        self.button3.grid(row=5, column=0, columnspan = 2)
    
    def createErrorMessage(self, message):
        '''
        Creates a popup window to tell the user when they have not filled out the form correctly
        '''
        errorWindow = tk.Toplevel(self)
        label1 = ttk.Label(errorWindow, text = 'ERROR : ' + message, font = 'Helvetica 10 bold')
        label1.pack()
        button1 = ttk.Button(errorWindow, text = 'Close', command=lambda :errorWindow.destroy())
        button1.pack()
        errorWindow.grab_set() #Freezes the other open windows whilst the error window is open
        self.wait_window(errorWindow) #Pauses the code here until the window is closed
        errorWindow.grab_release() #Unfreezes the other windows
        
    def createGraph(self, kw, location):
        '''
        Creates the google location trends graph in a new popup window
        '''
        if self.checkValid(kw, location) == True:
            self.e2.delete(0,'end') #Makes the entry form blank
            graphWindow = tk.Toplevel(self)
            graph = GoogleGraphLoc(graphWindow, kw, location)
            graph.pack()
            
    def checkValid(self, kw, location):
        '''
        Checks the users inputs are valid, if they are valid the graph is created
        '''
        if location != 'ERROR': 
            if kw != '':
                return True
            elif kw == '':
                self.createErrorMessage("Keyword not entered") 
                return False
        elif location == 'ERROR':
            self.createErrorMessage("Location not chosen")
            return False

class GooglePageTime(tk.Frame):
    '''
    Google Time Trend page
    User can input a set of keywords, a location, a start date and a end date and then can view a graph of the populairty over time of that keyword set
    '''
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.entries = []
        self.startDate = tk.StringVar(self) #Creating a tkinter string varible which allows the text on a button/label to be easily updated as the program is running
        self.startDate.set('Select Start Date') #Setting the value of the string varible which will be shown first
        self.endDate = tk.StringVar(self)
        self.endDate.set('Select End Date')
        self.dates = ['2004-01-00',''] #Create the default dates, 2004-01-00 must be used as a default date so that the user can select 2004-01-01 as the first possible date
        self.numOfKeywords = 0
        self.keywordDisplay = tk.StringVar(self)
        self.keywordDisplay.set('Current keywords: ')
        self.entryVar = tk.StringVar(self)
        self.label = ttk.Label(self, text="Google Trends\nTime", font='Helvetica 12 bold')
        self.label.grid(row=1,column=0,padx = 10, columnspan = 2)
        self.button = ttk.Button(self, text="Return", command=lambda: controller.show_frame(StartPage))
        self.button.grid(row=0, column = 0)
        self.button = ttk.Button(self, text="Location", command=lambda: controller.show_frame(GooglePageLoc))
        self.button.grid(row=2, column = 0)
        self.button2 = ttk.Button(self, text="Time", command=lambda: controller.show_frame(GooglePageTime))
        self.button2.grid(row=2, column = 1)
        self.label4 = ttk.Label(self, text="Choose Location :", font = 'Helvetica 10')
        self.label4.grid(row=3, column=0)
        self.tkvar = tk.StringVar(self)
        self.choices = COUNTRYCODES.keys() #Collecting the names of the countries
        self.tkvar.set('')
        self.popupMenu = ttk.OptionMenu(self, self.tkvar, *self.choices) #A ttk option menu is a drop down list 
        self.popupMenu.grid(row=3, column = 1)        
        self.label2 = ttk.Label(self, text="Enter keyword:",  font = 'Helvetica 10')
        self.label2.grid(row=4, column= 0)
        self.entry = ttk.Entry(self, textvariable=self.entryVar)
        self.entry.grid(row = 4, column =1)
        self.entry.bind('<Return>', lambda x:self.addToList()) #When the enter key is pressed whilst the entry box is selected the function addToList is ran
        self.label3 = ttk.Label(self, textvariable= self.keywordDisplay, font = 'Helvetica 10')
        self.label3.grid(row=6, column=0, columnspan= 2, sticky = 'w') 
        self.button3 = tk.Button(self, text="X", command= lambda: self.resetString(),height = 1, width = 1)
        self.button3.grid(row=6, column=2)
        self.button3 = ttk.Button(self, textvariable=self.startDate, command = lambda : self.getStartDate())
        self.button3.grid(row=7, column=0)
        self.button4 = ttk.Button(self, textvariable=self.endDate, command = lambda: self.getEndDate())
        self.button4.grid(row=7, column=1)
        self.button5 = ttk.Button(self, text='Create Graph', command = lambda: self.createGraph())#
        self.button5.grid(row=8, column=0, columnspan = 2) 
        
    def checkComplete(self):
        '''
        Checks that the user has filled the form out correctly 
        '''
        if COUNTRYCODES[self.tkvar.get()] == 'ERROR': #The dictionary contains a blank value that links to "ERROR"
            self.createErrorMessage("No location entered")
            return False
        elif self.entries == []:
            self.createErrorMessage("No keywords entered")
            return False
        elif self.dates[0] == '2004-01-00': #Default value for the start date and cannot be chosen
            self.createErrorMessage("No start date entered")
            return False
        elif self.dates[1] == '':
            self.createErrorMessage("No end date entered")
            return False
        else:
            return True
    
    def createErrorMessage(self, message):
        '''
        Creates a popup window to tell the user when they have not entered a value into the form
        '''
        errorWindow = tk.Toplevel(self)
        label1 = ttk.Label(errorWindow, text = 'ERROR : ' + message, font = 'Helvetica 10 bold')
        label1.pack()
        button1 = ttk.Button(errorWindow, text = 'Close', command=lambda :errorWindow.destroy())
        button1.pack()
        errorWindow.grab_set()
        self.wait_window(errorWindow)
        errorWindow.grab_release()
                                  
    def createGraph(self):
        '''
        Create the interest over time graph and then resets the varibles
        '''
        if self.checkComplete() == True:
            tf = self.dates[0] + ' ' + self.dates[1]
            graphWindow = tk.Toplevel()
            graph = GoogleGraphTime(graphWindow, self.entries, COUNTRYCODES[self.tkvar.get()], tf)   
            graph.pack()
            self.resetString()
            self.dates= ['2004-01-00', '']
            self.startDate.set('Select Start Date')
            self.endDate.set('Select End Date')
        
    def getStartDate(self):
        '''
        Creates a popup window that prompts the user to input the starting date for the trends
        '''
        window = tk.Toplevel(self)
        dateApp = DateSelector(window, maxDate=self.dates[1]) #Creates a new DateSelector object 
        dateApp.pack()
        window.grab_set()
        self.wait_window(window)
        window.grab_release()
        self.dates[0] = dateApp.returnData()
        self.startDate.set(self.dates[0])
        
    def getEndDate(self):
        '''
        Creates a popup window that prompts the user to input the ending date for the trends
        '''
        window = tk.Toplevel(self)
        dateApp = DateSelector(window, minDate=self.dates[0])
        dateApp.pack()
        window.grab_set()
        self.wait_window(window) #Freezes the main window until the date has been chosen
        window.grab_release()
        self.dates[1] = dateApp.returnData()
        self.endDate.set(self.dates[1])
        
    def resetString(self):
        '''
        Resets the keyword list when the 'x' button is clicked
        '''
        self.keywordDisplay.set('Current keywords: ')
        self.entries = []
        self.numOfKeywords = 0
        
    def addToList(self):
        '''
        Adds a new keyword into the list and displays it on the GUI
        '''
        if self.entryVar.get() != '':
            self.entries.append(self.entryVar.get())
            self.numOfKeywords += 1
            if self.numOfKeywords == 1: #Checking how many keywords have been entered to make sure the grammar while printing is correct
                self.keywordDisplay.set(self.keywordDisplay.get() + self.entryVar.get())
            else:
                self.keywordDisplay.set(self.keywordDisplay.get() + ', ' + self.entryVar.get())
            self.entry.delete(0,'end') #Empty the entry box
            
class TwitterGraph(tk.Frame):
    '''
    Twitter Graph
    Displays a live graph of the twitter trends in the given location with the ability to view tweets relating to the the trends
    '''
    def __init__(self, master, location):
        tk.Frame.__init__(self, master)
        self.location = location
        plt.cla() #Clears matplotlib frame
        master.wm_title(location)
        self.fig, self.n, self.trendData, self.location, self.numOfTrends, lat, long = trendsGraphTwitLine(self.location)   
        self.n += 1
        self.twitterBox = TwitterBox(self, self.trendData, lat, long)#This had to be made into a seperate class due to issues when packing frame
        self.twitterBox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1) 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self) 
        self.canvas.show() 
        self.tkgraph = self.canvas.get_tk_widget() #Loads the grpah as a tkinter object
        self.tkgraph.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self) #Adds the matplotlib toolbar to the graph
        self.toolbar.pack(side=tk.BOTTOM,expand=1, fill=tk.X)
        self.toolbar.update()
        self.twitterBox.updateBox(self.trendData)
        self.after(60000, self.updateGraph) #After a minute it will run the self.updateGraph command
    
    def updateGraph(self):
        '''
        Updates the graph and Text box
        '''
        self.fig, self.n, self.trendData, self.numOfTrends = updateTwitGraph(self.n, self.trendData, self.location, self.numOfTrends)
        self.tkgraph.destroy()
        self.toolbar.destroy()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.show()
        self.tkgraph = self.canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self) 
        self.toolbar.pack(side=tk.BOTTOM,expand=1, fill=tk.X)
        self.toolbar.update()        
        self.tkgraph.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.n += 1
        self.twitterBox.updateBox(self.trendData)        
        self.after(60000, self.updateGraph)
        
class GoogleGraphLoc(tk.Frame):
    '''
    Google location graph page
    Creates a bar graph of the populairty of 1 keyword in different locations
    '''
    def __init__(self, master, kw, location):
        tk.Frame.__init__(self, master)
        self.helpButton = tk.Button(self, text="?", command=lambda:self.helpBox(), height = 30, width = 1)
        plt.cla()
        master.wm_title(kw)
        self.fig, self.trendData = locationBarGraph(kw, location)
        self.text = tk.Text(self)
        self.scr= tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.scr.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, expand=1)
        self.helpButton.pack(side=tk.RIGHT)
        for trend in self.trendData:
            self.text.insert('insert', trend + ": " + str(self.trendData[trend]) + '\n')
        self.text.config(font = 'Helvetica 10', state = 'disabled')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.show()            
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.pack(side=tk.BOTTOM,expand=1, fill=tk.X)
        self.toolbar.update()
    
    def helpBox(self):
        helpWindow = tk.Toplevel(self)
        helpText = tk.Label(helpWindow, text="See in which location your term was most popular.\nValues are calculated on a scale from 0 to 100, where 100\nis the location with the most popularity as a fraction of total searches in that\nlocation, a value of 50 indicates a location which is half as popular, and a\nvalue of 0 indicates a location where the term was less than 1% as\npopular as the peak.\n\nNote: A higher value means a higher proportion of all queries, not a higher\nabsolute query count. So a tiny country where 80% of the queries are for\n'bananas' will get twice the score of a giant country where only 40% of\nthe queries are for 'bananas'.", font = "Helvetica 10")
        helpText.pack(anchor=tk.W)
        
class GoogleGraphTime(tk.Frame):
    '''
    Google time graph page
    Creates line graphs of the populairty of multiple keywords
    '''
    def __init__(self, master, kw_list, location, tf):  
        tk.Frame.__init__(self, master)
        plt.cla()
        master.wm_title('Google Time Trends Graph')
        self.helpButton = tk.Button(self, text="?", command=lambda:self.helpBox(), height = 30, width = 1)
        self.fig, self.trendData = timeLineGraph(kw_list, location, tf)
        self.text = tk.Text(self)
        self.scr= tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.scr.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, expand=1)
        self.helpButton.pack(side=tk.RIGHT)
        for trend in self.trendData:
            self.text.insert('end', trend + ":\n")
            for time in self.trendData[trend].keys():
                timestr = str(matplotlib.dates.num2date(time))[0:10].replace('1900-', '')
                self.text.insert('end', '\t' + timestr + ': ' + str(self.trendData[trend][time]) + '\n')          
        self.text.config(font = 'Helvetica 10', state = 'disabled')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.show()            
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.pack(side=tk.BOTTOM,expand=1, fill=tk.X)
        self.toolbar.update()    
    
    def helpBox(self):
        helpWindow = tk.Toplevel(self)
        helpText = tk.Label(helpWindow, text="Numbers represent search interest relative to the highest point on the\nchart for the given region and time. A value of 100 is the peak popularity\nfor the term. A value of 50 means that the term is half as popular.\nLikewise a score of 0 means the term was less than 1% as popular as the\npeak.", font = "Helvetica 10")
        helpText.pack(anchor=tk.W)    
        
class TwitterBox(tk.Frame):
    '''
    Used as an object in the TwitterGraph page
    '''
    def __init__(self, master, trendData, lat, long):
        tk.Frame.__init__(self, master)
        self.tweetMode = False
        self.trendData = trendData
        self.selectorMode() 
        self.lat = lat
        self.long = long
        
    def selectorMode(self):
        '''
        Default layout of the widgit
        '''
        self.text = tk.Listbox(self)
        self.scr= tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.button = ttk.Button(self, text = 'Load tweets', command=lambda:self.loadTweets(self.text.get(self.text.curselection()[0]).split(':')[0]))
        self.button.config(width=45, state='disabled')
        self.text.config(font = 'Helvetica 10',width=40)
        self.text.bind("<Button-1>", lambda x:self.button.config(state='normal')) #The button is disabled by default so the user cant run the loadTweets function with nothing selected, as soon as something is selected the button is enabled 
        self.scr.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.TOP,fill = tk.BOTH,expand=1)
        self.button.pack(side=tk.RIGHT)

    def updateBox(self, trendData):
        '''
        Update text in the text box 
        '''
        self.trendData = trendData
        if not self.tweetMode: #Whilst the widgit is displaying tweets it cannot be updated
            self.text.delete(0, 'end')
            for trend in trendData:
                self.text.insert('end', str(trendData[trend][2]) + ': ' + trend + ' - ' + str(trendData[trend][0][-1]) + '\n')

    def loadTweets(self, selection):
        '''
        Changes layout of widgit and loads tweets to display
        '''
        self.tweetMode = True
        self.button.destroy()
        self.text.destroy()
        self.text = tk.Text(self)
        self.button = ttk.Button(self, text = 'Back', command = lambda: self.resetWidgit())
        self.text.config(font = 'Helvetica 10',width=40)
        self.scr.config(command=self.text.yview)
        self.button.config(width=45)
        self.text.pack(side=tk.TOP,fill = tk.BOTH,expand=1)
        self.button.pack(side=tk.RIGHT)
        for trend in self.trendData:
            if self.trendData[trend][2] == int(selection):
                selectedTrend = trend
        loc= str(self.lat)+','+str(self.long)+',10mi' #Displays all tweets within 10 miles of the orginal given location
        search = api.search(selectedTrend, geocode = loc) #Searches using the tweepy api
        for result in search:
            if result.text[0:2] != 'RT': #If the tweet is a retweet it is not displayed
                char_list = [result.text[j] for j in range(len(result.text)) if ord(result.text[j]) in range(65536)] #Removes extra characters that tkinter cant display eg emoji
                tweet = ''.join(char_list)            
                self.text.insert('insert',result.user.name + ':\n')
                self.text.insert('insert',tweet + '\n\n')  
        self.text.config(state='disabled')
        
    def resetWidgit(self):
        '''
        Resets widgit to orginal layout so trend data can be displayed
        '''
        self.button.destroy()
        self.text.destroy()
        self.scr.destroy()
        self.tweetMode = False
        self.selectorMode()
        self.updateBox(self.trendData)
        
        
        
class DateSelector(tk.Frame):
    '''
    Allows the user to select a date within certain given boundaries 
    '''
    def __init__(self, master, minDate = '2004-01-00', maxDate  =''): 
        tk.Frame.__init__(self, master)                                  
        master.wm_title("Date Selector")                              
        self.monthsDay = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
        self.dayVar = tk.IntVar(self)
        self.dayVar.set(1)
        self.monthVar = tk.IntVar(self)
        self.monthVar.set(1)
        self.yearVar = tk.IntVar(self)      
        if maxDate == '':
            self.now = datetime.now() #Setting time varibles
            self.maxYear = self.now.year
            self.maxMonth = self.now.month
            self.maxDay = self.now.day
        else:
            self.maxYear, self.maxMonth, self.maxDay = self.dateSplitter(maxDate)
            if self.maxDay == 1:
                if self.maxMonth == 1:
                    self.maxYear -= 1
                    self.maxMonth = 12
                    self.maxDay = 31
                else:   
                    self.maxMonth -= 1
                    self.maxDay = self.monthsDay[self.maxMonth]
            else:
                self.maxDay -= 1
        self.minYear, self.minMonth, self.minDay = self.dateSplitter(minDate)
        if self.minDay == self.monthsDay[self.minMonth]:
            if self.minMonth == 12:
                self.minMonth += 1
                self.minMonth = 1
                self.minDay = 1
            else:
                self.minMonth += 1
                self.minDay = 1
        else:
            self.minDay += 1
        self.label1 = ttk.Label(self, text = 'Year', font = 'Helvetica 10')
        self.label1.grid(row=0,column=2)
        self.yearVar.set(self.maxYear)
        self.yearOptions = ttk.OptionMenu(self, self.yearVar, self.maxYear, *[year for year in range(self.maxYear, self.minYear-1, -1)], command = self.optupdate) 
        self.yearOptions.grid(row=1, column=2)
        self.label2 = ttk.Label(self, text = 'Month', font = 'Helvetica 10')
        self.label2.grid(row=0,column=1)
        if self.minYear == self.maxYear:
            self.monthVar.set(self.minMonth)
            if self.minMonth == self.maxMonth:
                self.dayVar.set(self.minDay)
        self.monthsOptions = ttk.OptionMenu(self, self.monthVar, self.maxMonth, *[x for x in range(self.monthVar.get(), self.maxMonth + 1)], command = self.optupdate)
        self.monthsOptions.grid(row=1, column=1)
        self.label3 = ttk.Label(self, text = 'Day', font = 'Helvetica 10')
        self.label3.grid(row=0, column=0)
        self.dayOptions = ttk.OptionMenu(self, self.dayVar, self.maxDay,*[x for x in range(self.dayVar.get(),self.maxDay+1)])
        self.dayOptions.grid(row=1,column=0)
        self.button = ttk.Button(self, text='Select', command = lambda:self.master.destroy())
        self.button.grid(row=2, column = 1)
    
    def dateSplitter(self, dateStr):
        '''
        Used to split a date into a list
        '''
        dateStr += '-'
        values = []
        temp = ''
        for x in dateStr:
            if x == '-':
                values.append(int(temp))
                temp = ''
            else:
                temp += x
        return values
        
    
    def returnData(self):
        '''
        Returns the date in a string formate
        '''
        return str(self.yearVar.get()) + '-' + str(self.monthVar.get()) + '-' + str(self.dayVar.get())
    
    def optupdate(self, value):
        '''
        When a dropdown box is selected the other boxes need to be updated so that a invalid date cant be chosen
        This function changes the boxes that that a date that is outside of the min/max dates arent selected and a date that doesnt exist isnt selected
        '''
        ly = 0
        if self.isLeapYear(self.yearVar.get()) == True and self.monthVar.get() == 2:
            ly = 1        
        tempMinMonth = 1
        tempMaxMonth = 12
        tempMinDays = 1
        tempMaxDays = self.monthsDay[self.monthVar.get()] + ly     
        if self.minYear == self.maxYear:
            if not(self.minMonth < self.monthVar.get() < self.maxMonth):
                self.monthVar.set(self.minMonth)
            tempMinMonth, tempMaxMonth = self.minMonth, self.maxMonth    
            if self.minMonth == self.maxMonth:
                tempMinDays, tempMaxDays = self.minDay, self.maxDay
                if not(self.minDay < self.dayVar.get() < self.maxDay):
                    self.dayVar.set(self.minDay)
            elif self.monthVar.get() == self.minMonth:
                tempMinDays = self.minDay
                if self.dayVar.get() < self.maxDay:
                    self.dayVar.set(self.minDay)
            elif self.monthVar.get() == self.maxMonth:
                tempMaxDays = self.maxDay
                if self.dayVar.get() > self.maxDay:
                    self.dayVar.set(self.maxDay)                
        elif self.yearVar.get() == self.maxYear:
            if self.monthVar.get() > self.maxMonth:
                self.monthVar.set(self.maxMonth)
            tempMaxMonth = self.maxMonth
            if self.monthVar.get() == self.maxMonth:
                tempMaxDays = self.maxDay
                if self.dayVar.get() > self.maxDay:
                    self.dayVar.set(self.maxDay)
        elif self.yearVar.get() == self.minYear:
            if self.monthVar.get() < self.minMonth:
                self.monthVar.set(self.minMonth)
            tempMinMonth = self.minMonth
            if self.monthVar.get() == self.minMonth:
                tempMinDays = self.minDay
                if self.dayVar.get() < self.maxDay:
                    self.dayVar.set(self.minDay)
        self.monthsOptions = ttk.OptionMenu(self, self.monthVar, self.monthVar.get(), *[x for x in range(tempMinMonth, tempMaxMonth+1)], command = self.optupdate)#Update the dropdown boxes
        self.monthsOptions.grid(row=1, column=1)
        self.dayOptions = ttk.OptionMenu(self, self.dayVar,self.dayVar.get(), *[x for x in range(tempMinDays,tempMaxDays+1)])
        self.dayOptions.grid(row=1,column=0)       
            
    def isLeapYear(self, year):
        '''
        Checks if the current year is a leapyear
        '''
        if ((year % 4 == 0 and (year % 100 != 0))) or (year % 400 == 0):
            return True
        return False
    
if __name__ == '__main__':
    app = TrendTracker()    
    app.mainloop()