# -*- coding: utf-8 -*

##
#  novelWriter – Data Wrapper Init File
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Data Wrapper initialisation
##

import logging as logger

from os                   import path, mkdir, listdir
from time                 import time
from hashlib              import sha256
from nw                   import *
from nw.book.scene        import Scene
from nw.book.bookopt      import BookOpt
from nw.book.bookmeta     import BookMeta
from nw.book.scenemeta    import SceneMeta
from nw.book.scenetext    import SceneText
from nw.book.scenesummary import SceneSummary
from nw.book.scenetiming  import SceneTiming

class Book():

    def __init__(self):

        """
        Description:
            Creates meta object and scene object.
            Links sub class functions.
        """

        # Core Objects
        self.mainConf  = CONFIG
        self.theOpt    = BookOpt()
        self.theMeta   = BookMeta(self.theOpt)
        self.allScenes = {}

        # Runtime Attributes
        self.bookLoaded = False

        # Connect to Scene Functions
        # self.createScene     = self.theScene.createScene
        # self.loadScene       = self.theScene.loadScene
        # self.closeScene      = self.theScene.closeScene
        # self.saveScene       = self.theScene.saveScene
        # self.saveTiming      = self.theScene.theTiming.saveTiming

        # Connect to Setters
        self.setBookTitle    = self.theMeta.setTitle
        self.setBookAuthor   = self.theMeta.setAuthor
        self.setBookRecent   = self.theMeta.setRecent
        # self.setBookFolder   = self.theOpt.setBookFolder
        # self.setBookDraft    = self.theOpt.setBookDraft
        # self.setSceneTitle   = self.theScene.theMeta.setTitle
        # self.setSceneSection = self.theScene.theMeta.setSection
        # self.setSceneChapter = self.theScene.theMeta.setChapter
        # self.setSceneNumber  = self.theScene.theMeta.setNumber
        # self.setSceneText    = self.theScene.theText.setText
        # self.setSceneSummary = self.theScene.theSummary.setSummary
        # self.setSceneTime    = self.theScene.theTiming.setTime

        # Connect to Getters
        self.getBookTitle    = self.theMeta.getTitle
        self.getBookAuthor   = self.theMeta.getAuthor
        self.getBookRecent   = self.theMeta.getRecent
        self.getBookFolder   = self.theOpt.getBookFolder
        self.getBookDraft    = self.theOpt.getBookDraft
        self.getSceneIndex   = self.theOpt.getSceneIndex
        # self.getSceneHandle  = self.theOpt.getSceneHandle
        # self.getSceneVersion = self.theOpt.getSceneVersion
        # self.getSceneTitle   = self.theScene.theMeta.getTitle
        # self.getSceneSection = self.theScene.theMeta.getSection
        # self.getSceneCreated = self.theScene.theMeta.getCreated
        # self.getSceneUpdated = self.theScene.theMeta.getUpdated
        # self.getSceneChapter = self.theScene.theMeta.getChapter
        # self.getSceneNumber  = self.theScene.theMeta.getNumber
        # self.getSceneWords   = self.theScene.theMeta.getWords
        # self.getSceneChars   = self.theScene.theMeta.getChars
        # self.getSceneChanged = self.theScene.theMeta.getSceneChanged
        # self.getSceneText    = self.theScene.theText.getText
        # self.getSceneWords   = self.theScene.theText.getWordCount
        # self.getSceneChars   = self.theScene.theText.getCharCount
        # self.getSceneSummary = self.theScene.theSummary.getSummary
        # self.getSceneTime    = self.theScene.theTiming.getTimeTotal

        # Connect to Methods
        # self.makeSceneIndex  = self.theScene.makeIndex
        # self.countWords      = self.theScene.theText.countWords
        # self.htmlCleanUp     = self.theScene.theText.htmlCleanUp

        return

    ##
    #  Create, Load and Save Book
    ##

    def clearContent(self):

        """
        Description:
            Clears book options
            Clears book metadata
            Clears scene content
        """

        logger.debug("Book.clearContent: Clearing content")

        # Clear Objects
        self.theOpt.clearContent()
        self.theMeta.clearContent()
        self.theScene.clearContent()

        self.bookLoaded = False

        return

    def createBook(self, rootFolder):

        """
        Description:
            Requires book title to be set.
            Close current book, if any
            Creates a folder based on the book title.
            Sets the draft number to 1, which will ensure the folder is created when metadata is reloaded.
            Saves the book, and reloads it causing the metadata file to be written and indices to be updated.
        """

        bookTitle = self.getBookTitle()
        if bookTitle == "":
            logger.debug("Book.createBook: Set title before creating new book")
            return

        self.closeBook()

        bookFolder = path.join(rootFolder,bookTitle)
        if not path.isdir(bookFolder):
            mkdir(bookFolder)
            logger.debug("Book.createBook: Created folder %s" % bookFolder)

        self.theOpt.setBookFolder(bookFolder)
        self.theOpt.setBookDraft(1)
        self.saveBook()

        return

    def loadBook(self, bookFolder):

        """
        Description:
            Closes the current book
            Sets the current book folder and checks that it's valid.
            Generates book index which looks for draft folders and sets the draft to load to the latest.
            Generates scene index from the latest draft folder.
            If a recent scene is listed, load it
            Sets last loaded book in config
        """

        logger.debug("Book.loadBook: Loading book from %s" % bookFolder)

        # Close Current Book
        if self.bookLoaded:
            self.closeBook()

        # Set Current Book Folder
        self.theOpt.setBookFolder(bookFolder)
        if self.theOpt.bookFolder is None:
            logger.debug("Book.loadBook: Path not found %s" % bookFolder)
            return

        # Scan Book Folder
        self.makeDraftIndex()
        self.theMeta.loadData()

        lastDraft = self.theOpt.getLastDraft()
        self.changeDraftFolder(lastDraft)

        self.makeSceneIndex()

        self.mainConf.setLastBook(bookFolder)
        self.bookLoaded = self.theMeta.bookLoaded

        return

    def closeBook(self):

        """
        Description:
            Check if a book is loaded
            Save current book and scene (close scene)
            Clear content
        """

        if not self.bookLoaded:
            logger.debug("Book.closeBook: No book loaded")
            return

        logger.debug("Book.closeBook: Closing book")

        self.saveBook()
        for sceneHandle in self.allScenes.keys():
            self.closeScene(sceneHandle)

        return

    def saveBook(self):

        """
        Description:
            Saves meta data. Scene data must be saved separately.
        """

        logger.debug("Book.saveBook: Saving book")
        self.theMeta.saveData()

        return

    ##
    #  Create, Load and Save Scene
    ##

    def createScene(self, sceneTitle, sceneNumber):

        """
        Description:
            Generate new scene handle
            Add new scene instance
            Append new scene to scene index
        """

        sceneHandle = sha256(str(time()).encode()).hexdigest()[0:12]
        self.allScenes[sceneHandle]  = Scene(self.theOpt,sceneHandle)
        self.theOpt.setSceneIndexEntry(sceneHandle,[sceneTitle,sceneNumber,0,0,0,1])

        return

    def loadScene(self, sceneHandle, metaOnly=False, skipVerify=False, readOnly=False):

        if not self.theOpt.isValidHandle(sceneHandle) and not skipVerify:
            logger.debug("Book.loadScene: Invalid scene handle %s" % sceneHandle)
            return

        if sceneHandle in self.allScenes.keys():
            logger.debug("Book.loadScene: Scene %s already loaded" % sceneHandle)
            return

        logger.debug("Book.loadScene: Loading scene %s" % sceneHandle)

        self.allScenes[sceneHandle] = Scene(self.theOpt,sceneHandle)
        self.allScenes[sceneHandle].loadScene(metaOnly,readOnly)

        return

    def saveScene(self, sceneHandle, saveAll=False):
        logger.debug("Book.saveScene: Saving scene %s" % sceneHandle)
        self.allScenes[sceneHandle].saveScene(saveTiming)
        return

    def closeScene(self, sceneHandle):
        logger.debug("Book.closeScene: Closing scene %s" % sceneHandle)
        self.allScenes[sceneHandle].saveScene(True)
        self.allScenes.pop(sceneHandle,None)
        self.theOpt.removeSceneIndexEntry(sceneHandle)
        return

    ##
    #  Methods
    ##

    def makeDraftIndex(self):

        bookIndex  = {}
        bookFolder = self.theOpt.bookFolder

        if bookFolder is None:
            logger.debug("Book.makeDraftIndex: Path not found %s" % bookFolder)
            return

        logger.debug("Book.makeDraftIndex: Scanning folder %s" % bookFolder)

        dirContent = listdir(bookFolder)
        for listItem in dirContent:
            itemPath = path.join(bookFolder,listItem)
            if path.isdir(itemPath):
                if listItem[:5] == "Draft":
                    bookDraft = int(listItem[6:])
                    bookIndex[bookDraft] = [listItem,0]

        self.theOpt.setBookIndex(bookIndex)
        # self.theOpt.setBookDraft(len(bookIndex))

        return

    def makeSceneIndex(self):

        sceneIndex  = {}
        sceneFolder = self.theOpt.sceneFolder

        if sceneFolder is None:
            logger.debug("Book.makeSceneIndex: Path not found %s" % sceneFolder)
            return

        logger.debug("Book.makeSceneIndex: Scanning folder %s" % sceneFolder)

        dirContent = listdir(sceneFolder)

        # Scene Book Folder
        for listItem in dirContent:
            itemPath = path.join(sceneFolder,listItem)
            if path.isfile(itemPath):
                if len(listItem) == 25 and listItem[-12:] == "metadata.cnf":
                    itemHandle = listItem[:12]
                    self.loadScene(itemHandle,True,True,True)
                    sceneIndex[itemHandle] = [
                        self.allScenes[itemHandle].getTitle(),
                        self.allScenes[itemHandle].getNumber(),
                        self.allScenes[itemHandle].getWords(),
                        self.allScenes[itemHandle].getSection(),
                        self.allScenes[itemHandle].getChapter(),
                        0
                    ]
                    self.closeScene(itemHandle)

        # Count File Versions
        for listItem in dirContent:
            itemPath = path.join(sceneFolder,listItem)
            if path.isfile(itemPath):
                if len(listItem) > 18 and listItem[12:19] == "-scene-" and listItem[-3:] == "txt":
                    itemHandle = listItem[:12]
                    sceneIndex[itemHandle][SCIDX_COUNT] += 1

        self.theOpt.setSceneIndex(sceneIndex)

        return

    def changeDraftFolder(self, bookDraft):

        if bookDraft < 1:
            logger.debug("Book.prepareDraftFolder: Invalid book draft. Set to 1")
            bookDraft = 1

        logger.debug("Book.changeDraftFolder: Loading Draft %d" % bookDraft)

        sceneFolder = path.join(self.theOpt.bookFolder,"Draft %d" % bookDraft)
        if not path.isdir(sceneFolder):
            mkdir(sceneFolder)

        self.theOpt.setBookDraft(bookDraft)
        self.theOpt.setSceneFolder(sceneFolder)

        return

# End Class Book
