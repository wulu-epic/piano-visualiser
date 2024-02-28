import os, mido
from mido import MidiFile

from modules.Notes import *
from modules.Output import *

from pygame import midi

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
            return {}

        mid = mido.MidiFile(midi_file, clip=True)
        self.result = {}
        
        for track in mid.tracks:
            self.result[track.name] = []
            track : mido.MidiTrack = track
            for event in track:
                if type(event) is mido.Message:
                    if event.type == "note_on":
                        self.result[track.name].append(Note(event.time, event.velocity, self.midi_note_number_to_name(event.note)))
        output(f"Successfully deserialized: {midi_file} with {len(self.result)} notes")
        return self.result, mid.tracks

class MIDIListener:
    def __init__(self):
        self.running = True
        self.input_midi_device = None

        midi.init()

    def get_all_midi_devices(self):
        return [midi.get_device_info(n) for n in range(midi.get_count())]
    
    def ask_for_input(self):
        devices = self.get_all_midi_devices()
        
        print("Available MIDI Devices:")
        for index, device in enumerate(devices):
            print(f"{index}. {device[1].decode()}")

        device_id = 0
        while True:
            device_id = int(input("Choose a device [integer]: "))
            if 0 <= device_id < len(devices):
                break
            print("Invalid choice. Please choose a valid device index.")

        chosen_device = devices[device_id]
        chosen_device_name = chosen_device[1].decode()        
        print(f"Device '{chosen_device_name}' has been chosen!")
        
        self.input_midi_device = midi.Input(device_id)
        return chosen_device

    def exit(self):
        self.running = False
        
    def listen(self):
        while self.running:
            if self.input_midi_device.poll():
                midi_events = self.input_midi_device.read(25)
                print(midi_events)
                yield midi_events

class MidiPlayer:
    def __init__(self) -> None:
        pass
      
class MidiSerializer:
    def __init__(self) -> None:
        pass