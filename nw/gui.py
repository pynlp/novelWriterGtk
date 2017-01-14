# -*- coding: utf-8 -*

##
#  novelWriter – Main GUI Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Sets up the main GUI and holds action and event functions
##

import logging as logger

import gi
gi.require_version("Gtk","3.0")

from gi.repository  import Gtk, GLib
from os             import path
from nw             import *
from nw.editor      import Editor
from nw.bookeditor  import BookEditor
from nw.filetrees   import SceneTree
from nw.timer       import Timer
from nw.book        import Book

class GUI():

    def __init__(self):

        self.guiLoaded  = False

        # Define Core Objects
        self.mainConf   = CONFIG
        self.guiBuilder = BUILDER

        self.getObject  = self.guiBuilder.get_object
        self.winMain    = self.getObject("winMain")

        # Prepare GUI Classes
        self.theBook    = Book()
        self.guiTimer   = Timer()
        self.webEditor  = Editor(self.guiTimer)
        self.bookEditor = BookEditor()
        self.sceneTree  = SceneTree()

        # Set Up Event Handlers
        guiHandlers = {
            # Main GUI
            "onClickNew"               :  self.onNewBook,
            "onClickOpen"              :  self.onOpenBook,
            "onClickSave"              :  self.onSaveBook,
            "onClickPreferences"       :  self.onEditBook,
            "onClickSceneAdd"          :  self.onSceneAdd,
            "onSelectTreeScene"        :  self.onSceneSelect,
            "onMainTabChange"          :  self.onMainTabChange,
            "onDestroyWindow"          :  self.onGuiDestroy,
            "onMainWinChange"          :  self.onWinChange,
            # WebKit Editor Signals
            "onToggleEditable"         :  self.webEditor.onToggleEditable,
            "onClickEditRefresh"       :  self.webEditor.onEditRefresh,
            "onClickEditUndo"          : (self.webEditor.onEditAction,"undo"),
            "onClickEditRedo"          : (self.webEditor.onEditAction,"redo"),
            "onClickEditCut"           :  self.webEditor.onEditCut,
            "onClickEditCopy"          :  self.webEditor.onEditCopy,
            "onClickEditPaste"         :  self.webEditor.onEditPaste,
            "onClickEditBold"          : (self.webEditor.onEditAction,"bold"),
            "onClickEditItalic"        : (self.webEditor.onEditAction,"italic"),
            "onClickEditUnderline"     : (self.webEditor.onEditAction,"underline"),
            "onClickEditStrikethrough" : (self.webEditor.onEditAction,"strikethrough"),
            "onToggleShowPara"         :  self.webEditor.onShowParagraphs,
            # Book Editor Signals
            "onClickBookCancel"        :  self.bookEditor.onBookCancel,
            "onClickBookSave"          :  self.bookEditor.onBookSave,
        }
        self.guiBuilder.connect_signals(guiHandlers)

        # Set Pane Positions
        self.getObject("panedContent").set_position(self.mainConf.mainPane)
        self.getObject("panedSide").set_position(self.mainConf.sidePane)

        # Prepare Editor
        self.getObject("scrollEditor").add(self.webEditor)
        self.getObject("textSource").set_editable(False)

        # Set Up Timers
        self.timerID    = GLib.timeout_add(200,self.guiTimer.onTick)
        self.autoTaskID = GLib.timeout_add_seconds(self.mainConf.autoSave,self.doAutoTasks)

        ##
        #  Content
        ##

        # Scene Chapter Selector
        adjScene = Gtk.Adjustment(1,1,100,1,1,1)
        numSceneChapter = self.getObject("numSceneChapter")
        numSceneChapter.configure(adjScene,1,0)

        ##
        #  Finalise GUI Setup
        ##

        # Remove Widgets Not In Use Yet
        boxDetails = self.getObject("boxDetails")
        boxDetails.remove(self.getObject("boxCharsNTime"))

        # Prepare Main Window
        self.winMain.set_title(self.mainConf.appName)
        self.winMain.resize(self.mainConf.winWidth,self.mainConf.winHeight)
        self.winMain.set_position(Gtk.WindowPosition.CENTER)
        self.winMain.show_all()

        # Load Last Book
        self.loadBook()

        self.guiLoaded = True

        return

    ##
    #  Load and Save Functions
    ##

    def loadBook(self, bookFolder=None):

        if bookFolder is None:
            bookFolder = self.mainConf.lastBook

        if bookFolder == "":
            return

        logger.debug("GUI.loadBook: Loading book")

        self.theBook.loadBook(bookFolder)
        self.sceneTree.loadContent(self.theBook)
        self.updateWindowTitle()

        return

    def saveBook(self):

        if self.theBook.bookLoaded:
            logger.debug("GUI.saveBook: Saving book")
            self.theBook.saveBook()

        return

    def loadScene(self, sceneHandle):

        logger.debug("GUI.loadScene: Loading scene")

        # Load Scene in Editor
        self.webEditor.loadText(sceneHandle,self.theBook)

        # Load Summary
        tmpBuffer  = self.getObject("textSceneSummary").get_buffer()
        tmpBuffer.set_text(self.theBook.getSceneSummary())

        # Load Scene Data
        scnTitle   = self.theBook.getSceneTitle()
        scnSection = self.theBook.getSceneSection()
        scnChapter = self.theBook.getSceneChapter()
        scnCreated = "Created "+formatDateTime(DATE_DATE,dateFromStamp(self.theBook.getSceneCreated()))
        scnUpdated = "Updated "+formatDateTime(DATE_DATE,dateFromStamp(self.theBook.getSceneUpdated()))
        scnVersion = "Draft %d, Version %d" % (self.theBook.getBookDraft(),self.theBook.getSceneVersion())

        # Set GUI Elements
        self.getObject("lblSceneTitle").set_label(scnTitle)
        self.getObject("lblSceneCreated").set_label(scnCreated)
        self.getObject("lblSceneUpdated").set_label(scnUpdated)
        self.getObject("lblSceneVersion").set_label(scnVersion)
        self.getObject("entrySceneTitle").set_text(scnTitle)
        self.getObject("cmbSceneSection").set_active(scnSection)
        self.getObject("numSceneChapter").set_value(scnChapter)

        self.updateWordCount()

        return

    def saveScene(self):

        logger.debug("GUI.saveScene: Saving scene")

        # Get Scene Values
        prevSection = self.theBook.getSceneSection()
        prevChapter = self.theBook.getSceneChapter()
        prevNumber  = self.theBook.getSceneNumber()
        scnTitle    = self.getObject("entrySceneTitle").get_text()
        scnSection  = self.getObject("cmbSceneSection").get_active()
        scnChapter  = self.getObject("numSceneChapter").get_value()
        scnChapter  = int(scnChapter)

        if scnSection != 2: scnChapter = 0

        scnSort = makeSortString(scnSection,scnChapter,0)
        if scnSort in self.sceneTree.chapCount:
            if scnSection == prevSection and scnChapter == prevChapter:
                scnNumber = prevNumber
            else:
                scnNumber = self.sceneTree.chapCount[scnSort] + 1
        else:
            scnNumber = 1

        # Get Summary Text
        tmpBuffer  = self.getObject("textSceneSummary").get_buffer()
        tmpStart   = tmpBuffer.get_start_iter()
        tmpEnd     = tmpBuffer.get_end_iter()
        scnSummary = tmpBuffer.get_text(tmpStart,tmpEnd,True)

        # Set Scene Data
        self.theBook.setSceneTitle(scnTitle)
        self.theBook.setSceneSection(scnSection)
        self.theBook.setSceneChapter(scnChapter)
        self.theBook.setSceneNumber(scnNumber)
        self.theBook.setSceneSummary(scnSummary)

        self.webEditor.saveText()
        self.sceneTree.loadContent(self.theBook)
        self.updateWordCount()
        
        return

    def loadSourceView(self):

        scnText = self.webEditor.getText()
        self.theBook.setSceneText(scnText)
        scnText = self.theBook.getSceneText()

        tmpBuffer = self.getObject("textSource").get_buffer()
        tmpBuffer.set_text(scnText)

        return

    ##
    #  Update Functions
    ##

    def updateWordCount(self):

        wordCount    = self.theBook.getSceneWords()

        sessionWords = str(wordCount[COUNT_ADDED])
        totalWords   = str(wordCount[COUNT_LATEST])

        self.getObject("lblWordsSessionValue").set_label(sessionWords)
        self.getObject("lblWordsTotalValue").set_label(totalWords)

        self.sceneTree.sumWords()

        return

    def updateWindowTitle(self):
        
        appName   = self.mainConf.appName
        bookTitle = self.theBook.getBookTitle()
        bookDraft = self.theBook.getBookDraft()

        if self.theBook.bookLoaded:
            winTitle = "%s - %s (Draft %d)" % (appName,bookTitle,bookDraft)
            self.getObject("winMain").set_title(winTitle)

        return

    ##
    #  Main ToolBar Button Events
    ##

    def onNewBook(self, guiObject):
        self.bookEditor.dlgWin.show()
        return

    def onOpenBook(self, guiObject):

        guiDialog = Gtk.FileChooserDialog("Open Book Folder",None,Gtk.FileChooserAction.SELECT_FOLDER,(
            Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        guiDialog.set_default_response(Gtk.ResponseType.OK)

        dlgReturn = guiDialog.run()
        if dlgReturn == Gtk.ResponseType.OK:
            self.loadBook(guiDialog.get_filename())

        guiDialog.destroy()

        return

    def onSaveBook(self, guiObject):
        self.saveBook()
        self.saveScene()
        return

    def onEditBook(self, guiObject):
        self.bookEditor.loadEditor(self.theBook)
        self.bookEditor.dlgWin.show()
        return

    ##
    #  Scene ToolBar Button Events
    ##

    def onSceneAdd(self, guiObject):
        scnSort  = makeSortString(0,0,0)
        sceneNum = self.sceneTree.chapCount[scnSort] + 1
        self.theBook.createScene("New Scene",sceneNum)
        #~ self.theBook.makeIndex()
        self.sceneTree.loadContent(self.theBook)
        return

    def onSceneSelect(self, guiObject):

        logger.debug("GUI.onSceneSelect: Select scene")

        itemHandle = ""

        listModel, pathList = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,self.sceneTree.COL_HANDLE)

        if itemHandle == "" or itemHandle is None: return

        self.loadScene(itemHandle)

        return

    ##
    #  Main Window Events
    ##

    def onMainTabChange(self, guiObject, guiChild, tabIdx):
        logger.debug("GUI.onMainTabChange: Main tab change")
        if tabIdx == MAIN_DETAILS:
            return
        if tabIdx == MAIN_EDITOR:
            return
        if tabIdx == MAIN_SOURCE:
            self.loadSourceView()
        return

    def onGuiDestroy(self, guiObject):

        logger.debug("GUI.onGuiDestroy: Exiting")

        mainPane = self.getObject("panedContent").get_position()
        sidePane = self.getObject("panedSide").get_position()
        self.mainConf.setMainPane(mainPane)
        self.mainConf.setSidePane(sidePane)
        self.mainConf.saveConfig()

        if self.theBook.bookLoaded:
            self.guiTimer.stopTimer()
            self.theBook.saveTiming(self.guiTimer.sessionTime)
            self.webEditor.saveText()

        Gtk.main_quit()

        return

    def onWinChange(self, guiObject, guiEvent):
        self.mainConf.setWinSize(guiEvent.width,guiEvent.height)
        return

    def doAutoTasks(self):
        self.mainConf.doAutoSave()
        self.webEditor.doAutoSave()
        self.updateWordCount()
        return True

# End Class GUI
