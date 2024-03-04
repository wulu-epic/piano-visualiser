import os, mido, pretty_midi
from mido import MidiFile
from pretty_midi import pretty_midi
from pygame import midi

import rtmidi, time
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

from modules.Piano import *
from modules.Output import *
from pretty_midi import *

class MidiParser:
    def __init__(self) -> None:
        self.result = {}
    
    def midi_note_number_to_name(self, note_number) -> str:
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 2
        note_index = note_number % 12
        note = notes[note_index]

        if note in ['C#', 'D#', 'F#', 'G#', 'A#']:
            key_name = f"{note}{octave}"
        else:
            key_name = f"{note}{octave}"
        return key_name
    
    def get_midi_length(self, result: dict) -> int: 
        if not result:
            error('Couldnt get the MIDI length due to the file not being deserialized.')
            return -1
        
        return max(result.keys())
    
    def get_note_range(self, note_array): #Get the smallest and lowest note start time
        if len(note_array) <= 0:
            return 0, 0
        
        return max(note.end for note in note_array), min(note.start for note in note_array)
    
    def deserialize_midi(self, midi_file) -> dict:
        warn(f"Deserializing: {midi_file}, please wait.")

        if ".mid" not in midi_file:
            error(f'The requested file: {midi_file} is not a MIDI file.')
            return {}
        
        self.result = {}

        f_midi_file = PrettyMIDI(midi_file)
        instrument_index : int = 0
        
        for instrument in f_midi_file.instruments:
            for note in instrument.notes:
                n_note = N_Note(note.start, note.end, note.pitch, note.velocity, instrument_index) 
                if n_note.start not in self.result:
                    self.result[n_note.start] = []    
                self.result[n_note.start].append(n_note)

        return self.result
    
class MIDIListener:
    def __init__(self):
        self.running = True
        self.input_midi_device = None

        midi.init()

    def get_all_midi_devices(self):
        return [midi.get_device_info(n) for n in range(midi.get_count())]
    
    def ask_for_input(self) -> midi.Input:
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
        return self.input_midi_device

    def exit(self) -> None:
        self.running = False
        
    def listen(self):
        while self.running:
            if self.input_midi_device.poll():
                midi_events = self.input_midi_device.read(25)
                yield midi_events

class MidiSynthesiser:
    def __init__(self) -> None:
        self.midi_out = rtmidi.MidiOut()
        self.port_open : bool = False

    def get_all_ports(self):
        return self.midi_out.get_ports()

    def open_port(self, port = 0) -> bool:
        self.midi_out.open_port(port)
        return self.midi_out.is_port_open() 
    
    def play_note(self, note, velocity) -> None:
        self.midi_out.send_message([NOTE_ON, note, velocity])

    def stop_note(self, note, velocity = 0) -> None: 
        self.midi_out.send_message([NOTE_OFF, note, velocity])
      
class MidiSerializer:
    def __init__(self) -> None:
        pass