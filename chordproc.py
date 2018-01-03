import glob
import os
import pickle
import re
import string
import subprocess
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from chordproc.design import Ui_MainWindow
from laudable.laudable import LAUD_data

# Todo:
#
# 1) Currently the fingerings for each songs are stored in the song class,
#    rather than the tunings class. We need to add an "add_fingering" method
#    to CRD_tuning and replace CRD_song.fingerings with CRD_tuning.fingerings.
#
# 2) We need to add a link from each song to the tunings page.
#    Songs can be hard to lookup in the tunings index because the
#    tunings are listed by their offset notation.
#

def common_html():
    lines = []
    #lines = [ '<link rel="stylesheet" type="text/css" href="style.css">' ]
    lines.append( '<link rel="stylesheet" type="text/css" href="style.css"     id="style">' )
    lines.append( '<link rel="stylesheet"  type="text/css" href="styleweb.css"  id="styleweb">' )
    lines.append( '<script>' )
    lines.append( 'document.getElementById("style").disabled    = false;' )
    lines.append( 'document.getElementById("styleweb").disabled = true;' )

    lines.append( 'function toggleStyle() {' )
    lines.append( '    if ( document.getElementById("style").disabled ) {' )
    lines.append( '        document.getElementById("style").disabled    = false;' )
    lines.append( '        document.getElementById("styleweb").disabled = true;' )
    lines.append( '        }' )
    lines.append( '    else {' )
    lines.append( '        document.getElementById("style").disabled    = true;' )
    lines.append( '        document.getElementById("styleweb").disabled = false;' )
    lines.append( '        }' )
    lines.append( '    }' )

    lines.append( '</script>' )
    #lines.append( '<button onclick="toggleStyle()">Toggle Style</button>' )

    return lines

