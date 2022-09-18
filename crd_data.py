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

DO_WORDLISTS = [ ] # [ "Bob Dylan" ]
DO_CRDFILES  = [ ] # [ "robyn_hitchcock.crd" ]
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
FIXED_WIDTH_CHORDS = True
DO_KEY_DIVS = False

def common_html(want_chord_controls=True):
    lines = [
    '<link rel="shortcut icon" href="thumb.ico" type="image/x-icon">',
    '<link rel="stylesheet" type="text/css" href="style1.css" id="style">',
    '<script src="script.js"></script>',
    '<a onclick="cycle_styles();" title="Cycle Styles"><div id=t_r></div></a>',
    ]
    if want_chord_controls:
        lines += [
        '<a onclick="transpose_topmost_song(true);" title="Transpose Up"><div id=t_l></div></a>',
        '<a onclick="transpose_topmost_song(false);" title="Transpose Down"><div id=b_l></div></a>',
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
        alphaname = alphaname.lower()
        self.fname = alphaname + '.html'
        self.index_fname = alphaname + '_songs.html'
        self.words_fname = alphaname + '_words.html'
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
            if album.gap_before: lines.append("<br>")
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
                pass # all non alpha characters in same section
            elif cur_letter != song.title_sort[0]:
                lines.append('<br>')
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
        lines += [ r'\usepackage{dejavu}' ]
        lines += [ r'\renewcommand{\familydefault}{\sfdefault}' ]
        lines += [ r'\usepackage{listings}' ]
        lines += [ r'\lstset{basicstyle=\footnotesize\ttfamily}' ]
        lines += [ r'\begin{document}' ]
        lines += [ r'\pagenumbering{gobble}' ]

        for album in self.albums:
            for song in album.songs:
                lines.append( r'\newpage' )
                lines += [ r'\begin{lstlisting}' ]
                lines += [ song.title ]
                lines += [ '=' * len(song.title) ]
                lines += [ '' ]
                for line in song.lines:
                    lines.append(line)
                lines += [ r'\end{lstlisting}' ]

        lines += [ r'\end{document}' ]

        if not os.path.isdir('tex'):
            os.makedirs('tex')

        name = self.fname.replace(".html", "")

        # with open('tex/' + name + ".tex", "w") as f:
        #     for line in lines:
        #         f.write(line + "\n")

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
        self.gap_before = False
        name = ( artist.name if artist else '' ) + '_' + self.title
        alpha = lambda x: ''.join( [y for y in x if y.isalnum()] )
        alphaname = ( alpha(artist.name) if artist else '' ) + '_' + alpha(self.title)
        alphaname = alphaname.lower()
        self.fname = alphaname + '.html'
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
            songs_body += song.html()[:]
        for song in self.songs:
            s_class = ' class=cover' if song.cover else ''
            if song.gap_before: lines.append("<br><br>")
            lines.append( '<li><a href=#%s%s>%s</a>' % ( song.link, s_class, song.title ) )
        lines += [ '</ol>' ]
        lines += songs_body
        lines += [ '<hr>' ]
        lines += [ '<br>' ] * 10
        lines += [ '</body>', '</html>' ]
        return lines
    def latex(self):
        lines  = [ r'\documentclass{article}' ]
        lines += [ r'\usepackage[a4paper,margin=2cm]{geometry}' ]
        lines += [ r'\usepackage{lstlisting}' ]
        lines += [ r'\usepackage{dejavu}' ]
        lines += [ r'\usepackage[T1]{fontenc}' ]
        lines += [ r'\begin{document}' ]
        lines += [ r'\pagenumbering{gobble}' ]

        for song in self.songs:
            lines.append( r'\newpage' )
            lines += [ r'\begin{lstlisting}' ]
            lines += [ song.title ]
            lines += [ '=' * len(song.title) ]
            lines += [ '' ]
            for line in song.lines:
                lines.append(line)
            lines += [ r'\end{lstlisting}' ]

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
        formatted = self.string
        transpose = transpose % 12

        if self.is_chord():
            max_width = len(formatted)

            if self.root:
                if len(self.root) == 1: max_width += 1

                try:
                    notes = self.__notes(self.root,prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    rootindex = lowernotes.index(self.root.lower())
                except ValueError:
                    notes = self.__notes(self.root,not prefer_sharp)
                    lowernotes = [ n.lower() for n in notes ]
                    rootindex = lowernotes.index(self.root.lower())
                newroot = notes[rootindex + transpose]
                formatted = newroot + formatted[len(self.root):]

            if self.bass:
                if len(self.bass) == 1: max_width += 1

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
                    formatted = '/' + newbass.lower()
                else:
                    formatted = formatted[:-len(self.bass)-1] + '/' + newbass.lower()

            if FIXED_WIDTH_CHORDS and len(formatted) < max_width:
                # pad up to max width to allow room for transposed symbol
                formatted += " " * (max_width - len(formatted))

        return formatted       
    def is_chord(self):
        if self.root == None and self.bass == None:
            return False

        if len(self.string) > 12:
            # G#add9(sus4)
            self.root = None
            self.bass = None
            return False

        nochord_chars = [ '-', 'o', 'r', 'l', 'k', 't', 'h', 'gg', 'y', 'ing' ]
        # we can't ignore "x" because of barre designations: A(ix)

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

        if self.string[0] != '/' and self.string[1:] in [ 'ome', 'a', 'ip', 'oo', 'gain', 'ocaine!', 'um', 'o', 'abe', 'ig', 'XP' ]:
            # Come  (Pissing in a River)
            # Ba    (Looking at Tomorrow)
            # Bip   (Looking at Tomorrow)
            # Doo   (Til I Die)
            # Again (Crumb Begging Baghead)
            # Cocaine, Dum, Do
            # Babe, Dig
            # EXP (Robyn Hitchcock)
            # print("Rejecting: " + self.string)
            return False

        return True

class CRD_tuning():
    def __init__(self,input_string,names=[],stock_tunings=None):
        self.input_string = input_string
        self.tuning = None
        self._name = None
        self.names = names
        self.fingerings = {}
        self.n_strings = 0
        self.stock_tunings = stock_tunings

        if not self.name():
            # extract tuning candidate
            splits = input_string.strip().split(':')
            candidate = splits[0] if len(splits) == 1 else splits[1]
            m = re.match( '([abcdefgABCDEFG#]+).*', candidate.strip() )
            if m:
                self.tuning = m.group(1)
            else:
                raise ValueError( "Failed to extract tuning from " + candidate.strip() )

        tmp_strings = self.tuning.replace("#","")
        tmp_strings = tmp_strings.replace("b","")
        self.n_strings = len(tmp_strings)
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
            if self.stock_tunings:
                for t in self.stock_tunings:
                    tuning_pattern = re.escape(t.tuning.lower())
                    if re.search( r"\b%s\b" % tuning_pattern, self.input_string.lower() ):
                        self.tuning = t.tuning
                        if t.names:
                            self._name = t.names[0]
                            self.names = t.names[:]
                        break

                    if not self._name:
                        for name in t.names:
                            if re.search( r"\b%s\b" % name.lower(), self.input_string.lower() ):
                                self.tuning = t.tuning
                                self._name = name
                                self.names.append(name)
                                break

        #if not self.tuning:
            # If this error gets thrown you may need to add the new tuning
            # to the list in resources/stock_tunings.crd
            #print("Error: no name for tuning: " + self.input_string)
        return self._name
    def standard(self):
        return self._name and self._name.lower() == 'standard'

class CRD_song():
    def __init__(self,title,artist,fpath,lnum,index):
        self.title, self.date = set_title_and_date(title)
        self.artist = artist
        self.fpath = fpath
        self.lnum = lnum
        self.index = index
        self.lines = []
        self.versions = []
        self.version_of = None
        self.tuning = None
        self.album = None
        self.fingerings = {}
        self.gap_before = False
        self.link = ''.join( [x for x in self.title if x.isalnum() ])
        self.title_sort = re.sub( '\AThe\s+', '', self.title)
        if self.title[0] in [ "'", '"', '(' ]:
            self.title_sort = self.title[1:]
        self.gui_item = None
        self.cover = None
        self.current_key = None # last encountered key set by song
        self.wordlist = []
    def add_fingering(self,chord,fingering):
        self.fingerings[ chord.format() ] = fingering.lower()
    def add_version(self,name,path,lnum):
        version = CRD_song(name,self.artist,path,lnum,-1)
        version.album = self.album
        version.version_of = self
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
        if line.strip().startswith('[') and line.strip().endswith(']'):
            m_ws = re.search('(^\s*)', line)
            return ( m_ws.group(1) + line.strip()[1:-1] ), "comment"

        if line.strip().startswith('<') and line.strip().endswith('>'):
            self.cover = line.strip()[1:-1].strip()
            newline = line.replace('<', '&lt;')
            newline = newline.replace('>', '&gt;')
            return newline, "cover"

        if line.lower().strip().startswith( 'capo' ):
            return line, "capo"
        elif line.lower().strip().startswith( 'harp:' ):
            return line, "harp"
        elif line.lower().strip().startswith( 'key:' ):
            key = line.strip()[4:].split()[0]
            return key, "key"
        elif line.lower().strip().startswith( 'tuning' ):
            if self.tuning:
                link = "<a href=\"tunings.html#%s\">%s</a>" % ( self.tuning.offset(), line )
                return link, "tuning"
            else:
                return line, "tuning" # highlight standard tunings, even without a link

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
            #return None, None # This allows chords to be identified in the fingering lines
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
    def markup_chord_line(self,line,transpose=0,prefer_sharp=False):
        comline, comtype = self.is_comment_line(line)
        if comline:
            if comtype == "harp":
                # strip leading "Harp key:" and format key as chord
                splits = comline.split()
                hkey = splits[1]
                chord = CRD_chord(hkey)
                if chord.is_chord():
                    formatted = chord.format(transpose,prefer_sharp)
                    splits[1] = "<div class=chord>%s</div>" % formatted
                    comline = " ".join(splits)
                    comtype = "comment"
            elif comtype == "capo":
                # format capo position and sounding key
                splits = comline.split()
                capo_position = splits[1]

                chord = None
                m = re.search("sounding key:?\s*([A-G#b]+)", comline)
                if m:
                    sounding_key = m.group(1)
                    #print("Sounding key: " + sounding_key)
                    chord = CRD_chord(sounding_key)

                if capo_position:
                    comline = "Capo: <div class=capo>%s</div> " % capo_position
                    comtype = "comment"
                    if chord and chord.is_chord():
                        formatted = chord.format(transpose, prefer_sharp)
                        comline += "(sounding key: <div class=chord>%s</div>)" % formatted 
            elif comtype == "cover":
                return ""
            elif comtype == "key":
                key = comline
                key_line = "<div class=comment>Key:</div>"
                if self.current_key and key != self.current_key:
                    key_line = "<div class=comment>Modulate to:</div>"
                key_line += " <div class=chord>%s</div>" % key
                self.current_key = key

                if DO_KEY_DIVS:
                    # Adds an invisible key div which can be read by the javascript
                    key_line = ("<div class=key>%s</div>" % comline) + key_line

                return key_line

            return '<div class=%s>%s</div>' % ( comtype, comline )
        splits = re.split( r'(\s+)', line)
        # this splits the line at start/end of whitespace regions,
        # so that contiguous whitespace counts as a word
        formatted = ''
        finger_regex = '([0-9xXA-G]{6,})' 
        got_a_not_chord = False
        for word in splits:
            if word == '':
                pass
            elif '--' in word:
                # disables highlighting on tab lines
                got_a_not_chord = True
                formatted += word
            #elif ',' in word:
                #got_a_not_chord = True
                #formatted += word
            elif word.replace('.','') == '':
                formatted += word
            elif word.isspace():
                if FIXED_WIDTH_CHORDS and formatted.endswith("</div>"):
                    nodiv = formatted[:-6]
                    trimmed = nodiv.rstrip()

                    n_pad = len(nodiv) - len(trimmed)
                    n_word = len(word)

                    if n_word > n_pad:
                        # replace padding with ws word inside div
                        formatted = trimmed + word + "</div>"
                    else:
                        # remove padding to avoid symbols running together
                        formatted = trimmed + "</div>" + word

                else:
                    formatted += word
            elif word == 'etc' or word == 'etc.':
                formatted += '...'
            elif word.lower() in [ 'n.c.', 'nc', 'n.c', 'n/c' ]:
                formatted += len(word) * ' '
            elif re.match( '\(?riff(\s*\d+)?\)?', word.lower() ):
                formatted += '<div class=comment>' + word + '</div>'
            elif re.match( '\[?intro\]?', word.lower() ):
                formatted += '<div class=comment>Intro</div>'
            elif re.match( finger_regex, word ):
                formatted += '<div class=comment>' + word + '</div>'
            elif re.match( '\$\d+', word ):
                # $1 $2 etc used for links between sections
                formatted += word
            elif word in [ '|', '-', '%', '*', '**', '***', '.', ',', '|:', ':|', '[', ']', '||', '(', ')', ':' ]:
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
                    formatted_crd = chord.format(transpose,prefer_sharp)
                    fingering = self.get_fingering(formatted_crd,True)
                    # if fingering == "" and self.tuning:
                    #     print( "[%s] No fingering for %s" % ( self.tuning.name(), formatted_crd ) )
                    formatted += starter + '<div class=chord%s>%s</div>%s' % \
                                                ( fingering, formatted_crd, ender )
                else:
                    got_a_not_chord = True
                    formatted += starter + word + ender
        if got_a_not_chord:
            line = re.sub( '<', '&lt;', line )
            line = re.sub( '>', '&gt;', line )
            return line
        return formatted
    def format_song_lines(self,transpose=0,prefer_sharp=False):
        formatted = []
        n_tab_lines = 0
        for ii,line in enumerate(self.lines):
            lastline = ii == len(self.lines)-1
            newline = self.markup_chord_line(line,transpose,prefer_sharp)

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
            elif "<div class=key>" in line:
                pass
            elif not in_span and not lastline:
                nextline = formatted[ii+1]
                if nextline != "":
                    line = "<span>" + line
                    in_span = True

            formatted_with_spans.append(line)

        if in_span:
            formatted_with_spans.append("</span>") # close last one

        n_empty_leaders = 0
        for line in formatted_with_spans:
            if re.search( "^\s*$", line): 
                n_empty_leaders += 1
            else:
                break

        formatted_with_spans = formatted_with_spans[n_empty_leaders:]

        for ii, line in enumerate(formatted_with_spans):
            if "<div class=key>" in line:
                del formatted_with_spans[ii+1]
                break

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
                self.tuning = CRD_tuning(line, [], self.artist.stock_tunings)
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
                elif t.tuning == self.tuning.tuning:
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
    def html(self,add_artist=False,transpose=0,prefer_sharp=False):
        self.inherit_fingerings()
        style = ' style="display:none"'
        qindex = "'%s'" % self.index

        # do this first, so that self.cover is set
        formatted_song_lines = self.format_song_lines(transpose,prefer_sharp)

        lines = []

        if not self.version_of:
            # case: top level

            top_version = None
            if not formatted_song_lines:
                # nothing at top level:
                if self.versions:
                    # use first version as top
                    top_version = self.versions.pop(0)
                    formatted_song_lines = top_version.format_song_lines(transpose,prefer_sharp)
                    self.cover = top_version.cover

            if self.versions:
                default = "Default"
                if top_version:
                    default = top_version.title
                elif self.album and self.album.date:
                    default = str(self.album.date.year) + " " + self.album.title
                elif self.date:
                    default = str(self.date.year) + " Default"

                versions = [ '<select id="%s.select" onchange="update_song_version(%s);">' % ( self.index, qindex ) ]
                versions.append( '<option value=0>%s</option>' % default )
                for i, version in enumerate(self.versions):
                    versions.append( '<option value=%d>%s</option>' % (i+1, version.title))
                versions.append('</select>')

            style = ' style="display:block"'
            lines += [ '<hr> <a name=%s></a>' % self.link ] 
            name = (' (%s)' % self.artist.name) if add_artist else ''
            lines += [ '<h3 id=%s>%s</h3>' % (self.index, self.title + name) ]

            # Buttons for versions and transposing:

            # button_trans_1 = '<input type="button" title="Transpose down" value="&flat;" ' \
            #                  'onclick="transpose_song(%s,false);">' % qindex
            # button_trans_2 = '<input type="button" title=Transpose up"" value="&sharp;" ' \
            #                  'onclick="transpose_song(%s,true);">' % qindex
            # button_cycle_1 = '<input type="button" title="Cycle versions" value="&lt;" ' \
            #                  'onclick="cycle_versions(%s,false);">' % qindex
            # button_cycle_2 = '<input type="button" title="Cycle versions" value="&gt;" ' \
            #                  'onclick="cycle_versions(%s,true);">' % qindex

            # lines += [ button_trans_1, button_trans_2 ]
            # if self.versions:
            #     lines += [ button_cycle_1, button_cycle_2 ]

            if self.cover:
                lines += [ '<div class=cover style="font-size:x-small">&lt;%s&gt;</div>' % self.cover ]

            # lines += [ button_trans_1, button_trans_2 ]
            if self.versions:
                lines += versions

        n_lines = len(self.lines)

        if n_lines > 100 and self.longest_line() <= 65:
            lines += [ '<div id=%s class="chords_3col version"%s>' % (self.index, style) ]
        elif n_lines > 50:
            lines += [ '<div id=%s class="chords_2col version"%s>' % (self.index, style) ]
        else:
            lines += [ '<div id=%s class="chords_1col version"%s>' % (self.index, style) ]

        lines += formatted_song_lines
        lines += [ '</div>' ]

        new_lines = []
        for i, line in enumerate(lines):
            if "<div class=key>" in line:
                if "span>" not in new_lines[-1]:
                    new_lines[-1] += line
                    continue
            new_lines.append(line)
        lines = new_lines

        for version in self.versions:
            #version.inherit_fingerings()
            version.index = self.index
            lines += version.html(add_artist,transpose,prefer_sharp)

        if not self.version_of:
            lines += [ "<br>" ]
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
        prev_album_close_line = 0
        prev_song_close_line = 0
        inherited_song_gap = False
        inherited_album_gap = False

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
                    if this_album:
                        if prev_song_close_line > 0 and prev_song_close_line != lnum - 1:
                            inherited_song_gap = True
                    elif this_artist:
                        if prev_album_close_line > 0 and prev_album_close_line != lnum - 1:
                            inherited_album_gap = True
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
                    if prev_album_close_line > 0 and prev_album_close_line != lnum - 1:
                        this_album.gap_before = True
                    if inherited_album_gap:
                        this_album.gap_before = True
                        inherited_album_gap = False
                elif len(title) > 4 and title[0:4] == 'song':
                    s_name = re.match( '.*song:\s+(.*)', line ).group(1)
                    if not this_artist:
                        this_artist = self.get_artist('Misc')
                    if not this_album:
                        this_album = this_artist.add_album('Misc')
                    this_song = this_album.add_song(s_name,path,lnum)
                    newsongs.append(this_song)
                    level_song = level
                    if prev_song_close_line > 0 and prev_song_close_line != lnum - 1:
                        this_song.gap_before = True
                    if inherited_song_gap:
                        this_song.gap_before = True
                        inherited_song_gap = False
                elif len(title) > 9 and title[0:7] == 'version':
                    v_name = re.match( '.*version:\s+(.*)', line ).group(1)
                    if not this_artist:
                        print("No artist for version: " + v_name)
                    if not this_album:
                        print("No album for version: " + v_name)
                    if not this_song:
                        print("No song for version: " + v_name)
                    this_version = this_song.add_version(v_name,path,lnum)
                    newsongs.append(this_version)
                    level_version = level
                else:
                    print("Unknown fold type in %s: %s" % (path, line.strip()))
            elif mclose:
                if comment_level > 0 and comment_level == level:
                    comment_level = 0
                    if this_album:
                        prev_song_close_line = lnum
                    else:
                        prev_album_close_line = lnum
                if this_song and level_song == level:
                    this_song = None
                    prev_song_close_line = lnum
                if this_album and level_album == level:
                    this_album  = None
                    prev_album_close_line = lnum
                    prev_song_close_line = 0
                    inherited_song_gap = False
                if this_artist and level_artist == level:
                    this_artist = None
                    prev_album_close_line = 0
                    prev_song_close_line = 0
                    inherited_album_gap = False
                if this_version and level_version == level:
                    this_version = None
                level -= 1
            elif comment_level > 0:
                pass # don't add commented lines to version or song
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
                        names = re.findall('\[([^]]+)\]', names_str )
                        current_tuning = CRD_tuning( notes, names )
                        if len(names) == 0:
                            print("Tuning %s has no name" % notes)
            elif current_tuning:
                splits = line.strip().split()
                if len(splits) > 1:
                    chord = splits[0]
                    fingering = splits[1]
                    current_tuning.fingerings[chord] = fingering

        # for t in tunings:
        #     names = ", ".join(("\"%s\"" % n) for n in t.names)
        #     print( "==== %s %s" % (t, names) )
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
        files = glob.glob(self.opts["root"] + '/*.crd')
        files.sort()
        for f in files:
            if not DO_CRDFILES:
                self.process_chord_file(f)
            else:
                for crdfile in DO_CRDFILES:
                    if crdfile in f:
                        self.process_chord_file(f)

        # add artists with few songs to misc:
        # for artist in self.artists:
        #     songs = artist.all_songs()
        #     if len(songs) < 5:
        #         print(artist.name)
        #         for song in songs:
        #             print("   ", song.title)

        self.artists.sort(key=lambda x: x.name)
        if os.path.isfile('collections.html'):
            lines = []
            with open('collections.html') as f:
                lines = f.readlines()
            self.collections = [ x for x in lines if 'href' in x ]

        # This doesn't work because we haven't formatted the songlines
        # and therefore we haven't set the cover.
        # for a1 in self.artists:
        #     print(a1.name)
        #     others_covers = []
        #     for a2 in self.artists:
        #         if a1 == a2: continue
        #         for s in a2.all_songs():
        #             if s.cover: print(s.cover)
        #             if s.cover == a1.name:
        #                 print(s.cover)
        # exit()

    def group_songs_by_tunings(self):
        if not self.tunings:
            self.tunings = []
            for artist in self.artists:
                for album in artist.albums:
                    songs = album.songs[:]
                    for song in album.songs:
                        songs += song.versions[:]
                    for song in songs:
                        if song.tuning:
                            try:
                                offsets = [ x.tuning.offset() for x in self.tunings ]
                                pos = offsets.index(song.tuning.offset())
                            except ValueError:
                                tuning_artist = CRD_artist(song.tuning.tuning)
                                tuning_artist.add_album('Misc')
                                tuning_artist.tuning = song.tuning
                                tuning_artist.fname = song.tuning.offset() + '.html'
                                self.tunings.append(tuning_artist)
                                pos = len(self.tunings)-1
                            self.tunings[pos].albums[0].songs.append(song)
            # sort by offset => similar tuning appear next to each other
            self.tunings.sort(key=lambda x: (-x.albums[0].songs[0].tuning.n_strings, -len(x.all_songs()) ))
        return self.tunings
    def make_artists_index(self):
        n_artists = 0
        n_albums = 0
        n_songs = 0
        links = []
        misc_links = []
        for artist in self.artists:
            n_artists += 1
            n_albums += len(artist.albums)
            n_songs += len(artist.all_songs())
            link = '<a href="%s">%s</a> <div class=count>%d/%d</div><br>' % \
               ( artist.fname, artist.name, len(artist.all_songs()), len(artist.albums) ) 

            if artist.name.startswith("Misc"):
                misc_links.append(link)
            else:
                links.append(link)

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

        return "%d/%d/%d" % (n_songs, n_albums, n_artists), links, misc_links
    def make_tuning_map(self):
        raw_lines = [
            '                                         EADGBE',
            '                                           |',
            '                  +-------------+----------------------+------------+',
            '                  |             |                      |            |',
            '                DADGBE        EADGBD                EADF#BE       CADGBE',
            '                  |             |                                   |',
            '                  +-------------+                                   |',
            '                         |                                          |',
            '                       DADGBD                                     CGDGBE',
            '                         |                                          |',
            '    +----------------------------------------+                      |',
            '    |                                        |            +-------------------+',
            '    |               +----------+         +---------+      |       CGCGBE      |',
            '    |               |  GDGBD   | > > > > | DGDGBD  |      |         |         |',
            '    |               |    |     |         |   |     |      |         |         |',
            '    |               |    |     |         |   |     |      |       CGCGGE      |',
            '    |               |  GDGBbD  | > > > > | DGDGBbD |      |         |         |',
            '    |               |    |     |         +---------+      |         |         |',
            '+---------+  capo5  |    |     |          G-family        |       CGCGCE      |',
            '| DADGAD  | < < < < |  GDGCD   |                          |         |         |',
            '|   |     |         |    |     |                          |   +-----------+   |',
            '|   |     |         |    |     |                          |   |           |   |',
            '| DADF#AD |         |  GCGCD   | > > > > > > > > > > > >  | CGCGCD     CGCFCE |',
            '|   |     |         |    |     |                          |               |   |',
            '|   |     |         |    |     |                          |               |   |',
            '| DADFAD  |         |  GCGCC   |                          |            CGDFCE |',
            '|   |     |         +----------+                          +-------------------+',
            '|   |     |            Banjo                                     C-family',
            '| DADEAD  |  ',
            '|   |     |  ',
            '|   |     |  ',
            '| DADDAD  |  ',
            '+---------+',
            ' D-family',
            '' # empty line for better in-line spacing
            ]

        lines = []

        for line in raw_lines:
            tunings = re.findall('[ABCDEFG#b]{5,}', line)
            for t in tunings:
                offset = None
                name = None
                for tartist in self.group_songs_by_tunings():
                    tt = tartist.albums[0].songs[0].tuning
                    if tt.tuning.lower() == t.lower():
                        offset = tartist.tuning.offset()
                        if tt.names:
                            name = tt.names[0]
                        break
                #print(t, offset, name)

                if offset:
                    link = "<a href=#%s title=\"%s\">%s</a>" % ( offset, name, t)
                    line = re.sub( r"\b" + t + r"\b", link, line)

            lines.append(line)

        return lines
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
        n_strings = 0
        for tartist in self.group_songs_by_tunings():
            if n_strings > 0 and n_strings != tartist.albums[0].songs[0].tuning.n_strings:
                lines.append('<br><br>')
            n_strings = tartist.albums[0].songs[0].tuning.n_strings
            n_tunings += 1
            n_tunings_songs += len(tartist.all_songs())
            offset = tartist.tuning.offset()

            # collect all possible names of this tuning
            names = []
            for song in tartist.all_songs():
                for name in song.tuning.names:
                    if name not in names:
                        names.append(name)
            names_string = "-".join('(' + name + ')' for name in names)
            name_fw = tartist.tuning.tuning.ljust(12,'-') + \
                    ('[' + offset + ']').ljust(10,'-') + \
                    names_string.ljust(40,'-')
            name = re.sub("-+", " ", name_fw)
        
            lines.append( '<li><a class=tuning href="#%s">%s</a> <div class=count>%d</div>' %
                    ( offset, name_fw, len(tartist.all_songs() ) ) )

            body.append( '<hr> <a name=%s></a>' % offset )
            body.append( '<h3>%s</h3>' % name )
            body.append( '<ol>' )

            for song in tartist.all_songs():
                s_link = song.album.fname + '#' + song.link
                s_title = song.title
                if song.version_of:
                    s_title = "%s (%s)" % ( song.version_of.title, song.title )
                    s_link = song.album.fname + '#' + song.version_of.link
                body.append( '<li> <a href="%s">%s</a> (%s)' % ( s_link, s_title, song.artist.name ) )
            body.append( '</ol>' )
            body.append( '<br>' )

        lines += [ '</ul>', '<br>' ]
        lines += [ "<div class=tuning_map>" ]
        lines += self.make_tuning_map()
        lines += [ "</div>" ]

        lines += body
        lines += [ '<br>' * 50, '</body>', '</html>' ]

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

        lines += [ '<br><br><hr>', 
                   #'<h3>#</h3>', 
                   '<div class=songindex>' ]
        allsongs = self.all_songs()
        cur_letter = None
        for song in allsongs:
            if cur_letter == None:
                pass
            elif not song.title_sort[0] in ALPHABET:
                pass # all non alpha characters in same section
            elif cur_letter != song.title_sort[0]:
                lines.append('</div>')
                lines.append('<a name="%s">' % song.title_sort[0])
                lines.append('<br><hr>')
                #lines.append('<h3>%s</h3>' % song.title_sort[0])
                lines.append('<div class=songindex>')
            cur_letter = song.title_sort[0]
            s_link = song.album.fname + '#' + song.link
            lines.append( '<a href=%s>%s</a> (%s, %s)' % ( s_link, song.title, song.artist.name, song.album.title ) )
        lines += [ '</div>', '</body>', '</html>' ]
        with open(self.opts["html_root"] + 'songs.html', 'w') as f:
            for l in lines:
                f.write('\n' + l)
    def make_html(self):
        if not DO_CRDFILES:
            self.make_song_index()
        artists_summary, artists_links, misc_links = self.make_artists_index()
        tunings_summary = self.make_tuning_index()

        lines  = [ '<html>', '<body>', '<head>' ]
        lines += [ '<title>Chordproc</title>' ]
        lines += common_html(False)
        lines += [ '</head>' ]
        timestamp =  datetime.datetime.now().strftime("%d %b %Y %X")
        lines += [ '<h2><div title="%s">ChordProc</div></h2>' % timestamp ]
        lines += [ '<hr>' ]
        lines += [ '<a href=songs.html>Song Index</a> <div class=count>%s</div><br>' % artists_summary ]
        lines += [ '<a href=tunings.html>Tuning Index</a> <div class=count>%s</div><br>' % tunings_summary ]
        lines += [ '<a href=theory.html>Chords and Scales</a>' ]
        lines += [ '<hr>' ]

        lines += [ '<div class=artistlist>' ]
        lines += artists_links
        lines += [ '</div>' ] 
        lines += [ '<hr>' ]

        if misc_links:
            lines += [ '<div>' ] # class=artistlist>' ]
            lines += misc_links
            lines += [ '</div>' ] 
            lines += [ '<hr>' ]

        lines += [ '</body>', '</html>' ]

        if not DO_CRDFILES:
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

