import random, pygame, time

from threading import Thread
from queue import Queue

import threading

from modules.Shapes import *
from modules.Notes import *

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
        self.t = 0.0

        self.timeline_speed = 0
        self.time_scale = 1000
        self.playing_notes = {}

        self.lock = threading.Lock()
        
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
    
    def find_midi_duration(self, mid_parser : MidiParser):
        if len(mid_parser.result) <= 0:
            return 'Need to deserialise some midi first!'
        
        greatest_time = max(note.time for note in mid_parser.result)
        return greatest_time
    
    def highlight_note(self, notes):
        for note in notes:
            shape = self.get_shape_by_key(note.note)
            shape.colour = self.KEY_DOWN_COLOUR
        
        start_time = pygame.time.get_ticks()

        # Determine the maximum duration among the notes in the chord
        max_duration = max(note.time for note in notes)

        while pygame.time.get_ticks() - start_time < max_duration:
            pygame.time.wait(10)

        # Reset the color for all notes in the chord
        for note in notes:
            shape = self.get_shape_by_key(note.note)
            shape.colour = shape.original_colour

    def play_track(self, channel):
        start_time = time.time()
        for notes in channel:
            elapsed_time = time.time() - start_time
            wait_time = max(note.time / self.time_scale for note in notes) - elapsed_time
            if wait_time > 0:
                time.sleep(wait_time)
            
            self.highlight_note(notes)

    def play_midi_thread(self, pianoVisualiser):
        pianoVisualiser.visualisation_running = True

        midParser = MidiParser()
        result, _ = midParser.deserialize_midi("C:/Users/Martin/Documents/MIDI Files/Ballade_No._1_Opus_23_in_G_Minor.mid")

        thread_list = []
        for track_name, notes in result.items():
            thread = Thread(target=self.play_track, args=(result[track_name], ))
            thread_list.append(thread)
            thread.start()

        for thread in thread_list:
            thread.join()

        print('Finished playing the midi file!')