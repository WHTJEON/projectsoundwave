
import numpy as np
import os
from scipy.io.wavfile import write
from scipy.io.wavfile import read
import tkinter as  tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import tkinter.font
import pyaudio
import matplotlib.pyplot as plt
import time
import sys
import seaborn as sns
import simpleaudio as sa

def center_window(window,w, h):

    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    if window == window:
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    else:
        window.geometry('%dx%d+%d+%d' % (w, h, x+10, y))

def wav_conversion():

    def openfile ():
        input_path = askopenfilename()
        inputbox.insert(0,"%s"%input_path)

    def convert():
        input_path=inputbox.get()

        try:
            input_file = read("%s"%input_path)
            filename = os.path.basename(input_path)

            sampling_rate, data=read("%s"%input_path)
            audio_length = len(np.array(input_file[1],dtype = float))

            option=messagebox.askyesno("Audio File Information","File Name: %s\nAudio Length: %s\nSample Rate: %sHz\n\nDo you wish to continue?"%(filename,audio_length,sampling_rate))
            if option == True:

                print ("\n[Audio File Information]")
                print ("File Name: %s"%filename)
                print ("Audio Length: %s, Sample Rate: %sHz\n"%(audio_length,sampling_rate))

                print("Creating INVERTED version..")
                original_audio =np.array(input_file[1],dtype = float)
                new_audio = original_audio * (-1)

                scaled = np.int16(new_audio/np.max(np.abs(new_audio))*32767)
                write("%s_inverted.wav"%filename[:-4],sampling_rate,scaled)
                print("Successfully Created %s_inverted.wav"%filename[:-4])
                messagebox.showwarning("File Conversion SUCCESS","Successfully Created\n%s_inverted.wav"%filename[:-4])

            else:
                print(option)
                print("Aborted")

        except ValueError:
            messagebox.showwarning("ERROR","File Type Not Supported")

        except FileNotFoundError:
            messagebox.showwarning("ERROR","File Does Not Exist")

    global inputbox
    win2 = tk.Tk()
    win2.title("WAV File Conversion")
    center_window(win2,400,200)
    win2.resizable(False, False)
    inputbox=tk.Entry(win2,width=36,justify='center')
    button1=tk.Button(win2,text="Choose File",height = 2,width=40,command=openfile)
    button2=tk.Button(win2,text="Convert",height = 2,width=40,command=convert)

    button2.place(x=17,y=150)
    button1.place(x=17,y=100)

    namelabel=tk.Label(win2,text="\nFile Path")
    namelabel.pack()
    inputbox.pack()

    win2.mainloop()

def realtime_mode():

    def start_recording ():
        global fs
        fs = 44100
        seconds = 0.000023  # 유사 1/44100 sec
        i = 0
        f, ax = plt.subplots(2)

        x = np.arange(10000)
        y = np.random.randn(10000)

        li, = ax[0].plot(x, y)
        ax[0].set_xlim(0, 1000)
        ax[0].set_ylim(-5000, 5000)
        ax[0].set_title("Raw Audio Signal")

        li2, = ax[1].plot(x, y)
        ax[1].set_xlim(0, 5000)
        ax[1].set_ylim(-100, 100)
        ax[1].set_title("Fast Fourier Transform")

        plt.pause(0.01)
        plt.tight_layout()

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 0.1
        WAVE_OUTPUT_FILENAME = "file.wav"

        CHUNK = 1024
        WIDTH = 2
        CHANNELS = 2

        global audio
        audio = pyaudio.PyAudio()
        p = pyaudio.PyAudio()

        global stream
        stream = p.open(format=p.get_format_from_width(WIDTH), channels=CHANNELS, rate=RATE, input=True, output=True,
                        frames_per_buffer=CHUNK)

        def plot_data(in_data):
            audio_data = np.fromstring(in_data, np.int16)
            dfft = 10. * np.log10(abs(np.fft.rfft(audio_data)))

            li.set_xdata(np.arange(len(audio_data)))
            li.set_ydata(audio_data)
            li2.set_xdata(np.arange(len(dfft)) * 10.)
            li2.set_ydata(dfft)

            plt.pause(0.01)
            if keep_going:
                return True
            else:
                return False

        def test(in_data):

            global p
            p = pyaudio.PyAudio()

            global stream
            stream = p.open(format=p.get_format_from_width(WIDTH), channels=CHANNELS, rate=RATE, input=True,
                            output=True,
                            frames_per_buffer=CHUNK)

            audio_data = np.fromstring(in_data, np.int16)
            audio_data_new = audio_data * (-1)
            dfft_new = 10. * np.log10(abs(np.fft.rfft(audio_data)))
            li.set_xdata(np.arange(len(audio_data)))
            li.set_ydata(audio_data_new)
            li2.set_xdata(np.arange(len(dfft_new)) * 10.)
            li2.set_ydata(dfft_new)
            stream.write(audio_data_new, CHUNK)

        t = np.linspace(0, 3, 3 * fs, False)
        note = np.sin(440 * t * 6 * np.pi)
        mnote = (-1) * np.sin(440 * t * 6 * np.pi)
        playaudiio = note * (2 ** 15 - 1) / np.max(np.abs(note))
        minusplayaudiio = mnote * (2 ** 15 - 1) / np.max(np.abs(mnote))

        # 16-bit data로 변
        playaudiio = playaudiio.astype(np.int16)
        minusplayaudiio = minusplayaudiio.astype(np.int16)

        global play_obbj
        play_obbj = sa.play_buffer(playaudiio, 1, 2, fs)
        play_obbj = sa.play_buffer(minusplayaudiio, 1, 2, fs)
        stream.start_stream()

        try:
            plot_data(stream.read(CHUNK))
            test(stream.read(CHUNK))
        except:
            pass

    def stop_recording():
        stream.stop_stream()
        stream.close()
        play_obbj.wait_done()
        audio.terminate()

    win3 = tk.Tk()
    win3.title("Real Time Mode")
    center_window(win3, 400, 200)
    win3.resizable(False, False)
    button1 = tk.Button(win3, text="Start Recording", height=2, width=40,command=start_recording)
    button2 = tk.Button(win3, text="Stop Recording", height=2, width=40,command=stop_recording)

    button2.place(x=17, y=150)
    button1.place(x=17, y=100)
    namelabel = tk.Label(win3, text="\nReal-Time Active Noise Cancelling")
    namelabel.pack()

    win3.mainloop()

window=tk.Tk()
window.title("HAS YOONG 2020")
window.resizable(False, False)
center_window(window,400,200)
font=tkinter.font.Font(family="Sandoll 네모니", size=27, weight="bold")
header=tk.Label(window,text="Noise Cancellation DEMO",font=font,pady=15)
label1=tk.Label(text="Powered by FTT (Fast Fourier Transform)")
label2=tk.Label(text="Developed & Designed by HAS10 최은우, 전서")
button1=tk.Button(text="ANC (Real-Time)",height = 2, width = 19,command=realtime_mode)
button3=tk.Button(text="WAV Conversion",height = 2, width = 19, command=wav_conversion)

header.pack()
label1.place(relx=0.5, y=70, anchor='center')
label2.place(relx=0.5, y=110, anchor='center')

button1.place(x=18,y=150)
button3.place(x=208,y=150)

window.mainloop()
