class N_Note:
    def __init__(self, start : float, end : float, pitch : float, velocity : float, parent_track : int, pedal : bool = False ) -> None:
        self.start : float = start
        self.end : float = end
        self.pitch : float = pitch

        self.velocity : int = velocity
        self.instrument_index : int = parent_track
        self.pedal = pedal

# Will move this class to Piano.py later on, cannot be fucked right now