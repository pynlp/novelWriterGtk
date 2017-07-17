# -*- coding: utf-8 -*
"""novelWriter Scene Text Class

novelWriter – Scene Text Class
====================================
Holds the text of the loaded scene

File History:
Created: 2017-01-14 [0.2.0]

"""

import logging as logger
import nw

from os      import path, rename, remove
from hashlib import sha256
from re      import sub
from bleach  import clean
from html    import unescape

class SceneText():

    def __init__(self, theOpt):

        # Core Objects
        self.mainConf    = nw.CONFIG
        self.theOpt      = theOpt

        # Attributes
        self.text        = ""
        self.textHash    = ""
        self.hasText     = False
        self.wordsOnLoad = 0
        self.charsOnLoad = 0
        self.wordsAdded  = 0
        self.charsAdded  = 0
        self.wordsLatest = 0
        self.charsLatest = 0

        return

    ##
    #  Load and Save
    ##

    def loadText(self):

        sceneFolder  = self.theOpt.sceneFolder
        sceneHandle  = self.theOpt.sceneHandle
        sceneVersion = self.theOpt.sceneVersion
        scenePath    = path.join(sceneFolder,sceneHandle)

        if not path.isdir(sceneFolder):
            logger.debug("SceneText.loadText: Folder not found %s" % sceneFolder)
            return

        if not path.isdir(scenePath):
            logger.error("SceneText.loadText: Scene handle invalid")
            return

        logger.debug("SceneText.loadText: Loading scene text")

        fileName = "scene-%03d.txt" % sceneVersion
        filePath = path.join(sceneFolder,sceneHandle,fileName)

        if not path.isfile(filePath):
            logger.debug("SceneText.loadText: File not found %s" % filePath)
            return

        fileObj   = open(filePath,encoding="utf-8",mode="r")
        self.text = fileObj.read()
        fileObj.close()

        words, chars     = self.countWords(self.text)
        self.wordsOnLoad = words
        self.charsOnLoad = chars
        self.wordsLatest = words
        self.charsLatest = chars
        self.textHash    = sha256(str(self.text).encode()).hexdigest()
        self.hasText     = True

        return

    def saveText(self):

        if not self.hasText:
            logger.debug("SceneText.saveText: No text to save")
            return False

        if self.textHash == sha256(str(self.text).encode()).hexdigest():
            logger.debug("SceneText.saveText: No changes to save")
            return False

        sceneFolder  = self.theOpt.sceneFolder
        sceneHandle  = self.theOpt.sceneHandle
        sceneVersion = self.theOpt.sceneVersion
        scenePath    = path.join(sceneFolder,sceneHandle)

        if not path.isdir(sceneFolder):
            logger.debug("SceneText.saveText: Folder not found %s" % sceneFolder)
            return False

        if not path.isdir(scenePath):
            logger.debug("SceneSummary.saveText: Unknown scene handle '%s'" % sceneHandle)
            return

        if not len(sceneHandle) == 20:
            logger.debug("SceneSummary.saveText: Invalid scene handle '%s'" % sceneHandle)
            return False

        if not sceneVersion > 0:
            logger.debug("SceneText.saveText: Invalid scene version %d" % sceneVersion)
            return False

        logger.debug("SceneText.saveText: Saving scene text")

        fileName = "scene-%03d.txt" % sceneVersion
        tempName = "scene-%03d.bak" % sceneVersion
        filePath = path.join(sceneFolder,sceneHandle,fileName)
        tempPath = path.join(sceneFolder,sceneHandle,tempName)

        # Back up old file
        if path.isfile(tempPath): remove(tempPath)
        if path.isfile(filePath): rename(filePath,tempPath)

        fileObj = open(filePath,encoding="utf-8",mode="w")
        fileObj.write(self.text)
        fileObj.close()

        words, chars     = self.countWords(self.text)
        self.wordsLatest = words
        self.charsLatest = chars
        self.textHash    = sha256(str(self.text).encode()).hexdigest()

        return True

    ##
    #  Setters
    ##

    def setText(self, srcText):
        if len(srcText) > 0:
            srcText          = self.htmlCleanUp(srcText)
            self.text        = srcText
            self.hasText     = True
            words,chars      = self.countWords(srcText)
            self.wordsAdded  = words - self.wordsOnLoad
            self.charsAdded  = chars - self.charsOnLoad
            self.wordsLatest = words
            self.charsLatest = chars
        return

    ##
    #  Getters
    ##

    def getText(self):
        return self.text

    def getWordCount(self):
        return [self.wordsOnLoad,self.wordsAdded,self.wordsLatest]

    def getCharCount(self):
        return [self.charsOnLoad,self.charsAdded,self.charsLatest]

    ##
    #  Methods
    ##

    def countWords(self, srcText):

        cleanText = srcText.strip()
        cleanText = sub("<.*?>"," ",cleanText)
        cleanText = sub("&.*?;","?",cleanText)
        cleanText = cleanText.strip()
        splitText = cleanText.split()

        return len(splitText), len(cleanText)

    def htmlCleanUp(self, srcText):

        okTags   = ["p","b","i","u","strike"]
        okAttr   = {"*" : ["style"]}
        okStyles = ["text-align"]

        srcText  = clean(srcText,tags=okTags,attributes=okAttr,styles=okStyles,strip=True)

        if srcText[0:3] != "<p>": srcText = "<p>"+srcText+"</p>"

        srcText = unescape(srcText)
        srcText = srcText.replace("</p> ","</p>")
        srcText = srcText.replace("<p></p>","")
        srcText = srcText.replace("</p>","</p>\n")
        srcText = srcText.replace('style=""',"")
        srcText = srcText.replace("style=''","")
        srcText = srcText.replace(" >",">")
        srcText = srcText.replace("\u00A0"," ")
        srcText = srcText.replace("\n ","\n")

        return srcText

# End Class SceneText
