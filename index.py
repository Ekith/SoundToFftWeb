from pyscript import display, when, document
from js import Uint8Array
import io
import gc

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile



current_file = None
current_channel_index = 0
fft_mode = False
grid_mode = False


audio_input = document.querySelector("#audio-input")
audio_input.removeAttribute("disabled")
display("Système prêt", target="affichage", append=False)


def enable_controls():
    document.querySelector("#previous-channel-button").removeAttribute("disabled")
    document.querySelector("#next-channel-button").removeAttribute("disabled")
    document.querySelector("#btn-plot-signal").removeAttribute("disabled")
    document.querySelector("#btn-plot-fft").removeAttribute("disabled")
    document.querySelector("#btn-grid").removeAttribute("disabled")


@when("change", "#audio-input")
async def open_file(event):
    file_list = event.target.files
    if not file_list:
        return
    

    file = file_list.item(0) # Utiliser .item(0) est plus sûr en JS/PyScript
    
    display(f"Chargement du fichier : {file.name}", target="affichage")
    
    array_buffer = await file.arrayBuffer()
    content = Uint8Array.new(array_buffer).to_bytes()
    
    # Création du flux mémoire
    file_bytes_stream = io.BytesIO(content)
    
    display("Lecture du fichier en cours...", target="affichage", append=True)

    global current_file
    try:
        # On passe le flux directement à ta classe
        current_file = AudioFile(file_bytes_stream)
        display("Chargement réussi !", target="affichage")
        
        res = f"Fréquence d'échantillonnage : {current_file.rate} Hz\n"
        res += f"Nombre de canaux : {current_file.nb_channels}"
        display(res, target="affichage", append=True)
        display_current_channel_index()
        enable_controls()
        
    except Exception as e:
        display(f"Erreur : {e}", target="affichage")



@when("click", "#previous-channel-button")
def previous_channel(event):
    if current_file is None:
        display("Aucun fichier n'a encore été chargé !", target="affichage")
        return
    
    global current_channel_index
    if current_channel_index > 0:
        current_channel_index -= 1
    display_current_channel_index()
    display_graph()
    

@when("click", "#next-channel-button")
def next_channel(event):
    if current_file is None:
        display("Aucun fichier n'a encore été chargé !", target="affichage")
        return
    
    global current_channel_index
    if current_channel_index < current_file.nb_channels - 1:
        current_channel_index += 1
    display_current_channel_index()
    display_graph()


def display_current_channel_index():
    if current_file is None:
        display("Aucun fichier n'a encore été chargé !", target="affichage", append=False)
        return
    display(f"Canal {current_channel_index+1} / {current_file.nb_channels}", target="current-channel-display", append=False)




@when("click", "#btn-plot-signal")
def display_graph_signal(event):
    global fft_mode
    fft_mode = False
    display_graph()


@when("click", "#btn-plot-fft")
def display_graph_fft(event):
    global fft_mode
    fft_mode = True
    display_graph()


@when("click", "#btn-grid")
def toggle_grid(event):
    global grid_mode
    grid_mode = not grid_mode
    display_graph()


def display_graph():
    global current_file
    
    if current_file is None:
        display("Veuillez d'abord charger un fichier WAV.", target="affichage")
        return

    plt.close('all')  # Close previous figures to avoid overlaps
    gc.collect()  # Force garbage collection to free memory
    # 1. Create the figure and the axis (indispensable for PyScript)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        # 2. Call your class method on the current channel index
        # It will draw directly on the 'ax' object we just created
        if fft_mode:
            current_file.plot_fft(current_channel_index, ax=ax)
        else:
            current_file.plot_channel(current_channel_index, ax=ax)
        
        ax.grid(grid_mode)  # Enable or disable grid based on grid_mode
        
        # 3. Adjust the layout
        fig.tight_layout()
        
        # 4. Display the figure in the HTML container
        # 'append=False' allows replacing the previous graph instead of adding a new one
        display(fig, target="graph-container", append=False)
        
    except Exception as e:
        display(f"Error during rendering: {e}", target="affichage")







class AudioFile : 
    
    def __init__(self, file_path):
        self.file_path = file_path
        
        self.rate, self.aud_data = self.load_wav_file(file_path)
        self.aud_data = self.aud_data.astype(np.float32)
        
        self.extract_channels()
        
        self.fft = [None] * self.nb_channels
                
    def extract_channels(self):
        self.nb_channels = self.aud_data.shape[1] if len(self.aud_data.shape) > 1 else 1
        self.channels = []
        if self.nb_channels == 1:
            self.channels.append(self.aud_data[:])
        else:
            for ch in range(self.nb_channels):
                self.channels.append(self.aud_data[:, ch])
    
    def load_wav_file(self, file_path):
        return scipy.io.wavfile.read(file_path)
    
    def get_channel_data(self, channel_index: int):
        if channel_index < 0 or channel_index >= self.nb_channels:
            raise ValueError("Invalid channel index")
        return self.channels[channel_index]
    
    def compute_fft(self, channel_index: int):
        data = self.get_channel_data(channel_index)
        n = len(data)  # Length of the signal
        k = np.arange(n)  # Frequency vector
        T = n / self.rate  # Sampling period
        freq = k / T  # Real frequency vector

        freq = freq[:n // 2]  # Keep only positive frequencies

        fft = np.fft.fft(data) / n  # Normalized Fourier Transform
        fft = fft[:n // 2]  # Keep only positive frequencies

        return freq, fft

    
    def plot_channel(self, channel_indice: int, ax=None):
        ax.plot(self.get_channel_data(channel_indice))
        ax.set_title(f"Audio Signal - Channel {channel_indice+1}")
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Amplitude")
    
    def plot_fft(self, channel_indice: int, ax=None):
        if self.fft[channel_indice] is None:
            freq, fft = self.compute_fft(channel_indice)
            self.fft[channel_indice] = (freq, fft)
        else:
            freq, fft = self.fft[channel_indice]
            
        ax.plot(freq, np.abs(fft))
        ax.set_title(f"FFT - Channel {channel_indice+1}")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Magnitude")

    def plot_channel_fft(self, channel_indice: int, ax : plt.Axes=None):
        if self.fft[channel_indice] is None:
            freq, fft = self.compute_fft(channel_indice)
            self.fft[channel_indice] = (freq, fft)
        else:
            freq, fft = self.fft[channel_indice]
            
        audio_data = self.get_channel_data(channel_indice)
        time = np.arange(len(audio_data)) / self.rate
        
        ax.plot(time, audio_data, label="Audio Signal")
        ax_twin = ax.twinx()
        ax_twin.plot(freq, np.abs(fft), color='orange', label="FFT")
        ax.set_title(f"Audio Signal and FFT - Channel {channel_indice+1}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax_twin.set_ylabel("FFT Magnitude")
        ax.legend(loc='upper left')
        ax_twin.legend(loc='upper right')
        