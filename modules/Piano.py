import random, pygame, time

from modules.Shapes import *
from modules.Midi import MidiParser

class PianoVisualiser:
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720

        self.TOTAL_WHITE_KEYS = 56
        self.WIDTH_WHITE_KEY_SPACE = 22

        self.WHITE_KEY_COLOUR = (255, 255, 255)
        self.BLACK_KEY_COLOUR = (0, 0, 0)
        self.KEY_DOWN_COLOUR = (0, 255, 0)

        self.MAX_CHORD_NOTES = 6 # No rach support sorry 🧌🧌🧌🧌

        self.NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTES_IN_OCTAVE = len(self.NOTES)

        self.white_key_width = self.screen_width / self.TOTAL_WHITE_KEYS
        self.white_key_height = (self.screen_height / 7) + 500

        self.keys = []
        self.notes_and_shapes = {}

        self.visualisation_running = False
        self.t = 0.0

        self.timeline_speed = 0.1 # BPM LATER ON WOOO
        
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
    
    def get_notes_by_t(self, mid_parser: MidiParser): 
        if len(mid_parser.result) <= 0:
            return []

        notes = []
        for note in mid_parser.result:
            if note.time - 0.1 <= self.t and note.time + 0.1 >= self.t:
                if len(notes) >= self.MAX_CHORD_NOTES:
                    return notes
                else:
                    notes.append(note)

        return notes
    
    def highlight_note(self, note):
        shape : Shape = self.get_shape_by_key(note.note)

        originalColour = shape.colour
        shape.colour = self.KEY_DOWN_COLOUR

        print(f'The note: {note.note} has a hold time of: {note.time}')

        time.sleep(note.time/1000)
        shape.colour = originalColour
    
    def play_midi_thread(self, pianoVisualiser):
        pianoVisualiser.visualisation_running = True
        midParser = MidiParser()
        midParser.deserialize_midi("C:/Users/Martin/Documents/MIDI Files/Ballade_No._1_Opus_23_in_G_Minor.mid")

        max_time = self.find_midi_duration(midParser)
        if not max_time:
            print(f'Failed to play the selected midi file')

        self.t = 0.0 # Will move acting as a timeline [have to reset it]
        for ms in range(0, int(max_time * 10), int(self.timeline_speed * 10) ):
            notes = self.get_notes_by_t(midParser)
            if len(notes) > 0:
                for note in notes:
                    self.highlight_note(note)

            print(ms)
            self.t += self.timeline_speed
        
        print('Finished playing the midi file!')



