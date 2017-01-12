# -*- coding: utf-8 -*

##
#  novelWriter – Main GUI Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Sets up the main GUI and holds action and event functions
##

import logging as logger

import gi
gi.require_version("Gtk","3.0")

from gi.repository  import Gtk
from os             import path
from nw             import *
from nw.editor      import Editor
from nw.bookeditor  import BookEditor
from nw.datawrapper import BookData, SceneData
from nw.filetrees   import SceneTree

class GUI():

    def __init__(self):

        self.guiLoaded  = False

        # Define Core Objects
        self.mainConf   = CONFIG
        self.guiBuilder = BUILDER

        self.getObject  = self.guiBuilder.get_object
        self.winMain    = self.getObject("winMain")

        # Data Files
        self.theBook    = BookData()

        # Prepare GUI Classes
        self.guiTimer   = None #Timer()
        self.webEditor  = Editor(self.guiTimer)
        self.bookEditor = BookEditor(self.theBook)
        self.sceneTree  = SceneTree()

        # Set Up Event Handlers
        guiHandlers = {
            "onClickNew"         : self.onNewBook,
            "onClickOpen"        : self.onOpenBook,
            "onClickSave"        : self.onSaveBook,
            "onClickPreferences" : self.onEditBook,
            "onClickSceneAdd"    : self.onSceneAdd,
            "onSelectTreeScene"  : self.onSceneSelect,
            "onDestroyWindow"    : self.onGuiDestroy,
            "onMainWinChange"    : self.onWinChange,

            "onClickBookCancel"  : self.bookEditor.onBookCancel,
            "onClickBookSave"    : self.bookEditor.onBookSave,
        }
        self.guiBuilder.connect_signals(guiHandlers)

        # Set Panes
        self.getObject("panedContent").set_position(self.mainConf.mainPane)
        self.getObject("panedSide").set_position(self.mainConf.sidePane)

        # Prepare Editor
        self.getObject("scrollEditor").add(self.webEditor)

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

    def loadBook(self):

        logger.debug("Loading Book")

        self.theBook = BookData()
        self.theBook.loadBook(self.mainConf.lastBook)
        self.sceneTree.loadContent(self.theBook)

        if self.theBook.bookLoaded:
            winTitle = self.mainConf.appName+" – "+self.theBook.bookTitle
            self.getObject("winMain").set_title(winTitle)
        
        return

    def saveBook(self):

        if self.theBook.bookLoaded:
            logger.debug("Saving Book")
            self.theBook.saveBook()

        return

    def loadScene(self, sceneHandle):

        self.theBook.loadScene(sceneHandle)
        self.webEditor.setText(self.theBook.getText())

        scnTitle   = self.theBook.getFileTitle()
        scnCreated = "Created "+formatDateTime(DATE_DATE,dateFromStamp(self.theBook.getFileCreated()))
        scnUpdated = "Updated "+formatDateTime(DATE_DATE,dateFromStamp(self.theBook.getFileUpdated()))
        scnVersion = "Draft %d, Version %d" % (self.theBook.bookDraft,self.theBook.getFileVersion())

        self.getObject("lblSceneTitle").set_label(scnTitle)
        self.getObject("lblSceneCreated").set_label(scnCreated)
        self.getObject("lblSceneUpdated").set_label(scnUpdated)
        self.getObject("lblSceneVersion").set_label(scnVersion)

        self.updateWordCount()

        return

    def saveScene(self):
        return

    ##
    #  Update Functions
    ##

    def updateWordCount(self):

        sessionWords = str(self.theBook.theScene.theText.wordsAdded)
        totalWords   = str(self.theBook.theScene.theText.wordsLatest)

        self.getObject("lblWordsSessionValue").set_label(sessionWords)
        self.getObject("lblWordsTotalValue").set_label(totalWords)

        return

    ##
    #  Main ToolBar Button Events
    ##

    def onNewBook(self, guiObject):
        self.bookEditor.dlgWin.show()
        return

    def onOpenBook(self, guiObject):
        return

    def onSaveBook(self, guiObject):
        self.saveBook()
        return

    def onEditBook(self, guiObject):
        self.bookEditor.loadEditor()
        self.bookEditor.dlgWin.show()
        return

    ##
    #  Scene ToolBar Button Events
    ##

    def onSceneAdd(self, guiObject):
        self.theBook.makeNewScene("New Scene")
        return

    def onSceneSelect(self, guiObject):

        logger.debug("GUI: Select Scene")

        itemHandle = ""

        (listModel, pathList) = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,self.sceneTree.COL_HANDLE)

        if itemHandle == "" or itemHandle is None: return

        self.loadScene(itemHandle)

        return

    ##
    #  Main Window Events
    ##

    # Close Program
    def onGuiDestroy(self, guiObject):
        logger.debug("Exiting")
        mainPane = self.getObject("panedContent").get_position()
        sidePane = self.getObject("panedSide").get_position()
        self.mainConf.setMainPane(mainPane)
        self.mainConf.setSidePane(sidePane)
        self.mainConf.saveConfig()
        Gtk.main_quit()
        return

    def onWinChange(self, guiObject, guiEvent):
        self.mainConf.setWinSize(guiEvent.width,guiEvent.height)
        return

# End Class GUI
