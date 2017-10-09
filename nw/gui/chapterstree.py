# -*- coding: utf-8 -*
"""novelWriter Chapters Tree Class

 novelWriter – Chapters Tree Class
===================================
 Wrapper class for the chapters tree

 File History:
 Created: 2017-10-09 [0.4.0]

"""

import logging as logger
import nw
import nw.const as NWC
import gi
gi.require_version("Gtk","3.0")

from gi.repository import Gtk

class GuiChaptersTree(Gtk.TreeView):

    # Constants
    COL_TYPE       = 0
    COL_NUMBER     = 1
    COL_TITLE      = 2
    COL_COMPILE    = 3
    COL_COMMENT    = 4
    COL_HANDLE     = 5
    
    def __init__(self, theBook):
        
        Gtk.TreeView.__init__(self)
        
        # Connect to GUI
        self.mainConf   = nw.CONFIG
        self.theBook    = theBook
        self.iterMap    = {}
        
        self.set_name("treeChapters")
        self.set_headers_visible(True)
        
        # Core Objects
        self.treeSelect = self.get_selection()
        self.listStore  = Gtk.ListStore(str,str,str,str,str,str)
        self.set_model(self.listStore)
        
        # Type
        self.colType  = Gtk.TreeViewColumn(title="Type")
        self.rendType = Gtk.CellRendererText()
        self.rendType.set_property("editable",True)
        self.colType.pack_start(self.rendType,True)
        self.colType.add_attribute(self.rendType,"text",0)
        self.colType.set_attributes(self.rendType,markup=0)
        
        # Number
        self.colNumber  = Gtk.TreeViewColumn(title="#")
        self.rendNumber = Gtk.CellRendererText()
        self.rendNumber.set_property("editable",True)
        self.colNumber.pack_start(self.rendNumber,False)
        self.colNumber.add_attribute(self.rendNumber,"text",1)
        
        # Title
        self.colTitle  = Gtk.TreeViewColumn(title="Title")
        self.rendTitle = Gtk.CellRendererText()
        self.rendTitle.set_property("editable",True)
        self.colTitle.pack_start(self.rendType,False)
        self.colTitle.add_attribute(self.rendType,"text",2)
        
        # Compile
        self.colCompile  = Gtk.TreeViewColumn(title="Compile")
        self.rendCompile = Gtk.CellRendererText()
        self.rendCompile.set_property("editable",True)
        self.colCompile.pack_start(self.rendCompile,False)
        self.colCompile.add_attribute(self.rendCompile,"text",3)
        
        # Comment
        self.colComment  = Gtk.TreeViewColumn(title="Comment")
        self.rendComment = Gtk.CellRendererText()
        self.rendComment.set_property("editable",True)
        self.colComment.pack_start(self.rendComment,False)
        self.colComment.add_attribute(self.rendComment,"text",4)
        
        # Add to TreeView
        self.append_column(self.colType)
        self.append_column(self.colNumber)
        self.append_column(self.colTitle)
        self.append_column(self.colCompile)
        self.append_column(self.colComment)
        
        return
    
    def loadContent(self):
        
        self.treeSelect.set_mode(Gtk.SelectionMode.NONE)
        self.listStore.clear()
        
        for treeItem in self.theBook.theTree:
            
            itemName    = treeItem[NWC.BookTree.NAME]
            itemClass   = treeItem[NWC.BookTree.CLASS]
            itemLevel   = treeItem[NWC.BookTree.LEVEL]
            itemType    = treeItem[NWC.BookTree.TYPE]
            itemHandle  = treeItem[NWC.BookTree.HANDLE]
            itemParent  = treeItem[NWC.BookTree.PARENT]
            
            if not itemClass == NWC.ItemClass.CONTAINER: continue
            if not itemLevel == NWC.ItemLevel.ITEM: continue
            if not itemType  == NWC.ItemType.BOOK: continue
            
            itemSubType = treeItem[NWC.BookTree.SUBTYPE].name
            itemNumber  = str(treeItem[NWC.BookTree.NUMBER])
            itemCompile = str(treeItem[NWC.BookTree.COMPILE])
            itemComment = treeItem[NWC.BookTree.COMMENT]
            
            tmpIter = self.listStore.append([
                itemSubType,
                itemNumber,
                itemName,
                itemCompile,
                itemComment,
                itemHandle
            ])
            self.iterMap[itemHandle] = tmpIter
        
        self.expand_all()
        self.treeSelect.set_mode(Gtk.SelectionMode.SINGLE)
        
        return
    
# End Class GuiCharsTree
