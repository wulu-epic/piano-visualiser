import random, pygame, time
import threading, numpy

from threading import Thread
from queue import Queue
from collections import defaultdict

from modules.Shapes import *
from modules.PianoObjects import *
from modules.Output import *
from modules.ObjectController import ObjectManager

from modules.Midi import MidiParser
from modules.Midi import MidiSynthesiser

class PianoVisualiser:
    def __init__(self, objManager : ObjectManager, renderManager ):
        self.screen_width = 1280
        self.screen_height = 720

        self.TOTAL_WHITE_KEYS = 56
        self.WIDTH_WHITE_KEY_SPACE = 22

        self.WHITE_KEY_COLOUR = (255, 255, 255)
        self.BLACK_KEY_COLOUR = (0, 0, 0)
        self.KEY_DOWN_COLOUR = (0, 255, 0)

        self.NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTES_IN_OCTAVE = len(self.NOTES)
        self.NOTE_SCALE = 100

        self.TIME_SCALE = .999
        self.TIME_STEP = 0.001 # -> This requires tweaking (SOMETIMES) unfortunately

        self.time = 0.0

        self.white_key_width = self.screen_width / self.TOTAL_WHITE_KEYS
        self.white_key_height = (self.screen_height / 7) + 500

        self.keys = []
        self.notes_and_shapes = {}

        self.midi_synthesier = MidiSynthesiser()
        self.object_manager : ObjectManager = objManager
        self.render_manager  = renderManager

        self.visualisation_running = False
        self.note_fall = True
        self.playing_piece = False

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
            error(f'Failed to get the shape for the pitch: {note_object.pitch} ({key_note})')
            return
        
        shape.colour = self.KEY_DOWN_COLOUR 

    def lift_note(self, note_object : N_Note, midParser : MidiParser) -> None:
        self.midi_synthesier.stop_note(note_object.pitch, note_object.velocity)

        key_note = midParser.midi_note_number_to_name(note_object.pitch)    
        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
    
        shape.colour = shape.original_colour

    def split_note_array_by_instruments(self, note_array: list[N_Note]) -> dict: # Creates a dictionary of notes sorted by instruments / tracks
        result = {}
        for note in note_array:
            if note.instrument_index not in result:
                result[note.instrument_index] = []
            
            result[note.instrument_index].append(note)

        return result
    
    def get_pedal_note_amount(self, note_array):
        n = 0
        for note in note_array:
            if note.pedal:
                n += 1
        return n
    
    def get_pedal_note(self, note_array):
        for index, note in enumerate(note_array):
            if note.pedal:
                return index, note
    
    def press_note_array(self, note_array : list, end_duration : float, start_duration : float, midParser : MidiParser) -> None:
        for note in note_array:
            self.press_note(note, midParser)
        
        scaled_length = ((end_duration - start_duration) * self.TIME_SCALE / len(note_array))
        time.sleep(scaled_length) 

        for note in note_array:
            self.lift_note(note, midParser) 
    
    def do_note_array(self, note_array : list, end_duration : float, start_duration : float, midParser : MidiParser) -> None:
        if end_duration == 0:
            return
        
        if len(note_array) != 1:
            note_array_by_instruments : dict = self.split_note_array_by_instruments(note_array)
            for instrument_index, note_arrays in note_array_by_instruments.items():
                Thread(target=self.press_note_array, args=(note_arrays, end_duration, start_duration, midParser, ), daemon=True).start()
                
                if self.note_fall:
                    Thread(target=self.fall_note_array, args=(note_arrays, midParser, ), daemon=True).start()
        else:
            Thread(target=self.press_note_array, args=(note_array, end_duration, start_duration, midParser, ), daemon=True).start()
            
            if self.note_fall:
                Thread(target=self.fall_note_array, args=(note_array, midParser, ), daemon=True).start()
    
    # object animations, will make into a own class later on (🙏🙏)
    def object_up_animate(self, object: Shape, duration: float):
        initial_y_position = 600
        CONST_SPEED = 200

        object = Square(object.position + Vector2(0, initial_y_position), object.size, (255,0,255))
        speed = -(CONST_SPEED)

        elapsed_time = 0
        time_step = 0.01
        object.size = (object.size[0], duration * self.NOTE_SCALE)
        
        object = self.render_manager.insert_object(object)
        duration_scaler = duration < 1.5 and 20 or 2
        while elapsed_time <= (duration * duration_scaler):
            elapsed_time += time_step
            time.sleep(time_step)

            delta_y = speed * elapsed_time  
            new_y = initial_y_position + delta_y

            new_position = Vector2(object.position.x, new_y)
            object.position = new_position

        self.render_manager.remove_object(object)

    def fall_note_array(self, note_array, midParser):
        for note in note_array:
            note_duration = note.end - note.start

            note_keyname = midParser.midi_note_number_to_name(note.pitch)
            if note_keyname:
                note_shape = self.get_shape_by_key(note_keyname)
                if note_shape:
                    Thread(target = self.object_up_animate, args=(note_shape, note_duration, ), daemon=True).start()

    def stop_midi(self) -> None:
        if self.playing_piece:
            self.playing_piece = False

    def play_midi(self, midParser: MidiParser, mid_parser_result: dict) -> None:
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
        self.playing_piece = True

        for i in numpy.arange(0, midi_length, self.TIME_STEP):
            self.time = i

            notes_to_play = []
            for timestamp in list(notes_by_timestamp.keys()):
                if (timestamp - i) < self.TIME_STEP:
                    notes_to_play = (notes_by_timestamp[timestamp])
                    del notes_by_timestamp[timestamp]

            longest_note, smallest_note = midParser.get_note_range(notes_to_play)
            self.do_note_array(notes_to_play, longest_note, smallest_note, midParser)

            elapsed_time = time.time() - start_time
            beat_time = (i * self.TIME_SCALE)

            time_to_wait = beat_time - elapsed_time
            if time_to_wait > 0:
                pygame.time.wait(int(time_to_wait * 1000))  

            if not self.playing_piece:
                break

            self.clock.tick()
        
        self.playing_piece = False

    def play_midi_thread(self, pianoVisualiser):
        pianoVisualiser.visualisation_running = True
        piece = 'C:/Users/Martin/Documents/MIDI Files/Liszt_Grandes_tudes_de_Paganini_in_A_Minor_Theme_and_Variations_S._141_No._6.mid'
        #self.render_manager.scene_objects.append(ImageRect(((1280/2) - 500, 720/2), "C:/Users/Martin/Pictures/Screenshots/Screenshot 2024-03-06 161319.png"))      

        midParser = MidiParser()
        result = midParser.deserialize_midi(piece)
        output(f'Now playing the selected file: {piece}')

        self.play_midi(midParser, result)
        output('Finished playing the midi file!')
