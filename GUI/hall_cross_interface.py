# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 10:21:09 2022

@author: BRasmussen, Mukesh

Code to plot Hall Cross voltages as function of field applied,
current applied as well as time. Visualizes hall cross experimental data
in real-time.
"""

# importing libraries

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pyvisa
from random import randint
import nidaqmx as daq
import tkinter as tk
import keithley220 as k220
from tkinter import END
from tkinter import ttk

import csv


from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use(['default', 'ggplot'])


# nidaqmx readers

# for random integers

# %%
# Correct ports need to be assigned to control the equiments, here Agilent multimeter and Keithley current source.
# After allocating the correct port address pyvisa library is used to manage the particular resource.

currentport = 'GPIB1::12::INSTR'    # port address for current source
dmmport = 'GPIB0::9::INSTR'     # port address for digital multimeter

# Devices
rm  = pyvisa.ResourceManager()
keithley = k220.Keithley220(currentport)    # initializing a current source object
multimeter = rm.open_resource(dmmport)

# %%


# Global plotting vectors

INTERVAL = 1000

# vector for keeping record of the voltage values obtained from multimeter while using different current values.
MM_VOLTAGE = []
CURRENT = []
FIELD = []
TIME = []
RESISTANCE = []

# this variable is used to set the value that is required as an output from the current source; takes one of the value assigned in the previous list RAMP_VEC(see below!) or uses a completely different value.
LAST_CURR = 0


# similar to LAST_CURR but is used to control the field created by the electromagnet; the electro magnet is controlled by voltage values.
LAST_FIELD_VOLT = 0

# Variables used for automatic/ramp mode for current increase.
# set of current values in fixed step sizes used by ramp/automatic mode. Each value is set to the current source in order.
RAMP_VEC = np.arange(0, 1.0e-6, 100e-9)
RAMP_VEC_FIELD = np.arange(0, 1, 0.1)

# index value to keep record of the position of current value inside RAMP_VEC.
RAMP_INDEX = 0
RAMP_MODE = 0
RAMP_SELECT_FLAG = 0

# index value to keep record of the position of current value inside RAMP_VEC.
RAMP_INDEX_field = 0
RAMP_MODE_field = 0       # flag to inform if ramp mode is selected.


# Temporary lists used for saving the signals when save button is pressed. These list copy the primary vectors allocated above which are cleared when stop button is pressed.
MM_VOL_TEMP = []
FIELD_TEMP = []
CURR_TEMP = []
TIME_TEMP = []
RES_TEMP = []

# Flags to include or exclude specific plots.
VOLT_FLAG = 1
CURR_FLAG = 1

# linear field calibration parameters:

slope_field = 848.2
intercept_field = -4


# %%

# Channels
# magnetization/power channel/port in nidaq that controls the electromagnet.
mag_channel = 'Dev1/ao1'
# channel/port in nidaq that acquires signal from photodiode.
pd_channel = 'Dev1/ai0'
# channel in nidaq that acquires signal from hall probe.
hp_channel = 'Dev1/ai1'

# %%

# DAQ functions for reading and communicating with DNC attached instruments to
# the nidaq unit:


def read_analog_in(channel=pd_channel, number_of_samples=1000, samplerate=50000, timeout=-1, range=(-10, 10)):
     ''' Reads an analog input from the DAQ.

           channel: the channel to read (eg. 'Dev1/ai0')
           number_of_samples: the number of samples to read; these are then averaged
               to give a final value
           samplerate: the sample rate to use (in Hz)
           timeout: maximum time (in s) to wait for the read to complete. Default
               (value of -1) is to wait a dynamic amount of time based on the number
               of samples and the samplerate (number_of_samples/samplerate + 10% + 1s).
           range: the output range to use. You should probably just keep this
               as (-10, 10), since only certain ranges are allowed
           num_divs: the number of divisions in the DAQ's full input range

           Returns the average of the samples read.'''

     # calculate timeout
     if timeout == -1:
         timeout = number_of_samples/samplerate*1.1 + 1

      # read values
     with daq.Task() as task:
         task.ai_channels.add_ai_voltage_chan(channel,
                                              min_val=range[0], max_val=range[1],
                                              units=daq.constants.VoltageUnits.VOLTS)
         task.timing.cfg_samp_clk_timing(
             samplerate, samps_per_chan=number_of_samples)
         task.start()
         data = task.read(number_of_samples_per_channel=daq.constants.READ_ALL_AVAILABLE,
                          timeout=timeout)

         # average and scale values
         # print(f'Max values = {np.max(data)}, min value = {np.min(data)}, std dev = {np.std(data)}')
     return np.mean(data)
    #return 100*np.sin(LAST_CURR) + 0.000001 * randint(0, 20)


def set_analog_out(channel, voltage, range=(-10, 10)):
     ''' Sets an analog output on the DAQ.

           channel: the channel to set (eg. 'Dev1/ao0')
           voltage: the voltage to set
           range: the output range to use. You should probably just keep this
               as (-10, 10), since only certain ranges are allowed'''
     if not (range[0] <= voltage <= range[1]):
         raise ValueError(
             'Voltage limits are {}<=V<={}'.format(range[0], range[1]))

     # write the value
     with daq.Task() as task:
         task.ao_channels.add_ao_voltage_chan(channel,
                                              min_val=range[0], max_val=range[1],
                                              units=daq.constants.VoltageUnits.VOLTS)
         task.write(voltage)
         task.start()
     pass


# Function to read the multimeter voltage values. Returns a float value with 4 decimal places!


def read_multimeter_voltage():
    
    try:
        mes1 = float(multimeter.query('MEAS:VOLT:DC?'))
        to_return = float('%.4g' % mes1)
        return to_return
    except:
            return 10*LAST_CURR ** 2 + LAST_FIELD_VOLT ** 0.5

# Function to initialize the current. Initializing the current puts the current source in operate mode! Requires and returns no arguments!


def initialize_current():
    keithley.initialize_current()
    pass


# Function to terminate the current. Does the opposite of initializing current; diables the operate mode! Requires and returns no arguments!


def terminate_current():
    keithley.terminate_current()
    pass


# Function to change/set different current values on current source. Uses global variable LAST_CURR to set to specific current value. Returns the current value taken by LAST_CURR!


def set_current():
    keithley.set_current(LAST_CURR)
    keithley.set_vlimit(5) # temporary fix for vlim (to get rid of 1v Vlimit)
    return LAST_CURR


def set_field():
    set_analog_out(mag_channel,LAST_FIELD_VOLT)
    return LAST_FIELD_VOLT


def weird_division(n, d):
    return n / d if d else 0

# %%


# Main figure used by the animate function. Subplots inside the figure are constantly updated by the animate function.
fig1 = Figure(dpi=80, figsize=(10, 10))



# TODO: calibrate field to voltage ratio

# Sub-plot 1 that plots multimeter voltage values against the applied current values. Useful to ensure if the sample is okay or blown!
subfig1 = fig1.add_subplot(221)
subfig1.set_xlabel('Applied Field [V]')
subfig1.set_ylabel('Hall Cross Voltage [V]')

# Sub-plot 2 that plots photodiode voltage against applied current. Useful to observe hysteresis while sweeping different current values. Still under development!
subfig2 = fig1.add_subplot(222)
subfig2.set_xlabel('Applied Current [uA]')
subfig2.set_ylabel('Hall Cross Voltage [V]')

# Sub-plot 3 that plots the hall cross voltage trend against elapsed time. Very useful to notice magnetization switching. Time axis has not been calibrated!
subfig3 = fig1.add_subplot(223)
subfig3.set_xlabel('Time')
subfig3.set_ylabel('Hall Cross Voltage [V]')

# Sub-plot 4 that plots the resistance of the sample as function of time
subfig4 = fig1.add_subplot(224)
subfig4.set_xlabel('Time')
subfig4.set_ylabel('Hall Cross Resistance')
# %%

# This function is responsible for acquiring and setting different signals from different equipments. Also the plots are updated here. When the user interacts with the interface,
# they change the global variables. FuncAnimation calls this function in infinite loops until it is stopped. The function uses the global variables which are updated/changed by the
# interface and follow the logic inside this function. The function uses several global flags to switch between different modes.


def animate(i, start_flag):

    global RAMP_INDEX   # writing global followed by the variable name allows the manipulation of global variables inside this function. Without declaring them first as 'global' will treat the variables as local function variables.
    global LAST_CURR
    global LAST_FIELD_VOLT
    global VOLT_FLAG
    global CURR_FLAG
    global RAMP_SELECT_FLAG

    #set_analog_out(mag_channel, LAST_FIELD_VOLT)

    if (start_flag == True):
        if(RAMP_MODE):

            if (RAMP_SELECT_FLAG == True):

                if (RAMP_INDEX < len(RAMP_VEC)):
                    LAST_CURR = RAMP_VEC[RAMP_INDEX]
                    RAMP_INDEX += 1
                else:
                    return

            elif (RAMP_SELECT_FLAG == False):

                if (RAMP_INDEX < len(RAMP_VEC)):
                    LAST_FIELD_VOLT = RAMP_VEC[RAMP_INDEX]
                    RAMP_INDEX += 1
                else:
                    return

        # TODO: add field ramp:

        # If time needs to be accurate, multiply by the calibration factor here!
        TIME.append(len(TIME)*INTERVAL*1e-3)

        mm_val = read_multimeter_voltage()
        MM_VOLTAGE.append(mm_val)

        if (VOLT_FLAG or CURR_FLAG == 1):
            curr_val = set_current()
            CURRENT.append(curr_val*1e6)

            subfig2.clear()
            subfig2.plot(CURRENT, MM_VOLTAGE, '--or')
            subfig2.set_xlabel('Applied Current [uA]')
            subfig2.set_ylabel('Hall Cross Voltage [V]')

        if (VOLT_FLAG == 1):
            field_val = set_field()
            FIELD.append(field_val)

            subfig1.clear()
            subfig1.plot(FIELD, MM_VOLTAGE, '--ob')
            subfig1.set_xlabel('Applied Field [V]')
            subfig1.set_ylabel('Hall Cross Voltage [V]')

        subfig3.clear()
        subfig3.plot(TIME, MM_VOLTAGE, '--om')
        subfig3.set_xlabel('Time[s]')
        subfig3.set_ylabel('Hall Cross Voltage [V]')

        resistance = weird_division(mm_val, LAST_CURR)
        RESISTANCE.append(resistance)
        subfig4.clear()
        subfig4.plot(TIME, RESISTANCE, '--oc')
        subfig4.set_xlabel('Time')
        subfig4.set_ylabel('Hall Cross Resistance')
        plt.show()
    pass

# %%

# Interface class using Tkinter that makes the construction of GUI easier.


class Interface(tk.Tk):
    '''
    Class that produces an interface with multiple self updating plots 
    for current, voltage and photodiode inputs and outputs. First part of the
    code constructs the GUI while the latter half is for functional methods.
    '''

    def __init__(self):
        super().__init__()
# %%
        # configures the base window
        self.title("Interface for Signal and Applied current Visualization")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=2)

# %%
        # frame0 that includes start, stop and save buttons.
        # Also includes checkboxes to include/ exclude different plots.
        self.frame0 = tk.Frame(self, bd=5)
        self.frame0.grid(row=0, column=0, rowspan=1, columnspan=4,
                         padx=5, pady=5, ipadx=0, ipady=0)
        self.frame0['relief'] = 'ridge'

        # start button for plotting

        self.start_button = tk.Button(self.frame0, text='Start')
        self.start_button['command'] = self.start_button_clicked
        self.start_button.grid(row=0, column=0, padx=(0, 150))

        # stop button for plotting

        self.stop_button = tk.Button(self.frame0, text='Stop')
        self.stop_button['command'] = self.stop_button_clicked
        self.stop_button['state'] = 'disabled'
        self.stop_button.grid(row=0, column=0, padx=(0, 0))

        # save button for saving dataset

        self.save_button = tk.Button(self.frame0, text='Save')
        self.save_button['state'] = 'normal'
        self.save_button.grid(row=0, column=0, padx=(150, 0))
        self.save_button['command'] = self.save_button_clicked

        self.var_volt = tk.IntVar()
        self.var_volt.set(1)
        self.var_curr = tk.IntVar()
        self.var_curr.set(1)

        self.include_label = tk.Label(self.frame0, text='Include: ')
        self.include_label.grid(row=0, column=1, padx=5)

        # Voltage checkbutton

        self.volt_checkbox = tk.Checkbutton(self.frame0, text='VOLTAGE', variable=self.var_volt, onvalue=1,
                                            offvalue=0, command=self.include_voltage)
        # Current checkbutton

        self.curr_checkbox = tk.Checkbutton(self.frame0, text='CURRENT', variable=self.var_curr, onvalue=1,
                                            offvalue=0, command=self.include_current)
        self.volt_checkbox.grid(row=0, column=3)
        self.curr_checkbox.grid(row=0, column=2)

# %%

        # Canvas/drawing area

        self.framecan = tk.Frame(self, bd=5)
        self.framecan.grid(row=1, column=1, rowspan=5,
                           padx=5, pady=5, ipadx=0, ipady=0)
        self.framecan['relief'] = 'sunken'
        canvas = FigureCanvasTkAgg(fig1, self.framecan)  # drawing area
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=5)

# %%
        ######## Current settings #########

        # frame: much easier to manipulate

        # frame1 that includes manual settings for controlling current values.

        self.frame1 = tk.Frame(self, bd=5)
        self.frame1.grid(row=4, column=4, rowspan=1,
                         padx=5, ipadx=5, ipady=5)
        self.frame1['relief'] = 'ridge'

        # Current entry space:

        self.current_label = tk.Label(self.frame1, text='Current Input (A)')
        self.current_label.grid(row=2, column=2, padx=5)

        # current_entry

        self.current_entry = tk.Entry(self.frame1, width=5, state='disabled')
        self.current_entry.grid(row=2, column=1)

        self.current_frame_label = tk.Label(
            self.frame1, text='Current Setting Controls:', font=('Arial', 12, 'underline'))
        self.current_frame_label.grid(
            row=1, column=1, columnspan=2, padx=10, pady=(5, 10))

        # +/_ Buttons for current setting:

        # btn_add_current

        self.btn_add_current = tk.Button(
            self.frame1, text='+', height=2, width=3, bg="#DAF5D6", activeforeground='cyan', state='disabled')
        self.btn_add_current.grid(row=3, column=1, padx=5)
        self.btn_add_current['command'] = self.add_value_to_current

        self.add_value = tk.StringVar(self.frame1)
        self.add_value.set('1 \u03BCA')  # default value

        # step_size_add (OptionMenu)

        self.step_size_add = tk.OptionMenu(
            self.frame1, self.add_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_add.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_add['state'] = 'disabled'
        self.step_size_add.grid(row=3, column=2, padx=5)

        # btn_subtract_current

        self.btn_subtract_current = tk.Button(
            self.frame1, text='-', height=2, width=3, bg="#F5D6D6", activeforeground='cyan', state='disabled')
        self.btn_subtract_current.grid(row=4, column=1, padx=5)
        self.btn_subtract_current['command'] = self.subtract_value_from_current

        self.subtract_value = tk.StringVar(self.frame1)
        self.subtract_value.set('1 \u03BCA')  # default value

        # step_size_subtract (OptionMenu)

        self.step_size_subtract = tk.OptionMenu(
            self.frame1, self.subtract_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_subtract.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_subtract['state'] = 'disabled'
        self.step_size_subtract.grid(row=4, column=2, padx=5)


# %%

        ######### Field Settings ########

        # frame 5 to control field settings.

        self.frame5 = tk.Frame(self, bd=5)
        # self.frame5.grid(row=4, column=4, rowspan=1,
        # padx=5, ipadx=5, ipady=5)
        self.frame5['relief'] = 'ridge'

        self.field_label = tk.Label(self.frame1, text='Voltage Input (V)')
        self.field_label.grid(row=6, column=2, padx=5)

        # field_entry

        self.field_entry = tk.Entry(self.frame1, width=5)
        self.field_entry.insert(-1, '0.0')
        self.field_entry.grid(row=6, column=1)

        self.field_frame_label = tk.Label(
            self.frame1, text='Field Setting Controls:', font=('Arial', 12, 'underline'))
        self.field_frame_label.grid(
            row=5, column=1, columnspan=2, padx=10, pady=(15, 10))

        # +/_ Buttons for field setting:

        # btn_add_field

        self.btn_add_field = tk.Button(
            self.frame1, text='+', height=2, width=3, bg="#DAF5D6", activeforeground='green')
        self.btn_add_field.grid(row=7, column=1, padx=5)
        self.btn_add_field['command'] = self.add_value_to_field

        self.add_value2 = tk.StringVar(self.frame5)
        self.add_value2.set('0.1 V')  # default value

        # step_size_add2

        self.step_size_add2 = tk.OptionMenu(
            self.frame1, self.add_value2, "0.1 V", "0.5 V", "1.0 V")
        self.step_size_add2.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_add2.grid(row=7, column=2, padx=5)

        # btn_subtract_field

        self.btn_subtract_field = tk.Button(
            self.frame1, text='-', height=2, width=3, bg="#F5D6D6", activeforeground='red')
        self.btn_subtract_field.grid(row=8, column=1, padx=5)
        self.btn_subtract_field['command'] = self.subtract_value_from_field

        self.subtract_value2 = tk.StringVar(self.frame1)
        self.subtract_value2.set('0.1 V')  # default value

        # step_size_subtract2

        self.step_size_subtract2 = tk.OptionMenu(
            self.frame1, self.subtract_value2, "0.1 V", "0.5 V", "1.0 V")
        self.step_size_subtract2.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_subtract2.grid(row=8, column=2, padx=5)

# %%

        ######### Automatic increasing current and field #########

        # frame 2 that includes Ramp control setting

        self.tabsystem = ttk.Notebook(self)

        self.frame2 = tk.Frame(self.tabsystem, bd=5)
        self.frame2.grid(row=2, column=4, rowspan=1,
                         padx=5, pady=5, ipadx=5, ipady=5)
        self.frame2['relief'] = 'ridge'

        self.tabsystem.add(self.frame2, text="  Field  ")
        self.tabsystem.grid(row=2, column=4)

        self.ramp_field_label = tk.Label(
            self.frame2, text='Field Ramp Settings:', font=('Arial', 12, 'underline'))
        self.ramp_field_label.grid(
            row=1, column=1, columnspan=2, padx=5, pady=(5, 10))

        self.min_field_label = tk.Label(
            self.frame2, text='Minimum Field Voltage (V)')
        self.min_field_label.grid(row=2, column=2, padx=5)

        # min_field_entry

        self.min_field_entry = tk.Entry(
            self.frame2, width=5, state='disabled')
        self.min_field_entry.grid(row=2, column=1)

        self.max_field_label = tk.Label(
            self.frame2, text='Maximum Field Voltage (V)')
        self.max_field_label.grid(row=3, column=2, padx=5)

        # max_field_entry

        self.max_field_entry = tk.Entry(
            self.frame2, width=5, state='disabled')
        self.max_field_entry.grid(row=3, column=1)

        self.field_step_size_label = tk.Label(
            self.frame2, text='Step Size (V)')
        self.field_step_size_label.grid(row=4, column=2, padx=5)

        # ramp_step_size_entry

        self.field_step_size_entry = tk.Entry(
            self.frame2, width=5, state='disabled')
        self.field_step_size_entry.grid(row=4, column=1)

        self.current_plus_ramp_entry = tk.Entry(self.frame2, width=5,state='disabled')
        self.current_plus_ramp_entry.grid(row=5,column=1)
        self.current_plus_ramp_label = tk.Label(self.frame2, text='Applied Current (A)')
        self.current_plus_ramp_label.grid(row=5, column=2, padx=5)
        # btn_set_ramp

        self.btn_set_ramp_field = tk.Button(
            self.frame2, text='Set', height=1, width=4, bg="#DAF5D6", activeforeground='cyan')
        self.btn_set_ramp_field.grid(row=6, column=1, padx=5)
        self.btn_set_ramp_field['command'] = self.set_ramp_setting

        ########## Current ramp settings: ##########

        self.frame6 = tk.Frame(self.tabsystem, bd=5)
        self.frame6.grid(row=2, column=4, rowspan=1,
                         padx=5, pady=5, ipadx=5, ipady=5)
        self.frame6['relief'] = 'ridge'

        self.tabsystem.add(self.frame6, text='Current')
        self.tabsystem.grid(row=2, column=4)

        self.ramp_frame_label = tk.Label(
            self.frame6, text='Current Ramp Settings:', font=('Arial', 12, 'underline'))
        self.ramp_frame_label.grid(
            row=1, column=1, columnspan=3, padx=(5, 5), pady=(5, 10))

        self.min_current_label = tk.Label(
            self.frame6, text='Minimum Current (A)')
        self.min_current_label.grid(row=2, column=2, padx=5)

        # min_current_entry

        self.min_current_entry = tk.Entry(
            self.frame6, width=5, state='disabled')
        self.min_current_entry.grid(row=2, column=1)

        self.max_current_label = tk.Label(
            self.frame6, text='Maximum Current (A)')
        self.max_current_label.grid(row=3, column=2, padx=5)

        # max_current_entry

        self.max_current_entry = tk.Entry(
            self.frame6, width=5, state='disabled')
        self.max_current_entry.grid(row=3, column=1)

        self.ramp_step_size_label = tk.Label(self.frame6, text='Step Size (A)')
        self.ramp_step_size_label.grid(row=4, column=2, padx=5)

        # ramp_step_size_entry

        self.ramp_step_size_entry = tk.Entry(
            self.frame6, width=5, state='disabled')
        self.ramp_step_size_entry.grid(row=4, column=1)

        # field during ramp entry
        
        self.field_plus_ramp_entry = tk.Entry(self.frame6, width=5,state='disabled')
        self.field_plus_ramp_entry.grid(row=5,column=1)
        self.field_plus_ramp_label = tk.Label(self.frame6, text='Applied Field (V)')
        self.field_plus_ramp_label.grid(row=5, column=2, padx=5)


        # btn_set_ramp

        self.btn_set_ramp = tk.Button(
            self.frame6, text='Set', height=1, width=4, bg="#DAF5D6", activeforeground='cyan')
        self.btn_set_ramp.grid(row=6, column=1, padx=5)
        self.btn_set_ramp['command'] = self.set_ramp_setting


# %%

        # frame 3 that includes maximum safe current and signal interval values.
        # Maximum safe current has not be programmed!

        # TODO: maximum safe current and voltage limit

        self.frame3 = tk.Frame(self, bd=2)
        self.frame3.grid(row=0, column=4, rowspan=1,
                         padx=15, pady=5, ipadx=5)
        self.frame3['relief'] = 'groove'
        self.safety_current_label = tk.Label(
            self.frame3, text='Maximum Safe Current (A)')
        self.safety_current_label.grid(row=1, column=1)

        # safety_current_entry

        self.safety_current_entry = tk.Entry(self.frame3, width=4)
        self.safety_current_entry.insert(-1, '0.101')
        self.safety_current_entry.grid(row=1, column=2)

        self.signal_interval_label = tk.Label(
            self.frame3, text='Signal Interval (ms)')
        self.signal_interval_label.grid(row=2, column=1)

        # signal_interval_entry

        self.signal_interval_entry = tk.Entry(self.frame3, width=4)
        self.signal_interval_entry.insert(-1, '1000')
        self.signal_interval_entry.grid(row=2, column=2)

# %%
        # frame 4 that includes radio buttons to switch between 'manual' and
        # 'ramp' current setting.

        self.frame4 = tk.Frame(self, bd=5)
        self.frame4.grid(row=1, column=4, rowspan=1,
                         padx=5, pady=5, ipadx=5, ipady=5)
        self.frame4['relief'] = 'ridge'

        self.selection_frame_label = tk.Label(
            self.frame4, text='Mode Settings', font=('Arial', 12, 'underline'))
        self.selection_frame_label.grid(
            row=1, column=1, columnspan=2, padx=5, pady=(5, 10))

        # radio buttons

        self.var_radio = tk.IntVar()
        self.var_radio.set(1)

        # off_state

        self.off_state = tk.Radiobutton(
            self.frame4, text='OFF', variable=self.var_radio, value=1, command=self.OFF_mode_selected)
        self.off_state.grid(row=2, column=1)

        # manual_mode

        self.manual_mode = tk.Radiobutton(
            self.frame4, text='Manual', variable=self.var_radio, value=2, command=self.manual_mode_selected)
        self.manual_mode.grid(row=4, column=1)

        # ramp_mode

        self.ramp_mode = tk.Radiobutton(
            self.frame4, text='Ramp', variable=self.var_radio, value=3, command=self.ramp_mode_selected)
        self.ramp_mode.grid(row=3, column=1)


# %%

# call for animate
        self.ani = animation.FuncAnimation(
            fig1, animate, fargs=(False,), interval=INTERVAL)

# %%
    ################ Method Section ##################

    def include_voltage(self):
        global VOLT_FLAG
        val = self.var_volt.get()
        if (val == 0):
            VOLT_FLAG = 0
        else:
            VOLT_FLAG = 1

    def include_current(self):
        global CURR_FLAG
        global VOLT_FLAG
        self.var_radio.set(1)
        self.OFF_mode_selected()
        val = self.var_curr.get()
        if (val == 0):
            self.var_volt.set(0)
            self.volt_checkbox['state'] = 'disabled'
            for child in self.frame4.winfo_children():
                child.configure(state='disabled')
            CURR_FLAG = 0
            VOLT_FLAG = 0
        else:
            self.volt_checkbox['state'] = 'normal'
            for child in self.frame4.winfo_children():
                child.configure(state='normal')
            CURR_FLAG = 1

    def set_ramp_setting(self):
        global RAMP_VEC
        global RAMP_INDEX
        global LAST_CURR
        global LAST_FIELD_VOLT
        
        currenttab = self.tabsystem.tab(self.tabsystem.select(), "text")

        try:
            if currenttab == "Current":
                start_val = float(self.min_current_entry.get())
                stop_val = float(self.max_current_entry.get())
                step = float(self.ramp_step_size_entry.get())
                field = float(self.field_plus_ramp_entry.get())
                RAMP_VEC = np.arange(start_val, stop_val, step)
                RAMP_INDEX = 0
                LAST_FIELD_VOLT = field
                print('Current Ramp settings updated!')
            elif currenttab == "  Field  ":
                start_val = float(self.min_field_entry.get())
                stop_val = float(self.max_field_entry.get())
                step = float(self.field_step_size_entry.get())
                current = float(self.current_plus_ramp_entry.get())
                RAMP_VEC = np.arange(start_val, stop_val, step)
                RAMP_INDEX = 0
                LAST_CURR = current
                print('Field Ramp settings updated!')

        except:
            print('Failed to set the ramp vector!')

    def stop_ramp(self):
        pass

    def add_value_to_field(self):
        step_size = self.add_value2.get()
        old = float(self.field_entry.get())
        new = 0
        if step_size == "0.1 V":
            new = old + 0.1
        elif step_size == "0.5 V":
            new = old + 0.5
        elif step_size == "1.0 V":
            new = old + 1.0
        else:
            print('something\'s wrong, I can feel it')
        if (new > 7.5):
            new = 7.5
        self.field_entry.delete(0, END)
        self.field_entry.insert(-1, "{:.9g}".format(new))
        # instrument.set_current(new)

        global LAST_FIELD_VOLT
        LAST_FIELD_VOLT = new

    def subtract_value_from_field(self):
        step_size = self.subtract_value2.get()
        old = float(self.field_entry.get())
        new = 0
        if step_size == "0.1 V":
            new = old - 0.1
        elif step_size == "0.5 V":
            new = old - 0.5
        elif step_size == "1.0 V":
            new = old - 1.0
        else:
            print('something\'s wrong, I can feel it')
        if (new < -5.0):
            new = -5.0
        self.field_entry.delete(0, END)
        self.field_entry.insert(-1, "{:.9g}".format(new))
        # instrument.set_current(new)

        global LAST_FIELD_VOLT
        LAST_FIELD_VOLT = new

    def OFF_mode_selected(self):
        self.current_entry.delete(0, END)
        self.min_current_entry.delete(0, END)
        self.max_current_entry.delete(0, END)
        self.ramp_step_size_entry.delete(0, END)
        for child in self.frame1.winfo_children():
            child.configure(state='disabled')
        for child in self.frame2.winfo_children():
            child.configure(state='disabled')
        for child in self.frame6.winfo_children():
            child.configure(state='disabled')
        terminate_current()
        set_analog_out(mag_channel, 0)
        global LAST_CURR
        LAST_CURR = 0.0
        set_current()
        global RAMP_MODE
        RAMP_MODE = 0

    def manual_mode_selected(self):
        for child in self.frame1.winfo_children():
            child.configure(state='normal')
        for child in self.frame2.winfo_children():
            child.configure(state='disabled')
        for child in self.frame6.winfo_children():
            child.configure(state='disabled')
        self.current_entry.delete(0, END)
        self.current_entry.insert(-1, '0.0e-9')
        initialize_current()
        global RAMP_MODE
        RAMP_MODE = 0

    def ramp_mode_selected(self):
        currenttab = self.tabsystem.tab(self.tabsystem.select(), "text")
        print(currenttab)
        for child in self.frame1.winfo_children():
            child.configure(state='disabled')

        global RAMP_MODE
        global RAMP_SELECT_FLAG

        # TODO: delete each entry every time it is clicked

        if currenttab == "Current":
            for child in self.frame6.winfo_children():
                child.configure(state='normal')
            for child in self.frame2.winfo_children():
                child.configure(state='disabled')
            # set default values
            self.min_current_entry.insert(-1, '0.0e-9')
            self.max_current_entry.insert(-1, '1.0e-6')
            self.ramp_step_size_entry.insert(-1, '100e-9')
            self.field_plus_ramp_entry.insert(-1, '0')
            initialize_current()

            RAMP_MODE = 1
            RAMP_SELECT_FLAG = 1
        elif currenttab == "  Field  ":
            for child in self.frame2.winfo_children():
                child.configure(state='normal')
            for child in self.frame6.winfo_children():
                child.configure(state='disabled')
            self.min_field_entry.insert(-1, '0')
            self.max_field_entry.insert(-1, '1')
            self.field_step_size_entry.insert(-1, '0.1')
            self.current_plus_ramp_entry.insert(-1, '0')
            initialize_current()
            
            RAMP_MODE = 1
            RAMP_SELECT_FLAG = 0
        else:
            print('This is not working')

    def set_initial_variables(self):
        global INTERVAL
        try:
            INTERVAL = float(self.signal_interval_entry.get())
        except:
            print('Invalid value for interval!')
            INTERVAL = 1000
        pass

    def add_value_to_current(self):
        step_size = self.add_value.get()
        old = float(self.current_entry.get())
        new = 0
        if step_size == "1 nA":
            new = old + 1e-9
        elif step_size == "10 nA":
            new = old + 1e-8
        elif step_size == "100 nA":
            new = old + 1e-7
        elif step_size == "1 \u03BCA":
            new = old + 1e-6
        elif step_size == "10 \u03BCA":
            new = old + 1e-5
        elif step_size == "100 \u03BCA":
            new = old + 1e-4
        elif step_size == "1 mA":
            new = old + 1e-3
        elif step_size == "10 mA":
            new = old + 1e-2
        else:
            print('something\'s wrong, I can feel it')
        self.current_entry.delete(0, END)
        self.current_entry.insert(-1, "{:.9g}".format(new))
        # instrument.set_current(new)

        global LAST_CURR
        LAST_CURR = float('%0.4g' % new)

    def subtract_value_from_current(self):
        step_size = self.subtract_value.get()
        old = float(self.current_entry.get())

        new = 0
        if step_size == "1 nA":
            new = old - 1e-9
        elif step_size == "10 nA":
            new = old - 1e-8
        elif step_size == "100 nA":
            new = old - 1e-7
        elif step_size == "1 \u03BCA":
            new = old - 1e-6
        elif step_size == "10 \u03BCA":
            new = old - 1e-5
        elif step_size == "100 \u03BCA":
            new = old - 1e-4
        elif step_size == "1 mA":
            new = old - 1e-3
        elif step_size == "10 mA":
            new = old - 1e-2
        else:
            print('something\'s wrong, I can feel it')
        self.current_entry.delete(0, END)

        self.current_entry.insert(-1, "{:.9g}".format(new))
        # instrument.set_current(new)

        global LAST_CURR
        LAST_CURR = float('%0.4g' % new)

    def start_button_clicked(self):
        self.set_initial_variables()
        self.ani = animation.FuncAnimation(
            fig1, animate, fargs=(True,), interval=INTERVAL)
        self.start_button['state'] = 'disabled'
        self.save_button['state'] = 'disabled'
        self.curr_checkbox['state'] = 'disabled'
        self.volt_checkbox['state'] = 'disabled'
        self.stop_button['state'] = 'normal'

    def stop_button_clicked(self):
        self.ani.event_source.stop()
        self.stop_button['state'] = 'disabled'
        self.start_button['state'] = 'normal'
        self.save_button['state'] = 'normal'
        self.curr_checkbox['state'] = 'normal'
        self.volt_checkbox['state'] = 'disabled'
        self.clear_variables()
        self.var_radio.set(1)
        self.OFF_mode_selected()
        terminate_current()
        set_analog_out(mag_channel, 0)

    def clear_variables(self):
        global CURR_TEMP
        global MM_VOL_TEMP
        global FIELD_TEMP
        global TIME_TEMP
        global LAST_CURR
        global RAMP_VEC
        global RAMP_INDEX
        global LAST_FIELD_VOLT
        global INTERVAL
        global RAMP_VEC_FIELD
        global RES_TEMP

        LAST_CURR = 0
        LAST_FIELD_VOLT = 0
        CURR_TEMP = CURRENT.copy()
        MM_VOL_TEMP = MM_VOLTAGE.copy()
        FIELD_TEMP = FIELD.copy()
        TIME_TEMP = TIME.copy()
        RES_TEMP = RESISTANCE.copy()

        CURRENT.clear()
        MM_VOLTAGE.clear()
        FIELD.clear()
        TIME.clear()
        RESISTANCE.clear()

        RAMP_VEC = np.arange(0, 1.0e-6, 100e-9)
        RAMP_VEC_FIELD = np.arange(0, 1, 0.1)
        RAMP_INDEX = 0

    def save_button_clicked(self):
        filename = tk.filedialog.asksaveasfilename(
            filetypes=[('csv file', '*.csv')], defaultextension='.csv')

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Applied Field[V]',
                            'Current[uA]', 'Multimeter Voltage[V]', 'Resistance[Ohms]'])
            for i in range(len(TIME_TEMP)):
                if (VOLT_FLAG == 0 and CURR_FLAG == 1):
                    writer.writerow(
                        [TIME_TEMP[i], FIELD_TEMP[i], CURR_TEMP[i], RES_TEMP[i]])
                elif (CURR_FLAG == 0):
                    writer.writerow([TIME_TEMP[i], FIELD_TEMP[i], RES_TEMP[i]])
                else:
                    writer.writerow(
                        [TIME_TEMP[i], FIELD_TEMP[i], CURR_TEMP[i], MM_VOL_TEMP[i], RES_TEMP[i]])
        csvfile.close()


if __name__ == "__main__":

    interface = Interface()

    interface.mainloop()
