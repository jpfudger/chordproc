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
DO_SOUNDING_KEY = False
WRITE_FINGERINGS = True
HARP_LINK = "theory.html#DiatonicHarmonicaPositions"
IGNORE_ARTISTS = [ "JPF" ] # omitted from the index
ARTIST_BAND_LINKS = {
    "Babyshambles" :        [ "Pete Doherty" ],
    "Band" :                [ "Bob Dylan" ],
    "Beach Boys" :          [ "Brian Wilson", "Carl Wilson", "Dennis Wilson" ],
    "Beatles" :             [ "Paul McCartney", "John Lennon", "George Harrison" ],
    "Buffalo Springfield" : [ "Neil Young" ],
    "Lou Reed" :            [ "David Bowie" ],
    "Libertines" :          [ "Pete Doherty" ],
    "Traveling Wilburys" : [ "Bob Dylan", "George Harrison", "Tom Petty" ],
    "Crosby, Stills, Nash & Young" : [ "Neil Young", "Buffalo Springfield" ],
    "Byrds" : [ "Buffalo Springfield", "Crosby, Stills, Nash & Young", "Gram Parsons" ],
    "Velvet Underground" : [ "John Cale", "Lou Reed" ],
    }

def html_header(title, chords=False, index_page=False, folk=False):
    lines = [ '<head>',
        '    <title>%s</title>' % title,
        '    <link rel="shortcut icon" href="thumb.ico" type="image/x-icon">',
        '    <link rel="stylesheet" type="text/css" href="style1.css" id="style">',
        '    <script src="script.js"></script>',
        ]

    
    # if chords:
    #     lines += [
    #     '<a onclick="transpose_topmost_song(true);" title="Transpose Up"><div id=t_l></div></a>',
    #     '<a onclick="transpose_topmost_song(false);" title="Transpose Down"><div id=b_l></div></a>',
    #     #'<a onclick="hide_chords();" title="Hide Chords"><div id=b_r></div></a>',
    #     ]
    lines += [ '</head>' ]

    lines += html_context_menu(index=index_page, chords=chords, folk=folk)

    return lines

def html_context_menu(index=False, chords=False, folk=False):
    lines = []

    lines.append("<div class=settings>")
    lines.append("  <img class=settings-icon src=menu.png>")
    #lines.append("  <img class=settings-icon onclick=\"toggle_settings_menu();\" src=menu.png>")
    #lines.append("  <div id=t_r></div></a>")
    lines.append("  <div class=settings-menu>")

    if chords:
        lines.append("    <a onclick=\"transpose_topmost_song(true);\">Transpose up (k)</a>")
        lines.append("    <a onclick=\"transpose_topmost_song(false);\">Transpose down (j)</a>")
        lines.append("    <a onclick=\"cycle_topmost_song(true);\">Cycle song versions (v)</a>")
        lines.append("    <a onclick=\"nashville_system();\">Toggle Nashville chords (n)</a>")
        lines.append("    <a onclick=\"lyrics_only();\">Toggle lyrics only (z)</a>")
        lines.append("    <a onclick=\"toggle_modulation();\">Toggle modulation (m)</a>")

    if index:
        lines.append("    <a onclick=\"toggle_sort();\">Toggle artist sort (s) </a>")

    if folk:
        lines.append("    <a onclick=\"toggle_sort();\">Toggle index sort (s) </a>")

    lines.append("    <a class=narrow onclick=\"\">-------------------------</a>")
    lines.append("    <a onclick=\"jump_to_page('index.html');\">Jump to artists index (i)</a>")
    lines.append("    <a onclick=\"jump_to_artist_index();\">Jump to current artists index (I)</a>")
    lines.append("    <a onclick=\"jump_to_page('songs.html');\">Jump to song index</a>")
    lines.append("    <a onclick=\"jump_to_page('tunings.html');\">Jump to tunings index</a>")
    lines.append("    <a onclick=\"jump_to_page('folk.html');\">Jump to folk index</a>")
    lines.append("    <a onclick=\"jump_to_page('theory.html');\">Jump to theory page</a>")
    lines.append("    <a class=narrow onclick=\"\">-------------------------</a>")
    lines.append("    <a onclick=\"toggle_multicolumn();\">Toggle multicolumn</a>")
    lines.append("    <a onclick=\"toggle_dark_mode();\">Toggle dark mode</a>")
    lines.append("    <a class=narrow onclick=\"\">-------------------------</a>")
    lines.append("    <a onclick=\"prompt_for_song_search();\">Find song (f)</a>")
    lines.append("    <a onclick=\"prompt_for_song_search(true);\">Find song (current artist) (F)</a>")
    lines.append("    <a onclick=\"prompt_for_tuning_search();\">Find tuning (n)</a>")
    lines.append("    <a onclick=\"random_song();\">Random song (r)</a>")
    lines.append("    <a onclick=\"random_song(true);\">Random song (current artist) (R)</a>")
    #lines.append("    <a onclick=\"cycle_styles();\">Cycle styles</a>")

    lines.append("  </div>")
    lines.append("</div>")

    return lines

def html_song_index(allsongs, artist=None):
    lines  = [ '<html>' ]

    if artist:
        lines += html_header(artist.name + " : Song Index")
        lines += ["<body>"]
        title_link = "<a href=%s>%s : Song Index</a>" % ( artist.fname, artist.name )
        lines += [ '<h2 title="%s">%s</h2>' % ( artist.index, title_link ) ]
    else:
        lines += html_header("ChordProc: Song Index")
        lines += ["<body>"]
        title_link = "<a href=index.html>Song Index</a>"
        lines += [ '<h2>%s</h2>' % title_link ]

    lines += [ '<hr>', '<div id=results>' ]

    # long lists of songs warrant alphabet links
    add_letter_links = len(allsongs) > 100

    if add_letter_links:
        alphastring = ''
        for char in list('#' + ALPHABET):
            alphastring += '<a href="#%s">%s</a> ' % ( char, char )
        lines += [ alphastring, '<hr>' ]

    lines += [ '<div class="songindex col2">' ]
    cur_letter = None

    for song in allsongs:
        if cur_letter == None:
            pass
        elif not song.title_sort[0] in ALPHABET:
            pass # all non alpha characters in same section
        elif cur_letter and cur_letter != song.title_sort[0]:
            if add_letter_links:
                lines.append('</div>')
                lines.append('<a name="%s">' % song.title_sort[0])
                lines.append('<hr>')
                lines.append('<div class="songindex col2">')
            else:
                lines.append('<br>')
        cur_letter = song.title_sort[0]
        s_link = song.album.fname + '#' + song.link
        s_class = ' class=cover' if song.cover else ''
        album = song.album.title if artist else (song.album.artist.name + ", " + song.album.title)
        title = song.title
        if song.misc_artist:
            title += f" [{song.misc_artist}]"
        lines.append( '<a href=%s%s>%s</a> (%s)' % ( s_link, s_class, title, album ) )
    
    lines += [ '</div>', '</div>', '<br>' ]
    lines += [ '</body>', '</html>' ]
    return lines

