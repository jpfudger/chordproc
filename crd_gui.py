import os
import re
import subprocess
import sys
import random
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from chordproc.crd_data import CRD_data, CRD_artist, CRD_album, CRD_song
from chordproc.crd_gui_design import Ui_MainWindow

class CRD_gui(QMainWindow, Ui_MainWindow):
    def __init__(self, chords, app):
        super(self.__class__, self).__init__()
        self.chords = chords
        self.app = app
        self.setupUi(self)
        self.searchLyrics = False
        self.searchPattern = ''
        self.importPattern = ''
        self.currentPlayLink = None
        self.currentEditLink = None
        self.currentEditLnum = None
        self.colour_comment = 'gray'
        self.colour_chord = 'red'
        self.colour_tab = 'blue'

        self.modelArtists = QStandardItemModel()
        self.treeArtists.setModel(self.modelArtists)
        self.rootArtists = self.modelArtists.invisibleRootItem()
        self.makeTree(self.rootArtists, self.chords.artists)

        self.modelTunings = QStandardItemModel()
        self.treeTunings.setModel(self.modelTunings)
        self.rootTunings = self.modelTunings.invisibleRootItem()
        self.makeTree(self.rootTunings, self.chords.tunings)

        self.modelSearch  = QStandardItemModel()
        self.treeSearch.setModel(self.modelSearch)
        self.rootSearch = self.modelSearch.invisibleRootItem()

        self.modelImport  = QStandardItemModel()
        self.treeImport.setModel(self.modelImport)
        self.rootImport = self.modelImport.invisibleRootItem()

        self.set_icon()
        self.populateTuningCombo()

        self.currentArtistSong = None
        self.currentArtistTranspose = 0
        self.currentTuningSong = None
        self.currentTuningTranspose = 0
        self.currentSearchSong = None
        self.currentSearchTranspose = 0
        self.currentImportSong = None
        self.currentImportTranspose = 0

        QShortcut(QKeySequence("Ctrl+Up"),      self, self.transposeUp)
        QShortcut(QKeySequence("Ctrl+Down"),    self, self.transposeDown)
        QShortcut(QKeySequence(Qt.Key_Return),  self, self.handleEnter)
        QShortcut(QKeySequence(Qt.Key_Left),    self, self.handleLeft)
        QShortcut(QKeySequence(Qt.Key_Right),   self, self.handleRight)
        QShortcut(QKeySequence("Ctrl+R"),       self, self.chooseRandomSong)

    def set_icon(self):
        path = self.chords.resource_root() + 'icon.jpg'
        app_icon = QIcon()
        app_icon.addFile(path)
        self.app.setWindowIcon(app_icon)

    def makeTree(self,root,collection):
        for artist in collection:
            branch = QStandardItem(artist.name)
            branch.setData(artist)
            total_songs = 0
            for album in artist.albums:
                album_item = QStandardItem(album.title)
                album_item.setData(album)
                album_item.setToolTip("%d songs" % len(album.songs))
                total_songs += len(album.songs)
                child = branch.appendRow(album_item)
                for song in album.songs:
                    song_item = QStandardItem(song.title)
                    song.gui_item = song_item
                    song_item.setData(song)
                    grandchild = album_item.appendRow(song_item)
            branch.setToolTip("%d albums, %d songs" % (len(artist.albums), total_songs))
            root.appendRow(branch)

    def make_browser(self):
        self.browser = QTextBrowser()
        self.browser.setReadOnly(True)
        font = QFont()
        font.setFamily("Courier")
        font.setPointSize(10)
        self.browser.setFont(font)
        self.browser.show()

    def tweak_html(self, song, transpose, prefer_sharp=False):
        add_artist = self.onTuningsTab()
        lines = song.html(add_artist,transpose,prefer_sharp)
        text = "\n".join(lines)
        text = re.sub( '<div class=chordline([^>]*)>([^<]*)</div>', 
                      r'<font color="%s" \1>\2</font>' % self.colour_chord, 
                      text )
        text = re.sub( '<div class=commentline([^>]*)>([^<]*)</div>', 
                      r'<font color="%s" \1>\2</font>' % self.colour_comment, 
                      text )
        text = re.sub( '<div class=tabline>', '<font color="%s">' % self.colour_tab,
                      text )
        text = re.sub( '</div> <!--tabline-->', '</font>',
                      text )
        #text = re.sub( '<(\/?)h1>', '<\1h1>', text )
        text = re.sub( '<h3>', '<font size="10"><b>', text )
        text = re.sub( '</h3>', '</b></font>', text )
        text = text.replace('<hr>','')
        return text

    def currentTree(self):
        if self.onArtistsTab():
            return self.treeArtists
        elif self.onTuningsTab():
            return self.treeTunings
        elif self.onSearchTab():
            return self.treeSearch
        elif self.onImportTab():
            return self.treeImport
        return None

    def onArtistsTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 0

    def onTuningsTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 1

    def onSearchTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 2

    def onChordFinderTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 3

    def onImportTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 4

    def onSettingsTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 5

    def currentViewer(self):
        if self.onArtistsTab():
            return self.viewerArtists
        elif self.onTuningsTab():
            return self.viewerTunings
        elif self.onSearchTab():
            return self.viewerSearch
        elif self.onImportTab():
            return self.viewerImport
        return None

    def currentTranspose(self,inc=None):
        if self.onArtistsTab():
            if inc == None:
                self.currentArtistTranspose = 0
            else:
                self.currentArtistTranspose += inc
            return self.currentArtistTranspose
        elif self.onTuningsTab():
            if inc == None:
                self.currentTuningTranspose = 0
            else:
                self.currentTuningTranspose += inc
            return self.currentTuningTranspose
        elif self.onSearchTab():
            if inc == None:
                self.currentSearchTranspose = 0
            else:
                self.currentSearchTranspose += inc
            return self.currentSearchTranspose
        elif self.onImportTab():
            if inc == None:
                self.currentImportTranspose = 0
            else:
                self.currentImportTranspose += inc
            return self.currentImportTranspose
        return 0

    def currentSong(self,new=None):
        if self.onArtistsTab():
            if new: self.currentArtistSong = new
            return self.currentArtistSong
        elif self.onTuningsTab():
            if new: self.currentTuningSong = new
            return self.currentTuningSong
        elif self.onSearchTab():
            if new: self.currentSearchSong = new
            return self.currentSearchSong
        elif self.onImportTab():
            if new: self.currentImportSong = new
            return self.currentImportSong
        return None

    def viewerLinkClicked(self, qurl):
        link = qurl.path()
        if not os.path.exists(link):
            print("Link not found: " + link)
        elif link.endswith(".m3u"):
            # We don't want to follow this link in the browser, so reset it:
            self.currentViewer().setSource(QUrl(""))
            # Now play the m3u:
            self.playAudio(link)
        else:
            print("Unhandled link: " + link)

    def playButtonClicked(self):
        if self.playButton.isEnabled():
            if self.currentPlayLink:
                self.playAudio(self.currentPlayLink)

    def editButtonClicked(self):
        if self.editButton.isEnabled():
            if self.currentEditLink:
                editor = "gvim " + self.currentEditLink
                command = " -c \"normal! %dggzvzt\"" % self.currentEditLnum
                print(editor + command)
                subprocess.Popen(editor + command, shell=True)

    def jumpToSong(self,ar,al,so,model,tree):
        #print("artist: " + ar)
        #print("albuma  " + al)
        #print("song:   " + so)

        for i in range(model.rowCount()):
            index = model.index(i,0)
            artist = model.itemFromIndex(index)
            #print(artist.data().name)
            if artist.data().name == ar:
                for j in range(artist.rowCount()):
                    album = artist.child(j)
                    if album.data().title == al:
                        for k in range(album.rowCount()):
                            song = album.child(k)
                            if song.data().title == so:
                                tree.setCurrentIndex(song.index())
                                self.treeIndexClicked(song.index())
                                break
                        break
                break

    def reloadButtonClicked(self):
        print("Reloading")
        self.chords.load_song_data(True)
        print("Reloaded")

        # should clear the search and chord tab results.

        # should store the current item (artist/album/song) and restore it afterwards

        artist_song = self.currentArtistSong
        tuning_song = self.currentTuningSong
        self.currentArtistSong = None
        self.currentTuningSong = None

        self.modelArtists = QStandardItemModel()
        self.treeArtists.setModel(self.modelArtists)
        self.rootArtists = self.modelArtists.invisibleRootItem()
        self.makeTree(self.rootArtists, self.chords.artists)

        self.modelTunings = QStandardItemModel()
        self.treeTunings.setModel(self.modelTunings)
        self.rootTunings = self.modelTunings.invisibleRootItem()
        self.makeTree(self.rootTunings, self.chords.tunings)

        print("Repopulated")

        self.jumpToSong( artist_song.artist.name, artist_song.album.title, artist_song.title, 
                         self.modelArtists, self.treeArtists )

    def chooseRandomSong(self):
        if self.onArtistsTab():
            songs = self.chords.all_songs()
            song = random.choice(songs)
            item = song.gui_item
            index = item.index()
            self.currentTree().setCurrentIndex(index)
            self.treeIndexClicked(index)

    def tabChanged(self,which):
        pass

    def playAudio(self,link):
        p = subprocess.Popen(['audacious', link], shell=False)

    def enablePlayButton(self,link=None):
        if link:
            self.playButton.setEnabled(True)
            self.currentPlayLink = link
            self.playButton.setToolTip(link)
        else:
            self.playButton.setEnabled(False)
            self.currentPlayLink = None
            self.playButton.setToolTip("")

    def enableEditButton(self,path=None,lnum=0):
        if path:
            self.editButton.setEnabled(True)
            self.currentEditLink = path
            self.currentEditLnum = lnum
            self.editButton.setToolTip(path)
        else:
            self.editButton.setEnabled(False)
            self.currentEditLink = None
            self.editButton.setToolTip("")

    def treeIndexClicked(self, index):
        item = index.model().itemFromIndex(index)
        self.enablePlayButton()
        self.enableEditButton()
        if not item.data():
            pass
        elif isinstance(item.data(),CRD_song):
            song = item.data()
            self.currentSong(song)
            text = self.tweak_html(self.currentSong(), self.currentTranspose())
            self.currentViewer().setHtml(text)
            links = song.get_mp3_link()
            if links:
                self.enablePlayButton(links)
            if song.fpath and song.lnum:
                self.enableEditButton(song.fpath,song.lnum)
        elif isinstance(item.data(),CRD_album):
            album = item.data()
            link = album.get_playlist_link()
            if link: 
                self.currentViewer().setHtml(link)
                self.enablePlayButton(album.get_playlist())

    def searchMainTabs(self):
        pattern = self.lineEdit.text()
        top = self.modelArtists.invisibleRootItem().index()

        for i in range(self.modelArtists.rowCount()):
            index = self.modelArtists.index(i,0)
            artist = self.modelArtists.itemFromIndex(index)
            artist_visible = False
            if artist:
                for j in range(artist.rowCount()):
                    album = artist.child(j)
                    album_visible = False
                    for k in range(album.rowCount()):
                        song = album.child(k)
                        song_visible = pattern.lower() in song.text().lower()
                        self.treeArtists.setRowHidden(song.row(),album.index(),not song_visible)
                        if song_visible:
                            album_visible = True
                            artist_visible = True
                    self.treeArtists.setRowHidden(album.row(),artist.index(),not album_visible)
                self.treeArtists.setRowHidden(artist.row(),top,not artist_visible)

        for i in range(self.modelTunings.rowCount()):
            index = self.modelTunings.index(i,0)
            artist = self.modelTunings.itemFromIndex(index)
            artist_visible = False
            if artist:
                for j in range(artist.rowCount()):
                    album = artist.child(j)
                    album_visible = False
                    for k in range(album.rowCount()):
                        song = album.child(k)
                        song_visible = pattern.lower() in song.text().lower()
                        self.treeTunings.setRowHidden(song.row(),album.index(),not song_visible)
                        if song_visible:
                            album_visible = True
                            artist_visible = True
                    self.treeTunings.setRowHidden(album.row(),artist.index(),not album_visible)
                self.treeTunings.setRowHidden(artist.row(),top,not artist_visible)

    def searchTab(self):
        if self.modelSearch.rowCount() > 0:
            self.modelSearch.clear()
            self.rootSearch = self.modelSearch.invisibleRootItem()

        pattern = self.searchPattern
        lyrics = self.searchLyrics

        if pattern != '':
            first = None
            for artist in self.chords.artists:
                for album in artist.albums:
                    for song in album.songs:
                        if song.search(pattern,lyrics):
                            song_item = QStandardItem(song.title)
                            song_item.setData(song)
                            song_item.setToolTip("%s - %s" % (artist.name, album.title))
                            if first == None:
                                first = song_item
                            self.rootSearch.appendRow(song_item)
            if first:
                # select and view first match:
                index = first.index()
                self.treeSearch.setCurrentIndex(index)
                self.treeSearch.setFocus()
                self.treeIndexClicked(index)

    def transposeUp(self):
        song = self.currentSong()
        viewer = self.currentViewer()
        if song and viewer:
            bar_value = None
            bar = viewer.verticalScrollBar()
            if bar:
                bar_value = bar.value()
            text = self.tweak_html(song, self.currentTranspose(1), False)
            self.currentViewer().setHtml(text)
            bar.setValue(bar_value)

    def transposeDown(self):
        song = self.currentSong()
        viewer = self.currentViewer()
        if song and viewer:
            bar_value = None
            bar = viewer.verticalScrollBar()
            if bar:
                bar_value = bar.value()
            text = self.tweak_html(song, self.currentTranspose(-1), False)
            self.currentViewer().setHtml(text)
            bar.setValue(bar_value)

    def patternChanged(self):
        text = self.lineEdit.text().lower()
        if text != self.searchPattern:
            self.searchPattern = text
            return True
        return False

    def importLines(self,lines,title):
        print("Importing %d lines" % len(lines))

        if "{{{" in "".join(lines):
            print("Expected format")
        else:
            print("Sandwiching in foldmarkers")

            newlines = [ "{{{ song: " + title ]
            for l in lines:
                newlines.append(l)
                print(l)
            newlines.append( "}}}" )
            lines = newlines

        options = {}
        options["update"]    = False
        options["html"]      = False
        options["gui"]       = False
        options["tunings"]   = None
        options["html_root"] = None
        options["root"]      = None
        options["pickle"]    = None
        import_data = CRD_data(options,lines)

        # Don't clear model - then we can still access previous imports
        # self.modelImport.clear()
        # self.rootImport = self.modelImport.invisibleRootItem()

        self.makeTree(self.rootImport, import_data.artists)

    def parseHTML(self,html,url):
        lines = html.split("\n")

        if 'ultimate-guitar' in url.lower():
            urlsplits = url.split('/')
            newlines = []

            for line in lines:
                if len(newlines) > 0:
                    newlines.append(line)
                    if re.search( '<\/pre\>', line ):
                        break
                if re.search( '<pre class=.*js-tab-content', line ):
                    newlines.append(line)

            if len(newlines) > 0:
                lines = []
                lines.append('{{{ artist: ' + urlsplits[-2] )
                lines.append('{{{ song: ' + urlsplits[-1] )
                #newlines = newlines[1:-1]

                for l in newlines:
                    l = l.replace( '<span>', '' )
                    l = l.replace( '</span>', '' )
                    lines.append(l)

                lines.append( '}}}' )
                lines.append( '}}}' )

            print( "Extracted %d from %d lines" % ( len(newlines), len(lines) ) )

        return lines

    def importGeneral(self):
        text = self.importPattern
        lines = None
        if os.path.exists(text):
            with open(text) as f:
                lines = f.readlines()
            if lines:
                self.importLines(lines,text)
        elif text.startswith('http') or text.startswith('www'):
            url = text
            html = None

            import urllib.request
            with urllib.request.urlopen(url) as response:
               html = response.read()
               lines = self.parseHTML(html.decode("utf-8"), url)

            if lines:
                self.importLines(lines,url)

        else:
            print("Unrecognised import")

    def importChanged(self):
        text = self.importEdit.text()
        if text != self.importPattern:
            self.importPattern = text
            return True
        return False

    def searchLyricsChanged(self,value):
        self.searchLyrics = value
        self.searchTab()

    def settingsChanged(self,value):
        self.colour_chord = self.colourChord.currentText().lower()
        self.colour_comment = self.colourComment.currentText().lower()

    def handleEnter(self):
        if self.onSearchTab():
            if self.patternChanged():
                #self.searchMainTabs()
                self.searchTab()
            else:
                tree = self.currentTree()
                if tree:
                    index = tree.selectedIndexes()[0]
                    self.treeIndexClicked(index)
        elif self.onImportTab():
            if self.importChanged():
                text = self.importEdit.text()
                self.importGeneral()
            else:
                tree = self.currentTree()
                if tree:
                    index = tree.selectedIndexes()[0]
                    self.treeIndexClicked(index)
        elif self.onChordFinderTab():
            self.lookupChord()
        else:
            tree = self.currentTree()
            if tree:
                index = tree.selectedIndexes()[0]
                self.treeIndexClicked(index)

    def handleLeft(self):
        if self.onSearchTab() or self.onChordFinderTab():
            return
        indices = self.currentTree().selectedIndexes()
        if len(indices) > 0:
            index = indices[0]
            item = index.model().itemFromIndex(indices[0])
            if not item.data():
                pass
            elif isinstance(item.data(),CRD_artist):
                self.currentTree().collapse(index)
            elif isinstance(item.data(),CRD_album):
                if self.currentTree().isExpanded(index):
                    self.currentTree().collapse(index)
                else:
                    self.currentTree().collapse(index.parent())
                    self.currentTree().setCurrentIndex(index.parent())
            elif isinstance(item.data(),CRD_song):
                self.currentTree().collapse(index.parent())
                self.currentTree().setCurrentIndex(index.parent())

    def handleRight(self):
        if self.onSearchTab() or self.onChordFinderTab():
            return
        indices = self.currentTree().selectedIndexes()
        if len(indices) > 0:
            index = indices[0]
            item = index.model().itemFromIndex(indices[0])
            if not item.data():
                pass
            elif isinstance(item.data(),CRD_artist):
                self.currentTree().expand(index)
            elif isinstance(item.data(),CRD_album):
                self.currentTree().expand(index)
            elif isinstance(item.data(),CRD_song):
                self.treeIndexClicked(index)

    def populateTuningCombo(self):
        tunings = self.chords.stock_tunings[:]
        tunings.sort(key=lambda x: x.name())

        standard = 0
        for i, tuning in enumerate(tunings):
            if tuning.name().lower() == "standard":
                standard = i
                break

        tunings.insert(0, tunings.pop(standard))

        for tuning in tunings:
            name = '%s (%s)' % ( tuning.tuning, tuning.name() )
            self.tuningCombo.addItem(name,tuning)

    def lookupChord(self):
        tuning = self.tuningCombo.itemData(self.tuningCombo.currentIndex())
        chord  = self.chordName.text()
        print("Looking up %s in %s" % ( chord, tuning.name() ))
        fingering = tuning.get_fingering(chord)
        fingering_string = fingering
        if fingering_string:
            fingering_string += " (stock)"
        lines = [ fingering_string ]

        for x in self.chords.lookup_chord(tuning,chord):
            if not fingering in x:
                lines.append(x)

        self.chordResult1.setText("\n".join(lines))

class CRD_interface():
    @staticmethod
    def gui(data):
        app = QApplication(sys.argv)
        form = CRD_gui(data,app)
        form.show()
        app.exec_()

