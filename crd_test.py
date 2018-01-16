#!/usr/bin/python3
import argparse, time
from chordproc.crd_data import CRD_chord

class CRD_test():
    def __init__(self):
        self.count = 0

    def test_chords(self):
        chords = [ 'F' ]
        results = []
        for chord in chords:
            result = CRD_chord(chord).is_chord()
            results.append(result)
        print(results)
        return results

    def test_nochords(self):
        chords = [ 'Free' ]
        results = []
        for chord in chords:
            result = CRD_chord(chord).is_chord()
            results.append(not result)
        print(results)
        return results

    def run(self):
        self.test_chords()
        self.test_nochords()