class CRD_artist():
    def __init__(self,name,index=0,data=None):
        self.name = name.strip()
        self.ignore = self.name in IGNORE_ARTISTS
        self.albums = []
        self.too_many_albums = False
        self.index = index
        self.player = None
        self.stock_tunings = None
        self.data = data
        if data:
            self.player = data.player
            self.stock_tunings = data.stock_tunings

        alphaname = ''.join( [y for y in self.name if y.isalnum()] )
        alphaname = alphaname.lower()
        self.fname = alphaname + '.html'
        self.index_fname = alphaname + '_songs.html'
        self.words_fname = alphaname + '_words.html'
        self.tunings_fname = alphaname + '_tunings.html'
        self.tuning = None
        self.words = {}
    def add_album(self,title):
        album_index = '%d.%d' % ( self.index, len(self.albums) + 1 )
        new_album = CRD_album( title, self, album_index, self.player )
        self.albums.append(new_album)
        if len(self.albums) > 30:
            self.too_many_albums = True
        return new_album
    def get_artist_links(self):
        artists = []

        for key, values in ARTIST_BAND_LINKS.items():
            if key.strip() == self.name:
                # add artists linked to band
                artists += values[:]
            else:
                for value in values:
                    if value == self.name:
                        # add artist's band
                        artists.append(key)

                        # but NOT the bandmates:
                        #artists += [ v for v in values if v != value ]

        artists = list(set(artists))
        artists.sort()
        return artists
    def all_songs(self):
        allsongs = []
        for album in self.albums:
            for song in album.songs:
                if song.dummy: 
                    continue
                allsongs.append(song)
        allsongs.sort(key=lambda x: x.title_sort)
        return allsongs
    def next_and_previous_links(self):
        n = None
        p = None

        index = self.data.artists.index(self)

        if index < len(self.data.artists)-1:
            n = self.data.artists[index+1]
            n = '<a href=%s id=next title="%s" style="display:none;">&gt;</a>' % (n.fname,n.name)
        if index > 0:
            p = self.data.artists[index-1]
            p = '<a href=%s id=prev title="%s" style="display:none;">&lt;</a>' % (p.fname,p.name)

        if n and p:
            return [n,p]
        elif n:
            return [n]
        elif p:
            return [p]
        
        return []
    def html(self,add_artist=False):
        lines  = [ '<html>' ]
        lines += html_header(self.name)
        lines += [ '<body>', '<h2 title="%s"><a href=index.html>%s</a></h2>' % (self.index, self.name) ]
        #total_songs = sum( [ len(a.songs) for a in self.albums ] )

        lines += self.next_and_previous_links()
        n_artist_tunings, n_artist_tuning_songs = self.make_tuning_index()

        c_origs, c_covers = self.song_counts()
        if c_covers:
            count_string = "(%d) (%d originals)" % (c_origs + c_covers, c_origs)
            count_string = "<div class=count>%d/%d</div>" % (c_origs, c_origs + c_covers)
        else:
            count_string = "(%d)" % (c_origs + c_covers)
            count_string = "<div class=count>%d</div>" % (c_origs + c_covers)

        lines += [ '<hr>' ]
        lines += [ '<a href="%s">Song Index</a> %s' % ( self.index_fname, count_string ) ]

        if n_artist_tunings > 0:
            lines += [ '<br>' ]
            count_string = "<div class=count>%d/%d</div>" % ( n_artist_tuning_songs, n_artist_tunings )
            lines += [ '<a href="%s">Tuning Index</a> %s' % (self.tunings_fname, count_string) ]

        if DO_WORDLISTS and self.name in DO_WORDLISTS:
            lines += [ '<br>', '<a href="%s">Word Index</a>' % ( self.words_fname ) ]

        related = self.get_artist_links()
        if related and not DO_CRDFILES:
            links = []
            for aname in related:
                a = self.data.get_artist(aname)
                if not a:
                    raise ValueError("Error: no artist object for: " + aname)
                link = "<a href=%s>%s</a>" % (a.fname, aname)
                links.append(link)
                
            link_list_string = ", ".join(links)
            lines += [ '<br>Related artists: ' + link_list_string ]

        col_class = "col2" if self.too_many_albums else "col1"
        lines += [ '<hr>' ]
        lines += [ '<div class="%s" style="display:block">' % col_class ]
        if self.too_many_albums: lines.append("<span>")

        #lines += [ '<ol>' ]
        decade = None
        for album in self.albums:
            #lines.append( '<li>' )


            if album.gap_before:
                lines.append("<br>")
            elif decade and album.date and decade != int(str(album.date.year)[:-1]):
                lines.append("</span><br><span>")

            style = " class=cover" if album.all_songs_are_covers() else ""
            if album.date:
                style += " title=%d" % album.date.year
            lines.append( '<a href=%s%s>%s</a> <div class=count>%d</div>'
                                % ( album.fname, style, album.title, album.n_songs() ) )
            lines.append( '<br>' )
            if self.too_many_albums and album.date: 
                decade = int(str(album.date.year)[:-1])

        if self.too_many_albums: lines.append("</span>")
        #lines += [ '</ol>' ]
        lines += [ '</div>' ]
        lines += [ '<hr>' ]
        lines += [ '<br>' ] * 10
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
                lines.append('<div class="songindex col2">')
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
                if s.dummy:
                    pass
                elif s.cover:
                    covers += 1
                else:
                    origs += 1

        return (origs, covers)
    def make_tuning_index(self):
        all_tunings = self.data.group_songs_by_tunings()
        n_artist_tunings = 0
        n_artist_tuning_songs = 0
        artist_tunings = {}
        for tuning in all_tunings:
            if tuning.tuning.standard(): continue
            artist_tuning_songs = []
            for song in tuning.all_songs():
                if song.artist.name == self.name:
                    artist_tuning_songs.append(song)

            if artist_tuning_songs:
                artist_tunings[tuning] = artist_tuning_songs
                n_artist_tunings += 1
                n_artist_tuning_songs += len(artist_tuning_songs)

        if n_artist_tunings > 0:
            with open(self.data.opts["html_root"] + self.tunings_fname, 'w') as f:
                title = "<a href=%s>%s : Tuning Index</a>" % ( self.fname, self.name )

                lines = [ "<html>" ]
                lines += html_header(self.name + " : Tuning Index")
                lines += [ "<body>", "<h2>%s</h2>" % title ]
                lines += [ "<hr>" ]

                body_lines = []

                tunings = list(artist_tunings.keys())
                tunings.sort(key=lambda t: (-len(artist_tunings[t]), t.tuning.offset()))

                lines += [ "<ul>" ]

                for tuning in tunings:
                    songs = artist_tunings[tuning]
                    full_name = tuning.tuning.name()
                    fingering_link = "fingerings.html#" + tuning.tuning.offset()

                    tuning_name = tuning.name.ljust(34,"-")
                    section_name = tuning.name

                    if full_name:
                        tuning_name = tuning.name.ljust(12,"-") + full_name.ljust(22,"-")
                        section_name = "%s (%s)" % (full_name, tuning.name)

                    count = "<div class=count>%d</div>" % len(songs)
                    link = "<a class=tuning href=#%s>%s</a>" % ( tuning.tuning.offset(), tuning_name )
                    lines += [ "    <li> %s %s </li>" % (link, count) ]

                    body_lines += [ "<hr>" ]
                    body_lines += [ "<a name=%s></a>" % tuning.tuning.offset() ]
                    body_lines += [ "<h2><a href=%s>%s</a></h2>" % (fingering_link, section_name) ]
                    body_lines += [ "<ul>" ]
                    for song in songs:
                        link = song.get_html_link(mark_covers=True, use_song_title_of_first_version=True)
                        body_lines.append( '<li> %s (%s)' % (link, song.album.title) )

                    body_lines += [ "</ul>", "<br>" ]

                lines += [ "</ul>" ]
                lines += body_lines
                lines += [ "</body>", "</html>" ]
                lines += [ "<br>" ] * 30

                for l in lines:
                    f.write(l + '\n')

        return n_artist_tunings, n_artist_tuning_songs

