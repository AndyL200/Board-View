import PyQt6.QtWidgets as Qtw
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as Qtc
import PyQt6.QtMultimedia as Qtmedia
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtQml import QQmlApplicationEngine
from scrape import Scraper

import json
import os
import shutil
import requests
import threading
from functools import partial
# from io import BytesIO



app = Qtw.QApplication([])


class AtomicInteger:
    def __init__(self, initial=0):
        self.value = initial
        self.lock = threading.Lock()
    def increment(self):
        with self.lock:
            self.value+=1

    def decrement(self):
        with self.lock:
            self.value-=1

    def set(self, val):
        with self.lock:
            self.value = val
            

    def get(self):
        with self.lock:
            return self.value
        


class MainWindow(Qtw.QMainWindow):

    settings_file = os.path.join('origin', 'settings.json')
    with open(settings_file, 'r') as file:
        settings_dict = json.load(file)
        searchList = settings_dict["searchList"]
        colorTheme = settings_dict["colorTheme"]
        colorOptions = settings_dict["colorOptions"]
        auto_scroll = settings_dict["auto_scroll"]
        backgroundTheme = settings_dict["backgroundTheme"]
        originalSizedImages = settings_dict["originalSize"]
        nsfw = settings_dict["NSFW"]
        tool_tips = settings_dict["tool_tips"]

    def __init__(self):
        super().__init__()


        self.monolist = self.searchList
        self.styles = {}
        self.setStyleSheet("font-family: helvetica;")
        self.setWindowTitle("Board View")
        self.setWindowIcon(QtGui.QIcon(os.path.join('origin', 'assets', 'pencil.png')))
        self.setGeometry(100, 100, 800, 600)
        
        try:
            requests.get(self.backgroundTheme)
            is_url = True
        except:
            is_url = False

        if is_url:
            self.styles["background-image"] = "background-image: url(" + str(self.backgroundTheme) + ");"
            
        elif '#' in self.backgroundTheme:
            self.styles["background-color"] =  "background-color:" + str(self.backgroundTheme) + ";"

        else:
            self.styles["background-image"] = ""
            self.styles["background-color"] = ""
        
        if self.nsfw[0]:
            self.monolist = {**self.monolist, **self.nsfw[1]}

        for k in self.styles:
            self.updateStyleSheet(self.styles[k])

        self.showFrame("StartPage")
       
    def isLight(self, color):
        hex_string = color[1:]
        if int(hex_string, 16) > 8388607:
            return True
        else:
            return False
        
    def reloadStyles(self):
        settings_file = os.path.join('origin', 'settings.json')
        with open(settings_file, 'r') as file:
            settings_dict = json.load(file)
            self.colorTheme = settings_dict["colorTheme"]
            self.colorOptions = settings_dict["colorOptions"]
            self.auto_scroll = settings_dict["auto_scroll"]
            self.backgroundTheme = settings_dict["backgroundTheme"]
            self.originalSizedImages = settings_dict["originalSize"]
            self.tool_tips = settings_dict["tool_tips"]

        if "https://" in self.backgroundTheme:
            self.styles["background-image"] = "background-image: url(" + str(self.backgroundTheme) + ");"
            
        elif '#' in self.backgroundTheme:
            self.styles["background-color"] =  "background-color:" + str(self.backgroundTheme) + ";"

        else:
            self.styles["background-image"] = ""
            self.styles["background-color"] = ""

        if self.nsfw[0]:
            self.monolist = {**self.monolist, **self.nsfw[1]}
        elif not self.nsfw[0]:
            for key in self.nsfw[1].keys():
                if key in self.monolist:
                    del self.monolist[key]

        notify_change_event = monolistChange(self.monolist)
        app.postEvent(self, notify_change_event)
        

        self.setStyleSheet("font-family: helvetica;")
        for k in self.styles:
            self.updateStyleSheet(self.styles[k])

        


    def showFrame(self, page_name, whatToShow=""):
        
        frame = Qtw.QFrame()
        if page_name == "StartPage":
            frame = StartPage(self)
           
        elif page_name == "SearchPage":
            frame = SearchPage(self)
            frame.whatToPull(whatToShow)
        elif page_name == "TopPage":
            frame = TopPage(self)
            frame.whatToPull(whatToShow)
        elif page_name == "Saves":
            frame = Saves(self)
            
        if self.layout().widget():
            self.layout().widget().setParent(None) #keep an eye on this
        self.layout().addWidget(frame)
        self.setCentralWidget(frame)
 
    def updateStyleSheet(self, new_style):
        current = self.styleSheet()

        if new_style not in current:
            combined_sheet = current + new_style
            self.setStyleSheet(combined_sheet)

class StartPage(Qtw.QFrame):
    def __init__(self, master):
        super().__init__()
                                                                                                                    #Page with start screen and buttons to the other pages
        self.master = master
        self.setStyleSheet("")
        self.installEventFilter(self)

       

        v_lay = Qtw.QVBoxLayout(self) #Vertical box layout

        my_label = Qtw.QLabel("Board View")

        my_label.setFont(QtGui.QFont("Helvetica", 18))
        my_label.setAlignment(Qtc.Qt.AlignmentFlag.AlignHCenter)

        v_lay.addWidget(my_label)
                                                                                                                        #selectible site list combobox
        self.my_combo = Qtw.QComboBox(self)
        self.my_combo.insertItems(0, self.master.monolist.keys())
        v_lay.addWidget(self.my_combo)
        h_lay = Qtw.QHBoxLayout()
        v_lay.addLayout(h_lay)

                                                                                                                        #Primary Page Navigation Buttons
        start_btn = Qtw.QPushButton("Search")
        if self.master.colorTheme:
            start_btn.setStyleSheet("border: 1px solid " + self.master.colorTheme + ";")
        start_btn.clicked.connect(lambda: master.showFrame("SearchPage", self.master.monolist[self.my_combo.currentText()]))
        top_btn = Qtw.QPushButton("Top")
        if self.master.colorTheme:
            top_btn.setStyleSheet("border: 1px solid " + self.master.colorTheme + ";")
        top_btn.clicked.connect(lambda: master.showFrame("TopPage", self.master.monolist[self.my_combo.currentText()]))
        saves_btn = Qtw.QPushButton("Saves")
        if self.master.colorTheme:
            saves_btn.setStyleSheet("border: 1px solid " + self.master.colorTheme + ";")
        saves_btn.clicked.connect(lambda: master.showFrame("Saves", self.master.monolist[self.my_combo.currentText()]))

        settings_tab = Settings(self.master)
        settings_btn = Qtw.QPushButton("Settings")
        if self.master.colorTheme:
            settings_btn.setStyleSheet("border: 1px solid " + self.master.colorTheme + ";")
        settings_btn.clicked.connect(settings_tab.show) 

        h_lay.addWidget(start_btn)
        h_lay.addWidget(top_btn)
        h_lay.addWidget(saves_btn)
        h_lay.addWidget(settings_btn)



        # self.layout().addWidget(self.container)
    def updateCombo(self):
        self.my_combo.clear()
        self.my_combo.insertItems(0, self.master.monolist.keys())

    def eventFilter(self, source, event):
        if event.type() == monolistChange.TYPE:
            self.updateCombo()
            return True
        return super().eventFilter(source, event)
    
class monolistChange(Qtc.QEvent):
    TYPE = Qtc.QEvent.Type(Qtc.QEvent.registerEventType())
    def __init__(self, new_monolist):
        super().__init__(self.TYPE)
        self.new_monolist = new_monolist
        
    

