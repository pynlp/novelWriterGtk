# -*- coding: utf-8 -*

##
#  novelWriter – Scene Tree Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Wrapper class for the scene tree in the main GUI.
##

import logging as logger

import gi
gi.require_version("Gtk","3.0")

from gi.repository import Gtk
from nw            import *

# Set to true to show sorting in all treeviews
debugShowSort = False

class SceneTree():

    def __init__(self):

        """
        Tree Store Structure:
        Col 1 : String : Scene title
        Col 2 : String : Scene number
        Col 3 : String : Word count
        Col 4 : String : List sorting column
        Col 5 : String : File handle
        """

        # Constants
        self.COL_TITLE  = 0
        self.COL_NUMBER = 1
        self.COL_WORDS  = 2
        self.COL_SORT   = 3
        self.COL_HANDLE = 4

        # Connect to GUI
        self.mainConf   = CONFIG
        self.getObject  = BUILDER.get_object

        # Core objects
        self.treeView   = self.getObject("treeScenes")
        self.treeSelect = self.getObject("treeScenesSelect")
        self.treeStore  = Gtk.TreeStore(str,str,str,str,str)
        self.treeSort   = Gtk.TreeModelSort(model=self.treeStore)

        # Data Sorting
        self.treeSort.set_sort_column_id(3,Gtk.SortType.ASCENDING)
        self.treeView.set_model(self.treeSort)

        # Columns
        cellCol0 = Gtk.CellRendererText()
        cellCol1 = Gtk.CellRendererText()
        cellCol2 = Gtk.CellRendererText()
        treeCol0 = self.treeView.get_column(0)
        treeCol1 = self.treeView.get_column(1)
        treeCol2 = self.treeView.get_column(2)

        treeCol0.pack_start(cellCol0,True)
        treeCol1.pack_start(cellCol1,False)
        treeCol2.pack_start(cellCol2,False)
        treeCol0.add_attribute(cellCol0,"text",0)
        treeCol1.add_attribute(cellCol1,"text",1)
        treeCol2.add_attribute(cellCol2,"text",2)
        treeCol0.set_attributes(cellCol0,markup=0)
        treeCol2.set_attributes(cellCol2,markup=2)

        cellCol2.set_alignment(1.0,0.5)

        # Enable to Show Sorting
        if debugShowSort:
            cellCol3 = Gtk.CellRendererText()
            treeCol3 = self.treeView.get_column(3)
            treeCol3.set_visible(True)
            treeCol3.pack_start(cellCol3,False)
            treeCol3.add_attribute(cellCol3,"text",3)

        # Data Maps and Lists
        self.iterMap   = {}
        self.chapMap   = {}
        self.chapCount = {}

        return

    def loadContent(self, theBook):

        self.treeSelect.set_mode(Gtk.SelectionMode.NONE)
        self.treeStore.clear()

        if not theBook.bookLoaded:
            logger.debug("SceneTree.loadContent: No book loaded")
            return

        self.iterMap   = {}
        self.chapMap   = {}
        self.chapCount = {}

        self.chapCount[makeSortString(0,0,0)] = 0
        sceneIndex = theBook.getSceneIndex()

        for itemHandle in sceneIndex.keys():

            itemData   = sceneIndex[itemHandle]

            tmpTitle   = itemData[SCIDX_TITLE]
            tmpWords   = itemData[SCIDX_WORDS]
            tmpSection = itemData[SCIDX_SECTION]
            tmpChapter = itemData[SCIDX_CHAPTER]
            tmpNumber  = itemData[SCIDX_NUMBER]

            scnNum     = makeSortString(tmpSection,tmpChapter,tmpNumber)
            scnSec     = makeSortString(tmpSection,tmpChapter,0)

            if scnSec in self.chapMap:
                parIter = self.chapMap[scnSec]
                self.chapCount[scnSec] += 1
            else:
                if tmpSection == SCN_NONE: scnChapter = "<b>Unassigned</b>"
                if tmpSection == SCN_PRO:  scnChapter = "<b>Prologue</b>"
                if tmpSection == SCN_CHAP: scnChapter = "<b>Chapter %d</b>" % tmpChapter
                if tmpSection == SCN_EPI:  scnChapter = "<b>Epilogue</b>"
                if tmpSection == SCN_ARCH: scnChapter = "<b>Archived</b>"
                parIter = self.treeStore.append(None,[scnChapter,None,None,scnSec,None])
                self.chapMap[scnSec]   = parIter
                self.chapCount[scnSec] = 1

            if tmpSection == SCN_ARCH:
                tmpTitle = "<span foreground='red'>"+str(tmpTitle)+"</span>"

            tmpData = [tmpTitle,str(tmpNumber),str(tmpWords),scnNum,itemHandle]
            tmpIter = self.treeStore.append(parIter,tmpData)
            self.iterMap[itemHandle] = tmpIter

        self.treeView.expand_all()
        self.sumWords()
        self.treeSelect.set_mode(Gtk.SelectionMode.SINGLE)

        return

    def clearContent(self):

        self.treeStore.clear()

        self.iterMap   = {}
        self.chapMap   = {}
        self.chapCount = {}

        return

    def sumWords(self):
        for chIter in self.chapMap.items():
            if self.treeStore.iter_has_child(chIter[1]):
                nChildren = self.treeStore.iter_n_children(chIter[1])
                wordSum   = 0
                for n in range(nChildren):
                    scnIter  = self.treeStore.iter_nth_child(chIter[1],n)
                    wordSum += int(self.treeStore.get_value(scnIter,self.COL_WORDS))
                wordCount = "<span foreground='blue'>"+str(wordSum)+"</span>"
                self.treeStore.set_value(chIter[1],self.COL_WORDS,wordCount)
        return

    def getIter(self, itemHandle):
        if itemHandle in self.iterMap: return self.iterMap[itemHandle]
        return None

    def setValue(self, itemHandle, colIdx, newValue):
        iterHandle = self.getIter(itemHandle)
        if iterHandle is not None:
            self.treeStore.set_value(iterHandle,colIdx,str(newValue))
        return

# End Class SceneTree