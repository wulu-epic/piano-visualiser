import os, mido
from mido import MidiFile

class MidiParser:
    def __init__(self) -> None:
            pass
    
    def deserialize_midi(self, midi_file):
        result = {}
        if ".mid" not in midi_file:
            print(f'The requested file: {midi_file} is not a midi file.')

        mid = MidiFile(midi_file, clip=True)
        for i in mid.tracks[0]:
            if type(i) is mido.Message:
                print(i.control)
                
        
    
class MidiPlayer:
    def __init__(self) -> None:
        pass
      
class MidiSerializer:
    def __init__(self) -> None:
        pass