class SearchPage(Qtw.QFrame):
    comp = ""
    scraper = None
    def __init__(self, master):
        super().__init__()
        self.setSizePolicy(Qtw.QSizePolicy.Policy.Expanding, Qtw.QSizePolicy.Policy.Expanding)
        
        self.gifThread = Qtc.QThread()



        self.master = master
        self.vidInt = AtomicInteger()
        
                                                                                                                        #atomic integer for image loading
        self.loading = AtomicInteger()
                                                
        
                                                                                                                        #making a container for the images on the page
        self.imgContain = Qtw.QWidget()
        self.scr = Qtw.QScrollArea()
        self.scr.setWidgetResizable(True)
                                                                                                                        #thread for image loading
        self.t = Qtc.QThread()
        
            
        


        self.scr.setWidget(self.imgContain)

        self.scr.verticalScrollBar().valueChanged.connect(self.checkScroll)
       
        self.vbox = AtomicClockVLayout(self.imgContain)
        self.vbox.setAlignment(Qtc.Qt.AlignmentFlag.AlignHCenter)
        





        if self.master.auto_scroll:
            
            self.autoScrollTimer = Qtc.QTimer()
            self.autoScrollTimer.setInterval(100)
            self.autoScrollTimer.setSingleShot(False)
            self.autoScrollTimer.timeout.connect(self.auto_scr)
            self.auto_scr()

        self.mainLayout = Qtw.QVBoxLayout(self)

                                                                                                                        #Bottom Page Navigation
        self.bottomWidget = Qtw.QWidget()
        self.hbox = Qtw.QHBoxLayout()
        back_btn = Qtw.QPushButton(text="Back")
        if self.master.tool_tips:
            back_btn.setToolTip("Go Back to Home Page")
        back_btn.setStyleSheet("""
                            float:left;
                               """)
        back_btn.clicked.connect(lambda: self.switchBack())
        back_layout = Qtw.QHBoxLayout()
        back_layout.addWidget(back_btn)

                                                                                                                        #tag search thread
        self.bottomNavThread = Qtc.QThread()
        self.findingTags = AtomicInteger()


                                                                                                                        #Input Group
        input_group = Qtw.QVBoxLayout()

        self.tag_input = Qtw.QLineEdit()
        if self.master.tool_tips:
            self.tag_input.setToolTip("Search for tags here. Type as many as you want and press return on the keyboard")

        grid_possible = Qtw.QGridLayout()
        
        
        self.poss_widget = Qtw.QWidget()
        self.poss_widget.setLayout(grid_possible)
        if self.master.tool_tips:
            self.poss_widget.setToolTip("Tags here will be searched on when the enter button is pressed")

        self.grid_scroll = Qtw.QScrollArea()
        self.grid_scroll.setWidget(self.poss_widget)
        
        self.grid_scroll.setWidgetResizable(True)
       
        # grid_scroll.setMinimumHeight(tag_input.height())
        # grid_scroll.setMinimumWidth(tag_input.width())
        self.grid_scroll.hide()

        input_group.addWidget(self.tag_input)
        # tag_lay.setStretch(0,3)
        # tag_lay.setStretch(1,1)

        
        input_group.addWidget(self.grid_scroll)
      

       #change to a custom listener
        # cust_input_event = Qtc.QEvent()

        

        


        self.tag_input.textEdited.connect(self.tagFinderTimer)


                                                                                                                        #Enter Group
        enter_group = Qtw.QVBoxLayout()

        mod_plus_enter = Qtw.QHBoxLayout()

        ratingCombo = Qtw.QComboBox()
        ratingCombo.setPlaceholderText("rating")
        ratingCombo.addItems(["rating", "rating:general", "rating:safe","rating:explicit", "rating:questionable"])
        scoreCombo = Qtw.QComboBox()
        scoreCombo.setPlaceholderText("score")
        scoreCombo.addItems(["score", "score:>=50", "score:>=100", "score:>=250", "score:>=500", "score:>=1000"])

        tag_btn = Qtw.QPushButton(text="Enter")
        if self.master.tool_tips:
            tag_btn.setToolTip("Search on input tags or other restrictions")
            ratingCombo.setToolTip("Specificy a rating level for the images presented")
            scoreCombo.setToolTip("Restrict images by score")

        mod_plus_enter.addWidget(ratingCombo)
        mod_plus_enter.addWidget(scoreCombo)
        mod_plus_enter.addWidget(tag_btn)


        loaded_grid = Qtw.QGridLayout()

        self.col = 0
        self.row = 0
        self.colCount = 6
        self.gridPush = []

        enter_group.addLayout(mod_plus_enter)
        enter_group.addLayout(loaded_grid)



        self.hbox.addLayout(back_layout)
        self.hbox.addLayout(input_group)
        self.hbox.addLayout(enter_group)

        self.bottomWidget.setLayout(self.hbox)
        

        back_layout.setAlignment(Qtc.Qt.AlignmentFlag.AlignTop)
        input_group.setAlignment(Qtc.Qt.AlignmentFlag.AlignTop)
        enter_group.setAlignment(Qtc.Qt.AlignmentFlag.AlignTop)

        

        self.tag_input.returnPressed.connect(lambda:self.insertIcon(self.tag_input, loaded_grid))
        tag_btn.clicked.connect(lambda: self.tagSearch(loaded_grid, ratingCombo, scoreCombo))
       

        

        self.imageViewer = ImageViewer(self, self.master.originalSizedImages)
        self.imageIndex = 0
        
        # tagComboScroll.setStyleSheet("""
        #                             background-color:white;
        #                             """)        


        



        # self.mainLayout.addWidget(self.hbox)
        print("Main GUI Thread: " + str(threading.get_ident()))                                         #Main GUI Thread Check

        self.mainLayout.addWidget(self.scr)
        self.mainLayout.addWidget(self.bottomWidget)

        self.mainLayout.setStretch(0, 10)
        self.mainLayout.setStretch(1,1)


        self.setLayout(self.mainLayout)
        self.installEventFilter(self)



    def auto_scr(self):
        scroll_bar = self.scr.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.value()+5)
        self.autoScrollTimer.start()

    def tagFinderTimer(self):
        self.timer = Qtc.QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.openBottomNavThread(self.tag_input))

        self.timer.start()


    @Qtc.pyqtSlot(bool, name="hideShow")
    def gridScrollVisibility(self, bool):
        if bool:
            self.grid_scroll.show()
        else:
            self.grid_scroll.hide()

    def switchBack(self):
        self.loading.set(1)
        self.findingTags.set(1)
        self.t.quit()
        self.bottomNavThread.quit()
        self.t.wait()
        self.bottomNavThread.wait()
        self.mainLayout.deleteLater()                                                                                   #self layout delete later + back button functionality
        self.master.showFrame("StartPage")
        

    def openBottomNavThread(self, tag_input):
        if self.bottomNavThread.isRunning():
            self.findingTags.set(1)
            self.bottomNavThread.quit()
            self.bottomNavThread.wait()

        self.bottomNavThread = Qtc.QThread()
        bwork = BottomWorker(self.scraper)
        bwork.progress.connect(self.bottomNavWork)
        bwork.show.connect(self.gridScrollVisibility)
        bwork.finished.connect(self.bottomNavThread.quit)
        bwork.finished.connect(bwork.deleteLater)
        bwork.moveToThread(self.bottomNavThread)

        self.bottomNavThread.started.connect(partial(bwork.run, self.findingTags, tag_input.text().split(' ')))

        self.findingTags.set(0)
        self.bottomNavThread.start()

    @Qtc.pyqtSlot(list, list,  name="bottom")
    def bottomNavWork(self, names, counts):
        self.grid_scroll.setMaximumHeight(self.tag_input.height()*3)
        self.grid_scroll.setMaximumWidth(self.tag_input.width())

        grid = Qtw.QGridLayout()
        col = 0
        row = 0
        colCount = 2
        for i in range(len(names)):
            j=i
            h_rows = Qtw.QHBoxLayout()
            name_btn = Qtw.QPushButton(text=names[i])
            name_btn.clicked.connect(partial(self.insertText, self.tag_input, names[i], self.grid_scroll))
            if self.master.colorTheme:
                if self.isLight(self.master.colorTheme):
                    name_btn.setStyleSheet(f"border-radius: 40%;font-weight: bold; background-color:{self.master.colorTheme}; color: black")
                else:
                    name_btn.setStyleSheet(f"border-radius: 40%;font-weight: bold; background-color:{self.master.colorTheme}; color: white")

            else:
                name_btn.setStyleSheet(f"border-radius: 40%;font-weight: bold; background-color:#5C9BED;")

            h_rows.addWidget(name_btn)
            if j < len(counts):
                count_label = Qtw.QLabel(text=str(counts[j]))
                if self.master.colorTheme:
                    reverse = self.reverseColor(self.master.colorTheme)
                    if self.isLight(reverse):
                        count_label.setStyleSheet(f"background-color:{reverse}; color: black;font-weight: bold;")
                    else:
                        count_label.setStyleSheet(f"background-color:{reverse}; color: white;font-weight: bold;")

                else:
                    count_label.setStyleSheet(f"background-color:#5CEDE3;font-weight: bold;")

                h_rows.addWidget(count_label)

            grid.addLayout(h_rows, row, col)
            col+=1
            if col >= colCount:
                col = 0
                row+=1

        self.poss_widget = Qtw.QWidget()
        self.grid_scroll.setWidget(self.poss_widget)
        self.poss_widget.setLayout(grid)

          
    def isLight(self, color):
        hex_string = color[1:]
        if int(hex_string, 16) > 8388607:
            return True
        else:
            return False
    def reverseColor(self, color):
        hex_string = color
        sub1 = hex_string[1] + hex_string[2]
        sub2 = hex_string[3] + hex_string[4]
        sub3 = hex_string[5] + hex_string[6]
        red = int(sub1, 16)
        green = int(sub3, 16)
        blue = int(sub2, 16)
        counter_part = "#" + str(255-red) + str(255-green) + str(255-blue)
        return counter_part
        

    def insertText(self, inp, text, scroll):
        input_string = inp.text().split(' ')
        new_input = ""
        for i in range(len(input_string)-1):
            new_input += input_string[i] + ' '
        new_input += text
        inp.setText(new_input)
        scroll.hide()
    def removeIcon(self, grid):
        button = self.sender()
        grid.removeWidget(button)
        self.gridPush.remove(button)
        button.deleteLater()
        self.restructureGrid(grid)

    def restructureGrid(self, grid):
        for i in reversed(range(grid.count())):
            grid.itemAt(i).widget().setParent(None)
        
        self.col = 0
        self.row = 0
        for w in self.gridPush:
            grid.addWidget(w, self.row, self.col)
            self.col+=1
            if self.col == self.colCount:
                self.col = 0
                self.row +=1
        

    def clearWidget(self):
      
        if self.t and self.t.isRunning():
            self.worker.stop = True
            self.t.quit()
            self.t.wait()

        self.loading.set(1)
        i = self.vbox.atom_count.get()
        while i >= 0:
            try:
                item = self.vbox.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()
            except:
                i-=1
                continue
            i-=1
        self.vbox.atom_count.set(0)
        self.imageIndex = 0
            
        
        # self.vbox.setParent(None)
        # v = Qtw.QVBoxLayout()
        # v.setAlignment(Qtc.Qt.AlignmentFlag.AlignHCenter)


            # if widget is not None:
            #     widget.setParent(None)
            #     widget.deleteLater()

    def tagSearch(self, grid, rating, score):
        tags = []

        for i in range(grid.count()):
            tags.append(grid.itemAt(i).widget().text())
        if not rating.currentText() == "rating":
            tags.append(rating.currentText())
        if not score.currentText() == "score":
            tags.append(score.currentText())

        tag_string = ""
        for t in tags:
            tag_string = tag_string + t + "+"
        self.whatToPullCustom(self.comp, tag_string)
    
    def insertIcon(self, input, grid):
        inputtext = input.text().split(' ')
        inputtext = [s for s in inputtext if s.strip()]
        for s in inputtext:
                btn = Qtw.QPushButton(text=s.strip())
                btn.clicked.connect(lambda: self.removeIcon(grid))
                if self.master.colorTheme:
                    if self.isLight(self.master.colorTheme):
                        btn.setStyleSheet(f"border-radius: 25%; font-weight: bold; background-color:{self.master.colorTheme};color: black")
                    else:
                        btn.setStyleSheet(f"border-radius: 25%; font-weight: bold;background-color:{self.master.colorTheme};color: white")

                else:
                    btn.setStyleSheet(f"border-radius: 25%; font-weight: bold;background-color:#3fc4a3;")
                alreadyThereFlag = False
                for i in range(grid.count()):
                    if btn.text() == grid.itemAt(i).widget().text():
                        alreadyThereFlag = True
                        break
                if not alreadyThereFlag:
                    grid.addWidget(btn, self.row, self.col)
                    self.col+=1
                    self.gridPush.append(btn)
                    if self.col == self.colCount:
                        self.col = 0
                        self.row+=1
        # self.restructureGrid(grid)
    
    def checkScroll(self):
        scroll_bar = self.scr.verticalScrollBar()
        if scroll_bar.value() > scroll_bar.maximum() * 0.99 and not self.t.isRunning():
            with self.scraper.lock:
                self.scraper.site.pid+=1                                                                                                                     #scraper pid
                self.loadThread()

    def whatToPullCustom(self, url, tags):
        scap = Scraper(url, tags=tags)
        print("::url" + url + tags + "\n")
        self.scraper = scap
        

        self.clearWidget()

        with self.scraper.lock:
            self.loading.set(0)
            self.loadThread()
    # def imageCombos(self, json, i):
        
    #     comboBox = Qtw.QComboBox()   
    #     posts = json['post']
    #     for key in posts[i]:
    #         action = Qtw.QWidgetAction(comboBox)
    #         widget = Qtw.QWidget()
    #         vbox = Qtw.QVBoxLayout()
    #         label = Qtw.QLabel(text=key)
    #         pbtn = Qtw.QPushButton(text=str(posts[i][key]))
    #         vbox.addWidget(label)
    #         vbox.addWidget(pbtn)
    #         widget.setLayout(vbox)
    #         action.setDefaultWidget(widget)                           #emit combobox
    #         comboBox.addAction(action)
    #     return comboBox
    def eventFilter(self, source, event):                                                                                               #event filter native SearchPage
        if source == self and event.type() == Qtc.QEvent.Type.KeyPress:
            if event.key() == Qtc.Qt.Key.Key_P:
                if self.master.auto_scroll:
                    if self.autoScrollTimer and self.autoScrollTimer.isActive():
                        print("timer stopped")
                        self.autoScrollTimer.stop()
                    elif self.autoScrollTimer and not self.autoScrollTimer.isActive():
                        self.autoScrollTimer.start()

        return super().eventFilter(source, event)
    def imageCombos(self, posts):
        keys = list(posts.keys())
        for att in keys:
            if '@' in att:
                new_att = att.strip('@')
                posts[new_att] = posts.pop(att)
        comboBox = Qtw.QComboBox()   
        comboBox.setInsertPolicy(Qtw.QComboBox.InsertPolicy.NoInsert)
        listWidget = Qtw.QListWidget()
        comboBox.setModel(listWidget.model())
        comboBox.setView(listWidget)
       

        for key in posts:
            if key == "score" or key == "rating" :
                item = Qtw.QListWidgetItem(listWidget)
                widget = Qtw.QWidget()
                vbox = Qtw.QVBoxLayout()
                label = Qtw.QLabel(text=key)
                pbtn = Qtw.QPushButton(text=str(posts[key]))
                if key == "score":
                    pbtn.clicked.connect(partial(self.whatToPullCustom, self.comp, "score:" + str(posts[key])))

                elif key == "rating":
                    pbtn.clicked.connect(partial(self.whatToPullCustom, self.comp, "rating:" + str(posts[key])))

                vbox.addWidget(label)
                vbox.addWidget(pbtn)
                vbox.setContentsMargins(0,0,0,0)
                widget.setLayout(vbox)

                item.setSizeHint(widget.sizeHint())
                listWidget.addItem(item)
                listWidget.setItemWidget(item, widget)                      #Using ListWidget for custom combobox
            elif key == 'tags':
                tags = posts[key].strip().split(' ')
                row = 0
                col = 0
                colCount = 3

                widget = Qtw.QWidget()
                vbox = Qtw.QVBoxLayout()
                grid = Qtw.QGridLayout()
                grid.setContentsMargins(0,0,0,0)
                item = Qtw.QListWidgetItem(listWidget)

                for tag in tags:
                    
                    pbtn = Qtw.QPushButton(text=tag)
                    pbtn.clicked.connect(partial(self.whatToPullCustom, self.comp, tag))
                    pbtn.clicked.connect(partial(self.insertText, self.tag_input, tag, self.grid_scroll))
                    grid.addWidget(pbtn, row, col)
                    col+=1
                    if col >= colCount:
                        col=0
                        row+=1
                   

                label = Qtw.QLabel(text="tags")
                vbox.addWidget(label)
                vbox.addLayout(grid)
                widget.setLayout(vbox)

                item.setSizeHint(widget.sizeHint())
                listWidget.addItem(item)
                listWidget.setItemWidget(item, widget)

                    
                

        
        return comboBox
    # def autoScroll(self):                                                                                                                              #why is this here?
    #     self.scroll
    def whatToPull(self, url):
        self.comp = url
        scap = Scraper(url, tags="")
        self.scraper = scap
        

        with self.scraper.lock:
            self.loadThread()


    def loadThread(self):
        if self.loading.get() == 0:
            self.loading.set(1)
            self.worker = Worker(self.comp, self.scraper)
            self.worker.progress.connect(self.addImageToLayout)
            self.worker.finished.connect(self.t.quit)
            self.worker.finished.connect(self.worker.deleteLater)

            self.worker.moveToThread(self.t)

            self.t.started.connect(self.worker.run)
            self.t.start()

    @Qtc.pyqtSlot(bytes, dict, bool, bool, name="imageLoad")
    def addImageToLayout(self, data, json, vidFlag, gifFlag):
        # self.json = json
        
        widget = Qtw.QWidget()
        widget.setFixedWidth(int(self.master.width()*0.7))
        widget.setFixedHeight(int(self.master.height()*0.9))
        
        

        inner_card_layout = Qtw.QVBoxLayout()
        inner_card_layout.setSpacing(0)
        
        label = ClickableLabels(self.imageIndex, self.vbox)
        label.setScaledContents(True)
        if self.master.tool_tips:
            label.setToolTip("Double Click for Image Viewer")
        label.clicked.connect(self.imageViewer.initalizeView)
        

        heart_icon = QtGui.QIcon('origin/loveheart_empty.png')
        save_btn = ButtonWithState()
        save_btn.setIcon(heart_icon)
          
        save_btn.clicked.connect(partial(self.save_feature, json, save_btn))
    
      
        if gifFlag:                                                                                                                                     #gif worker
            
            
            gif_worker = GifWorker(label, json)
            
            gif_worker.handle_gif.connect(self.makeMovie_handleGif)
            gif_worker.finished.connect(self.gifThread.quit)
            gif_worker.finished.connect(gif_worker.deleteLater)

            gif_worker.moveToThread(self.gifThread)
            


            self.gifThread.started.connect(gif_worker.run)

            self.gifThread.start()


            
            
            
            inner_card_layout.addWidget(label)
            label.setMinimumSize(int(widget.width()*0.9), int(widget.height()*0.9))

            combos_saves_horizontal = Qtw.QHBoxLayout()
            spacer = Qtw.QSpacerItem(20,20, Qtw.QSizePolicy.Policy.Expanding, Qtw.QSizePolicy.Policy.Minimum)
            combo = self.imageCombos(json)
            combos_saves_horizontal.addWidget(combo)
            combos_saves_horizontal.addSpacerItem(spacer)
            combos_saves_horizontal.addWidget(save_btn)
        
            combo.installEventFilter(self.createEventFilter(combo, combos_saves_horizontal))


            combos_saves_horizontal.setStretch(0, 5)
            combos_saves_horizontal.setStretch(1, 8)
            combos_saves_horizontal.setStretch(2, 2)
            inner_card_layout.addLayout(combos_saves_horizontal)

        elif vidFlag:

            container = videoContainer(json)
            simpleLayout = Qtw.QVBoxLayout()
            video = QVideoWidget()
            audio = Qtmedia.QAudioOutput()
            audio.setVolume(0.5)
            audioDevice = Qtmedia.QMediaDevices.defaultAudioOutput()
            audio.setDevice(audioDevice)
            volIcon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioVolumeMedium)
            volumeBtn = Qtw.QPushButton(icon=volIcon)
            #set video sink?
            audio_slider = Qtw.QSlider(video, orientation=Qtc.Qt.Orientation.Vertical)
            audio_slider.setStyleSheet("QSlider {bottom:0;} QSlider::handle:horizontal {margin: 0; height:30px; width:10px; background-color:grey;}  QSlider::grove:horizontal: {height:30px; background-color: blue; border: 1px solid #bbb;}")
            audio_slider.setRange(0,100)
            audio_slider.valueChanged.connect(lambda value: audio.setVolume(value/100))
            audio_slider.setValue(50)
            audio_slider.hide()
            volumeBtn.clicked.connect(lambda: self.sliderShow_audio(audio_slider))

            video_slider = Qtw.QSlider()
           
            video_slider.setStyleSheet("QSlider::handle:horizontal {margin: 0; height:10px; width:10px; background-color:grey;}  QSlider::grove:horizontal: {height:10px; background-color: blue; border: 1px solid #bbb;}")
            # video_slider.setFixedWidth()
            video_slider.setRange(0,100)
            
            

            player = Qtmedia.QMediaPlayer()
            # video.videoFrameChanged.connect(lambda: self.handle_video(video.videoFrame(), label))
            player.setVideoOutput(video)
            player.setAudioOutput(audio)

            play_icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart)
            play_btn = Qtw.QPushButton(icon=play_icon)
            if self.master.tool_tips:
                play_btn.setToolTip("Play video")
            play_btn.clicked.connect(partial(self.handle_video, player, play_btn, json))

            
            video_slider.valueChanged.connect(lambda value: player.setPosition(int(player.duration()*value/100)))
            video_slider.setOrientation(Qtc.Qt.Orientation.Horizontal)

            h_box = Qtw.QHBoxLayout()
            h_box.addWidget(play_btn)
            h_box.addWidget(video_slider)
            h_box.addWidget(volumeBtn)
            h_box.addWidget(save_btn)
            h_box.setStretch(0, 1)
            h_box.setStretch(1, 8)
            h_box.setStretch(2, 1)
            h_box.setStretch(3, 1)
            
            
            
           
            # h_box.setStretch(0, 4)
            # h_box.setStretch(1,2)
            

            player.positionChanged.connect(partial(self.videoTimerStart, video_slider, player))
            
            
           
            
            
            

            simpleLayout.addWidget(video)
            simpleLayout.addLayout(h_box)
            simpleLayout.setStretch(0,10)
            simpleLayout.setStretch(1,2)

            container.setLayout(simpleLayout)
            inner_card_layout.addWidget(container)
            inner_card_layout.addWidget(self.imageCombos(json))

            
        else:    
            img = QtGui.QImage()
            img.loadFromData(data)
            pixmap = QtGui.QPixmap.fromImage(img)
            scaled_pixmap = pixmap.scaled(widget.width(), widget.height(), aspectRatioMode=Qtc.Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qtc.Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            inner_card_layout.addWidget(label)

            combos_saves_horizontal = Qtw.QHBoxLayout()
            spacer = Qtw.QSpacerItem(20,20, Qtw.QSizePolicy.Policy.Expanding, Qtw.QSizePolicy.Policy.Minimum)
            combo = self.imageCombos(json)
            combos_saves_horizontal.addWidget(combo)
            combos_saves_horizontal.addSpacerItem(spacer)
            combos_saves_horizontal.addWidget(save_btn)
        
            combo.installEventFilter(self.createEventFilter(combo, combos_saves_horizontal))


            combos_saves_horizontal.setStretch(0, 5)
            combos_saves_horizontal.setStretch(1, 8)
            combos_saves_horizontal.setStretch(2, 2)
            inner_card_layout.addLayout(combos_saves_horizontal)




        widget.setLayout(inner_card_layout)
        widget.setSizePolicy(Qtw.QSizePolicy.Policy.Expanding, Qtw.QSizePolicy.Policy.Expanding)
        self.vbox.addWidget(widget, stretch=10, alignment=Qtc.Qt.AlignmentFlag.AlignCenter)
        
        self.vbox.atom_count.increment()
        print(self.vbox.atom_count.get())
        self.imageIndex += 1
        self.loading.set(0)


   
    def copyVid(self, current_vid):
            container = Qtw.QWidget()
            simpleLayout = Qtw.QVBoxLayout()
            video = QVideoWidget()
            audio = Qtmedia.QAudioOutput()
            audio.setVolume(0.5)
            audioDevice = Qtmedia.QMediaDevices.defaultAudioOutput()
            audio.setDevice(audioDevice)
            volIcon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioVolumeMedium)
            volumeBtn = Qtw.QPushButton(icon=volIcon)
            #set video sink?
            audio_slider = Qtw.QSlider(video, orientation=Qtc.Qt.Orientation.Vertical)
            audio_slider.setStyleSheet("QSlider {bottom:0;} QSlider::handle:horizontal {margin: 0; height:30px; width:10px; background-color:grey;}  QSlider::grove:horizontal: {height:30px; background-color: blue; border: 1px solid #bbb;}")
            audio_slider.setRange(0,100)
            audio_slider.valueChanged.connect(lambda value: audio.setVolume(value/100))
            audio_slider.setValue(50)
            audio_slider.hide()
            volumeBtn.clicked.connect(lambda: self.sliderShow_audio(audio_slider))

            video_slider = Qtw.QSlider()
           
            video_slider.setStyleSheet("QSlider::handle:horizontal {margin: 0; height:10px; width:10px; background-color:grey;}  QSlider::grove:horizontal: {height:10px; background-color: blue; border: 1px solid #bbb;}")
            # video_slider.setFixedWidth()
            video_slider.setRange(0,100)
            
            

            player = Qtmedia.QMediaPlayer()
            player.setVideoOutput(video)
            player.setAudioOutput(audio)

            play_icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart)
            play_btn = Qtw.QPushButton(icon=play_icon)
            play_btn.clicked.connect(partial(self.handle_video, player, play_btn, current_vid.json))

            heart_icon = QtGui.QIcon('origin/assets/loveheart_empty.png')
            save_btn = ButtonWithState()
            save_btn.setIcon(heart_icon)
          
            save_btn.clicked.connect(partial(self.save_feature, current_vid.json, save_btn))
            

            h_box = Qtw.QHBoxLayout()
            h_box.addWidget(play_btn)
            h_box.addWidget(video_slider)
            h_box.addWidget(volumeBtn)
            h_box.addWidget(save_btn)
            h_box.setStretch(0, 1)
            h_box.setStretch(1, 8)
            h_box.setStretch(2, 1)
            h_box.setStretch(3, 1)
            
            
            
           
            # h_box.setStretch(0, 4)
            # h_box.setStretch(1,2)
            

            player.positionChanged.connect(partial(self.videoTimerStart, video_slider, player))

            video_slider.valueChanged.connect(lambda value: player.setPosition(int(player.duration()*value/100)))
            video_slider.setOrientation(Qtc.Qt.Orientation.Horizontal)
            
            
           
            
            
            

            simpleLayout.addWidget(video)
            simpleLayout.addLayout(h_box)
            simpleLayout.setStretch(0,5)
            simpleLayout.setStretch(1,5)

            container.setLayout(simpleLayout)
            return container
    def copyMovie(self, current_movie):
        new_movie = Qtw.QLabel()
        new_movie.setScaledContents(True)
        new_movie.setMovie(current_movie.movie())
        return new_movie
    def copyImg(self, current_img):
        new_img = Qtw.QLabel()
        new_img.setScaledContents(True)
        new_img.setPixmap(current_img.pixmap())
        return new_img    
    def createEventFilter(self, combo, hbox):
        class EventFilter(Qtc.QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.combo = combo
                self.hbox = hbox
                self.master = parent
            def eventFilter(self, source, event):
                if source == self.combo:
                    if event.type() == Qtc.QEvent.Type.HoverEnter:
                        self.LabelCombosResizing(self.hbox)
                    elif event.type() == Qtc.QEvent.Type.HoverLeave:
                        self.baseLabelSizing(self.hbox)
                
                return super().eventFilter(source, event)
            def LabelCombosResizing(self, hbox):
                hbox.setStretch(0, 12)
                hbox.setStretch(1, 1)
                hbox.setStretch(2, 2)
            def baseLabelSizing(self, hbox):
                hbox.setStretch(0, 5)
                hbox.setStretch(1, 8)
                hbox.setStretch(2, 2)
        return EventFilter(self)
    def videoTimerStart(self, slider, player):
        
        if isinstance(slider, Qtw.QSlider) and player:
            try:
                slider.blockSignals(True)
                if player.duration() > 0:
                    sliderValue = int(player.position()/player.duration()*100)
                    if sliderValue > slider.value():
                        slider.setValue(sliderValue)
                slider.blockSignals(False)
            except:
                return
        
    def sliderShow_audio(self, slider):
        if slider.isVisible():
            slider.hide()
        else:
            slider.show()
    # def video_sliders_handles(self, player, value):
    #     player.position = player.duration * value
    @Qtc.pyqtSlot(object, str)
    def makeMovie_handleGif(self, label, filename):
            movie = QtGui.QMovie(filename)
            
            label.setMovie(movie)
            label.movie().start()
           


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.imageViewer.resizeWidget()
        self.resizeWidget()
    def resizeWidget(self):
        for i in range(self.vbox.count()): #self.vbox.atom_count.get()? for thread safety?
            item = self.vbox.itemAt(i).widget()
            if not item.size() == Qtc.QSize(int(self.master.width()*0.7), int(self.master.height()*0.9)):
                item.setFixedSize(int(self.master.width()*0.7), int(self.master.height()*0.9))
    def handle_video(self, player, btn, json):
        
        if not player.source().isValid() or player.source().isEmpty():
            try:
                file_url = json['file_url']
            except:
                file_url = json['@file_url']
            os.makedirs('video_assets', exist_ok=True)
            if not os.path.exists('video_assets' + file_url):
                filename = os.path.join('video_assets', os.path.basename(file_url))
                res = requests.get(file_url)

                with open(filename, 'wb') as file:
                    file.write(res.content)

                player.setSource(Qtc.QUrl.fromLocalFile(filename))
            else:
                filename = 'video_assets/' + file_url
                player.setSource(Qtc.QUrl.fromLocalFile(filename))

            player.play()
        else:
            
            state = player.playbackState()
            if  state == Qtmedia.QMediaPlayer.PlaybackState.PlayingState:
                icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackPause)
                btn.setIcon(icon)
                player.pause()
            else:
                icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart)
                btn.setIcon(icon)
                player.play()
    def save_feature(self, json, btn):
        filepath = os.path.join('origin','saves.txt')
        if btn.state == 0:
            icon = QtGui.QIcon('origin/assets/red-heart-icon.png')
            btn.setIcon(icon)
            btn.state = 1
            if os.path.exists(os.path.join(filepath)):
                try:
                    file_url = json['file_url']
                except:
                    file_url = json['@file_url']

                alreadyThereFlag = False
                with open(filepath, 'r+') as file:
                    lines = file.readlines()
                    for line in lines:
                        if line == file_url:
                            alreadyThereFlag = True
                            break
                    if not alreadyThereFlag:
                        file.seek(0, os.SEEK_END)
                        file.write(file_url + '\n')

            else:
                with open(filepath, 'w') as file:
                    file.write(file_url + '\n')

        
        elif btn.state == 1 and os.path.exists(filepath):
            icon = QtGui.QIcon('origin/assets/loveheart_empty.png')
            btn.setIcon(icon)

            try:
                    file_url = json['file_url']
            except:
                    file_url = json['@file_url']


            with open(filepath, 'r') as file:
                lines = file.readlines()
                
            with open(filepath, 'w') as file:
                for line in lines:
                    if line.strip() != file_url:
                        file.write(line)
            btn.state = 0
        print(os.path.exists(filepath))
        print(btn.icon())
        print(QtGui.QIcon('origin/assets/loveheart_empty.png'))


    

