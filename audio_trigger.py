import numpy as np
from scipy.io import wavfile
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hann
import matplotlib.pyplot as plt
import pyaudio
import logging
from common import *
import time 

STFT_WIN_N = 1000
STFT_HOP = 500
FS = 44100

FRAMES_PER_BUFFER = 64
DEBOUNCE_TIME = 3 # seconds
DEFAULT_AUDIO_RMSE_THRESHOLD = 15


class AudioInputManager():
    def __init__(self, input_idx=None, output_idx=None, host_api_idx = None) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.p = pyaudio.PyAudio()
        self.input_idx = input_idx if input_idx is not None else self.p.get_default_input_device_info().get("index")
        self.output_idx = output_idx if output_idx is not None else self.p.get_default_output_device_info().get("index")
        self.host_api_idx = host_api_idx if host_api_idx is not None else self.p.get_default_host_api_info().get("index")
        self.input_devices = self.get_input_devices()
        self.output_devices = self.get_output_devices()
        self._start_stream()
        
    def read(self):
        if self.stream.is_active:
            return self.stream.read(self.stream.get_read_available())
    
    def write(self, data):
        self.stream.write(data)

    def _start_stream(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=FS,
                    input=True,
                    output=True,
                    input_device_index=self.input_idx,
                    output_device_index=self.output_idx,
                    frames_per_buffer=FRAMES_PER_BUFFER)
    
    def set_input_index(self, idx):
        self.input_idx = idx
        self.reset_stream()

    def set_output_index(self, idx):
        self.output_idx = idx
        self.reset_stream()
        
    def reset_stream(self):
        self.stream.close()
        self._start_stream()

    def get_input_devices(self):
        self.input_devices = dict()
        for i in range(self.p.get_device_count()):      
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info.get('maxInputChannels') > 0 and dev_info.get("hostApi") == self.host_api_idx:
                self.input_devices[i] = dev_info
        return self.input_devices
    
    def get_output_devices(self):
        self.output_devices = dict()
        for i in range(self.p.get_device_count()):      
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info.get('maxOutputChannels') > 0 and dev_info.get("hostApi") == self.host_api_idx:
                self.output_devices[i] = dev_info
        return self.output_devices


class AudioTrigger():
    def __init__(self, audio_file, callback, input_idx=None, output_idx=None) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.audio_file = audio_file
        self.callback = callback
        self.SFT = ShortTimeFFT(hann(STFT_WIN_N), STFT_HOP, FS)
        self.Sx2 = None
        self.Sx_dB = None
        self.Sx_dB_norm = None
        self.target_frames = None
        self.audio = AudioInputManager(input_idx, output_idx)
        self.input_idx = input_idx if input_idx is not None else self.audio.p.get_default_input_device_info().get("index")
        self.output_idx = output_idx if output_idx is not None else self.audio.p.get_default_output_device_info().get("index")
        self.get_target_spectrogram()

        self.input_buffer = np.zeros(len(self.target_frames))
        self.err = 100
        self.threshold = 100
        self.in_debounce = False
        self.debounce_start_t = time.time()

        self.is_active = False


    def set_output_index(self, idx):
        self.output_idx = idx
        self.audio.set_output_index(idx)
        
    def set_input_index(self, idx):
        self.input_idx = idx
        self.audio.set_input_index(idx)
    
    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_target_spectrogram(self):
        T_x, data = wavfile.read(self.audio_file) 
        self.Sx2 = self.SFT.spectrogram(data)
        self.Sx_dB  = 10 * np.log10(np.fmax(self.Sx2, 1e-4))
        self.Sx_dB_norm = self.Sx_dB / np.max(self.Sx_dB)
        self.target_frames = data

    def update(self):
        audio_data = self.audio.read()
        if audio_data: 
            # get audio frames from input
            frames = np.frombuffer(audio_data, np.int16).astype(np.int16)
            # update buffer with new frames
            self.input_buffer = np.concatenate((self.input_buffer[len(frames):], frames))
            # get spectrogram on buffer
            Sx2 = self.SFT.spectrogram(self.input_buffer)
            Sx_dB = 10 * np.log10(np.fmax(Sx2, 1e-4))
            Sx_dB_norm = Sx_dB / np.max(Sx_dB)
            if self.is_active:
                # get RMSE of spectrogram and target
                err = np.sqrt(np.mean((Sx_dB_norm - self.Sx_dB_norm)**2)) * 100
                self.err = round(err , 1)

                if self.in_debounce:
                    if time.time() - self.debounce_start_t >= DEBOUNCE_TIME:
                        # leave debounce
                        self.input_buffer = np.zeros(len(self.target_frames))
                        self.in_debounce = False

                elif err < self.threshold:
                    # Hit sound match; start debounce; clear buffer
                    # self.input_buffer = np.zeros(len(self.target_frames))
                    self.in_debounce = True
                    self.debounce_start_t = time.time()
                    self.logger.info("Hit threshold")
                    self.callback()

            # write audio frames to output
            frames = frames.tobytes()
            self.audio.write(frames)
    

if __name__ == "__main__":
    def foo():
        print("callback")
    file = "C:\\Users\\Julius\\Repos\\Python\\Projects\\autoclickerv2\\audio_files\\minecraft_fishing_catch_sound_short.wav"
    cable_output = 2
    headphones_input = 5
    audio_trigger = AudioTrigger(file, foo, cable_output, headphones_input)


    T_x, data = wavfile.read(file)
    N = data.shape[0]
    SFT = ShortTimeFFT(hann(STFT_WIN_N), STFT_HOP, FS)
    Sx2 = SFT.spectrogram(data)
    print(Sx2.shape)
    
    fig1, ax1 = plt.subplots(figsize=(6., 4.))  # enlarge plot a bit
    t_lo, t_hi = SFT.extent(N)[:2]  # time range of plot
    Sx_dB = 10 * np.log10(np.fmax(Sx2, 1e-4))  # limit range to -40 dB
    im1 = ax1.imshow(Sx_dB, origin='lower', aspect='auto', interpolation="none",
                    extent=SFT.extent(N), cmap='magma')
    fig1.colorbar(im1)

    # Shade areas where window slices stick out to the side:
    fig1.tight_layout()
    plt.show()