def set_title_and_date(title):
    # also extracts misc artist (in square brackets)
    date = None
    artist = None
    
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

    regex_artist = "\[\s*([^]]+)\s*\]"
    m_artist = re.search(regex_artist, title)

    if m_artist:
        title = re.sub(regex_artist, "", title)
        title = title.strip()
        artist = m_artist.group(1)
        artist = artist.strip()

    # if date: print(date)
    title  = " ".join( x[0].upper() + x[1:] for x in title.strip().split())

    return title, date, artist

class CRD_album():
    def __init__(self,title,artist,index,player):
        self.title, self.date, self.misc_artist = set_title_and_date(title)
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
    def next_and_previous_links(self):
        n = None
        p = None

        index = self.artist.albums.index(self)

        if index < len(self.artist.albums)-1:
            n = self.artist.albums[index+1]
            n = '<a href=%s id=next title="%s" style="display:none;">&gt;</a>' % (n.fname,n.title)
        if index > 0:
            p = self.artist.albums[index-1]
            p = '<a href=%s id=prev title="%s" style="display:none;">&lt;</a>' % (p.fname,p.title)

        if n and p:
            return [n,p]
        elif n:
            return [n]
        elif p:
            return [p]
        
        return []
    def html(self):
        title = self.artist.name + ' : ' + self.title

        year_sub = ""
        if self.date and self.date.year:
            year_sub = " <div class=count>%d</div>" % self.date.year

        title_link = '<a href=%s>%s</a> : %s%s' % (self.artist.fname, self.artist.name, self.title, year_sub)
        lines  = [ '<html>' ]
        lines += html_header(title, chords=True)
        lines += [ '<body>', '<h2 title="%s">%s</h2>' % (self.index, title_link) ]
        #lines += [ self.get_playlist_link() ]

        lines += self.next_and_previous_links()

        lines += [ '<hr>', '<ol>' ]
        songs_body = []
        for song in self.songs:
            # needs to be done separately, so that song.cover gets set
            songs_body += song.html()[:]
        for song in self.songs:
            if song.gap_before: lines.append("<br><br>")
            if song.dummy:
                # can't have dummies that are covers, but that's okay
                lines.append( '<li><div class=dummy>%s</div>' % ( song.title ) )
            else:
                s_class = ' class=cover' if song.cover else ''
                s_year = ' title=%d' % song.date.year if song.date else ''
                nv_sub = ""
                if song.versions:
                    nv_sub = " <div class=count>+%d</div>" % len(song.versions)
                lines.append( '<li><a href=#%s%s%s>%s</a>%s' % ( song.link, s_class, s_year, song.title, nv_sub ) )
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
    def n_songs(self):
        n = 0
        for song in self.songs:
            if song.dummy:
                continue
            n += 1
        return n
    def all_songs_are_covers(self):
        for song in self.songs:
            if not song.cover:
                return False
        return True

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
    def __notes(self,which=None,prefer_sharp=False):
        notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ]
        if prefer_sharp or (which and '#' in which):
            notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ]
        return notes + notes
    def format(self,transpose=0,prefer_sharp=False):
        formatted = self.string
        transpose = transpose % 12

        if self.is_chord():
            max_width = len(formatted)

            if self.root:
                if len(self.root) == 1: max_width += 1

                # get notes in the form that the root note can be looked up:
                notes = self.__notes(self.root)
                lowernotes = [ n.lower() for n in notes ]
                rootindex = lowernotes.index(self.root.lower())

                # get notes in form requested by caller; index will be the same
                notes = self.__notes(None,prefer_sharp)
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

        if self.string[0] != '/' and self.string[1:] in [ 'ome', 'a', 'ip', 'oo', 'gain', 'ocaine!', 'um', 'o', 'abe', 'ig', 'XP', 'aa' ]:
            # Come  (Pissing in a River)
            # Ba    (Looking at Tomorrow)
            # Baa   (Mr Sheep
            # Bip   (Looking at Tomorrow)
            # Doo   (Til I Die)
            # Again (Crumb Begging Baghead)
            # Cocaine, Dum, Do
            # Babe, Dig
            # EXP (Robyn Hitchcock)
            # print("Rejecting: " + self.string)
            return False

        return True

CHORD_CACHE = {}

def get_chord(string):
    global CHORD_CACHE

    chord = None

    if string in CHORD_CACHE:
        chord = CHORD_CACHE[string]
    else:
        chord = CRD_chord(string)
        CHORD_CACHE[string] = chord

    return chord

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
        self.songs = [] # much better than using a dummy CRD_artist! Could even be a dictionary of artists?
    def get_fingering(self,crd_string,as_title=False):
        crd_string = crd_string.strip()
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
        return "standard" in [ n.lower() for n in self.names ]

