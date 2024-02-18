import os, mido
from mido import MidiFile
from modules.Notes import *

class MidiParser:
    def __init__(self) -> None:
            self.result = []
            pass
    
    def midi_note_number_to_name(self, note_number):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 2
        note_index = note_number % 12
        note = notes[note_index]

        if note in ['C#', 'D#', 'F#', 'G#', 'A#']:
            key_name = f"{note}{octave}"
        else:
            key_name = f"{note}{octave}"
        return key_name
    
    def deserialize_midi(self, midi_file):
        print(f"Deserializing: {midi_file}, please wait.")

        if ".mid" not in midi_file:
            print(f'The requested file: {midi_file} is not a MIDI file.')
            return

        mid = mido.MidiFile(midi_file, clip=True)
        for track in mid.tracks:
            for event in track:
                if type(event) is mido.Message and event.type == "note_on":
                    self.result.append(Note(event.time, event.velocity, self.midi_note_number_to_name(event.note)))

        print(f"Successfully deserialized: {midi_file} with {len(self.result)} notes!")
        return self.result

class MidiPlayer:
    def __init__(self) -> None:
        pass
      
class MidiSerializer:
    def __init__(self) -> None:
        pass