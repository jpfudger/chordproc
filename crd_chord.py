import re

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

    def format(self,transpose=0,prefer_sharp=False,fixed_width=False):
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

            if fixed_width and len(formatted) < max_width:
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

def CRD_get_chord(string):
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

