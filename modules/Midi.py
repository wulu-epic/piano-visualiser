import os, mido
from mido import MidiFile

from modules.Notes import *
from modules.Output import *

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
        warn(f"Deserializing: {midi_file}, please wait.")

        if ".mid" not in midi_file:
            error(f'The requested file: {midi_file} is not a MIDI file.')
            return []

        mid = mido.MidiFile(midi_file, clip=True)
        self.result = []
        current_chord_notes = []

        for track in mid.tracks:
            for event in track:
                if type(event) is mido.Message:
                    if event.type == "note_on" and event.velocity != 0:
                        key = self.midi_note_number_to_name(event.note)
                        current_chord_notes.append(Note(event.time, event.velocity, key))

                    elif event.type == "note_off" or (event.type == "note_on" and event.velocity == 0):
                        key = self.midi_note_number_to_name(event.note)

                        current_chord_notes.append(Note(event.time, event.velocity, key))
                        self.result.append(Chord(current_chord_notes, event.time))

                        current_chord_notes = []

        output(f"Successfully deserialized: {midi_file} with {len(self.result)} notes and chords!")
        return self.result


class MidiPlayer:
    def __init__(self) -> None:
        pass
      
class MidiSerializer:
    def __init__(self) -> None:
        pass