class CRD_artist():
    def __init__(self,name,index=0,laud_data=None):
        self.name = name
        self.albums = []
        self.index = index
        self.laud_data = laud_data
        self.fname = name.lower() + '.html'
        self.fname = re.sub( ' ', '_', self.fname )
        self.fname = re.sub( '#', 's', self.fname )
        self.index_fname = re.sub( '.html', '_index.html', self.fname )
        self.tuning = None
    def add_album(self,title):
        album_index = '%d.%d' % ( self.index, len(self.albums) + 1 )
        new_album = CRD_album( title, self, album_index, self.laud_data )
        self.albums.append(new_album)
        return new_album
    def all_songs(self):
        allsongs = []
        for album in self.albums:
            for song in album.songs:
                allsongs.append(song)
        allsongs.sort(key=lambda x: x.title_sort)
        return allsongs
    def html_songs(self,stock_tunings,add_artist=False):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % self.name ]
        lines += common_html()
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s</div></h2>' % (self.index, self.name) ]
        lines += [ '<hr>', '<ol>' ]
        for song in self.all_songs():
            lines.append( '<li><a href=#%s>%s</a>' % ( song.link, song.title ) )
        lines += [ '</ol>' ]
        for song in self.all_songs():
            lines += song.html(stock_tunings,add_artist)[:]
        lines += [ '<hr>' ]
        lines += [ '<br>' ] * 10
        lines += [ '</body>', '</html>' ]
        return lines
    def html_albums(self,add_artist=False):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % self.name ]
        lines += common_html()
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s</title></h2>' % (self.index, self.name) ]
        lines += [ '<hr>', '<a href="%s">Song Index</a>' % self.index_fname ]
        lines += [ '<hr>' ]
        #lines += [ '<ol>' ]
        for album in self.albums:
            #lines.append( '<li>' )
            n_songs = len(album.songs)
            lines.append( '<a href=%s>%s</a> <div class=count>%d</div>' 
                                % ( album.fname, album.title, n_songs ) )
            lines.append( '<br>' )
        #lines += [ '</ol>' ]
        lines += [ '<hr>' ]
        lines += [ '<br>' ] * 10
        lines += [ '</body>', '</html>' ]
        return lines
    def html(self,stock_tunings,add_artist=False):
        if len(self.albums) == 1 and self.albums[0].title == 'Misc':
            return self.html_songs(stock_tunings,add_artist)
        else:
            return self.html_albums(add_artist)
    def html_index(self):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % self.name ]
        lines += common_html()
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s Song Index</title></h2>' % (self.index, self.name) ]
        lines += [ '<hr>', '<div class=songindex>' ]
        #lines += [ '<ol>' ]
        allsongs = self.all_songs()
        cur_letter = None
        for song in allsongs:
            if cur_letter == None:
                pass
            elif cur_letter != song.title_sort[0]:
                lines.append('<br>')
                lines.append('<br>')
            else:
                lines.append( '<br>' )
            cur_letter = song.title_sort[0]
            s_link = song.album.fname + '#' + song.link
            lines.append( '<a href=%s>%s</a> (%s)' % ( s_link, song.title, song.album.title ) )
        #lines += [ '</ol>' ]
        lines += [ '</div>' ]
        lines += [ '</body>', '</html>' ]
        return lines
    def latex(self):
        lines  = [ r'\documentclass{article}' ]
        lines += [ r'\usepackage[a4paper,margin=2cm]{geometry}' ]
        lines += [ r'\begin{document}' ]
        lines += [ r'\pagenumbering{gobble}' ]

        for album in self.albums:
            for song in album.songs:
                lines.append( r'\newpage' )
                lines += [ r'\begin{verbatim}' ]
                lines += [ song.title ]
                lines += [ '=' * len(song.title) ]
                lines += [ '' ]
                for line in song.lines:
                    lines.append(line)
                lines += [ r'\end{verbatim}' ]

        lines += [ r'\end{document}' ]

        if not os.path.isdir('tex'):
            os.makedirs('tex')

        p = subprocess.Popen(['pdflatex','-output-directory=tex', '-jobname=chordproc'], shell=False,
                             stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        output = p.communicate(input='\n'.join(lines).encode())
        #print(output)

class CRD_album():
    def __init__(self,title,artist,index,laud_data):
        self.title  = title
        self.artist = artist
        self.index  = index
        self.laud_data = laud_data
        self.songs  = []
        name = ( artist.name if artist else '' ) + '_' + title
        alpha = lambda x: ''.join( [y for y in x if y.isalnum()] )
        alphaname = ( alpha(artist.name) if artist else '' ) + '_' + alpha(title)
        self.fname = 'album_' + alphaname + '.html'
    def add_song(self,title,fpath):
        song_index = self.index + '.%d' % ( len(self.songs) + 1 )
        new_song = CRD_song(title,self.artist.name,fpath,song_index)
        self.songs.append(new_song)
        new_song.album = self
        return new_song
    def html(self,stock_tunings):
        title = self.artist.name + ' : ' + self.title
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % title ]
        lines += common_html()
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s</div></h2>' % (self.index, title) ]
        lines += [ self.get_playlist_link() ]
        lines += [ '<hr>', '<ol>' ]
        for song in self.songs:
            lines.append( '<li><a href=#%s>%s</a>' % ( song.link, song.title ) )
        lines += [ '</ol>' ]
        for song in self.songs:
            lines += song.html(stock_tunings)[:]
        lines += [ '<hr>' ]
        lines += [ '<br>' ] * 10
        lines += [ '</body>', '</html>' ]
        return lines
    def latex(self):
        lines  = [ r'\documentclass{article}' ]
        lines += [ r'\usepackage[a4paper,margin=2cm]{geometry}' ]
        lines += [ r'\begin{document}' ]
        lines += [ r'\pagenumbering{gobble}' ]

        for song in self.songs:
            lines.append( r'\newpage' )
            lines += [ r'\begin{verbatim}' ]
            lines += [ song.title ]
            lines += [ '=' * len(song.title) ]
            lines += [ '' ]
            for line in song.lines:
                lines.append(line)
            lines += [ r'\end{verbatim}' ]

        lines += [ r'\end{document}' ]

        if not os.path.isdir('tex'):
            os.makedirs('tex')

        p = subprocess.Popen(['pdflatex','-output-directory=tex', '-jobname=chordproc'], shell=False,
                             stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        output = p.communicate(input='\n'.join(lines).encode())
        #print(output)
    def get_playlist_link(self):
        try:
            alb = self.laud_data.find_album(self.artist.name,self.title)
            m3u = alb.playlist
            img = alb.image
            link = '<a href="%s"><img class=cover src="%s"></a>' % ( alb.playlist, alb.image )
        except AttributeError:
            link = ''
        return link

class CRD_chord():
    def __init__(self,string):
        self.string = string
        self.root = None
        self.bass = None
        self.__identify()
    def __identify(self):
        tones = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G' ]
        flats = [ 'Ab', 'Bb', 'Db', 'Eb', 'Gb' ]
        sharps = [ 'A#', 'C#', 'D#', 'F#', 'G#' ]

        allnotes = [ n.lower() for n in ( sharps + flats + tones ) ]

        for t in allnotes:
            if self.string.lower().startswith(t):
                self.root = t
                break

        for t in allnotes:
            if self.string.lower().endswith( '/' + t) or self.string.lower().endswith( '\\' + t):
                self.bass = t
                break
    def __notes(self,which,prefer_sharp=False):
        notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ]
        if prefer_sharp or '#' in which:
            notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ]
        return notes + notes
    def format(self,transpose=0,prefer_sharp=False):
        newchord = self.string
        transpose = transpose % 12

        if self.is_chord():
            if self.root:
                try:
                    notes = self.__notes(self.root,prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    rootindex = lowernotes.index(self.root.lower())
                except ValueError:
                    notes = self.__notes(self.root,not prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    rootindex = lowernotes.index(self.root.lower())
                newroot = notes[rootindex + transpose]
                newchord = newroot + newchord[len(self.root):]

            if self.bass:
                try:
                    notes = self.__notes(self.bass,prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    bassindex = lowernotes.index(self.bass.lower())
                except ValueError:
                    notes = self.__notes(self.bass,not prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    bassindex = lowernotes.index(self.bass.lower())
                newbass = notes[bassindex + transpose]

                if not self.root:
                    newchord = '/' + newbass.lower()
                else:
                    newchord = newchord[:-len(self.bass)-1] + '/' + newbass.lower()

        return newchord       
    def is_chord(self):
        if self.root == None and self.bass == None:
            return False

        if len(self.string) > 12:
            # G#add9(sus4)
            self.root = None
            self.bass = None
            return False

        nochord_chars = [ 'l', 'k', 't', 'h', 'gg', 'y', 'v', 'ing' ]

        for c in nochord_chars:
            if c in self.string.lower():
                self.root = None
                self.bass = None
                return False

        # n can only appear in min
        if re.search( '[^i]n', self.string ):
            self.root = None
            self.bass = None
            return False

        # j can only appear in maj
        if re.search( '[^a]j', self.string ):
            self.root = None
            self.bass = None
            return False

        # s can only appear in sus
        if 's' in self.string.replace('sus','xxx'):
            self.root = None
            self.bass = None
            return False

        return True

class CRD_tuning():
    def __init__(self,input_string,names=[]):
        self.input_string = input_string
        self.tuning = None
        self._name = None
        self.names = names
        self.fingerings = {}

        if not self.name():
            # extract tuning candidate
            splits = input_string.strip().split(':')
            candidate = splits[0] if len(splits) == 1 else splits[1]
            m = re.match( '([abcdefgABCDEFG#]+).*', candidate.strip() )
            if m:
                self.tuning = m.group(1)
            else:
                raise ValueError( "Failed to extract tuning from " + candidate.strip() )
    def get_fingering(self,crd_string):
        fingering = ''
        try:
            fingering = self.fingerings[crd_string]
            fingering = ' title="%s = %s"' % ( crd_string, fingering )
        except KeyError:
            pass
        return fingering
    def __str__(self):
        return self.tuning
    def __note_offset(self,root,note):
        if '#' in note + root:
            notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ]
        else:
            notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ]
        notes = notes + notes
        root_index = notes.index(root)
        notes = notes[root_index:]
        return notes.index(note)
    def note_list(self):
        chars = list(self.tuning)
        notes = []
        for char in chars:
            if re.match( '[A-G]', char ):
                notes.append(char)
            else:
                notes[-1] += char
        return notes
    def offset(self):
        nl = self.note_list()
        previous = nl[0]
        encoded = [ previous ]

        for note in nl[1:]:
            offset = self.__note_offset( previous, note ) 
            encoded.append(offset)
            previous = note

        return ''.join( [str(x) for x in encoded[1:] ] )
    def root(self):
        return self.note_list()[0]
    def name(self):
        # also sets self.tuning if successful
        if not self._name:
            self._name = None
            maps = [ [ 'DGDGBD',  'open G' ],
                     [ 'DGDGBbD', 'open Gm' ],
                     [ 'DADF#AD', 'open D' ],
                     [ 'DADFAD',  'open Dm' ],
                     [ 'DADGBE',  'drop D' ],
                     [ 'CADGBE',  'drop C' ],
                     [ 'CGDGBE',  'drop C' ],
                     [ 'DADGBD',  'double drop D' ],
                     [ 'EADGBE',  'standard' ],
                     [ 'EAC#EAE', 'open A' ],
                   ]
            if 'standard' in self.input_string.lower():
                self.tuning = 'EADGBE'
                self._name = 'standard'
            else:
                for m in maps:
                    if m[0].lower() in self.input_string.lower():
                        self.tuning = m[0]
                        self._name = m[1]
                    elif m[1].lower() in self.input_string.lower():
                        self.tuning = m[0]
                        self._name = m[1]
        return self._name
    def standard(self):
        return self._name and self._name.lower() == 'standard'
    def summary(self):
        tuning_pad = 12 - len(self.tuning)
        name_pad = 15 
        if self._name:
            name_pad -= len(self._name)

        string = self.tuning + ' ' + ( '_' * tuning_pad )
        string += ' [' + self.offset() + '] __'
        if self._name:
            string += self._name
        string += '_' * name_pad

        return string

class CRD_song():
    def __init__(self,title,artist,fpath,index=0):
        self.title = title
        self.artist = artist
        self.fpath = fpath
        self.index = index
        self.lines = []
        self.tuning = None
        self.album = None
        self.comchar = '%'
        self.fingerings = {}
        self.link = ''.join( [x for x in title if x.isalnum() ])
        self.title_sort = re.sub( '\AThe\s+', '', title)
    def add_fingering(self,chord,fingering):
        self.fingerings[ chord.format() ] = fingering
    def get_fingering(self,crd_string):
        fingering = ''
        try:
            fingering = self.fingerings[crd_string]
            fingering = ' title="%s = %s"' % ( crd_string, fingering )
        except KeyError:
            pass
        return fingering
    def is_comment_line(self,line):
        if line.strip().startswith( self.comchar + ' '):
            comline = line.replace( self.comchar + ' ', '', 1 )
            return comline
        elif line.strip().startswith( self.comchar ):
            comline = line.replace( self.comchar, '', 1 )
            return comline

        if line.lower().strip().startswith( 'capo' ):
            return line
        elif line.lower().strip().startswith( 'tuning' ):
            return line

        autocomment = False
        if autocomment:
            commentwords = [ 'intro', 'outro', 'twice', 'capo', 
                             'note:', 'verse', 'chorus',
                             'solo', 'tuning' ]

            for cw in commentwords:
                if cw.lower() in line.lower():
                    return line

        regex = '([0-9xX]{6,})' 
        m = re.search(regex, line)
        if m:
            # there is at least 1 fingering on this line
            # fingerings (e.g. 0x0434) should always be commented
            splits = re.split( r'(\s+)', line)
            enders = [ ':', '=' ]
            chord = None
            fingering = None

            # loop over line looking for fingerings (may be many per line)
            for word in splits:
                if word == '':
                    continue
                elif word in enders:
                    continue
                for ender in enders:
                    if word.endswith(ender):
                        word = word[:-1]
                        break

                if chord and chord.is_chord():
                    # already got a chord... check for fingerings
                    m = re.search(regex, word)
                    if m:
                        # word is fingering
                        fingering = m.group(1)
                        self.add_fingering( chord, fingering )
                        chord = None
                        fingering = None
                else:
                    chord = CRD_chord(word)
            return line

        return None
    def strip_delimeters(self,word):
        starter = ''
        ender = ''
        chars = [ '*', '|', '-', '[', ']', '{', '}', '(', ')', '.' ]

        # Some charts use | and - to for timing, 
        # so we need to strip them off before chord processing,
        # and save them for reapplying afterwards

        for x in chars:
            if word.startswith(x):
                word = word[1:]
                starter = x
                break

        for x in chars:
            if word.endswith(x):
                word = word[:-1]
                ender = x
                break

        if starter == '[' and ender == ']':
            # Ignore [] delimiting chords
            starter = ''
            ender = '  '

        if starter == '(' and ender == ')':
            # Ignore () delimiting chords
            starter = ''
            ender = '  '
        elif starter == '(':
            word = '(' + word
            starter = ''
        elif ender == ')':
            word += ')'
            ender = ''
            

        # if starter == '{' and ender == '}' ):
        #     # Ignore {} delimiting chords
        #     starter = ''
        #     ender = '  '

        return word, starter, ender
    def markup_chord_line(self,line,transpose,prefer_sharp):
        comline = self.is_comment_line(line)
        if comline:
            return '<br><div class=commentline>' + re.sub( ' ', '&nbsp;', comline ) + '</div>'
        splits = re.split( r'(\s+)', line)
        # this splits the line at start/end of whitespace regions,
        # so that contiguous whitespace counts as a word
        formatted = '<br>'
        got_a_not_chord = False
        for word in splits:
            if word == '':
                pass
            elif '---' in word:
                # disables highlighting on tab lines
                got_a_not_chord = True
                formatted += word
            elif ',' in word:
                got_a_not_chord = True
                formatted += word
            elif word.isspace():
                formatted += re.sub( ' ', '&nbsp;', word )
            elif word == 'etc' or word == 'etc.':
                formatted += '...'
            elif word in [ 'n.c.', 'nc', 'n.c' ]:
                if word == 'n.c.':
                    formatted += '<div class=chordline>n/c</div> '
                elif word == 'n.c':
                    formatted += '<div class=chordline>n/c</div>'
                elif word == 'nc':
                    formatted += '<div class=chordline>n/c</div>'
            elif word in [ '|', '-', '%', '*', '.', '|:', ':|' ]:
                # | and - are used for timing (and are also allowed as starter/ender delimieters)
                # % is sometimes used for repetition.
                formatted += word
            elif re.match( '\(?\s*[xX]\s*\d+\s*\)?', word ):
                # this is to match (x4) for repetition
                formatted += '<div class=commentline>' + word + '</div>'
            else:
                word, starter, ender = self.strip_delimeters(word)
                chord = CRD_chord(word)
                if chord.is_chord():
                    crd = chord.format(transpose,prefer_sharp)
                    fingering = self.get_fingering(crd)
                    # if fingering == "" and self.tuning:
                    #     print( "[%s] No fingering for %s" % ( self.tuning.name(), crd ) )
                    formatted += starter + '<div class=chordline%s>%s</div>%s' % \
                                                ( fingering, crd, ender )
                else:
                    got_a_not_chord = True
                    formatted += starter + word + ender
        if got_a_not_chord:
            return '<br>' + re.sub( ' ', '&nbsp;', line )
        return formatted
    def format_song_lines(self,transpose=0,prefer_sharp=False):
        formatted = [ self.markup_chord_line(line,transpose,prefer_sharp) for line in self.lines ]
        return formatted
    def add_line(self,newline):
        line = newline.rstrip()
        self.lines.append(line)
        if not self.tuning:
            if 'tuning:' in line.lower():
                self.tuning = CRD_tuning(line)
                if self.tuning.standard():
                    self.tuning = None
    def longest_line(self):
        lengths = [ len(l) for l in self.lines ]
        return max(lengths)
    def inherit_fingerings(self,stock_tunings):
        # looks up the current tuning in the stock_tunings list
        # and uses it to inject unspecified fingerings into the 
        # self.tuning object
        stock_tuning = None
        for t in stock_tunings:
            if self.tuning:
                if t.name() == self.tuning.name():
                    stock_tuning = t
                    break
            elif t.name() == 'standard':
                stock_tuning = t
                break
        if stock_tuning:
            for crd, fing in t.fingerings.items():
                if self.get_fingering( crd ) == "":
                    self.add_fingering( crd, fing )
    def html(self,stock_tunings=[],add_artist=False,transpose=0,prefer_sharp=False):
        self.inherit_fingerings(stock_tunings)
        lines  = [ '<hr> <a class=songlink name=%s>' % self.link ] 
        name = ''
        if add_artist:
            name = ' (%s)' % self.artist
        lines += [ '<h3><div title="%s">%s</div></h3>' % (self.index, self.title + name) ]
        if len(self.lines) > 100 and self.longest_line() <= 83:
            lines += [ '<div class=chords_3col>' ]
        elif len(self.lines) > 50:
            lines += [ '<div class=chords_2col>' ]
        else:
            lines += [ '<div class=chords_1col>' ]
        lines += self.format_song_lines(transpose,prefer_sharp)
        lines += [ '</div>' ]
        lines += [ '<br><br>' ]
        return lines
    def latex(self):
        lines  = [ r'\documentclass{article}' ]
        lines += [ r'\usepackage[a4paper,margin=2cm]{geometry}' ]
        lines += [ r'\begin{document}' ]
        lines += [ r'\pagenumbering{gobble}' ]
        lines += [ r'\begin{verbatim}' ]
        lines += [ self.title ]
        lines += [ '=' * len(self.title) ]
        lines += [ '' ]
        for line in self.lines:
            lines.append(line)
        lines += [ r'\end{verbatim}' ]
        lines += [ r'\end{document}' ]

        if not os.path.isdir('tex'):
            os.makedirs('tex')

        p = subprocess.Popen(['pdflatex','-output-directory=tex', '-jobname=chordproc'], shell=False,
                             stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        output = p.communicate(input='\n'.join(lines).encode())
        #print(output)
    def search(self,pattern):
        pass
        # return list of artists

class CRD_data():
    def __init__(self,opts,lines=None):
        self.opts = opts
        self.artists = []
        self.tunings = []
        self.n_artists = 0
        self.albums = []
        self.songs = []
        self.collections = []
        self.laud_data = LAUD_data()
        self.stock_tunings = self.load_tuning_data()

        if lines:
            self.process_chord_lines(lines)
        else:
            self.load_song_data()
    def __update_options(self,opts):
        newopts = {}
        newopts["update"]    = opts.get("update",    False)
        #newopts["html"]      = opts.get("html",      False)
        #newopts["gui"]       = opts.get("gui",       False)
        newopts["tunings"]   = opts.get("tunings",   None)
        newopts["html_root"] = opts.get("html_root", r'html/')
        newopts["root"]      = opts.get("root",      r'crds')
        newopts["pickle"]    = opts.get("pickle",    r'/home/jpf/bin/chord_pickle')
        return newopts
    def summarise_data(self):
        print( "artists: %d" % len(self.artists) )
        print( "albums:  %d" % len(self.all_albums() ) )
        print( "songs:   %d" % len(self.all_songs() ) )
        print( "tunings: %d" % len(self.tunings) )

        artists = self.artists[:]
        artists.sort(key=lambda x: len(x.albums))

        for artist in artists:
            n_albums = len(artist.albums)
            n_songs = len(artist.all_songs())
            print( "%s : %d / %d" % ( artist.name.rjust(35), n_albums, n_songs ) )
    def all_albums(self):
        if len(self.albums) == 0:
            for artist in self.artists:
                for album in artist.albums:
                    self.albums.append(album)
            self.albums.sort( key=lambda x: x.title )
        return self.albums
    def all_songs(self):
        if len(self.songs) == 0:
            for album in self.all_albums():
                for song in album.songs:
                    self.songs.append(song)
            self.songs.sort( key=lambda x: x.title_sort )
        return self.songs
    def get_artist(self,name):
        for a in self.artists:
            if a.name == name:
                return a
        self.n_artists += 1
        a = CRD_artist(name,self.n_artists,self.laud_data)
        self.artists.append(a)
        return a
    def process_chord_file(self,path):
        lines = []
        try:
            with open(path,encoding='utf-8') as f:
                lines = f.readlines()
            self.process_chord_lines(lines,path)
        except:
            raise
            #print("Failed to process " + path + " (non-ASCII character?)")
    def process_chord_lines(self,lines,path=None):
        level = 0
        this_artist = None
        this_album  = None
        this_song   = None
        level_artist = 0
        level_album  = 0
        level_song   = 0
        comment_level = 0
        newsongs = []
        for line in lines:
            mopen = re.match('^\s*\{\{\{\s+(.*)',line)
            mclose = re.match('^\s*\}\}\}',line)
            mblank = re.match('^\s*$',line)
            mc = re.match('^\s*\{\{\{\s*---',line)
            if mopen:
                level += 1
                title = mopen.group(1)
                if comment_level > 0:
                    pass
                elif len(title) >= 3 and title[0:3] == '---':
                    comment_level = level
                elif len(title) > 6 and title[0:6] == 'artist':
                    a_name = re.match( '.*artist:\s+(.*)', line ).group(1)
                    this_artist = self.get_artist(a_name)
                    level_artist = level
                elif len(title) > 6 and title[0:5] == 'album':
                    a_name = re.match( '.*album:\s+(.*)', line ).group(1)
                    if not this_artist:
                        this_artist = self.get_artist('Misc')
                    this_album = this_artist.add_album(a_name)
                    level_album = level
                elif len(title) > 4 and title[0:4] == 'song':
                    s_name = re.match( '.*song:\s+(.*)', line ).group(1)
                    if not this_artist:
                        this_artist = self.get_artist('Misc')
                    if not this_album:
                        this_album = this_artist.add_album('Misc')
                    this_song = this_album.add_song(s_name,path)
                    newsongs.append(this_song)
                    level_song = level
                else:
                    print("Unknown fold type in %s: %s" % (path, line.strip()))
            elif mclose:
                if this_song and level_song == level:
                    this_song = None
                if this_album and level_album == level:
                    this_album  = None
                if this_artist and level_artist == level:
                    this_artist = None
                if comment_level > 0 and comment_level == level:
                    comment_level = 0
                level -= 1
            elif this_song:
                this_song.add_line(line.rstrip())
        for song in newsongs:
            # strip empty lines at start and end
            start_index = 0
            end_index = len(song.lines)
            for line in song.lines:
                if len(line.strip()) > 0:
                    break
                start_index += 1
            for line in reversed(song.lines):
                if len(line.strip()) > 0:
                    break
                end_index -= 1
            song.lines = song.lines[ start_index : end_index ]
    def load_tuning_data(self):
        lines = []
        if self.opts["tunings"] and os.path.isfile(self.opts["tunings"]):
            with open(self.opts["tunings"]) as f:
                lines = f.readlines()

        current_tuning = None
        tunings = []

        for line in lines:
            mopen = re.match('^\s*\{\{\{\s+(.*)',line)
            mclose = re.match('^\s*\}\}\}',line)
            mblank = re.match('^\s*$',line)
            mc = re.match('^\s*\{\{\{\s*---',line)
            if mblank:
                pass
            elif mclose and current_tuning:
                tunings.append( current_tuning )
                current_tuning = None
            elif mopen:
                splits = mopen.group(1).split()
                if len(splits) > 0:
                    if splits[0] == 'tuning:':
                        notes = splits[1]
                        names_str = " ".join(splits[2:])
                        names = re.findall('\[([a-zA-Z0-9 ]+)\]', names_str )
                        if len(names) > 0:
                            current_tuning = CRD_tuning( notes, names )
                        else:
                            print("Tuning %s has no name" % notes)
            elif current_tuning:
                splits = line.strip().split()
                if len(splits) == 2:
                    chord = splits[0]
                    fingering = splits[1]
                    current_tuning.fingerings[chord] = fingering

        # for t in tunings:
        #     print( "==== %s" % t )
        #     for key, value in t.fingerings.items():
        #         print( "     " + key.ljust(10) + value )

        return tunings
    def load_song_data(self):
        if self.opts["update"] or not os.path.isfile(self.opts["pickle"]):
            self.build_song_data()
            self.group_songs_by_tunings()
            with open(self.opts["pickle"],'wb') as f:
                pickle.dump( ( self.artists, self.tunings, self.collections ), f )
        else:
            with open(self.opts["pickle"],'rb') as f:
                self.artists, self.tunings, self.collections = pickle.load(f)
        #self.summarise_data()
    def build_song_data(self):
        for f in glob.glob(self.opts["root"] + '/*.crd'):
            self.process_chord_file(f)
        self.artists.sort(key=lambda x: x.name)
        if os.path.isfile('collections.html'):
            lines = []
            with open('collections.html') as f:
                lines = f.readlines()
            self.collections = [ x for x in lines if 'href' in x ]
    def group_songs_by_tunings(self):
        if not self.tunings:
            self.tunings = []
            for artist in self.artists:
                for album in artist.albums:
                    for song in album.songs:
                        if song.tuning:
                            try:
                                offsets = [ x.tuning.offset() for x in self.tunings ]
                                pos = offsets.index(song.tuning.offset())
                            except ValueError:
                                tuning_artist = CRD_artist(song.tuning.summary())
                                tuning_artist.add_album('Misc')
                                tuning_artist.tuning = song.tuning
                                tuning_artist.fname = song.tuning.offset() + '.html'
                                self.tunings.append(tuning_artist)
                                pos = len(self.tunings)-1
                            self.tunings[pos].albums[0].songs.append(song)
            # sort by offset => similar tuning appear next to each other
            self.tunings.sort(key=lambda x: x.tuning.offset())
        return self.tunings
    def make_html(self):
        artist_lines  = [ '<html>', '<body>', '<head>' ]
        artist_lines += [ '<title>Chordproc</title>' ]
        artist_lines += common_html()
        artist_lines += [ '</head>' ]
        artist_lines += [ '<h2>ChordProc</h2>' ]
        artist_lines += [ '<hr>' ]
        artist_lines += [ '<br>' ]
        artist_lines += [ '<div class=artistlist>' ]
        artist_lines += [ '<ul>' ]
        misc = []
        for artist in self.artists:
            if not artist.name == 'Misc':
                artist_lines.append( '<li><a href="%s">%s</a> <div class=count>%d/%d</div>' % 
                    ( artist.fname, artist.name, len(artist.all_songs()), len(artist.albums) ) )
            with open(self.opts["html_root"] + artist.fname, 'w') as f:
                for l in artist.html(self.stock_tunings):
                    f.write('\n' + l)
            for album in artist.albums:
                album_path = self.opts["html_root"] + album.fname
                with open(album_path, 'w') as f:
                    for l in album.html(self.stock_tunings):
                        f.write('\n' + l)
                if artist.name == 'Misc':
                    misc.append( [ album, album.fname ] )
            with open(self.opts["html_root"] + artist.index_fname, 'w') as f:
                for l in artist.html_index():
                    f.write('\n' + l)
        artist_lines += [ '</ul>', '</div>' ] 

        artist_lines += [ '<hr>' ]
        artist_lines += [ '<div class=artistlist>' ]
        # indices
        artist_lines += [ '<br>Indices', '<ul>' ]
        artist_lines += [ '<li> <a href=tunings.html>Tuning Index</a>' ]
        artist_lines += [ '<li> <a href=allsongs.html>Song Index</a>' ]
        artist_lines += [ '</ul>' ]
        artist_lines += [ '<br>' ]
        artist_lines += [ '<br>' ]
        artist_lines += [ '<br>' ]

        # misc
        artist_lines += [ '<br>Misc by genre:', '<ul>' ]
        for album, path in misc:
            artist_lines.append( '<li><a href=%s>%s</a>' % ( path, album.title ) )
        artist_lines += [ '</ul>' ]

        # collections
        if len(self.collections) > 0:
            artist_lines += [ '<br>External collections:', '<ul>' ]
            for collection in self.collections:
                artist_lines.append( collection )
            artist_lines += [ '</ul>' ]
            artist_lines += [ '<br>' ]
            artist_lines += [ '<br>' ]
            artist_lines += [ '<br>' ]
            artist_lines += [ '<br>' ]
            artist_lines += [ '<br>' ]
            artist_lines += [ '<br>' ]

        artist_lines += [ '</div>' ]
        artist_lines += [ '<hr>' ]

        artist_lines += [ '</body>', '</html>' ]
        with open(self.opts["html_root"] + 'index.html', 'w') as f:
            for l in artist_lines:
                f.write('\n' + l)
        
        tuning_lines  = [ '<html>', '<body>', '<head>' ]
        tuning_lines += [ '<title>Chordproc</title>' ]
        tuning_lines += common_html()
        tuning_lines += [ '</head>' ]
        tuning_lines += [ '<h2>ChordProc Tunings</h2>' ]
        tuning_lines += [ '<ul>' ]
        for tuning in self.group_songs_by_tunings():
            tuning_lines.append( '<li><a class=tuning href="%s">%s</a> <div class=count>%d</div>' % 
                    ( tuning.fname, tuning.name, len(tuning.all_songs() ) ) )
            with open(self.opts["html_root"] + tuning.fname, 'w') as f:
                for l in tuning.html(self.stock_tunings,True):
                    f.write('\n' + l)
        tuning_lines += [ '</ul>', '</body>', '</html>' ]
        with open(self.opts["html_root"] + 'tunings.html', 'w') as f:
            for l in tuning_lines:
                f.write('\n' + l)

        index_lines  = [ '<html>', '<body>', '<head>' ]
        index_lines += [ '<title>Chordproc</title>' ]
        index_lines += common_html()
        index_lines += [ '</head>' ]
        index_lines += [ '<h2>ChordProc Song Index</h2>' ]
        index_lines += [ '<hr>', '<div class=songindex>' ]
        allsongs = self.all_songs()
        cur_letter = None
        for song in allsongs:
            if cur_letter == None:
                pass
            elif cur_letter != song.title_sort[0]:
                index_lines.append('<br>')
                index_lines.append('<br>')
            else:
                index_lines.append( '<br>' )
            cur_letter = song.title_sort[0]
            s_link = song.album.fname + '#' + song.link
            index_lines.append( '<a href=%s>%s</a> (%s)' % ( s_link, song.title, song.artist ) )
        index_lines += [ '</div>', '</body>', '</html>' ]
        with open(self.opts["html_root"] + 'allsongs.html', 'w') as f:
            for l in index_lines:
                f.write('\n' + l)

class CRD_gui(QMainWindow, Ui_MainWindow):
    def __init__(self, chords):
        super(self.__class__, self).__init__()
        self.chords = chords
        self.setupUi(self)
        self.searchPattern = ''
        self.importPattern = ''

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

    def makeTree(self,root,collection):
        for artist in collection:
            branch = QStandardItem(artist.name)
            branch.setData(artist)
            for album in artist.albums:
                album_item = QStandardItem(album.title)
                album_item.setData(album)
                child = branch.appendRow(album_item)
                for song in album.songs:
                    song_item = QStandardItem(song.title)
                    song_item.setData(song)
                    grandchild = album_item.appendRow(song_item)
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
        lines = song.html([],add_artist,transpose,prefer_sharp)
        text = "\n".join(lines)
        text = re.sub( '<div class=chordline[^>]*>([^<]*)</div>', 
                      r'<font color="blue">\1</font>', text )
        text = re.sub( '<(\/?)h1>', '<\1h1>', text )
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

    def onSearchTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 2

    def onImportTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 3

    def onArtistsTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 0

    def onTuningsTab(self):
        tabindex = self.tabWidget.currentIndex()
        return tabindex == 1

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

    def onArtistClick(self, index):
        item = index.model().itemFromIndex(index)
        if not item.data():
            pass
        elif isinstance(item.data(),CRD_song):
            self.currentArtistSong = item.data()
            text = self.tweak_html(self.currentArtistSong, self.currentTranspose())
            self.currentViewer().setHtml(text)
        elif isinstance(item.data(),CRD_album):
            album = item.data()
            link = album.get_playlist_link()
            if link: self.currentViewer().setHtml(link)

    def onTuningClick(self, index):
        item = index.model().itemFromIndex(index)
        song = item.data()
        if song:
            self.currentTuningSong = song
            text = self.tweak_html(self.currentTuningSong,self.currentTranspose())
            self.currentViewer().setHtml(text)

    def onSearchClick(self, index):
        item = index.model().itemFromIndex(index)
        song = item.data()
        if song:
            self.currentSearchSong = song
            text = self.tweak_html(self.currentSearchSong,self.currentTranspose())
            self.currentViewer().setHtml(text)

    def onImportClick(self, index):
        item = index.model().itemFromIndex(index)
        song = item.data()
        if song:
            self.currentImportSong = song
            text = self.tweak_html(self.currentImportSong,self.currentTranspose())
            self.currentViewer().setHtml(text)

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

        if self.searchPattern != '':
            first = None
            for artist in self.chords.artists:
                for album in artist.albums:
                    for song in album.songs:
                        if self.searchPattern in song.title.lower():
                            song_item = QStandardItem(song.title)
                            song_item.setData(song)
                            if first == None:
                                first = song_item
                            self.rootSearch.appendRow(song_item)
            if first:
                # select and view first match:
                index = first.index()
                self.treeSearch.setCurrentIndex(index)
                self.treeSearch.setFocus()
                self.onArtistClick(index)

    def transposeUp(self):
        if self.onArtistsTab():
            song = self.currentArtistSong
            if song:
                text = self.tweak_html(self.currentArtistSong,self.currentTranspose(1),True)
                self.currentViewer().setHtml(text)
        elif self.onSearchTab():
            song = self.currentSearchSong
            if song:
                text = self.tweak_html(self.currentSearchSong,self.currentTranspose(1),True)
                self.currentViewer().setHtml(text)
        elif self.onImportTab():
            song = self.currentImportSong
            if song:
                text = self.tweak_html(self.currentImportSong,self.currentTranspose(1),True)
                self.currentViewer().setHtml(text)

    def transposeDown(self):
        if self.onArtistsTab():
            song = self.currentArtistSong
            if song:
                text = self.tweak_html(self.currentArtistSong,self.currentTranspose(-1),False)
                self.currentViewer().setHtml(text)
        elif self.onSearchTab():
            song = self.currentSearchSong
            if song:
                text = self.tweak_html(self.currentSearchSong,self.currentTranspose(-1),False)
                self.currentViewer().setHtml(text)
        elif self.onImportTab():
            song = self.currentImportSong
            if song:
                text = self.tweak_html(self.currentImportSong,self.currentTranspose(-1),False)
                self.currentViewer().setHtml(text)

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

        self.modelImport.clear()
        self.rootImport = self.modelImport.invisibleRootItem()

        self.makeTree(self.rootImport, import_data.artists)

    def parseHTML(self,html,url):
        # Works nicely for ultimate-guitar
        # https://tabs.ultimate-guitar.com/tab/belle_and_sebastian/seeing_other_people_chords_61835

        lines = html.split("\n")
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
            newlines = newlines[1:-2]

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

    def handleEnter(self):
        if self.onSearchTab():
            if self.patternChanged():
                #self.searchMainTabs()
                self.searchTab()
            else:
                tree = self.currentTree()
                if tree:
                    index = tree.selectedIndexes()[0]
                    self.onSearchClick(index)
        elif self.onImportTab():
            if self.importChanged():
                text = self.importEdit.text()
                self.importGeneral()
            else:
                tree = self.currentTree()
                if tree:
                    index = tree.selectedIndexes()[0]
                    self.onImportClick(index)
        else:
            tree = self.currentTree()
            if tree:
                index = tree.selectedIndexes()[0]
                self.onArtistClick(index)

    def handleLeft(self):
        indices = self.currentTree().selectedIndexes()
        if len(indices) > 0:
            index = indices[0]
            item = index.model().itemFromIndex(indices[0])
            if not item.data():
                pass
            if isinstance(item.data(),CRD_artist):
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

class CRD_interface():
    @staticmethod
    def gui(data):
        app = QApplication(sys.argv)
        form = CRD_gui(data)
        form.show()
        app.exec_()

