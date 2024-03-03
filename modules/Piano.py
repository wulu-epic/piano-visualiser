import random, pygame, time

from threading import Thread
from queue import Queue
from collections import defaultdict

import threading, numpy

from modules.Shapes import *
from modules.PianoObjects import *
from modules.Output import*

from modules.Midi import MidiParser
from modules import Output

class PianoVisualiser:
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720

        self.TOTAL_WHITE_KEYS = 56
        self.WIDTH_WHITE_KEY_SPACE = 22

        self.WHITE_KEY_COLOUR = (255, 255, 255)
        self.BLACK_KEY_COLOUR = (0, 0, 0)
        self.KEY_DOWN_COLOUR = (0, 255, 0)

        self.NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTES_IN_OCTAVE = len(self.NOTES)

        self.white_key_width = self.screen_width / self.TOTAL_WHITE_KEYS
        self.white_key_height = (self.screen_height / 7) + 500

        self.keys = []
        self.notes_and_shapes = {}

        self.visualisation_running = False
          
    def draw_keys(self):
        key_space = 0

        for i in range(self.TOTAL_WHITE_KEYS):
            white_key = Square(pygame.Vector2(key_space, self.white_key_height), (self.WIDTH_WHITE_KEY_SPACE, 120), self.WHITE_KEY_COLOUR)
            self.keys.append(white_key)

            if i % 7 != 2 and i % 7 != 6:
                black_key = Square(pygame.Vector2(key_space + (self.white_key_width - self.WIDTH_WHITE_KEY_SPACE / 2), self.white_key_height), (self.WIDTH_WHITE_KEY_SPACE / 2, 80), self.BLACK_KEY_COLOUR)
                self.keys.append(black_key)

            key_space += self.white_key_width

        self.assign_key_names()
        return self.keys

    def assign_key_names(self):
        for i, key in enumerate(self.keys):
            octave = i // self.NOTES_IN_OCTAVE
            note_index = i % self.NOTES_IN_OCTAVE

            note = self.NOTES[note_index]
            if note in ['C#', 'D#', 'F#', 'G#', 'A#']:
                key_name = f"{note}{octave}"
            else:
                key_name = f"{note}{octave}"

            self.notes_and_shapes[key_name] = key

    def get_shape_by_key(self, key):
        return self.notes_and_shapes.get(key, None)
    
    def highlight_note(self, note_object : N_Note, midParser : MidiParser):
        key_note = midParser.midi_note_number_to_name(note_object.pitch)
        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
        
        shape.colour = self.KEY_DOWN_COLOUR

    def unhighlight_note(self, note_object : N_Note, midParser : MidiParser):
        key_note = midParser.midi_note_number_to_name(note_object.pitch)
        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
        
        shape.colour = shape.original_colour

    def press_note_array(self, note_array : list, length : float, midParser : MidiParser) -> None:
        for note in note_array:
            self.highlight_note(note, midParser)
        
        time.sleep(length / 2)

        for note in note_array:
            self.unhighlight_note(note, midParser)
    
    def play_midi(self, midParser: MidiParser, mid_parser_result: dict):
        midi_length = midParser.get_midi_length(mid_parser_result)
        result_clone = mid_parser_result.copy() 

        notes_by_timestamp = defaultdict(list)
        for timestamp, note_array in result_clone.items():
            for note in note_array:
                notes_by_timestamp[timestamp].append(note)

        time_step = 1
        timestamps = (notes_by_timestamp.keys())

        for i in numpy.arange(0, midi_length, time_step):
            for timestamp in timestamps:
                if abs(i - timestamp) < time_step:
                    note_array = notes_by_timestamp[timestamp]
                    longest_note = midParser.note_array_largest(note_array)
                    self.press_note_array(note_array, longest_note, midParser)
                    
    def play_midi_thread(self, pianoVisualiser):
        pianoVisualiser.visualisation_running = True
        
        midParser = MidiParser()
        result = midParser.deserialize_midi("C:/Users/Martin/Documents/MIDI Files/Fur Elise.mid")

        self.play_midi(midParser, result)
        print('Finished playing the midi file!')