class CRD_song():
    def __init__(self,title,artist,fpath,lnum,index):
        self.title, self.date, self.misc_artist = set_title_and_date(title)
        self.artist = artist
        self.dummy = True
        self.fpath = fpath
        self.lnum = lnum
        self.index = index
        self.lines = []
        self.version_index = 0
        self.versions = []
        self.version_of = None
        self.capo = 0
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
        self.cover_title = None # if the original song has a different name
        self.cover_link = None
        self.roud = None
        self.child = None
        self.comment_links = []
        self.current_key = None # last encountered key set by song
        self.wordlist = []
        self.songs_with_same_name = []
    def add_fingering(self,chord,fingering):
        chord_string = chord.format().strip()
        self.fingerings[ chord_string ] = fingering.lower()
    def add_version(self,name,path,lnum):
        self.dummy = False
        version = CRD_song(name,self.artist,path,lnum,-1)
        version.album = self.album
        version.version_of = self
        self.versions.append(version)
        version.version_index = len(self.versions) - 1
        if self.lines: 
            # if the master song has song lines (meaning is not in a version fold)
            # we need to increment the version index so the links work properly.
            version.version_index += 1
        return version
    def get_all_versions(self):
        all_versions = [self] + self.versions
        return all_versions
    def get_fingering(self,crd_string,as_title=False):
        crd_string = crd_string.strip()
        fingering = ''
        try:
            fingering = self.fingerings[crd_string]
            if as_title:
                fingering = ' title="%s = %s"' % ( crd_string, fingering )
        except KeyError:
            pass

        #print(self.fingerings)
        #print(crd_string, "=>", fingering)
        return fingering
    def markup_comment_chords(self,line):
        line = re.sub( r"@([A-Za-z0-9+/#]+)" , r"<div class=chord>\1</div>", line )
        return line
    def is_comment_line(self,line):
        if line.strip().startswith('[') and line.strip().endswith(']'):
            m_ws = re.search('(^\s*)', line)
            line = m_ws.group(1) + line.strip()[1:-1]
            w_url = re.search('(https?:\S+)', line)
            line = re.sub( '(https?:\S+)', '<a href="\\1">\\1</a>', line)

            if "{" in line:
                # extract comment links
                for link in self.comment_links:
                    if link["text"] and link["link"]:
                        line = line.replace( link["text"], link["link"] )

            if "@" in line:
                line = self.markup_comment_chords(line)

            return line, "comment"

        if line.strip().startswith('<') and line.strip().endswith('>'):
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

        n_strings = self.tuning.n_strings if self.tuning else 6
        finger_regex = '([0-9xXA-G]{%d,})' % n_strings
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
                    chord = get_chord(word)

            if "@" in line:
                line = self.markup_comment_chords(line)

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
    def parse_capo_position(self,input_string):
        string = input_string.upper().strip()

        capo_integer = None
        capo_numeral = None
        capo_negative = False

        if string.startswith("-"):
            capo_negative = True
            string = string[1:]

        NUMERALS = [ "0", "I", "II", "III", "IV", "V",
                     "VI", "VII", "VIII", "IX", "X", "XI",
                     "XII", "XIII", "XIV", "XV",
                   ]

        try:
            capo_integer = int(string)
            capo_numeral = NUMERALS[capo_integer]
        except ValueError:
            if string in NUMERALS:
                capo_numeral = string
                capo_integer = NUMERALS.index(capo_numeral)

        if (capo_numeral is None) != ( capo_integer is None):
            raise ValueError(f"Error parsing capo position {input_string}")

        if capo_negative and capo_integer:
            capo_integer = -capo_integer
            capo_numeral = "-" + capo_numeral

        return capo_integer, capo_numeral
    def markup_chord_line(self,line,transpose=0,prefer_sharp=False):
        comline, comtype = self.is_comment_line(line)
        if comline:
            if comtype == "harp":
                # strip leading "Harp key:" and format key as chord
                splits = comline.split()
                hchord = get_chord(splits[1])
                if hchord.is_chord():
                    formatted = hchord.format(transpose,prefer_sharp)
                    hcomment = "<div class=chord>%s</div>" % formatted

                    if self.capo != 0:
                        formatted_nocapo = hchord.format(self.capo, prefer_sharp)
                        nocapo_link = "<div class=\"chord fixed\">%s</div>" % formatted_nocapo

                        #hcomment += f" (chords) / {nocapo_link} (capo)"
                        hcomment += f" [or {nocapo_link} with capo]"

                    theory_link = "<a href=%s>Harp:</a>" % HARP_LINK

                    comline = theory_link + " " + hcomment

                    trailing = " ".join(splits[2:])
                    if "@" in trailing:
                        trailing = self.markup_comment_chords(trailing)
                    if trailing:
                        comline += " " + trailing

                    comtype = "comment"
            elif comtype == "capo":
                # format capo position and sounding key
                splits = comline.split()
                capo_integer, capo_numeral = self.parse_capo_position(splits[1])

                if capo_integer:
                    self.capo = capo_integer
                    comline = "<a class=capo_button onclick=\"toggle_capo(this);\">Capo</a>: "
                    comline += "<div class=capo>%s</div>" % capo_numeral

                    if len(splits) > 2:
                        trailing = " ".join(splits[2:])
                        if "@" in trailing:
                            trailing = self.markup_comment_chords(trailing)
                        comline += "  " + trailing # two spaces, one to account for #/b
                    
                    comtype = "comment"
            elif comtype == "cover":
                return ""
            elif comtype == "key":
                key = comline
                key_text = "Key:"
                if self.current_key and key != self.current_key:
                    key_text = "<a class=capo_button onclick=\"toggle_modulation();\">Modulate to:</a>"

                key_chord = "<div class=\"key chord\">%s</div>" % key
                self.current_key = key
                sounding_key_text = ""

                if DO_SOUNDING_KEY and self.capo != 0:
                    # this only affects "key" and "modulate to" comments when there is a capo.
                    key_crd = CRD_chord(key)
                    if key_crd:
                        key_nocapo = key_crd.format(self.capo, prefer_sharp)
                        sounding_key_chord = "<div class=\"chord fixed\">%s</div>" % key_nocapo
                        sounding_key_text = " (sounding %s)" % sounding_key_chord

                key_comment_text = key_text + " " + key_chord + sounding_key_text
                key_line = "<div class=comment>%s</div>" % ( key_comment_text )

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

        valid_chordline_chards = [ '|', '-', # used for timing and as starter/ender delims
                                   '%',      # sometimes used for repeats
                                   '*', '**', '***', 
                                   '.', ',', '|:', ':|', '[', ']', 
                                   '||', '(', ')', ':' ]

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
                if FIXED_WIDTH_CHORDS:
                    if formatted.endswith("</div>"):
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
                    elif re.search("\s+</div>\)$", formatted):
                        #print(formatted)
                        m = re.search("(\s+)</div>\)$", formatted)
                        if m:
                            n_pre_ws = len(m.group(1))
                            n_word = len(word)

                            if n_word > n_pre_ws:
                                # subtract previous padding from next padding...
                                formatted += " " * (n_word - n_pre_ws)
                            else:
                                formatted += word

                            #print(pre_bracket_ws)
                    else:
                        formatted += word
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
            elif word in valid_chordline_chards:
                formatted += word
            elif re.match( '\(?\s*[xX]?\s*\d+[xX]?\s*\)?', word ):
                # this is to match (x4) for repetition
                formatted += '<div class=comment>' + word + '</div>'
            else:
                word, starter, ender = self.strip_delimeters(word)
                chord = get_chord(word)
                if chord.is_chord():
                    if transpose == 0:
                        prefer_sharp = "#" in word
                    formatted_crd = chord.format(transpose,prefer_sharp)
                    fingering = self.get_fingering(formatted_crd,True)
                    
                    if not fingering and ("#" in formatted_crd or "b" in formatted_crd):
                        formatted_crd_alt = chord.format(transpose,not prefer_sharp)
                        fingering = self.get_fingering(formatted_crd_alt,True)

                    # if not fingering:
                    #     tname = self.tuning.name() if self.tuning else "standard"
                    #     print("No fingering for %s in %s (%s)" % (formatted_crd,tname,self.title))

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
                if n_tab_lines in [3,4,5,6]: # dulcimer/bass/banjo/guitar tabs
                    #if n_tab_lines == 3: print("New dulcimer tab in: " + self.title)
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

        if line.strip().startswith('<') and line.strip().endswith('>'):
            # set cover/roud/child
            self.cover = line.strip()[1:-1].strip()
            self.cover_title = self.title

            if ":" in self.cover:
                splits = self.cover.split(":")

                if len(splits) > 2:
                    print("Error: unhandled cover song entry: " + self.cover)

                self.cover = splits[0].strip()
                self.cover_title = splits[1].strip()

            m_roud = re.search('roud\s+(\w+)', line.lower())
            m_child = re.search('child\s+(\w+)', line.lower())
            if m_roud: 
                self.roud = m_roud.group(1)
            if m_child: 
                self.child = m_child.group(1)
            
            if self.version_of and not self.version_of.cover:
                # back-fill the main song, if it isn't already
                self.version_of.cover = self.cover
                self.version_of.cover_link = self.cover_link
                self.version_of.cover_title = self.cover_title
                self.version_of.roud = self.roud
                self.version_of.child = self.child
        elif "{" in line and "}" in line:
            links = re.findall('(\{[^}]+\})', line )
            # store a link for later processing in add_comment_links
            for link in links:
                link_dict = { "text"   : link,
                              "artist" : None,
                              "album"  : None,
                              "song"   : None,
                              "link"   : None,
                              }

                link = link[1:-1]

                splits = link.split("|")
                link_dict["song"] = splits[-1]
                #link_dict["artist"] = self.artist.name # default to current artist
                if len(splits) > 1:
                    link_dict["artist"] = splits[0]
                if len(splits) > 2:
                    link_dict["album"] = splits[1]

                self.comment_links.append(link_dict)
        else:
            # if it has a line which is not a cover artist, it can't be a dummy
            self.dummy = False

        self.lines.append(line)
        if not self.tuning:
            if 'tuning:' in line.lower():
                self.tuning = CRD_tuning(line, [], self.artist.stock_tunings)
                if self.tuning.standard():
                    self.tuning = None
                elif self.tuning.tuning.lower() not in line.lower():
                    pass
                    #print("Wrong tuning?", line, "=>", self.tuning.tuning)

                # set tuning of main song to tuning of first version
                # (this is required for filtering in group_songs_by_tunings)
                # if self.version_index == 1 and self.version_of and not self.version_of.tuning:
                #     self.version_of.tuning = self.tuning
    def longest_line(self):
        lengths = [ len(l) for l in self.lines ]
        return max(lengths)
    def inherit_fingerings(self):
        # looks up the current tuning in the stock_tunings list
        # and uses it to inject unspecified fingerings into the 
        # self.tuning object
        stock_tuning = None
        for t in self.artist.stock_tunings:
            if self.tuning and not self.tuning.standard():
                if t.name() == self.tuning.name():
                    stock_tuning = t
                    break
                elif t.tuning == self.tuning.tuning:
                    stock_tuning = t
                    break
            elif 'Standard' in t.names:
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
        v_lines = [] # lines for version selector, for adding later
        a_lines = [] # lines for other artists songlines, for adding later

        if not self.version_of:
            # case: top level
            top_version = None
            if not formatted_song_lines:
                # nothing at top level:
                if self.versions:
                    # use first version as top
                    top_version = self.versions.pop(0)
                    self.lines = top_version.lines
                    top_version.inherit_fingerings()
                    formatted_song_lines = top_version.format_song_lines(transpose,prefer_sharp)
                    self.cover = top_version.cover

            if self.versions:
                default = "Lyrics and Chords"
                if top_version:
                    default = top_version.title
                elif self.album and self.album.date:
                    default = str(self.album.date.year) + " " + self.album.title
                elif self.date:
                    default = str(self.date.year) + " Lyrics and Chords"

                n_vers = 1 + len(self.versions)
                js_index = "%s.version" % self.index
                js_call = "update_song_version('%s');" % self.index
                v_lines = ['<select class=versions id="%s" onchange="%s">' % (js_index, js_call)]
                v_lines.append( '<option value=0>Version 1/%d: %s</option>' % (n_vers, default))
                for i, version in enumerate(self.versions):
                    label = "Version %d/%d: %s" % (i+2, n_vers, version.title)
                    v_lines.append( '<option value=%d>%s</option>' % (i+1, label))
                v_lines.append('</select>')

            year = ""
            if self.date and not self.album.date:
                year = " <div class=count>%d</div>" % self.date.year

            style = ' style="display:block"'
            lines += [ '<hr> <a name=%s></a>' % self.link ] 
            name = self.title
            if self.misc_artist:
                name += f" [{self.misc_artist}]"
            if add_artist:
                name += f" ({self.artist.name})"

            lines += [ '<h3 id=%s>%s%s</h3>' % (self.index, name, year) ]

            if self.cover:
                cname = self.cover
                if self.cover_link:
                    cname = "<a class=cover href=%s>%s</a>" % (self.cover_link, self.cover)
                lines += [ '<div class=cover style="font-size:x-small">&lt;%s&gt;</div>' % cname ]

            if self.songs_with_same_name:
                js_index = "%s.same_names" % self.index
                js_call = "jump_to_same_name('%s');" % self.index
                a_lines = ['<select class=same_names id="%s" onchange="%s">' % (js_index, js_call)]

                inc_self = self.songs_with_same_name[:] + [ self ]
                inc_self.sort(key=lambda s: s.artist.name)

                for i, s in enumerate(inc_self):
                    artist_name = s.artist.name
                    album_name = s.album.title

                    if s.misc_artist:
                        artist_name = s.misc_artist
                        album_name = s.artist.name + " | " + s.album.title

                    label = "Artist %d/%d: %s" % (i+1, len(inc_self), artist_name)
                    selected = " selected" if s == self else ""
                    line = '<option value=%d data-link="%s"%s>%s</option>' \
                                % (i, s.get_link(), selected, label)
                    a_lines.append(line)
                a_lines.append('</select>')

            if v_lines or a_lines:
                lines += [ "<div class=selectors>" ]

                if v_lines:
                    lines += v_lines
                if a_lines:
                    lines += a_lines

                lines += [ "</div>" ]

        n_lines = len(self.lines)

        if n_lines > 100 and self.longest_line() <= 65:
            lines += [ '<div id=%s class="chords col3 version"%s>' % (self.index, style) ]
        elif n_lines > 50:                           
            lines += [ '<div id=%s class="chords col2 version"%s>' % (self.index, style) ]
        else:                                        
            lines += [ '<div id=%s class="chords col1 version"%s>' % (self.index, style) ]

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
            version.inherit_fingerings()
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
    def get_link(self):
        s_link = self.album.fname + '#' + self.link
        if self.version_of:
            s_link = self.album.fname
            if self.version_index > 0:
                s_link += '?v=' + str(self.version_index) # pass index by url
            s_link += '#' + self.version_of.link
        return s_link
    def get_html_link(self, mark_covers=False, use_song_title_of_first_version=False):
        s_link = self.get_link()

        s_title = self.title
        if self.version_of:
            if use_song_title_of_first_version and self.version_index == 0:
                s_title = self.version_of.title
            else:
                s_title = "%s (%s)" % ( self.version_of.title, self.title )

        s_class = ""
        if mark_covers and (self.cover or (self.version_of and self.version_of.cover)):
            s_class = "class=cover "

        link = '<a %shref="%s">%s</a>' % ( s_class, s_link, s_title )
        return link