class AtomicClockVLayout(Qtw.QVBoxLayout):
    atom_count = AtomicInteger()
    def __init__(self, master):
        super().__init__(master)

class ImageViewer(Qtw.QWidget):
    
    def __init__(self, master, flag):
        super().__init__(master)
        self.imageHandlingFlag = flag
        self.master = master
        self.index=0
        self.master_layout = None
        self.setFixedSize(self.master.width(), self.master.height())

        self.setWindowFlags(Qtc.Qt.WindowType.WindowStaysOnTopHint)

        self.main_layout_hbox = Qtw.QHBoxLayout()
        
        self.main_layout_hbox.setGeometry(self.geometry())

        leftIcon = QtGui.QIcon('origin/assets/d_arrow_left_light.png')
        leftbtn = Qtw.QPushButton()
        leftbtn.setStyleSheet("background:None; min-width:40px; min-height:40px;")
        leftbtn.setIcon(leftIcon)
        leftbtn.clicked.connect(self.decrementView)

        rightIcon = QtGui.QIcon('origin/assets/d_arrow_right_light.png')
        rightbtn = Qtw.QPushButton() 
        rightbtn.setStyleSheet("background:None; min-width:40px; min-height:40px;")
        rightbtn.setIcon(rightIcon)
        rightbtn.clicked.connect(self.incrementView)

        self.main_layout_hbox.addWidget(leftbtn, stretch=1, alignment=Qtc.Qt.AlignmentFlag.AlignLeft)
        self.main_layout_hbox.addSpacerItem(Qtw.QSpacerItem(20,20,Qtw.QSizePolicy.Policy.Expanding, Qtw.QSizePolicy.Policy.Minimum))
        self.main_layout_hbox.addWidget(rightbtn, stretch=1, alignment=Qtc.Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(self.main_layout_hbox)
        self.installEventFilter(self)
        self.hide()
    def initalizeView(self, layout, index):
        if not self.isVisible():
            self.index = index
            self.master_layout = layout
            if self.imageHandlingFlag == True:
                show_widget = self.copyWidget_original_size(layout.itemAt(self.index).widget())
            else:
                show_widget = self.copyWidget(layout.itemAt(self.index).widget())
            self.main_layout_hbox.removeWidget(self.main_layout_hbox.itemAt(1).widget())
            self.main_layout_hbox.insertWidget(1, show_widget, stretch=10, alignment= Qtc.Qt.AlignmentFlag.AlignCenter)
            self.show()
            self.raise_()
    def incrementView(self):
        if self.index+1 < self.master_layout.count():
            self.index += 1
            if self.imageHandlingFlag == True:
                next_widget = self.copyWidget_original_size(self.master_layout.itemAt(self.index).widget())
            else:
                next_widget = self.copyWidget(self.master_layout.itemAt(self.index).widget())
            
            self.main_layout_hbox.removeWidget(self.main_layout_hbox.itemAt(1).widget())
            self.main_layout_hbox.insertWidget(1, next_widget, stretch=10, alignment= Qtc.Qt.AlignmentFlag.AlignCenter)
    def decrementView(self):
        if self.index-1 >= 0:
            self.index -= 1
            if self.imageHandlingFlag == True:
                next_widget = self.copyWidget_original_size(self.master_layout.itemAt(self.index).widget())
            else:
                next_widget = self.copyWidget(self.master_layout.itemAt(self.index).widget())            

            self.main_layout_hbox.removeWidget(self.main_layout_hbox.itemAt(1).widget())
            self.main_layout_hbox.insertWidget(1, next_widget, stretch=5, alignment= Qtc.Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeWidget()
    def resizeWidget(self):
        self.setFixedSize(self.master.width(), self.master.height())
        # self.main_layout_hbox.setGeometry(self.geometry())

        
       
    def eventFilter(self, source, event):
        if source == self:
            if event.type() == Qtc.QEvent.Type.MouseButtonPress:
                click_pos = event.pos()
                if not self.withinBounds(click_pos):
                    self.hide()
        return super().eventFilter(source, event)
    
    def withinBounds(self, click_pos):
        for i in range(self.main_layout_hbox.count()):
            item = self.main_layout_hbox.itemAt(i)
            widget = item.widget()
            if widget and widget.geometry().contains(click_pos):
                return True
        return False
    

    def copyWidget_original_size(self, widget):
        if widget is None:
            return None
        if isinstance(widget, videoContainer):
            new_widget = self.master.copyVid(widget)
            
            return new_widget
        elif isinstance(widget, Qtw.QLabel) and isinstance(widget.movie(), QtGui.QMovie):
            new_widget = self.master.copyMovie(widget)

            return new_widget

        elif isinstance(widget, Qtw.QLabel):
            new_widget = self.master.copyImg(widget)

            return new_widget
        
        new_widget = Qtw.QWidget()
        if widget.layout() and not widget.layout().isEmpty():
            new_layout = self.copyLayout(widget.layout())
            new_widget.setLayout(new_layout)

        
        return new_widget
    
    def copyWidget(self, widget):
        if widget is None:
            return None
        if isinstance(widget, videoContainer):
            new_widget = self.master.copyVid(widget)
            new_widget.setMaximumHeight(int(self.height()*0.9))
            new_widget.setMaximumWidth(int(self.width()*0.9))
            new_widget.setFixedSize(int(self.width()*0.9), int(self.height()*0.9))
            return new_widget
        elif isinstance(widget, Qtw.QLabel) and isinstance(widget.movie(), QtGui.QMovie):
            new_widget = self.master.copyMovie(widget)
            new_widget.setMaximumHeight(int(self.height()*0.9))
            new_widget.setMaximumWidth(int(self.width()*0.9))
            new_widget.setFixedSize(int(self.width()*0.9), int(self.height()*0.9))

            return new_widget

        elif isinstance(widget, Qtw.QLabel):
            new_widget = self.master.copyImg(widget)
            new_widget.setMaximumHeight(self.height())
            new_widget.setMaximumWidth(self.width())
            new_widget.setFixedSize(int(self.width()*0.9), int(self.height()*0.9))

            return new_widget
        
        new_widget = Qtw.QWidget()
        if widget.layout() and not widget.layout().isEmpty():
            new_layout = self.copyLayout(widget.layout())
            new_widget.setLayout(new_layout)

        
        return new_widget

    def copyLayout(self, layout):
        new_layout = Qtw.QVBoxLayout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, Qtw.QWidgetItem):
                if item.widget():
                    new_layout.addWidget(self.copyWidget(item.widget()))
            elif isinstance(item, Qtw.QLayoutItem):
                if item.layout() and not item.layout().isEmpty():
                    new_layout.addLayout(self.copyLayout(item.layout()))
        return new_layout
    
class videoContainer(Qtw.QWidget):
    def __init__(self, json):
        super().__init__()
        self.json = json

class ButtonWithState(Qtw.QPushButton):
    state = 0
    def __init__(self):
        super().__init__()

class GifWorker(Qtc.QObject):
    handle_gif = Qtc.pyqtSignal(object, str)
    finished = Qtc.pyqtSignal()
    def __init__(self, label, json):
        super().__init__()
        self.json = json
        self.label = label
        
        
    def run(self):
        
        self.threadActive = True

        os.makedirs('video_assets', exist_ok=True)
        try:
            file_url = self.json['file_url']
        except:
            file_url = self.json['@file_url']
        if not os.path.exists(os.path.join('video_assets', os.path.basename(file_url))):
            filename = os.path.join('video_assets', os.path.basename(file_url))
            res = requests.get(file_url)

            with open(filename, 'wb') as file:
                file.write(res.content)

        else:
            filename = os.path.join('video_assets', os.path.basename(file_url))

        self.handle_gif.emit(self.label, filename)
        print("Inner Thread" + str(threading.get_ident()))

        self.finished.emit()
  
    def stop(self):
        self.threadActive = False
        self.quit()
class VidWorker(Qtc.QThread):
    handle_gif = Qtc.pyqtSignal(object, str)
    finished = Qtc.pyqtSignal()


class Worker(Qtc.QObject):
    progress = Qtc.pyqtSignal(bytes, dict, bool, bool, name="imageLoad")
    finished = Qtc.pyqtSignal(name="imageLoad")

    def __init__(self, url, scraper):
        super().__init__()
        self.url = url
        self.scraper = scraper
        self.stop = False
        
    def run(self):
      

        
        siteJson = self.scraper.site.retJson()
        L = self.scraper.site.imagePop()

        i = 0
        for i in range(len(L)):
            if self.stop:
                # self.loading = False
                return
            try:
                res = requests.get(L[i], timeout=2)
                self.progress.emit(res.content, siteJson[i], self.isVideo(L[i]), self.isGif(L[i]))

            except:
                continue
       
        self.finished.emit()

    def isVideo(self, url):
        url = url.lower()
        video_extensions =['.mp4', '.avi', '.mov', '.mkv']
        for v in video_extensions:
            if url.endswith(v):
                return True
        return False
    def isGif(self, url):    
        url = url.lower()
        if url.endswith('.gif'):
            return True
        else:
            return False

class BottomWorker(Qtc.QObject):
    progress = Qtc.pyqtSignal(list, list, name="bottom")
    show = Qtc.pyqtSignal(bool, name="showHide")
    finished = Qtc.pyqtSignal(name="bottom")
    # finished = Qtc.pyqtSignal(name="bottom")
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
    def run(self, atomicint, input_string):  
        if input_string is not None:      
            searchFlag = False
        
                                                                #check for this need outside
            if len(input_string[-1]) > 0:
                if input_string[-1][-1].isdigit():
                    searchFlag = True
                elif input_string[-1][-1].isalpha():
                    searchFlag = True
                if searchFlag:
                    try:
                        if atomicint.get() == 0:                                                            #is this really necessary
                            tag = input_string[-1]
                            tagList = self.scraper.site.tagPop(tag)
                        
                            
                                
                            self.show.emit(True)

                            self.progress.emit(tagList[0], tagList[1])
                    except:
                        self.show.emit(False)

            else:
                self.show.emit(False)



        self.finished.emit()

class ClickableLabels(Qtw.QLabel):
    clicked = Qtc.pyqtSignal(object, int)

    def __init__(self, index, vbox):
        super().__init__()
        self.index = index
        self.vbox = vbox
        self.installEventFilter(self)
    def eventFilter(self, source, event):
        if source == self:
            if event.type() == Qtc.QEvent.Type.MouseButtonDblClick:
                self.clicked.emit(self.vbox, self.index)
                return True
        return super().eventFilter(source, event)

    
class TopPage(SearchPage):
    def __init__(self, master):
        super().__init__(master)

    def whatToPull(self, url):
        self.comp = url
        scap = Scraper(url, tags="score:>=50")
        self.scraper = scap

        with self.scraper.lock:
            self.loadThread()

class Saves(Qtw.QFrame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.centralWidget = Qtw.QWidget(self)
        savedGrid = Qtw.QGridLayout()
        savedGrid.setContentsMargins(0,0,0,0)
        savedGrid.itemAt(1)
        colCount = 5
        rowCount = 5


        self.imageView = ImageViewer(self, self.master.originalSizedImages)

        self.initializeGrid(savedGrid, colCount, rowCount)

        self.centralWidget.setLayout(savedGrid)
        self.centralWidget.setStyleSheet("""
                                         padding:5px;

""")
        bottomNav = Qtw.QWidget()
        back_btn = Qtw.QPushButton(text="Back")
        back_btn.clicked.connect(lambda: self.master.showFrame("StartPage"))
        h_row = Qtw.QHBoxLayout()
        h_row.addWidget(back_btn)
        bottomNav.setLayout(h_row)

        self.mainlayout = Qtw.QVBoxLayout()
        self.mainlayout.addWidget(self.centralWidget)
        self.mainlayout.addWidget(bottomNav)
        self.mainlayout.setStretch(0, 13)
        self.mainlayout.setStretch(1, 2)
        self.setLayout(self.mainlayout)
        # self.setFixedWidth(self.master.width())
        # self.setFixedHeight(self.master.height())
        self.installEventFilter(self)
        
        self.setLayout(self.mainlayout)
    def initializeGrid(self, grid, colCount, rowCount):
        with open("origin/saves.txt", mode='r') as file:
            lines = file.readlines()
            i = 0
            for row in range(rowCount):
                for col in range(colCount):
                    try:
                        line = lines[i].strip()
                    except:
                        line = None
                   
                    label = ClickableLabels(i, grid)
                    label.clicked.connect(partial(self.imageView.initalizeView, grid, i))                        
                    label.setMaximumSize(int(self.width()/5), int(self.height()/5))
                    label.setScaledContents(True)


                    if line is not None:
                        print(line + ">>line")
                        res = requests.get(line, timeout=5)
                        img = QtGui.QImage()
                        img.loadFromData(res.content)
                        pixmap = QtGui.QPixmap.fromImage(img).scaled(label.size(), Qtc.Qt.AspectRatioMode.KeepAspectRatio, Qtc.Qt.TransformationMode.SmoothTransformation)
                        label.setPixmap(pixmap)
                        grid.addWidget(label, row, col)
                    else:
                        img = QtGui.QImage("origin/assets/red-heart-icon.png")
                        pixmap = QtGui.QPixmap.fromImage(img).scaled(label.size(), Qtc.Qt.AspectRatioMode.KeepAspectRatio, Qtc.Qt.TransformationMode.SmoothTransformation)
                        label.setPixmap(pixmap)
                        grid.addWidget(label, row, col)
                    i+=1

    def copyImg(self, current_img):
        new_img = Qtw.QLabel()
        new_img.setScaledContents(True)
        new_img.setPixmap(current_img.pixmap())
        return new_img
    def resizeEvent(self, event):
        self.imageView.resizeEvent(event)
        return super().resizeEvent(event)
class Settings(Qtw.QDialog):
    def __init__(self, master):
        super().__init__(master)    
        self.master = master
        self.setWindowFlag(Qtc.Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qtc.Qt.WidgetAttribute.WA_TranslucentBackground)

       
        self.setStyleSheet("font-size:32px; color:white; ")

        vbox = Qtw.QVBoxLayout(self)

        self.label = Qtw.QLabel(text="Settings")
        self.label.setStyleSheet("""
                            font-size:40px;
                            """)
        vbox.addWidget(self.label)

        self.safeCheck = Qtw.QCheckBox(self, text="NSFW")
        if self.master.nsfw[0]:
            self.safeCheck.setCheckState(Qtc.Qt.CheckState.Checked)
        else:
            self.safeCheck.setCheckState(Qtc.Qt.CheckState.Unchecked)
        self.safeCheck.checkStateChanged.connect(self.nsfw_toggle)
        vbox.addWidget(self.safeCheck)

        self.colorLabel = Qtw.QLabel(text="ColorTheme")
        self.colorTheme = AddableCombo(self)
        for item in self.master.colorOptions:
            self.colorTheme.add_itm_wid(item)
        
        self.colorTheme.REMOVE_SIGNAL.connect(self.colorThemeChange)
        self.colorTheme.combo.setCurrentText(self.master.colorTheme)
        self.colorTheme.addBtn.clicked.connect(self.show_color_theme_add_message_box)
        self.colorTheme.plus_btn.clicked.connect(self.show_color_theme_add_message_box)
        self.colorTheme.combo.setPlaceholderText("Rgb")
        self.colorTheme.combo.currentTextChanged.connect(self.colorThemeChange)
        vbox.addWidget(self.colorLabel)
        vbox.addWidget(self.colorTheme)

        self.autoCheck = Qtw.QCheckBox(self, text="AutoScroll?")
        self.autoCheck.setToolTip("Press P to pause")
        if self.master.auto_scroll:
            self.autoCheck.setCheckState(Qtc.Qt.CheckState.Checked)
        else:
            self.autoCheck.setCheckState(Qtc.Qt.CheckState.Unchecked)
        self.autoCheck.checkStateChanged.connect(self.autoChange)
        vbox.addWidget(self.autoCheck)

        self.backgroundLabel = Qtw.QLabel(text="Custom Background Image")
        self.backGroundCustom = AddableCombo(self)


        
        if self.master.backgroundTheme:

            self.backGroundCustom.combo.setCurrentText(self.master.backgroundTheme)
            self.backGroundCustom.add_itm_wid(self.master.backgroundTheme)
        else:
            self.backGroundCustom.combo.setCurrentText("url")

        self.backGroundCustom.combo.currentTextChanged.connect(self.backgroundColorChange)
        self.backGroundCustom.REMOVE_SIGNAL.connect(self.backgroundColorChange)
        self.backGroundCustom.addBtn.clicked.connect(self.show_background_theme_add_msgbox)
        self.backGroundCustom.plus_btn.clicked.connect(self.show_background_theme_add_msgbox)
        vbox.addWidget(self.backgroundLabel)
        vbox.addWidget(self.backGroundCustom)

        self.toolTipToggle = Qtw.QCheckBox(self, text="ToolTips?")
        if self.master.tool_tips:
            self.toolTipToggle.setCheckState(Qtc.Qt.CheckState.Checked)
        else:
            self.toolTipToggle.setCheckState(Qtc.Qt.CheckState.Unchecked)
        self.toolTipToggle.checkStateChanged.connect(self.tool_tip_check)
        vbox.addWidget(self.toolTipToggle)

        self.originalSizedImages = Qtw.QCheckBox(self, text="Original Size Images?")
        if self.master.originalSizedImages:
            self.originalSizedImages.setCheckState(Qtc.Qt.CheckState.Checked)
        else:
            self.originalSizedImages.setCheckState(Qtc.Qt.CheckState.Unchecked)
        self.originalSizedImages.checkStateChanged.connect(self.og_size_image)
        vbox.addWidget(self.originalSizedImages)

        quitbtn = Qtw.QPushButton(self, text="quit")
        quitbtn.clicked.connect(self.hide)
        vbox.addWidget(quitbtn)

        self.setLayout(vbox)


    def nsfw_toggle(self):
        if self.safeCheck.isChecked():
            self.master.nsfw[0] = True
        elif not self.safeCheck.isChecked():
            self.master.nsfw[0] = False


        self.setting_set()

    def tool_tip_check(self):
        if self.toolTipToggle.isChecked():
            self.master.tool_tips = True
        elif not self.toolTipToggle.isChecked():
            self.master.tool_tips = False
        
        self.setting_set()
    def colorThemeChange(self):
        self.master.colorTheme = self.colorTheme.combo.currentText()
        new_options = []
        for i in range(self.colorTheme.combo.count()):
            new_options.append(self.colorTheme.combo.itemText(i))
        self.master.colorOptions = new_options
        self.setting_set()
        
    def backgroundColorChange(self):
        text = self.backGroundCustom.combo.currentText()
        if text and len(text) > 1:
            self.master.backgroundTheme = text
        
        self.setting_set()

    def setting_set(self):
        settings = {
                "originalSize": self.master.originalSizedImages,
                "colorTheme": self.master.colorTheme,
                "colorOptions": self.master.colorOptions,
                "auto_scroll": self.master.auto_scroll,
                "backgroundTheme": self.master.backgroundTheme,
                "searchList": self.master.searchList,
                "NSFW": self.master.nsfw,
                "tool_tips": self.master.tool_tips

            }
        self.updateSettings(settings)
    def updateSettings(self, new_setting):
        with open('origin/settings.json', 'w') as file:
            json.dump(new_setting, file, indent=4)
        
        self.master.reloadStyles()

    def og_size_image(self):
        if self.originalSizedImages.isChecked():
            self.master.originalSizedImages = True
        elif not self.originalSizedImages.isChecked():
            self.master.originalSizedImages = False

        self.setting_set()


    def autoChange(self):
        if self.autoCheck.isChecked():
            self.master.auto_scroll = True
        elif not self.autoCheck.isChecked():
            self.master.auto_scroll = False



        self.setting_set()


    def show_color_theme_add_message_box(self):
        Popup = self.colorThemeAddMessageBox(self)
        
        
        Popup.show()
    class colorThemeAddMessageBox(Qtw.QDialog):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.setWindowFlag(Qtc.Qt.WindowType.FramelessWindowHint)
            # self.setWindowFlag(Qtc.Qt.WindowType.WindowStaysOnTopHint)
            main_layout = Qtw.QVBoxLayout()
            label = Qtw.QLabel(text="Input Color in Hex format (#FFFFFF)")
            main_layout.addWidget(label)
            hbox = Qtw.QHBoxLayout()
            input = Qtw.QLineEdit()
            input.setPlaceholderText("#FFFFFF")
            input.returnPressed.connect(lambda: self.submit(input.text().strip()))
            submit_btn = Qtw.QPushButton(text="Enter")
            submit_btn.clicked.connect(lambda: self.submit(input.text().strip()))
            hbox.addWidget(input)
            hbox.addWidget(submit_btn)
            main_layout.addLayout(hbox)
            self.setLayout(main_layout)
        def submit(self, text):
            if text and len(text) > 1:
                self.master.colorTheme.add_itm_wid(text)
                self.master.master.colorOptions.append(text)

                self.hide()
            else:
                self.hide()
    def show_background_theme_add_msgbox(self):
        Popup = self.backgroundThemeMsgBox(self)

        Popup.show()
    class backgroundThemeMsgBox(Qtw.QDialog):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.setWindowFlag(Qtc.Qt.WindowType.FramelessWindowHint)
            main_layout = Qtw.QVBoxLayout()
            label = Qtw.QLabel(text="Background Image or Color In Url or Hex Format")
            hbox = Qtw.QHBoxLayout()
            input = Qtw.QLineEdit()
            input.setPlaceholderText("url or #FFFFFF")
            input.returnPressed.connect(lambda: self.submit(input.text().strip()))
            submit_btn = Qtw.QPushButton(text="Enter")
            submit_btn.clicked.connect(lambda: self.submit(input.text().strip()))
            hbox.addWidget(input)
            hbox.addWidget(submit_btn)
            main_layout.addWidget(label)
            main_layout.addLayout(hbox)
            self.setLayout(main_layout)
        def submit(self, text):
            if text and len(text) > 1:
                self.master.backGroundCustom.add_itm_wid(text)
                self.hide()
            else:
                self.hide()
        


class AddableCombo(Qtw.QWidget):
    REMOVE_SIGNAL = Qtc.pyqtSignal()
    def __init__(self, master):
        super().__init__(master)

        self.combo = Qtw.QComboBox()
        self.combo.setDuplicatesEnabled(False)
        self.list_widg = Qtw.QListWidget()
        self.combo.setModel(self.list_widg.model())
        self.combo.setView(self.list_widg)

        self.action = Qtw.QWidgetAction(self) 
        self.addBtn = Qtw.QPushButton(text="Add")
        self.action.setDefaultWidget(self.addBtn)

        hbox = Qtw.QHBoxLayout()

        icon = QtGui.QIcon("origin/assets/plus_light.png")
        self.plus_btn = Qtw.QPushButton()
        self.plus_btn.setFixedSize(40,40)
        self.plus_btn.setIcon(icon)
        self.plus_btn.setStyleSheet("border: none; background: transparent; margin:10%;")
        self.plus_btn.setCursor(Qtc.Qt.CursorShape.PointingHandCursor)
        self.combo.setContextMenuPolicy(Qtc.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.combo.addAction(self.action)
        inner_layout = Qtw.QHBoxLayout()
        inner_layout.addStretch()
        inner_layout.addWidget(self.plus_btn)
        self.combo.setLayout(inner_layout)

        hbox.addWidget(self.combo)
        self.setLayout(hbox)


    def add_itm_wid(self, text):
        background_item = Qtw.QListWidgetItem()
        inner_background_widget = Qtw.QWidget()
        inner_background_item_layout = Qtw.QHBoxLayout()
        remove_icon = QtGui.QIcon("origin/assets/minus.png")
        remove_btn = Qtw.QPushButton(inner_background_widget)
        remove_btn.setIcon(remove_icon)
        background_item_text = status_labels()
        background_item_text.setText(text)
        background_item_text.clicked.connect(lambda: self.combo.setCurrentText(background_item_text.text()))
        
        
        inner_background_item_layout.addWidget(background_item_text)
        inner_background_item_layout.addStretch()
        inner_background_item_layout.addWidget(remove_btn)
        inner_background_widget.setLayout(inner_background_item_layout)

        self.list_widg.addItem(background_item)
        self.list_widg.setItemWidget(background_item, inner_background_widget)
        n = self.list_widg.count()-1
        
        remove_btn.clicked.connect(partial(self.remove_itm_wid, n))
        
    def remove_itm_wid(self, n):
        self.combo.removeItem(n)
        self.REMOVE_SIGNAL.emit()

class status_labels(Qtw.QLabel):
    clicked = Qtc.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self:
            if event.type() == Qtc.QEvent.Type.MouseButtonPress:
                self.clicked.emit()
                return True
        return super().eventFilter(source, event)
    

engine = QQmlApplicationEngine()

we = MainWindow()





we.show()
app.exec()

app.exit()

try:
    shutil.rmtree('video_assets')
    print("Goodbye")

except PermissionError as e:

    target = 'video_assets'
    if not os.path.isdir(target):
        raise

    for root, drs, files in os.walk(target, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            if name != e.filename:
                try:
                    os.remove(file_path)
                except PermissionError:
                    pass
        for name in drs:
            file_path = os.path.join(root, name)
            try:
                shutil.rmtree(file_path)
            except PermissionError or OSError:
                pass
    try:
        shutil.rmtree(target)
    except OSError:
        pass

except:
    print("Goodbye")
