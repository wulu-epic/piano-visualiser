import random, pygame, time
import threading, numpy

from threading import Thread
from queue import Queue
from collections import defaultdict

from modules.Shapes import *
from modules.PianoObjects import *
from modules.Output import*

from modules.Midi import MidiParser
from modules.Midi import MidiSynthesiser

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

        self.TIME_SCALE = 1
        self.TIME_STEP = 0.1 # -> This requires a lot of tweaking unfortunately, need to figure our another method or make it dynamic.

        self.white_key_width = self.screen_width / self.TOTAL_WHITE_KEYS
        self.white_key_height = (self.screen_height / 7) + 500

        self.keys = []
        self.notes_and_shapes = {}

        self.midi_synthesier = MidiSynthesiser()
        self.visualisation_running = False

        pygame.init()
        self.clock = pygame.time.Clock()
          
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
            octave = (i // self.NOTES_IN_OCTAVE) 
            note_index = i % self.NOTES_IN_OCTAVE

            note = self.NOTES[note_index]
            if note in ['C#', 'D#', 'F#', 'G#', 'A#']:
                key_name = f"{note}{octave}"
            else:
                key_name = f"{note}{octave}"

            self.notes_and_shapes[key_name] = key

    def get_shape_by_key(self, key):
        return self.notes_and_shapes.get(key, None)
    
    def press_note(self, note_object : N_Note, midParser : MidiParser):
        self.midi_synthesier.play_note(note_object.pitch, note_object.velocity)
        key_note = midParser.midi_note_number_to_name(note_object.pitch)

        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
        
        shape.colour = self.KEY_DOWN_COLOUR

    def lift_note(self, note_object : N_Note, midParser : MidiParser):
        key_note = midParser.midi_note_number_to_name(note_object.pitch)
        self.midi_synthesier.stop_note(note_object.pitch, note_object.velocity)

        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
        
        shape.colour = shape.original_colour

    def press_note_array(self, note_array : list, end_duration : float, start_duration : float, midParser : MidiParser) -> None:
        if end_duration == 0:
            return

        for note in note_array:
            self.press_note(note, midParser)
        
        scaled_length = ((end_duration - start_duration) * self.TIME_SCALE / len(note_array))
        time.sleep(scaled_length) 

        for note in note_array:
            self.lift_note(note, midParser)
    
    def play_midi(self, midParser: MidiParser, mid_parser_result: dict):
        if not self.midi_synthesier.open_port():
            error('Failed to open a port! Audio will not work!')
            return
        else:
            output('Opened a midi output port successfully!')

        midi_length = midParser.get_midi_length(mid_parser_result)
        warn(f'This piece is: ~{midi_length // 60} minutes long.')

        result_clone = mid_parser_result.copy()

        notes_by_timestamp = defaultdict(list)
        for timestamp, note_array in result_clone.items():
            for note in note_array:
                notes_by_timestamp[timestamp].append(note)

        start_time = time.time()

        for i in numpy.arange(0, midi_length, self.TIME_STEP):
            notes_to_play = []
            for timestamp in list(notes_by_timestamp.keys()):
                if (timestamp - i) < self.TIME_STEP:
                    notes_to_play = (notes_by_timestamp[timestamp])
                    del notes_by_timestamp[timestamp]

            longest_note, smallest_note = midParser.get_note_range(notes_to_play)
            self.press_note_array(notes_to_play, longest_note, smallest_note, midParser)

            elapsed_time = time.time() - start_time
            beat_time = (i * self.TIME_SCALE)
            time_to_wait = beat_time - elapsed_time

            if time_to_wait > 0:
                pygame.time.wait(int(time_to_wait * 1000))  

            self.clock.tick()

    def play_midi_thread(self, pianoVisualiser):
        pianoVisualiser.visualisation_running = True
        piece = 'C:/Users/Martin/Documents/MIDI Files/Moment Musicaux No. 4 in E Minor Rachmaninoff.mid'

        midParser = MidiParser()
        result = midParser.deserialize_midi(piece)

        output(f'Now playing the selected file: {piece}')
        self.play_midi(midParser, result)
        output('Finished playing the midi file!')


class PianoAnimations(PianoVisualiser):
    def note_fall(self) -> None:
        pass