class CRD_data():
    def __init__(self,opts,lines=None):
        self.opts = opts
        self.artists = []
        self.tunings = []
        self.n_artists = 0
        self.albums = []
        self.songs = []
        self.song_titles = {}
        self.dummy_songs = []
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
        print( "dummies: %d" % len(self.all_dummy_songs() ) )
        print( "tunings: %d" % len(self.tunings) )
        print( "usongs:  %d" % len(self.all_song_titles() )) # sets "songs_with_same_name"

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
                    if song.dummy: continue
                    self.songs.append(song)
            self.songs.sort( key=lambda x: x.title_sort.lower() )
        return self.songs
    def all_song_titles(self):
        if not self.song_titles:
            # build dictionary of unique song titles
            for song in self.all_songs():
                # title = re.sub("\[[^]]+\]", "", song.title)
                # title = title.strip()
                if song.title not in self.song_titles:
                    self.song_titles[song.title] = []
                self.song_titles[song.title].append(song)

            # attach list of songs with the same name to the song object
            for title, songs in self.song_titles.items():
                if len(songs) == 1:
                    continue
                if len(songs) > 2:
                    print("%d duplicates: %s" % (len(songs), title))
                for song1 in songs:
                    for song2 in songs:
                        if song2 == song1:
                            continue

                        # this code restricts matches to cases where
                        # the song artist matches with the cover artist,
                        # but this only makes sense if misc [artists]
                        # are handled properly

                        keep = False
                        if song2.cover and song2.cover == song1.cover:
                            keep = True
                        if song2.cover and song2.cover == song1.misc_artist:
                            keep = True
                        if song1.cover and song1.cover == song2.misc_artist:
                            keep = True
                        if song1.cover == song2.artist.name: 
                            keep = True
                        if song2.cover == song1.artist.name:
                            keep = True

                        if keep:
                            song1.songs_with_same_name.append(song2)

        return self.song_titles
    def all_dummy_songs(self):
        if len(self.dummy_songs) == 0:
            for album in self.all_albums():
                for song in album.songs:
                    if not song.dummy: continue
                    print("Dummy song: %s/%s/%s" % ( album.artist.name, album.title, song.title ))
                    raise Exception("Dummy songs are not currently supported")
                    self.dummy_songs.append(song)
            self.dummy_songs.sort( key=lambda x: x.title_sort.lower() )
        return self.dummy_songs
    def get_artist(self,name,add=False):
        for a in self.artists:
            if a.name == name:
                return a
        
        if add:
            self.n_artists += 1
            a = CRD_artist(name,self.n_artists,self)
            self.artists.append(a)
            return a
        
        return None
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
                    if this_song:
                        pass # don't let commented versions affect song gaps
                    elif this_album:
                        if prev_song_close_line > 0 and prev_song_close_line != lnum - 1:
                            inherited_song_gap = True
                    elif this_artist:
                        if prev_album_close_line > 0 and prev_album_close_line != lnum - 1:
                            inherited_album_gap = True
                elif len(title) > 6 and title[0:6] == 'artist':
                    a_name = re.match( '.*artist:\s+(.*)', line ).group(1)
                    this_artist = self.get_artist(a_name, add=True)
                    level_artist = level
                elif len(title) > 6 and title[0:5] == 'album':
                    a_name = re.match( '.*album:\s+(.*)', line ).group(1)
                    if not this_artist:
                        this_artist = self.get_artist('Misc', add=True)
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
                        this_artist = self.get_artist('Misc', add=True)
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
                    raise ValueError("Unknown fold type")
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
                    prev_song_close_line = 0
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

        if self.opts.get("tunings") and os.path.isfile(self.opts.get("tunings")):
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
            mcf = re.match('^\s*\{\{\{\s*---',line)
            mcl = re.match('^\s*#',line)

            if mblank or mcl:
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
            self.add_covers()
            self.add_comment_links()

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
                #print("== " + artist.name)
                for album in artist.albums:
                    songs = []
                    for song in album.songs:
                        version_tunings = []
                        for version in song.get_all_versions():
                            if version.tuning:
                                version_tunings.append(version.tuning.offset())
                            else:
                                version_tunings.append(None) # standard

                        uniq_version_tunings = list(set(version_tunings))

                        if len(uniq_version_tunings) == 0:
                            pass
                        elif len(uniq_version_tunings) == 1:
                            songs.append(song) # all versions same tuning => just add song
                        else:
                            #print(song.title)
                            #print(uniq_version_tunings)
                            for uvt in uniq_version_tunings:
                                for version in song.get_all_versions():
                                    if version.tuning and version.tuning.offset() == uvt:
                                        # set title_sort to include the version_of title
                                        if version.version_of:
                                            version.title_sort = "%s (%s)" % ( version.version_of.title_sort, version.title)
                                        songs.append(version)

                                        break

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
                        elif song.fingerings:
                            # standard tuning
                            try:
                                offsets = [ x.tuning.offset() for x in self.tunings ]
                                pos = offsets.index("55545")
                            except ValueError:
                                tuning_artist = CRD_artist("EADGBE")
                                tuning_artist.add_album('Misc')
                                tuning_artist.tuning = CRD_tuning('EADGBE', ['Standard'])
                                tuning_artist.fname = '55545.html'
                                self.tunings.append(tuning_artist)
                                pos = len(self.tunings)-1
                            song.tuning = self.tunings[pos].tuning
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
            elif not artist.ignore:
                links.append(link)

            for album in artist.albums:
                album_path = self.opts["html_root"] + album.fname
                with open(album_path, 'w') as f:
                    for l in album.html():
                        f.write(l + '\n')
            with open(self.opts["html_root"] + artist.fname, 'w') as f:
                for l in artist.html():
                    f.write(l + '\n')

            if DO_WORDLISTS and artist.name in DO_WORDLISTS:
                with open(self.opts["html_root"] + artist.words_fname, 'w') as f:
                    for line in artist.words_html():
                        f.write(line + '\n')

            with open(self.opts["html_root"] + artist.index_fname, 'w') as f:
                allsongs = artist.all_songs()
                for l in html_song_index(allsongs, artist):
                    f.write(l + '\n')

        return "%d/%d/%d" % (n_songs, n_albums, n_artists), links, misc_links
    def make_tuning_map(self):
        lines = []
        lines.append("<div class=tuning-map>")
        lines.append("<img class=img-tuning-map src=\"tuning_map.png\" usemap=#tuning-link-map>")
        lines.append("</div>")

        lines.append("<div id=image-map>")
        lines.append("<map name=tuning-link-map>")
        lines.append('    <area shape=rect coords="" href=#75545  alt="DADGBE">')
        lines.append('    <area shape=rect coords="" href=#55543  alt="EADGBD">')
        lines.append('    <area shape=rect coords="" href=#75543  alt="DADGBD">')
        lines.append('    <area shape=rect coords="" href=#55455  alt="EADF#BE">')
        lines.append('    <area shape=rect coords="" href=#95545  alt="CADGBE">')
        lines.append('    <area shape=rect coords="" href=#77545  alt="CGDGBE">')
        lines.append('    <area shape=rect coords="" href=#75525  alt="DADGAD">')
        lines.append('    <area shape=rect coords="" href=#75435  alt="DADF#AD">')
        lines.append('    <area shape=rect coords="" href=#75345  alt="DADFAD">')
        lines.append('    <area shape=rect coords="" href=#75255  alt="DADEAD">')
        lines.append('    <area shape=rect coords="" href=#75075  alt="DADDAD">')
        lines.append('    <area shape=rect coords="" href=#7543   alt="GDGBD">')
        lines.append('    <area shape=rect coords="" href=#7552   alt="GDGCD">')
        lines.append('    <area shape=rect coords="" href=#5743   alt="GCGBD">')
        lines.append('    <area shape=rect coords="" href=#7534   alt="GDGBbD">')
        lines.append('    <area shape=rect coords="" href=#9552   alt="FDGCD">')
        lines.append('    <area shape=rect coords="" href=#5752   alt="GCGCD">')
        lines.append('    <area shape=rect coords="" href=#5750   alt="GCGCC">')
        lines.append('    <area shape=rect coords="" href=#5754   alt="GCGCE">')
        lines.append('    <area shape=rect coords="" href=#57543  alt="DGDGBD">')
        lines.append('    <area shape=rect coords="" href=#57534  alt="DGDGBbD">')
        lines.append('    <area shape=rect coords="" href=#75709  alt="CGCGGE">')
        lines.append('    <area shape=rect coords="" href=#75754  alt="CGCGCE">')
        lines.append('    <area shape=rect coords="" href=#75752  alt="CGCGCD">')
        lines.append('    <area shape=rect coords="" href=#75574  alt="CGCFCE">')
        lines.append('    <area shape=rect coords="" href=#77374  alt="CGDFCE">')
        lines.append("</map>")
        lines.append("</div>")

        return lines
    def make_tuning_index(self):
        lines  = [ '<html>' ]
        lines += html_header("Tuning Index")
        lines += [ '<body>' ]
        lines += [ '<h2> <a href=index.html>Tuning Index</a> </h2>' ]
        lines += [ '<hr>' ]
        lines += [ '<a href=fingerings.html>All Fingerings</a>' ]
        lines += [ '<hr>' ]
        lines += [ '<ul>' ]

        body = []

        fingerings_lines = []

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

            fingerings = {}

            # collect all possible names of this tuning
            names = []
            for song in tartist.all_songs():
                if WRITE_FINGERINGS:
                    # collect fingerings
                    for f in song.fingerings:
                        if f not in fingerings:
                            fingerings[f] = []
                        fingerings[f].append(song.fingerings[f])

                for name in song.tuning.names:
                    if name not in names:
                        names.append(name)

            spacer = "-"
            names_string = spacer.join('(' + name + ')' for name in names)
            name_fw = tartist.tuning.tuning.ljust(10,spacer) + \
                    names_string.ljust(39,spacer)
                    #('[' + offset + ']').ljust(10,spacer) + \
            name = re.sub(spacer + "+", " ", name_fw)
            
            splits = name.split(" ", maxsplit=1)
            name = '<a href=fingerings.html#%s>%s</a> ' % (offset, splits[0])
            name += splits[1]

            if WRITE_FINGERINGS:
                ### make fingerings page
                # To do this we need to inherit the stock fingerings, and the
                # custom fingerings from each song logged against the tuning.
                # This is slow. But we should already have done it while generating
                # the html for each song. Can we store them as we go?
                if fingerings:
                    tname = tartist.tuning.tuning
                    if tartist.tuning.names:
                        tname += " (%s)" % (", ".join(tartist.tuning.names))
                    fingerings_lines.append( "<hr>" )
                    fingerings_lines.append( "<a name=%s></a>" % tartist.tuning.offset())
                    fingerings_lines.append( "<h3>%s</h3>" % tname)
                    fingerings_lines.append( "<div class=\"chords col1\">" )

                    all_chords = list(fingerings.keys())
                    all_chords.sort(key=lambda c: ( get_chord(c).root, c))

                    root = None
                    for chord in all_chords:
                        this_root = get_chord(chord).root
                        if root and root != this_root:
                            fingerings_lines.append("")
                        fings = list(set(fingerings[chord]))
                        fings.sort()
                        fingerings_lines.append("  " + chord.ljust(15) + (", ".join(fings)))
                        root = this_root

                    fingerings_lines.append( "</div>" )

            if tartist.tuning.standard(): continue

            lines.append( '<li><a class=tuning href="#%s">%s</a> <div class=count>%d</div>' %
                ( offset, name_fw, len(tartist.all_songs() ) ) )

            body.append( '<hr> <a name=%s></a>' % offset )
            body.append( '<h3>%s</h3>' % name )
            body.append( '<ol>' )

            for song in tartist.all_songs():
                link = song.get_html_link(use_song_title_of_first_version=True)
                body.append( '<li> %s (%s)' % ( link, song.artist.name ) )

            body.append( '</ol>' )
            body.append( '<br>' )

        lines += [ '</ul>', '<br>' ]
        lines += self.make_tuning_map()

        lines += body
        lines += [ '<br>' * 50, '</body>', '</html>' ]

        if WRITE_FINGERINGS:
            header = [ "<html>" ]
            header += html_header("Fingerings")
            header += [ "<body>" ]
            footer = [ "</body>", "</html>'" ]
            fingerings_lines = header + fingerings_lines + footer
            with open(self.opts["html_root"] + 'fingerings.html', 'w') as f:
                for l in fingerings_lines:
                    f.write(l + "\n")

        with open(self.opts["html_root"] + 'tunings.html', 'w') as f:
            for l in lines:
                f.write('\n' + l)

        return "%d/%d" % (n_tunings_songs, n_tunings)
    def make_html(self):
        if not DO_CRDFILES:
            allsongs = self.all_songs()
            with open(self.opts["html_root"] + 'songs.html', 'w') as f:
                for l in html_song_index(allsongs):
                    f.write('\n' + l)

        artists_summary, artists_links, misc_links = self.make_artists_index()
        tunings_summary = self.make_tuning_index()
        folk_summary = self.make_folk_index()

        lines  = [ '<html>' ]
        lines += html_header("Chords", index_page=True)
        lines += [ '<body>' ]
        timestamp =  datetime.datetime.now().strftime("%d %b %Y %X")
        lines += [ '<h2 title="%s">Chords</h2>' % timestamp ]
        lines += [ '<hr>' ]
        lines += [ '<a href=songs.html>Song Index</a> <div class=count>%s</div>' % artists_summary ]
        lines += [ '<br> <a href=folk.html>Folk Index</a> <div class=count>%s</div>' % folk_summary ]
        lines += [ '<br> <a href=tunings.html>Tuning Index</a> <div class=count>%s</div>' % tunings_summary ]
        lines += [ '<br> <a href=theory.html>Chords and Scales</a>' ]
        lines += [ '<hr>' ]

        lines += [ '<div class=col4>' ]
        lines += artists_links
        lines += [ '</div>' ] 
        lines += [ '<hr>' ]

        if misc_links:
            lines += [ '<div>' ] # class=col4>' ]
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
    def make_folk_index(self):
        html_lines = [ "<html>" ]
        html_lines += html_header("Folk Index", folk=True)
        html_lines += [ "<body>" ]
        html_lines += [ "<h2> <a href=index.html>Folk Song Index</a> </h2>" ]
        html_lines += [ "<table>" ]

        # Could link to Roud Index, e.g. https://www.vwml.org/roudnumber/5
        # What about Child Ballads?

        trad_songs = []

        for song in self.all_songs():
            if song.cover and song.cover.startswith("Trad"):
                    trad_songs.append(song)
            
            if False and song.cover:
                # check for inconsistent covers
                covers = [ str(song.cover) ]

                for version in song.versions:
                    covers.append(str(version.cover))

                covers = list(set(covers))

                if len(covers) > 1:
                    print("Inconsistent covers: ", covers)

        trad_songs.sort(key=lambda s: s.title_sort)

        for song in trad_songs:
            # one row per song
            line = "<tr>"

            s_link = song.album.fname + '#' + song.link
            line += "<td> <a name=%s> <a href=%s>%s</a> </td>" % (song.link, s_link, song.title)

            a_name = "" 
            if song.artist.name.startswith("Misc:"):
                if song.misc_artist:
                    a_name = song.misc_artist
            else:
                a_name = song.artist.name

            line += "<td> %s </td>" % a_name

            roud = ""
            child = ""

            if song.roud:
                url = "https://www.vwml.org/roudnumber/%s" % song.roud
                roud = "<a href=%s target=_blank>Roud %s</a>" % ( url, song.roud )

            if song.child:
                url = "https://www.childballadrecordings.com/all?ballad_id=%s" % song.child
                child = "<a href=%s target=_blank>Child %s</a>" % ( url, song.child )
        
            line += "<td> %s </td>" % child
            line += "<td> %s </td>" % roud

            line += "</tr>"

            html_lines.append(line)

        html_lines += [ "</table>", "</body>", "</html>" ]
        html_lines += [ "<br> <br> <br> <br> <br>" ]

        with open(self.opts["html_root"] + 'folk.html', 'w') as f:
            for l in html_lines:
                f.write('\n' + l)

        return "%s" % len(trad_songs)
    def add_covers(self):
        # This needs to called after song.cover is set
        # which is currently in format_song_lines so there's no easy place to call it.
        # Can we just set song.cover from song.add_line?
        cover_artists_songs = {}

        for song in self.all_songs():
            # collect cover songs; set cover_link for trad
            if song.cover:
                if song.cover.startswith("Trad"):
                    song.cover_link = "folk.html" + "#" + song.link
                    continue
                if song.cover not in cover_artists_songs:
                    cover_artists_songs[song.cover] = []

                cover_artists_songs[song.cover].append(song)
        
        for covered_artist, songs in cover_artists_songs.items():
            # look up original song and set cover_link
            artist = self.get_artist(covered_artist)

            if artist:
                for csong in songs:
                    found = False
                    csong.cover_link = artist.fname
                    for song in artist.all_songs():
                        if song.title == csong.cover_title:
                            found = True
                            csong.cover_link = song.album.fname + '#' + song.link
                            break
                    if not found:
                        print("Cover version has original artist but no song: %s / %s" % \
                                ( artist.name, csong.title ))
            #else:
                #print("Cover version original artist not found: %s" % covered_artist )

            # If the covered artist exists, but the song doesn't, we could 
            # add the song to a new album. But this would lead to overcounting
            # the song, which is tricky to solve.

            # Also, if an original song is found, we could add links to the cover(s).
    def add_comment_links(self):
        all_songs = self.all_songs()

        #artist = self.get_artist(covered_artist)
        for song in all_songs:
            for version in song.get_all_versions():
                for link in version.comment_links:
                    #print(link["song"])
                    #print("====================")

                    matching_songs = []

                    for s in all_songs:
                        if link["song"].lower() != s.title.lower():
                            continue
                        if link["artist"] and link["artist"].lower() != s.artist.name.lower():
                            continue
                        if link["album"] and link["album"].lower() != s.album.title.lower():
                            continue

                        matching_songs.append(s)

                    if len(matching_songs) == 0:
                        print("No song matching comment_link: " + link["song"])
                    elif len(matching_songs) > 1:
                        print("Ambiguous song comment_link: " + link["song"])
                        for ms in matching_songs:
                            print( "  ", ms.album.fname + "#" + ms.link )

                    for ms in matching_songs:
                        url = ms.album.fname + "#" + ms.link
                        title = ms.artist.name + " | " + ms.album.title + " | " + ms.title
                        s_link = "<a href=%s class=cover title=\"%s\">%s</a>" % (url, title, link["song"])
                        link["link"] = s_link

