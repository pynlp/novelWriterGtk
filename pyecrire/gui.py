# -*- coding: utf-8 -*

##
#  pyÉcrire – Main GUI Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Sets up the main GUI and holds action and event functions
##

import logging as logger

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')

from gi.repository        import Gtk, GLib, WebKit
from time                 import sleep
from pyecrire.constants   import *
from pyecrire.editor      import Editor
from pyecrire.timer       import Timer
from pyecrire.project     import Project
from pyecrire.treeviews   import *
from pyecrire.datalist    import DataList
from pyecrire.datawrapper import DataWrapper
from pyecrire.functions   import makeTimeStamp

class GUI():

    def __init__(self, config):

        self.guiLoaded = False

        # Define Core Objects
        self.mainConf   = config
        self.projData   = Project(self.mainConf)

        # Initialise GUI
        self.guiBuilder = Gtk.Builder()
        self.guiBuilder.add_from_file("pyecrire/gui/winMain.glade")

        self.getObject  = self.guiBuilder.get_object
        self.winMain    = self.getObject("winMain")

        # Prepare GUI Classes
        self.webEditor  = Editor(self.guiBuilder,self.mainConf)
        self.guiTimer   = Timer(self.guiBuilder,self.mainConf)
        self.projTree   = ProjectTree(self.guiBuilder,self.mainConf)
        self.bookTree   = BookTree(self.guiBuilder,self.mainConf)
        self.univTree   = UniverseTree(self.guiBuilder,self.mainConf)
        self.scneTree   = SceneTree(self.guiBuilder,self.mainConf)
        self.fileTree   = FileVersionTree(self.guiBuilder,self.mainConf)

        # Set Up Event Handlers
        guiHandlers = {
            "onDestroyWindow"          : self.guiDestroy,
            "onEventKeyPress"          : self.eventWinKeyPress,
            "onEventWinChange"         : self.eventWinChange,
            "onSwitchPageMainNoteBook" : self.eventMainTabChange,
            "onSwitchPageSideNoteBook" : self.eventSideTabChange,
            "onChangeTreeProject"      : self.onSelectBook,
            "onChangeTreeBook"         : self.onSelectBookFile,
            "onChangeTreeUniverse"     : self.onSelectUniverseFile,
            "onChangeTreeFileVersion"  : self.onSelectFileVersion,
            "onClickNew"               : self.projData.newProject,
            "onClickSave"              : self.onFileSave,
            "onToggleEditable"         : self.webEditor.onToggleEditable,
            "onClickEditBold"          : self.webEditor.onEditAction,
            "onClickEditItalic"        : self.webEditor.onEditAction,
            "onClickEditUnderline"     : self.webEditor.onEditAction,
            "onClickEditStrikeThrough" : self.webEditor.onEditAction,
            "onClickEditColour"        : self.webEditor.onEditColour,
            "onClickTimerStart"        : self.guiTimer.onTimerStart,
            "onClickTimerPause"        : self.guiTimer.onTimerPause,
            "onClickTimerStop"         : self.guiTimer.onTimerStop,
            "onClickSceneAdd"          : self.onSceneAdd,
            "onClickSceneRemove"       : self.onSceneRemove,
            "onClickSceneUp"           : self.onSceneUp,
            "onClickSceneDown"         : self.onSceneDown,
            "onClickSceneSave"         : self.onSceneSave,
            "onChangeTreeScenes"       : self.onSelectScene,
            "onToggleNewUniverse"      : self.onToggleNewUniverse,
            "onMenuActionHelpAbout"    : self.onActionShowAbout,
            "onMenuActionFileSave"     : self.onFileSave,
            "onMenuActionFileQuit"     : self.guiDestroy,
        }
        self.guiBuilder.connect_signals(guiHandlers)

        # Prepare Panes
        self.guiPaned     = self.getObject("innerPaned")
        self.guiPaned.set_position(self.mainConf.winPane)

        # Prepare Editor
        self.scrollEditor = self.getObject("scrollEditor")
        self.scrollEditor.add(self.webEditor)

        # Prepare Statusbar
        self.statusBar  = self.getObject("mainStatus")
        self.statusCID  = self.statusBar.get_context_id("Main")
        self.progStatus = self.getObject("progressStatus")

        # Set Up Timers
        self.timerID    = GLib.timeout_add(200,self.guiTimer.onTick)
        self.autoTaskID = GLib.timeout_add_seconds(30,self.autoTasks)

        ##
        #  Content
        ##

        # Gtk ListStore and TreeStore
        self.bookType   = Gtk.ListStore(str)

        # Scenes Chapter Selector
        adjScene = Gtk.Adjustment(1,1,100,1,1,1)
        numSceneChapter = self.getObject("numSceneChapter")
        numSceneChapter.configure(adjScene,1,0)

        # Book Details Universe List
        cmbDetailsBookUniverse  = self.getObject("cmbBookUniverse")
        cmbDetailsBookUniverse.set_model(self.projTree.listUnivs)

        # Load Project Data
        self.projTree.loadContent()
        self.bookTree.loadContent(None)
        self.univTree.loadContent(None)

        # Prepare Main Window
        self.winMain.set_title(self.mainConf.appName)
        self.winMain.resize(self.mainConf.winWidth,self.mainConf.winHeight)
        self.winMain.set_position(Gtk.WindowPosition.CENTER)
        self.winMain.show_all()

        self.guiLoaded = True

        return

    # Close Program
    def guiDestroy(self, guiObject):
        logger.debug("Exiting")
        self.mainConf.setWinPane(self.guiPaned.get_position())
        self.mainConf.autoSaveConfig()
        Gtk.main_quit()
        return

    # Automated Tasks
    def autoTasks(self):

        statusBar = self.getObject("mainStatus")
        statusCID = self.statusBar.get_context_id("File")

        saveConf = self.mainConf.autoSaveConfig()

        self.projData.theFile.setText(self.webEditor.getText())
        saveText = self.projData.theFile.autoSaveText()

        if saveConf: statusBar.push(statusCID,makeTimeStamp(4)+" Config auto-saved")
        if saveText: statusBar.push(statusCID,makeTimeStamp(4)+" Current file auto-saved")

        if saveText: self.fileTree.loadContent(self.projData.theFile.fileList)

        return True

    ##
    #  Tree Selection Actions
    ##

    def onSelectBook(self, guiObject):

        logger.debug("Select Book")
        if not self.guiLoaded: return

        (listModel, pathList) = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,3)

        if len(pathItem) == 1:
            self.getObject("treeProject").expand_row(pathItem,False)

        if len(pathItem) == 2:
            parIter   = listModel.get_iter(pathItem[0])
            parHandle = listModel.get_value(parIter,3)
            itemPath  = self.projTree.getPath(itemHandle)
            parPath   = self.projTree.getPath(parHandle)
            self.projData.loadProject(itemPath,itemHandle,parPath,parHandle)
            self.displayBook()
            self.scneTree.loadContent(itemPath)

        return

    def onSelectBookFile(self, guiObject):

        logger.debug("Select File")
        if not self.guiLoaded: return

        itemHandle = ""

        (listModel, pathList) = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,3)

        if itemHandle == "" or itemHandle is None: return

        # If the file is a book tree file, load it
        filePath = self.bookTree.getPath(itemHandle)
        fileType = self.bookTree.getType(itemHandle)
        if filePath is not None:
            self.projData.newFile(fileType)
            self.projData.loadFile(filePath,itemHandle)
            self.projData.theFile.loadText()
            self.fileTree.loadContent(self.projData.theFile.fileList)
            self.webEditor.setText(self.projData.theFile.text)
            self.getObject("mainNoteBook").set_current_page(TABM_EDIT)

        return

    def onSelectUniverseFile(self, guiObject):
        return

    def onSelectScene(self, guiObject):

        logger.debug("Select Scene")
        if not self.guiLoaded: return

        itemHandle = ""

        (listModel, pathList) = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,5)

        if itemHandle == "" or itemHandle is None: return

        filePath = self.scneTree.getPath(itemHandle)
        self.projData.newFile(NAME_SCNE)
        self.projData.loadFile(filePath,itemHandle)
        self.updateSceneDetails()

        return

    def onSelectFileVersion(self, guiObject):

        logger.debug("Select File Version")
        if not self.guiLoaded: return

        (listModel, pathList) = guiObject.get_selected_rows()
        for pathItem in pathList:
            listIter   = listModel.get_iter(pathItem)
            itemHandle = listModel.get_value(listIter,1)

        if itemHandle == "" or itemHandle is None: return

        itemPath = self.projData.theFile.getFilePath(itemHandle)

        self.projData.theFile.setLoadFile(itemPath)
        self.projData.theFile.loadText()
        self.webEditor.setText(self.projData.theFile.text)
        self.webEditor.setEditable(False)

        return

    ##
    #  Form Content
    ##

    def displayBook(self):

        self.getObject("entryBookTitle").set_text(self.projData.bookTitle)
        self.getObject("cmbBookUniverse").set_active_iter(self.projTree.univMap[self.projData.theBook.parent])

        return

    def updateSceneDetails(self):

        self.getObject("entrySceneTitle").set_text(self.projData.fileTitle)
        self.getObject("cmbSceneSection").set_active(self.projData.theFile.section)
        self.getObject("numSceneChapter").set_value(self.projData.theFile.chapter)

        return

    ##
    #  Main Button Actions
    ##

    def onFileSave(self, guiObject):

        logger.debug("Saving")

        guiPage = self.getObject("mainNoteBook").get_current_page()

        if guiPage == TABM_BOOK:

            bookTitle      = self.getObject("entryBookTitle").get_text()
            chkNewUniverse = self.getObject("chkNewUniverse")

            self.projData.createBook(bookTitle)

            if chkNewUniverse.get_active():
                univTitle = self.getObject("entryBookUniverse").get_text()
                self.projData.createUniverse(univTitle)
            else:
                univIdx  = self.getObject("cmbBookUniverse").get_active()
                univItem = self.univList[univIdx]
                self.projData.setUniverse(univItem[1],self.allUniverses.getItem(univItem[1]))

            self.projData.saveProject()

        if guiPage == TABM_EDIT:

            self.projData.theFile.setText(self.webEditor.getText())
            self.projData.theFile.saveText()
            self.fileTree.loadContent(self.projData.theFile.fileList)

        return

    ##
    #  Menu Action
    ##

    def onActionShowAbout(self, guiObject):

        dlgAbout = Gtk.AboutDialog()
        dlgAbout.set_transient_for(self.winMain)
        dlgAbout.set_program_name(self.mainConf.appName)
        dlgAbout.set_version(self.mainConf.appVersion)
        dlgAbout.set_website(self.mainConf.appURL)
        dlgAbout.run()
        dlgAbout.destroy()

        return

    ##
    #  Scene Settings Action Buttons
    ##

    def onSceneAdd(self, guiObject):

        if self.projData.bookHandle == "": return

        scnSort  = makeSceneNumber(1,0,0,0)
        sceneNum = self.scneTree.chapCount[scnSort] + 1

        self.projData.newFile(NAME_SCNE)
        self.projData.createFile("New Scene")
        self.projData.setFileParent(NAME_BOOK)
        self.projData.setFileNumber(sceneNum)
        self.projData.saveFile()

        self.scneTree.loadContent(self.projData.bookPath)
        if self.getObject("sideNoteBook").get_current_page() == TABS_BOOK:
            self.bookTree.loadContent(self.projData.bookPath)

        return

    def onSceneRemove(self, guiObject):
        return

    def onSceneUp(self, guiObject):
        return

    def onSceneDown(self, guiObject):
        return

    def onSceneSave(self, guiObject):

        logger.debug("Scene save clicked")

        prevSection = self.projData.theFile.section
        prevChapter = self.projData.theFile.chapter
        prevNumber  = self.projData.theFile.number

        scnTitle    = self.getObject("entrySceneTitle").get_text()
        scnSection  = self.getObject("cmbSceneSection").get_active()
        scnChapter  = self.getObject("numSceneChapter").get_value()
        scnPOV      = self.getObject("cmbSceneCharacter").get_active_text()

        if scnSection != 2: scnChapter = 0

        scnSort = makeSceneNumber(GRP_SCNE,scnSection,scnChapter,0)
        if scnSort in self.scneTree.chapCount:
            if scnSection == prevSection and scnChapter == prevChapter:
                scnNumber = prevNumber
            else:
                scnNumber = self.scneTree.chapCount[scnSort] + 1
        else:
            scnNumber = 1

        self.projData.setSceneSettings(scnTitle,scnSection,scnChapter,scnNumber,scnPOV,"")
        self.projData.saveFile()

        self.scneTree.loadContent(self.projData.bookPath)
        if self.getObject("sideNoteBook").get_current_page() == TABS_BOOK:
            self.bookTree.loadContent(self.projData.bookPath)

        return

    ##
    #  Tab Changes
    ##

    def eventMainTabChange(self, guiObject, guiChild, tabIdx):
        logger.debug("Tab change")
        if tabIdx == TABM_SRCE:
            print("Source View")
            strSource = self.webEditor.getHtml()
            bufferSource = Gtk.TextBuffer()
            bufferSource.set_text(strSource)
            textSource = self.getObject("textSource")
            textSource.set_buffer(bufferSource)
            print(strSource)
        return

    def eventSideTabChange(self, guiObject, guiChild, tabIdx):
        logger.debug("Tree tab change")
        if tabIdx == TABS_PROJ:
            self.getObject("mainNoteBook").set_current_page(TABM_BOOK)
        if tabIdx == TABS_BOOK:
            self.bookTree.loadContent(self.projData.bookPath)
        if tabIdx == TABS_UNIV:
            self.univTree.loadContent(self.projData.univPath)
        return

    ##
    #  Main Window Events
    ##

    def eventWinKeyPress(self, guiObject, guiEvent):
        self.guiTimer.resetAutoPause()
        return

    def eventWinChange(self, guiObject, guiEvent):
        self.mainConf.setWinSize(guiEvent.width,guiEvent.height)
        return

    def onToggleNewUniverse(self, guiObject):
        if guiObject.get_active():
            self.getObject("entryBookUniverse").set_can_focus(True)
        else:
            self.getObject("entryBookUniverse").set_can_focus(False)
        return

# End Class GUI
