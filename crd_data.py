import glob
import os
import pickle
import re
import subprocess
import datetime

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

DO_WORDLISTS = [] # [ "Bob Dylan" ]
VERSIONS_ARE_SONGS = False # whether versions are separate songs, or appended to main song
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def common_html(want_chord_controls=True):
    lines = [
    '<link rel="shortcut icon" href="thumb.ico" type="image/x-icon">',
    '<link rel="stylesheet" type="text/css" href="style1.css" id="style">',
    '<script src="script.js"></script>',
    '<a onclick="cycle_styles();" title="Cycle Styles"><div id=t_r></div></a>',
    ]
    if want_chord_controls:
        lines += [
        '<a onclick="transpose_up();" title="Transpose Up"><div id=t_l></div></a>',
        '<a onclick="transpose_down();" title="Transpose Down"><div id=b_l></div></a>',
        '<a onclick="hide_chords();" title="Hide Chords"><div id=b_r></div></a>',
        ]
    return lines

class CRD_artist():
    def __init__(self,name,index=0,data=None):
        self.name = name.strip()
        self.albums = []
        self.index = index
        self.player = None
        self.stock_tunings = None
        if data:
            self.player = data.player
            self.stock_tunings = data.stock_tunings

        alphaname = ''.join( [y for y in self.name if y.isalnum()] )
        self.fname = 'artist_' + alphaname + '.html'
        self.index_fname = 'artist_' + alphaname + '_index.html'
        self.words_fname = 'artist_' + alphaname + '_words.html'
        self.tuning = None
        self.words = {}
    def add_album(self,title):
        album_index = '%d.%d' % ( self.index, len(self.albums) + 1 )
        new_album = CRD_album( title, self, album_index, self.player )
        self.albums.append(new_album)
        return new_album
    def all_songs(self):
        allsongs = []
        for album in self.albums:
            for song in album.songs:
                allsongs.append(song)
        allsongs.sort(key=lambda x: x.title_sort)
        return allsongs
    def html(self,add_artist=False):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % self.name ]
        lines += common_html(False)
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s</title></h2>' % (self.index, self.name) ]
        #total_songs = sum( [ len(a.songs) for a in self.albums ] )
        c_origs, c_covers = self.song_counts()
        if c_covers:
            count_string = "(%d) (%d originals)" % (c_origs + c_covers, c_origs)
        else:
            count_string = "(%d)" % (c_origs + c_covers)
        lines += [ '<hr>', '<a href="%s">Song Index %s</a>' % ( self.index_fname, count_string ) ]

        if DO_WORDLISTS and self.name in DO_WORDLISTS:
            lines += [ '<br>', '<a href="%s">Word Index</a>' % ( self.words_fname ) ]

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
    def html_index(self):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % self.name ]
        lines += common_html(False)
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s Song Index</title></h2>' % (self.index, self.name) ]
        lines += [ '<hr>', '<br>', '<div class=songindex>' ]
        #lines += [ '<ol>' ]
        allsongs = self.all_songs()
        cur_letter = None
        for song in allsongs:
            if cur_letter == None:
                pass
            elif not song.title_sort[0] in ALPHABET:
                lines.append( '<br>' ) # all non alpha characters in same section
            elif cur_letter != song.title_sort[0]:
                lines.append('<br>')
                lines.append('<br>')
            else:
                lines.append( '<br>' )
            cur_letter = song.title_sort[0]
            s_link = song.album.fname + '#' + song.link
            s_class = ' class=cover' if song.cover else ''
            lines.append( '<a href=%s%s>%s</a> (%s)' % ( s_link, s_class, song.title, song.album.title ) )
        #lines += [ '</ol>' ]
        lines += [ '</div>', '<br>' ]
        lines += [ '</body>', '</html>' ]
        return lines
    def latex(self):
        lines  = [ r'\documentclass{article}' ]
        lines += [ r'\usepackage[a4paper,margin=1cm]{geometry}' ]
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

        name = self.fname.replace(".html", "")

        p = subprocess.Popen(['pdflatex','-output-directory=tex', '-jobname='+name], shell=False,
                             stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        output = p.communicate(input='\n'.join(lines).encode())
        print(name)
    def remove_abbreviations(self, words):
        delwords = []
        for word in words.keys():
            if word.endswith("'"):
                unabbr = word[:-1] + "G"
                if unabbr in words:
                    words[unabbr] += words[word]
                    delwords.append(word)

        for word in delwords:
            del words[word]
    def get_words(self):
        if not self.words:
            for album in self.albums:
                for song in album.songs:
                    song.get_words(album.words)

                self.remove_abbreviations(album.words)

                for word in album.words:
                    if word not in self.words:
                        album.new_words.append(word)

                for song in album.songs:
                    song.get_words(self.words)

                print(str(len(album.words)).rjust(10), album.title, len(album.new_words))

            self.remove_abbreviations(self.words)

        return self.words
    def words_html(self):
        words = self.get_words()
        wordlist = list(words.keys())
        wordlist.sort()
        print(self.name, len(words), "words")
        #wordlist.sort(key=lambda w: len(words[w])) # sort by number of songs

        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Concordance: %s</title>' % self.name ]
        lines += [ '</head>' ]
        lines += [ '<h2>Concordance: %s</h2>' % self.name ]
        lines += [ '<hr>' ]
        lines += [ str(len(wordlist)) ]

        alphastring = ''
        for char in list(ALPHABET):
            alphastring += '<a href="#%s">%s</a> ' % ( char, char )
        lines += [ alphastring ]

        lines += [ '<hr>' ]

        cur_letter = None
        for word in wordlist:
            if cur_letter == None:
                pass
            elif not word[0] in ALPHABET:
                lines.append('<br>')
            elif cur_letter != word[0]:
                lines.append('</div>')
                lines.append('<a name="%s">' % word[0])
                lines.append('<br><hr>')
                #lines.append('<h3>%s</h3>' % word[0])
                lines.append('<div class=songindex>')
            else:
                lines.append('<br>')
            cur_letter = word[0]

            line = "<b>" + word + "</b>"
            songs = words[word]
            songs.sort(key = lambda s: s.title_sort.lower())
            for song in songs:
                link = song.album.fname + '#' + song.link
                line += ' | <a href="%s">%s</a>' % ( link, song.title ) 
            lines.append(line)

        lines += [ '</ul>' ]
        lines += [ '</body>', '</html>' ]

        return lines
    def song_counts(self):
        origs = 0
        covers = 0
        for a in self.albums:
            for s in a.songs:
                if s.cover:
                    covers += 1
                else:
                    origs += 1

        return (origs, covers)

def set_title_and_date(title):
    date = None
    
    regex_date = "\s*<(\d\d\d\d)-(\d\d)-(\d\d)>\s*$"
    m_date = re.search(regex_date, title)

    if m_date:
        title = re.sub(regex_date, "", title)
        date = datetime.date(int(m_date.group(1)), int(m_date.group(2)), int(m_date.group(3)))
    else:
        regex_year = "\s*<(\d\d\d\d)>\s*$"
        m_year = re.search(regex_year, title)

        if m_year:
            title = re.sub(regex_year, "", title)
            date = datetime.date(int(m_year.group(1)), 1, 1)

    # if date: print(date)
    title  = " ".join( x[0].upper() + x[1:] for x in title.strip().split())
    return title, date

class CRD_album():
    def __init__(self,title,artist,index,player):
        self.title, self.date = set_title_and_date(title)
        self.artist = artist
        self.index  = index
        self.player = player
        self.songs  = []
        self.words  = {}
        self.new_words = []
        name = ( artist.name if artist else '' ) + '_' + title
        alpha = lambda x: ''.join( [y for y in x if y.isalnum()] )
        alphaname = ( alpha(artist.name) if artist else '' ) + '_' + alpha(title)
        self.fname = 'album_' + alphaname + '.html'
    def add_song(self,title,fpath,lnum):
        song_index = self.index + '.%d' % ( len(self.songs) + 1 )
        apath = os.path.abspath(fpath)
        new_song = CRD_song(title,self.artist,apath,lnum,song_index)
        self.songs.append(new_song)
        new_song.album = self
        return new_song
    def html(self):
        title = self.artist.name + ' : ' + self.title
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc: %s</title>' % title ]
        lines += common_html()
        lines += [ '</head>' ]
        lines += [ '<h2><div title="%s">%s</div></h2>' % (self.index, title) ]
        #lines += [ self.get_playlist_link() ]
        lines += [ '<hr>', '<ol>' ]
        songs_body = []
        for song in self.songs:
            songs_body += song.html()[:] # must do this first, to set song.cover
            if VERSIONS_ARE_SONGS:
                for version in song.versions:
                    songs_body += version.html()[:]
        for song in self.songs:
            s_class = ' class=cover' if song.cover else ''
            lines.append( '<li><a href=#%s%s>%s</a>' % ( song.link, s_class, song.title ) )
            if VERSIONS_ARE_SONGS and song.versions:
                lines.append('<ul>')
                for version in song.versions:
                    lines.append( '<li><a href=#%s>%s</a>' % ( version.link, version.title ) )
                lines.append('</ul>')
        lines += [ '</ol>' ]
        lines += songs_body
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
    def get_playlist(self):
        playlist, image = self.player(self.artist.name, self.title)
        return playlist
    def get_playlist_link(self):
        playlist, image = self.player(self.artist.name, self.title)
        if playlist and image:
            link = '<a href="%s"><img class=cover src="%s"></a>' % ( playlist, image )
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

        nochord_chars = [ 'l', 'k', 't', 'h', 'gg', 'y', 'ing' ]

        # the following notes cannot occur consecutively (e.g. Free) 
        for note in [ 'c', 'e', 'f', 'g' ]:
            if note + note in self.string.lower():
                self.root = None
                self.bass = None
                return False

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

        if self.string[0] != '/' and self.string[1:] in [ 'ome', 'a', 'ip', 'oo', 'gain', 'ocaine!', 'um', 'o' ]:
            # Come  (Pissing in a River)
            # Ba    (Looking at Tomorrow)
            # Bip   (Looking at Tomorrow)
            # Doo   (Til I Die)
            # Again (Crumb Begging Baghead)
            # Cocaine, Dum, Do
            # print("Rejecting: " + self.string)
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
    def get_fingering(self,crd_string,as_title=False):
        fingering = ''
        try:
            fingering = self.fingerings[crd_string]
            if as_title:
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
                     [ 'CGCGCE',  'open C' ],
                     [ 'CGDGBE',  'drop C/g' ],
                     [ 'DADGBD',  'double drop D' ],
                     [ 'EADGBE',  'standard' ],
                     [ 'EAC#EAE', 'open A' ],
                     [ 'EBEG#BE', 'open E' ],
                     [ 'EBEGBE', 'open Em' ],
                     [ 'DADGAD', 'open Dsus4' ],
                     [ 'CFCFCF', 'open F5' ],
                     [ 'DADEAD', 'open Dsus2' ],
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
        if not self.tuning:
            print("Error: no name for tuning: " + self.input_string)
        return self._name
    def standard(self):
        return self._name and self._name.lower() == 'standard'
    def summary(self):
        tuning = self.tuning
        offset = "[" + self.offset() + "]"
        name = self._name if self._name else ""
        return tuning.ljust(12,"_") + offset.ljust(10,"_") + name.ljust(20,"_")

class CRD_song():
    def __init__(self,title,artist,fpath,lnum,index):
        self.title, self.date = set_title_and_date(title)
        self.artist = artist
        self.fpath = fpath
        self.lnum = lnum
        self.index = index
        self.lines = []
        self.versions = []
        self.version = False
        self.tuning = None
        self.album = None
        self.comchar = '%'
        self.fingerings = {}
        self.link = ''.join( [x for x in title if x.isalnum() ])
        self.title_sort = re.sub( '\AThe\s+', '', title)
        if title[0] in [ "'", '"', '(' ]:
            self.title_sort = self.title[1:]
        self.gui_item = None
        self.cover = None
        self.wordlist = []
    def add_fingering(self,chord,fingering):
        self.fingerings[ chord.format() ] = fingering.lower()
    def add_version(self,name,path,lnum):
        version = CRD_song(name,self.artist,path,lnum,-1)
        version.version = True
        self.versions.append(version)
        return version
    def get_fingering(self,crd_string,as_title=False):
        fingering = ''
        try:
            fingering = self.fingerings[crd_string]
            if as_title:
                fingering = ' title="%s = %s"' % ( crd_string, fingering )
        except KeyError:
            pass
        return fingering
    def is_comment_line(self,line):
        if line.strip().startswith( self.comchar + ' '):
            comline = line.replace( self.comchar + ' ', '', 1 )
            return comline, "comment"
        elif line.strip().startswith( self.comchar ):
            comline = line.replace( self.comchar, '', 1 )
            return comline, "comment"

        if line.strip().startswith('[') and line.strip().endswith(']'):
            m_ws = re.search('(^\s*)', line)
            return ( m_ws.group(1) + line.strip()[1:-1] ), "comment"

        if line.strip().startswith('<') and line.strip().endswith('>'):
            self.cover = line.strip()[1:-1].strip()
            newline = line.replace('<', '&lt;')
            newline = newline.replace('>', '&gt;')
            return newline, "comment"

        if line.lower().strip().startswith( 'capo' ):
            return line, "capo"
        elif line.lower().strip().startswith( 'harp key:' ):
            return line, "harp"
        elif self.tuning and line.lower().strip().startswith( 'tuning' ):
            link = "<a href=\"tunings.html#%s\">%s</a>" % ( self.tuning.offset(), line )
            return link, "tuning"

        autocomment = False
        if autocomment:
            commentwords = [ 'intro', 'outro', 'twice', 'capo', 
                             'note:', 'verse', 'chorus',
                             'solo', 'tuning' ]

            for cw in commentwords:
                if cw.lower() in line.lower():
                    return line, "comment"

        finger_regex = '([0-9xXA-G]{6,})' 
        if '---' in line:
            pass # line is probably a tab
        elif re.search(finger_regex, line):
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
                    m = re.search(finger_regex, word)
                    if m:
                        # word is fingering
                        fingering = m.group(1)
                        self.add_fingering( chord, fingering )
                        chord = None
                        fingering = None
                else:
                    chord = CRD_chord(word)
            return line, "fingering"

        return None, None
    def strip_delimeters(self,word):
        starter = ''
        ender = ''
        multichars = [ '.' ]
        chars = [ '"', '|', '-', '[', ']', '{', '}', '(', ')' ]

        for x in multichars:
            while word.startswith(x):
                word = word[1:]
                starter += x

            while word.endswith(x):
                word = word[:-1]
                ender += x

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
            starter = '('
            ender = ')'
        elif starter == '(':
            word = word
            starter = '('
        elif ender == ')':
            if '(' in word:
                word += ')'
                ender = ''
            else:
                word += ''
                ender = ')'
            

        # if starter == '{' and ender == '}' ):
        #     # Ignore {} delimiting chords
        #     starter = ''
        #     ender = '  '

        return word, starter, ender
    def markup_chord_line(self,line,transpose=0,prefer_sharp=False,explicit_ws=False):
        leader = '<br>' if explicit_ws else ''
        nbsp = '&nbsp;' if explicit_ws else ' '
        comline, comtype = self.is_comment_line(line)
        if comline:
            if comtype == "harp":
                # strip leading "Harp key:" and format key as chord
                splits = comline.split()
                hkey = splits[2]
                chord = CRD_chord(hkey)
                if chord.is_chord():
                    splits[2] = "<div class=chord>%s</div>" % chord.format(transpose,prefer_sharp)
                    comline = " ".join(splits)
                    comtype = "comment"
            return leader + '<div class=%s>%s</div>' % ( comtype, re.sub( ' ', nbsp, comline ) )
        splits = re.split( r'(\s+)', line)
        # this splits the line at start/end of whitespace regions,
        # so that contiguous whitespace counts as a word
        formatted = leader
        got_a_not_chord = False
        for word in splits:
            if word == '':
                pass
            elif '--' in word:
                # disables highlighting on tab lines
                got_a_not_chord = True
                formatted += word
            elif ',' in word:
                got_a_not_chord = True
                formatted += word
            elif word.replace('.','') == '':
                formatted += word
            elif word.isspace():
                formatted += re.sub( ' ', nbsp, word )
            elif word == 'etc' or word == 'etc.':
                formatted += '...'
            elif word.lower() in [ 'n.c.', 'nc', 'n.c', 'n/c' ]:
                formatted += len(word) * nbsp
            elif re.match( '\(?riff(\s*\d+)?\)?', word.lower() ):
                formatted += '<div class=comment>' + word + '</div>'
            elif re.match( '\$\d+', word ):
                # $1 $2 etc used for links between sections
                formatted += word
            elif word in [ '|', '-', '%', '*', '**', '***', '.', '|:', ':|', '[', ']', '||', '(', ')' ]:
                # | and - are used for timing (and are also allowed as starter/ender delimieters)
                # % is sometimes used for repetition.
                formatted += word
            elif re.match( '\(?\s*[xX]?\s*\d+[xX]?\s*\)?', word ):
                # this is to match (x4) for repetition
                formatted += '<div class=comment>' + word + '</div>'
            else:
                word, starter, ender = self.strip_delimeters(word)
                chord = CRD_chord(word)
                if chord.is_chord():
                    crd = chord.format(transpose,prefer_sharp)
                    fingering = self.get_fingering(crd,True)
                    # if fingering == "" and self.tuning:
                    #     print( "[%s] No fingering for %s" % ( self.tuning.name(), crd ) )
                    formatted += starter + '<div class=chord%s>%s</div>%s' % \
                                                ( fingering, crd, ender )
                else:
                    got_a_not_chord = True
                    formatted += starter + word + ender
        if got_a_not_chord:
            line = re.sub( ' ', nbsp, line )
            line = re.sub( '<', '&lt;', line )
            line = re.sub( '>', '&gt;', line )
            return leader + line
        return formatted
    def format_song_lines(self,transpose=0,prefer_sharp=False,explicit_ws=False):
        formatted = []
        n_tab_lines = 0
        for ii,line in enumerate(self.lines):
            lastline = ii == len(self.lines)-1
            newline = self.markup_chord_line(line,transpose,prefer_sharp,explicit_ws)

            formatted.append(newline)

            change_range = []
            if ('-' in line) and ('|' in line):
                n_tab_lines += 1
                if lastline:
                    change_range = range(1,n_tab_lines+1)
            else:
                if n_tab_lines > 0:
                    change_range = range(2,n_tab_lines+2)
                
            if change_range:
                if n_tab_lines in [4,5,6]: # bass/banjo/guitar tabs
                    for i in change_range:
                        l = formatted[-i]
                        formatted[-i] = '<div class=tabline>%s</div>' % l
                n_tab_lines = 0

        if DO_WORDLISTS and self.artist.name in DO_WORDLISTS:
            self.wordlist_from_formatted_lines(formatted)

        # Now run over list of formatted lines adding spans around 
        # blocks of non-empty lines.

        formatted_with_spans = []
        in_span = False
        for ii, line in enumerate(formatted):
            lastline = ii == len(formatted)-1

            if line == "":
                if in_span:
                    line = "</span>"
                    in_span = False
            elif not in_span and not lastline:
                nextline = formatted[ii+1]
                if nextline != "":
                    line = "<span>" + line
                    in_span = True

            formatted_with_spans.append(line)

        formatted_with_spans.append("</span>") # close last one

        return formatted_with_spans
    def ignore_word(self,word):
        return word in [
        "IT", "THE", "TO", "AND", "THAT", "IN", "YOU", "OF", "MY", "ON",
        "ME", "FOR", "BUT", "ALL", "THERE", "WITH", "IS", "BE", "YOUR", "DOWN",
        "SO", "JUST", "UP", "WHEN", "LIKE", "WHAT", "HE", "NO", "WAS", "DON'T",
        "KNOW", "I'M", "ARE", "FROM", "CAN", "OUT", "GOT", "HAVE", "SHE", "SEE",
        "WELL", "ONE", "IF", "THEY", "NOW", "AT", "GO", "DO", "NOT", "BY",
        "WHERE", "YOU'RE", "AS", "BACK", "THIS", "WILL", "BEEN", "COME", "HIS", "GET",
        "SAY", "CAN'T", "DAY", "OR", "TWO", "WHO", "HAD", "HER", "THROUGH", "SOME", 
        "OH", "COULD", "MORE", "I'LL", "I'VE", "AIN'T", "THEN", "THEM", "THIS", "LET",
        "DID", "GONE", "GONNA", "WOULD", "WERE", "HIM", "ABOUT", "AROUND", "INTO", "ONLY",
        "AN", "MUCH", "ALWAYS", "THEIR", "THEY'RE", "DIDN'T", "YOU'VE", "AM", "I", "THESE",
        ]
    def wordlist_from_formatted_lines(self, formatted):
        songwords = []
        for line in formatted:
            if "<" in line: continue # this is safe because we haven't added <span> yet
            line_words = re.findall("([A-Z']+)", line.upper())
            songwords += line_words

        songwords = list(set(songwords))

        for word in songwords:
            if word.startswith("-") or word.startswith("'"):
                continue
            if word.endswith("-"):
                word = word[:-1]

            # Possessive 's (girl's)
            if word.endswith("'S"):
                word = word[:-2]

            # Grammatical trailing apostrophe (girls')
            if word.endswith("S'"):
                word = word[:-1]

            if len(word) == 1:
                continue

            if re.match('^(LA+)+$', word):
                word = 'LA'
            elif re.match('^O+H+$', word):
                word = 'OH'
            elif re.match('^A+H+$', word):
                word = 'AH'
            elif re.match('^BA+$', word):
                word = 'BA'
            elif re.match('^OO+$', word):
                word = 'OO'
            elif re.match('^DA+$', word):
                word = 'DA'
            elif re.match('^HA+$', word):
                word = 'HA'
            elif re.match('^HO+$', word):
                word = 'HO'
            elif re.match('^HM+$', word):
                word = 'HM'
            elif re.match('^MM+$', word):
                word = 'MM'
            elif re.match('^U+H+$', word):
                word = 'UH'
            elif re.match('^WOO+H*$', word):
                word = 'WOO'

            # Split up a-changing:
            if word.startswith("A-"):
                word = word[2:]
            elif word.startswith("A'"):
                word = word[2:]

            if len(word) == 0:
                continue
            if self.ignore_word(word):
                continue

            self.wordlist.append(word)

        self.wordlist = list(set(self.wordlist))

        return
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
    def inherit_fingerings(self):
        # looks up the current tuning in the stock_tunings list
        # and uses it to inject unspecified fingerings into the 
        # self.tuning object
        stock_tuning = None
        for t in self.artist.stock_tunings:
            if self.tuning:
                if t.name() == self.tuning.name():
                    stock_tuning = t
                    break
            elif t.name() == 'standard':
                stock_tuning = t
                break
        if stock_tuning:
            for crd, fing in t.fingerings.items():
                if self.get_fingering(crd,True) == "":
                    self.add_fingering( crd, fing )
    def process_local_fingerings(self):
        # extract local fingerings from each song line
        for line in self.lines:
            if re.search('[x0-9A-G]{6}', line):
                self.is_comment_line(line)
    def html(self,add_artist=False,transpose=0,prefer_sharp=False,explicit_ws=False):
        self.inherit_fingerings()
        lines = []
        if not self.version:
            lines += [ '<hr> <a name=%s></a>' % self.link ] 
        name = ''
        if add_artist:
            name = ' (%s)' % self.artist.name
        lines += [ '<h3><div title="%s">%s</div></h3>' % (self.index, self.title + name) ]

        n_lines = len(self.lines)
        if not VERSIONS_ARE_SONGS:
            for version in self.versions:
                n_lines += len(version.lines)

        if not self.version:
            if n_lines > 100 and self.longest_line() <= 65:
                lines += [ '<div class=chords_3col>' ]
            elif n_lines > 50:
                lines += [ '<div class=chords_2col>' ]
            else:
                lines += [ '<div class=chords_1col>' ]

        lines += self.format_song_lines(transpose,prefer_sharp,explicit_ws)

        if not VERSIONS_ARE_SONGS:
            for version in self.versions:
                lines += [ "<br>" ]
                lines += version.html(add_artist,transpose,prefer_sharp,explicit_ws)
                #version.inherit_fingerings()
                #lines += [ "<br> <hr> <h2>%s</h3>" % version.title ]
                #lines += version.format_song_lines(transpose,prefer_sharp,explicit_ws)

        if not self.version:
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
    def search(self,pattern,lyrics):
        string = self.title + " "
        if lyrics:
            string += " ".join(self.lines)

        pattern = pattern.lower()
        string = string.lower()

        return re.search(pattern, string)
    def get_mp3_link(self):
        playlist, image  = self.album.player(self.album.artist.name, \
                                             self.album.title, self.title)
        return playlist
    def get_words(self,words,include_covers=False):
        if not include_covers and self.cover: 
            return

        wordlists = [ self.wordlist ]
        for version in self.versions:
            wordlists.append(version.wordlist)

        for wordlist in wordlists:
            for word in wordlist:
                if word in words:
                    words[word].append(self)
                else:
                    words[word] = [self]
        return

class CRD_data():
    def __init__(self,opts,lines=None):
        self.opts = opts
        self.artists = []
        self.tunings = []
        self.n_artists = 0
        self.albums = []
        self.songs = []
        self.collections = []
        self.player = opts.get('player')

        # Note: the "player" callback is a function which takes three strings:
        # an artist name, an album name, and/or a song name
        # It should return a tuple of playlist path and image path
        # (both of which can be None).

        self.stock_tunings = self.load_tuning_data()

        if lines:
            self.process_chord_lines(lines)
        else:
            self.load_song_data( self.opts["update"] )

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
    def resource_root(self):
        # resources prefix
        path = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'resources' + os.sep
        return path
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
            self.songs.sort( key=lambda x: x.title_sort.lower() )
        return self.songs
    def get_artist(self,name):
        for a in self.artists:
            if a.name == name:
                return a
        self.n_artists += 1
        a = CRD_artist(name,self.n_artists,self)
        self.artists.append(a)
        return a
    def process_chord_file(self,path):
        lines = []
        try:
            with open(path,encoding='utf-8') as f:
                lines = f.readlines()
            self.process_chord_lines(lines,path)
        except:
            raise ValueError("Failed to process " + path + " (non-ASCII character?)")
    def process_chord_lines(self,lines,path=None):
        level = 0
        this_artist  = None
        this_album   = None
        this_song    = None
        this_version = None
        level_artist = 0
        level_album  = 0
        level_song   = 0
        comment_level = 0
        newsongs = []
        lnum = 0
        for line in lines:
            lnum += 1
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
                    this_song = this_album.add_song(s_name,path,lnum)
                    newsongs.append(this_song)
                    level_song = level
                elif len(title) > 9 and title[0:7] == 'version':
                    v_name = re.match( '.*version:\s+(.*)', line ).group(1)
                    if not this_artist:
                        print("No artist for version: " + v_name)
                    if not this_album:
                        print("No album for version: " + v_name)
                    if not this_song:
                        print("No song for version: " + v_name)
                    this_version = this_song.add_version(v_name,path,lnum)
                    level_version = level
                else:
                    print("Unknown fold type in %s: %s" % (path, line.strip()))
            elif mclose:
                if this_song and level_song == level:
                    this_song = None
                if this_album and level_album == level:
                    this_album  = None
                if this_artist and level_artist == level:
                    this_artist = None
                if this_version and level_version == level:
                    this_version = None
                if comment_level > 0 and comment_level == level:
                    comment_level = 0
                level -= 1
            elif this_version:
                this_version.add_line(line.rstrip())
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
        path = self.resource_root() + 'stock_tunings.crd'

        if self.opts["tunings"] and os.path.isfile(self.opts["tunings"]):
            path = self.opts["tunings"]

        if os.path.isfile(path):
            with open(path) as f:
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
                if len(splits) > 1:
                    chord = splits[0]
                    fingering = splits[1]
                    current_tuning.fingerings[chord] = fingering

        # for t in tunings:
        #     print( "==== %s" % t )
        #     for key, value in t.fingerings.items():
        #         print( "     " + key.ljust(10) + value )

        return tunings
    def load_song_data(self,update):
        self.artists = []
        self.tunings = []
        self.albums = []
        self.songs = []
        self.collections = []
        if update or not os.path.isfile(self.opts["pickle"]):
            self.build_song_data()

            # This performs the part of song.html() which adds song-specific
            # fingerings to the local chord dictionary. 
            # We generate it here so it will be pickled.
            for s in self.all_songs():
                s.process_local_fingerings()

            self.group_songs_by_tunings()
            with open(self.opts["pickle"],'wb') as f:
                pickle.dump( ( self.artists, self.tunings, self.collections ), f )
        else:
            with open(self.opts["pickle"],'rb') as f:
                self.artists, self.tunings, self.collections = pickle.load(f)
        #self.summarise_data()
    def build_song_data(self):
        for f in glob.glob(self.opts["root"] + '/*.crd'):
            #if not 'neil_young.crd' in f: continue
            #if not 'bob_dylan.crd' in f: continue
            #if not 'bert_jansch.crd' in f: continue
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
    def make_artists_index(self):
        n_artists = 0
        n_albums = 0
        n_songs = 0
        links = []
        for artist in self.artists:
            n_artists += 1
            n_albums += len(artist.albums)
            n_songs += len(artist.all_songs())
            links.append( '<a href="%s">%s</a> <div class=count>%d/%d</div><br>' % 
               ( artist.fname, artist.name, len(artist.all_songs()), len(artist.albums) ) )
            for album in artist.albums:
                album_path = self.opts["html_root"] + album.fname
                with open(album_path, 'w') as f:
                    for l in album.html():
                        f.write('\n' + l)
            with open(self.opts["html_root"] + artist.fname, 'w') as f:
                for l in artist.html():
                    f.write('\n' + l)

            if DO_WORDLISTS and artist.name in DO_WORDLISTS:
                with open(self.opts["html_root"] + artist.words_fname, 'w') as f:
                    for line in artist.words_html():
                        f.write('\n' + line)

            with open(self.opts["html_root"] + artist.index_fname, 'w') as f:
                for l in artist.html_index():
                    f.write('\n' + l)

        return "%d/%d/%d" % (n_songs, n_albums, n_artists), links
    def make_tuning_index(self):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc</title>' ]
        lines += common_html(False)
        lines += [ '</head>' ]
        lines += [ '<h2>ChordProc Tuning Index</h2>' ]
        lines += [ '<hr>' ]
        lines += [ '<ul>' ]

        body = []

        n_tunings = 0
        n_tunings_songs = 0
        for tartist in self.group_songs_by_tunings():
            n_tunings += 1
            n_tunings_songs += len(tartist.all_songs())
            offset = tartist.tuning.offset()
            lines.append( '<li><a class=tuning href="#%s">%s</a> <div class=count>%d</div>' %
                    ( offset, tartist.name, len(tartist.all_songs() ) ) )

            body.append( '<hr> <a name=%s></a>' % offset )
            body.append( '<h3>%s</h3>' % tartist.name )
            body.append( '<ol>' )

            for song in tartist.all_songs():
                s_link = song.album.fname + '#' + song.link
                body.append( '<li> <a href="%s">%s</a> (%s)' % ( s_link, song.title, song.artist.name ) )
            body.append( '</ol>' )
            body.append( '<br>' )

        lines += [ '</ul>', '<br>' ]
        lines += body
        lines += [ '<br>', '</body>', '</html>' ]

        with open(self.opts["html_root"] + 'tunings.html', 'w') as f:
            for l in lines:
                f.write('\n' + l)

        return "%d/%d" % (n_tunings_songs, n_tunings)
    def make_song_index(self):
        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc</title>' ]
        lines += common_html(False)
        lines += [ '</head>' ]
        lines += [ '<h2>ChordProc Song Index</h2>' ]

        alphastring = ''
        for char in list('#' + ALPHABET):
            alphastring += '<a href="#%s">%s</a> ' % ( char, char )
        lines += [ alphastring ]

        lines += [ '<br><hr>', '<h3>#</h3>', '<div class=songindex>' ]
        allsongs = self.all_songs()
        cur_letter = None
        for song in allsongs:
            if cur_letter == None:
                pass
            elif not song.title_sort[0] in ALPHABET:
                lines.append( '<br>' ) # all non alpha characters in same section
            elif cur_letter != song.title_sort[0]:
                lines.append('</div>')
                lines.append('<a name="%s">' % song.title_sort[0])
                lines.append('<br><hr>')
                lines.append('<h3>%s</h3>' % song.title_sort[0])
                lines.append('<div class=songindex>')
            else:
                lines.append( '<br>' )
            cur_letter = song.title_sort[0]
            s_link = song.album.fname + '#' + song.link
            lines.append( '<a href=%s>%s</a> (%s, %s)' % ( s_link, song.title, song.artist.name, song.album.title ) )
        lines += [ '</div>', '</body>', '</html>' ]
        with open(self.opts["html_root"] + 'allsongs.html', 'w') as f:
            for l in lines:
                f.write('\n' + l)
    def make_html(self):
        self.make_song_index()
        artists_summary, artists_links = self.make_artists_index()
        tunings_summary = self.make_tuning_index()

        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc</title>' ]
        lines += common_html(False)
        lines += [ '</head>' ]
        timestamp =  datetime.datetime.now().strftime("%d %b %Y %X")
        lines += [ '<h2><div title="%s">ChordProc</div></h2>' % timestamp ]
        lines += [ '<hr>' ]
        lines += [ '<a href=allsongs.html>Song Index</a> <div class=count>%s</div><br>' % artists_summary ]
        lines += [ '<a href=tunings.html>Tuning Index</a> <div class=count>%s</div><br>' % tunings_summary ]
        lines += [ '<hr>' ]

        lines += [ '<div class=artistlist>' ]
        lines += artists_links
        lines += [ '</div>' ] 
        lines += [ '<hr>' ]
        lines += [ '</body>', '</html>' ]

        with open(self.opts["html_root"] + 'index.html', 'w') as f:
            for l in lines:
                f.write('\n' + l)
    def lookup_chord(self,tuning,chord):
        fingerings = []
        for song in self.all_songs():
            if song.tuning and song.tuning.name() and song.tuning.name() != tuning.name():
                pass
            else:
                fingering = song.get_fingering(chord)
                if fingering:
                    fingerings.append(fingering)

        fingerings = list(set(fingerings))
        return fingerings
    def make_latex_book(self):
        n_artists = 0
        n_albums = 0
        n_songs = 0
        for artist in self.artists:
            artist.latex()

