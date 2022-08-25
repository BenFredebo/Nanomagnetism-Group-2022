# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 09:40:59 2022

@author: BRasmussen

ben.f.rasmussen@gmail.com

keithley 220 programmable current source interface
"""

import tkinter as tk
import keithley220 as k220
from tkinter import END
from tkinter import ttk

# correct port for device
k220port = 'GPIB1::12::INSTR'


# %% Checks for usb inputs and creates reource manager:

#   rm = pyvisa.ResourceManager('C:\Windows\System32\\visa64.dll')
#   reslist = rm.list_resources(query='?*')

# %%


# General instance of keithley class used within the interface:

instrument = k220.Keithley220(k220port)


class Interface(tk.Tk):
    '''
    Code to produce a fully interactible interface for the Keithley 220 current
    source. The master frame for Tkinter is called as a Tkinter object and 
    used as the object for this class. Much of the first code controls the 
    layout of the interface while the section on helper functions calls the
    Keithley220 python module directly. 

    '''

    def __init__(self):
        super().__init__()

        # configures base window
        self.title("Keithley 220 Programming Interface")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=2)
        self.grid_columnconfigure(5, weight=1)

        # frame for parameter input

        frame1 = tk.Frame(self, bd=5)
        frame1.grid(row=0, column=4, rowspan=8,
                    padx=5, pady=5, ipadx=5, ipady=5, sticky='n')
        frame1['relief'] = 'ridge'

        # trigger and terminate buttons:
        self.btn_trigger = tk.Button(
            self, text='  Trigger   ', height=4, width=8, bg="#DAF5D6", activeforeground='green')
        self.btn_trigger["command"] = self.trigger_button_clicked
        self.btn_trigger.grid(row=2, column=1, columnspan=1, padx=5)
        self.btn_terminate = tk.Button(
            self, text="Terminate", height=4, width=8, bg="#F5D6D6", activeforeground='red')
        self.btn_terminate["command"] = self.terminate_button_clicked
        self.btn_terminate['state'] = 'disabled'
        self.btn_terminate.grid(row=2, column=2, padx=5, pady=10)

        # write to memory location button:
        self.btn_memory = tk.Button(
            self, text='Write to Memory', bg="#e1e0e0", height=2, activeforeground='white')
        self.btn_memory["command"] = self.write_to_memory_clicked
        self.btn_memory.grid(row=5, column=5, columnspan=1, padx=5)

        # program control and polarity reversal buttons:
        self.btn_reverse = tk.Button(
            self, text='  Reverse \n  polarity   ', height=4, width=8, bg="#DAD6F5", activeforeground='white')
        self.btn_reverse["command"] = self.reverse_polarity_clicked
        self.btn_reverse.grid(row=2, column=3, columnspan=1)
        self.btn_reverse['state'] = 'normal'

        self.btn_program_on = tk.Button(
            self, text='ON', height=1, width=2, bg="#DAF5D6", activeforeground='green')
        self.btn_program_on['command'] = self.program_on_helper
        self.btn_program_on.grid(row=5, column=1, padx=(0, 42))

        self.btn_program_off = tk.Button(
            self, text='OFF', height=1, width=2, bg="#F5D6D6", activeforeground='red')
        self.btn_program_off['command'] = self.program_off_helper
        self.btn_program_off.grid(row=5, column=1, padx=(40, 0))
        self.btn_program_off['state'] = 'disabled'

        self.program_label = tk.Label(self, text='Program Control Buttons')
        self.program_label.grid(row=5, column=2, padx=(10, 0))

        # Move to memory button and input:
        self.btn_move_to = tk.Button(
            self, text='*', height=20, width=60, bitmap='info', bg="#e1e0e0", activeforeground='red')

        self.btn_move_to["command"] = self.move_to_clicked
        self.btn_move_to.grid(row=3, column=1, pady=5)

        # display parameter entries:
        self.current_label = tk.Label(frame1, text='Current (A)')
        self.current_label.grid(row=2, column=4)
        self.current_entry = tk.Entry(frame1)
        self.current_entry.insert(-1, '0.0e-9')
        self.current_entry.grid(row=3, column=4)

        self.vlimit_label = tk.Label(frame1, text='Voltage Limit (V)')
        self.vlimit_label.grid(row=4, column=4)
        self.vlimit_entry = tk.Entry(frame1)
        self.vlimit_entry.insert(-1, '1')
        self.vlimit_entry.grid(row=5, column=4)

        self.dwell_time_label = tk.Label(frame1, text='Dwell Time (s)')
        self.dwell_time_label.grid(row=6, column=4)
        self.dwell_time_entry = tk.Entry(frame1)
        self.dwell_time_entry.insert(-1, '3e-3')
        self.dwell_time_entry.grid(row=7, column=4)

        self.buffer_label = tk.Label(frame1, text='Memory Location')
        self.buffer_label.grid(row=8, column=4)
        self.buffer_entry = tk.Entry(frame1)
        self.buffer_entry.insert(-1, '001')
        self.buffer_entry.grid(row=9, column=4)

        self.move_to_label = tk.Label(self, text='Location to Move to:')
        self.move_to_label.grid(row=3, column=2, padx=(15, 0))
        self.move_to_entry = tk.Entry(self, width=7)
        self.move_to_entry.insert(-1, '001')
        self.move_to_entry.grid(row=3, column=3)

        # dropdown for program modes:

        self.program_mode_label = tk.Label(self, text='Program Mode Dropdown')
        self.program_mode_label.grid(row=4, column=2, padx=(15, 0))
        mode = tk.StringVar(self)
        mode.set("step")  # default value
        self.program_mode = tk.OptionMenu(
            self, mode, "step", "cont.", "single", command=self.program_mode_clicked)
        self.program_mode.config(height=1, width=4, bg="#e1e0e0")
        self.program_mode.grid(row=4, column=1)

        # trying to add customizable +/- x A button:

        # button

        self.btn_add_current = tk.Button(
            self, text='+', height=2, width=2, bg="#DAF5D6", activeforeground='cyan')
        self.btn_add_current.grid(row=2, column=5, padx=(0, 70))
        self.btn_add_current['command'] = self.add_value_to_current

        self.add_value = tk.StringVar(self)
        self.add_value.set('1 \u03BCA')  # default value
        self.step_size_add = tk.OptionMenu(
            self, self.add_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_add.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_add.grid(row=2, column=5, padx=(40, 10))

        self.btn_subtract_current = tk.Button(
            self, text='-', height=2, width=2, bg="#F5D6D6", activeforeground='cyan')
        self.btn_subtract_current.grid(
            row=3, column=5, padx=(0, 70))
        self.btn_subtract_current['command'] = self.subtract_value_from_current

        self.subtract_value = tk.StringVar(self)
        self.subtract_value.set('1 \u03BCA')  # default value
        self.step_size_subtract = tk.OptionMenu(
            self, self.subtract_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_subtract.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_subtract.grid(row=3, column=5, padx=(40, 10))

        # frame to add in a current pulse generator control

        # adds tabs for different waves

        tabsystem = ttk.Notebook(self)

        frame2 = tk.Frame(tabsystem, bd=4, height=75, width=305)
        frame2.grid(row=6, column=2, columnspan=4,
                    pady=25, padx=(25, 0), sticky='w')
        frame2['relief'] = 'sunken'

        tabsystem.add(frame2, text='Pulse')
        tabsystem.grid(row=6, column=2, pady=15, columnspan=4)

        self.pulse_gen_label = tk.Label(
            frame2, text='Current Pulse Generator Control:', font=('Arial', 9, 'underline'))
        self.pulse_gen_label.grid(row=1, column=1, padx=(0, 80), pady=10)

        self.pulse_length_entry = tk.Entry(frame2, width=7)
        self.pulse_length_entry.insert(-1, '1.0')
        self.pulse_length_entry.grid(sticky='w', padx=(30, 0))

        self.pulse_length_label = tk.Label(
            frame2, text='Length of Current Pulse (s)')
        self.pulse_length_label.grid(row=2, column=1, padx=(0, 60))

        self.pause_length_entry = tk.Entry(frame2, width=7)
        self.pause_length_entry.insert(-1, '1.0')
        self.pause_length_entry.grid(sticky='w', padx=(30, 0), pady=(10, 5))

        self.pause_length_label = tk.Label(
            frame2, text='Length of Pause Between Pulses \n (repeater mode) (s)')
        self.pause_length_label.grid(
            row=3, column=1, padx=(0, 60), pady=(0, 0))

        self.pulse_height_entry = tk.Entry(frame2, width=7)
        self.pulse_height_entry.insert(-1, '0.0e-9')
        self.pulse_height_entry.grid(sticky='w', padx=(30, 0), pady=5)

        self.pulse_height_label = tk.Label(
            frame2, text='Amplitude of Current Pulse (A)')
        self.pulse_height_label.grid(row=4, column=1, padx=(0, 60), pady=5)

        self.pulse_mode_label = tk.Label(
            frame2, text='Flavour of pulse generated')

        self.pulse_mode_label.grid(row=5, column=1, padx=(0, 60))

        self.pulse_mode = tk.StringVar(self)
        self.pulse_mode.set('single')  # default value
        self.pulse_mode_menu = tk.OptionMenu(
            frame2, self.pulse_mode, "single", "repeater")
        self.pulse_mode_menu.config(
            height=1, width=4, bg="#e1e0e0")
        self.pulse_mode_menu.grid(row=5, padx=(20, 0))

        self.btn_set = tk.Button(
            frame2, text='Set', height=2, width=4, bg="#DAD6F5", activeforeground='white')
        self.btn_set["command"] = self.pulse_generator
        self.btn_set.grid(row=2, column=2, padx=(0, 40), sticky='w')
        self.btn_set['state'] = 'normal'

        self.btn_send = tk.Button(
            frame2, text='Send', height=2, width=4, bg="#DAF5D6", activeforeground='white')
        self.btn_send["command"] = self.send_pulse_helper
        self.btn_send.grid(row=3, column=2, padx=(0, 40), sticky='w')
        self.btn_send['state'] = 'normal'

        self.btn_stop = tk.Button(
            frame2, text='Stop', height=2, width=4, bg="#F5D6D6", activeforeground='white')
        self.btn_stop.grid(row=4, column=2, padx=(0, 40), sticky='w')
        self.btn_stop['command'] = self.program_off_helper
        
#        self.btn_operate = tk.Button(
#            frame2, text='Operate', height=2, width=6, bg="#DAF5D6", activeforeground='cyan')
#        self.btn_operate.grid(row=5, column=2, padx=(0, 40), sticky='w')
#        self.btn_operate['command'] = self.operate_current

        # sine wave tab:

        frame3 = tk.Frame(tabsystem, bd=4, height=75, width=305)
        frame3.grid(row=6, column=2, columnspan=4,
                    pady=25, padx=(25, 0), sticky='w')
        frame3['relief'] = 'sunken'
        tabsystem.add(frame3, text='Sine Wave')
        tabsystem.grid(row=6, column=2, pady=15, columnspan=4)

        self.sine_gen_label = tk.Label(
            frame3, text='Sine Wave Generator Control:', font=('Arial', 9, 'underline'))
        self.sine_gen_label.grid(row=1, column=1, padx=(0, 80), pady=10)

        self.sine_period_entry = tk.Entry(frame3, width=7)
        self.sine_period_entry.insert(-1, '1.0')
        self.sine_period_entry.grid(sticky='w', padx=(30, 0))

        self.sine_period_label = tk.Label(
            frame3, text='Period of Sine Wave (s)')
        self.sine_period_label.grid(row=2, column=1, padx=(0, 60))

        self.sine_height_entry = tk.Entry(frame3, width=7)
        self.sine_height_entry.insert(-1, '0.0e-9')
        self.sine_height_entry.grid(sticky='w', padx=(30, 0), pady=(10, 5))

        self.sine_height_label = tk.Label(
            frame3, text='Amplitude of Sine Wave (A)')
        self.sine_height_label.grid(
            row=3, column=1, padx=(0, 60), pady=(0, 0))

        self.number_samples_entry = tk.Entry(frame3, width=7)
        self.number_samples_entry.insert(-1, '20')
        self.number_samples_entry.grid(sticky='w', padx=(30, 0), pady=5)

        self.number_samples_label = tk.Label(
            frame3, text='Number of Memory Locations (1-100)')
        self.number_samples_label.grid(row=4, column=1, padx=(30, 40), pady=5)

        self.btn_set = tk.Button(
            frame3, text='Set \n (wait)', height=2, width=4, bg="#DAD6F5", activeforeground='white')
        self.btn_set["command"] = self.sine_generator
        self.btn_set.grid(row=2, column=2, padx=(0, 40), sticky='w')
        self.btn_set['state'] = 'normal'

        self.btn_send = tk.Button(
            frame3, text='Start', height=2, width=4, bg="#DAF5D6", activeforeground='white')
        self.btn_send["command"] = self.send_sine_helper
        self.btn_send.grid(row=3, column=2, padx=(0, 40), sticky='w')
        self.btn_send['state'] = 'normal'

        self.btn_stop = tk.Button(
            frame3, text='Stop', height=2, width=4, bg="#F5D6D6", activeforeground='white')
        self.btn_stop.grid(row=4, column=2, padx=(0, 40), sticky='w')
        self.btn_stop['command'] = self.program_off_helper
        # TODO: self.btn_stop["command"]=self....
        # button states

        # Ramp wave generator tab:

        frame4 = tk.Frame(tabsystem, bd=4, height=75, width=305)
        frame4.grid(row=6, column=2, columnspan=4,
                    pady=25, padx=(25, 0), sticky='w')
        frame4['relief'] = 'sunken'
        tabsystem.add(frame4, text='Ramp Wave')
        tabsystem.grid(row=6, column=2, pady=15, columnspan=4)

        self.ramp_gen_label = tk.Label(
            frame4, text='Ramp Wave Generator Control:', font=('Arial', 9, 'underline'))
        self.ramp_gen_label.grid(row=1, column=1, padx=(0, 80), pady=10)

        self.ramp_period_entry = tk.Entry(frame4, width=7)
        self.ramp_period_entry.insert(-1, '1.0')
        self.ramp_period_entry.grid(sticky='w', padx=(30, 0))

        self.ramp_period_label = tk.Label(
            frame4, text='Period of Ramp Wave (s)')
        self.ramp_period_label.grid(row=2, column=1, padx=(0, 60))

        self.ramp_height_entry = tk.Entry(frame4, width=7)
        self.ramp_height_entry.insert(-1, '0.0e-9')
        self.ramp_height_entry.grid(sticky='w', padx=(30, 0), pady=(10, 5))

        self.ramp_height_label = tk.Label(
            frame4, text='Amplitude of Ramp Wave (A)')
        self.ramp_height_label.grid(
            row=3, column=1, padx=(0, 60), pady=(0, 0))

        self.number_samples_entry2 = tk.Entry(frame4, width=7)
        self.number_samples_entry2.insert(-1, '20')
        self.number_samples_entry2.grid(sticky='w', padx=(30, 0), pady=5)

        self.number_samples_label = tk.Label(
            frame4, text='Number of Memory Locations (1-100)')
        self.number_samples_label.grid(row=4, column=1, padx=(30, 40), pady=5)

        self.btn_set = tk.Button(
            frame4, text='Set \n (wait)', height=2, width=4, bg="#DAD6F5", activeforeground='white')
        self.btn_set["command"] = self.ramp_generator
        self.btn_set.grid(row=2, column=2, padx=(0, 40), sticky='w')
        self.btn_set['state'] = 'normal'

        self.btn_send = tk.Button(
            frame4, text='Start', height=2, width=4, bg="#DAF5D6", activeforeground='white')
        self.btn_send["command"] = self.send_sine_helper
        self.btn_send.grid(row=3, column=2, padx=(0, 40), sticky='w')
        self.btn_send['state'] = 'normal'

        self.btn_stop = tk.Button(
            frame4, text='Stop', height=2, width=4, bg="#F5D6D6", activeforeground='white')
        self.btn_stop.grid(row=4, column=2, padx=(0, 40), sticky='w')
        self.btn_stop['command'] = self.program_off_helper
        

        # reset button for all memory and default controls:

        self.btn_reset = tk.Button(
            self, text='Reset \n (wait)', height=2, width=4, bg="#F5D6D6", activeforeground='cyan')
        self.btn_reset.grid(row=6, column=1)
        self.btn_reset['command'] = self.reset_all_helper
        

        # TODO: add kill switch to running program generators

        # TODO:
        # TODO: make it with bind function or updating prior to trigger

    # %% Helper functions:
#    def operate_current(self):
#        instrument.initialize_current()
    
    def trigger_button_clicked(self):
        '''
        Used to begin current output for the keithley. Controlled by the 
        trigger button. Disables the terminate button

        '''
        self.current_entry_pressed()
        self.vlimit_entry_pressed()
        self.dwell_time_entry_pressed()
        self.btn_trigger['state'] = 'disabled'
        self.btn_terminate['state'] = 'active'
        instrument.initialize_current()

    def terminate_button_clicked(self):
        '''
        Used to end current output for the keithley. Controlled by the 
        terminate button. Disables trigger button. 

        '''
        self.btn_trigger['state'] = 'active'
        self.btn_terminate['state'] = 'disabled'
        instrument.terminate_current()

    def reverse_polarity_clicked(self):
        B = float(self.move_to_entry.get())
        instrument.reverse_polarity(B)

    def move_to_pressed(self):
        L = float(self.move_to_entry.get())
        instrument.moveto_memory(L)

    def move_to_clicked(self):
        self.move_to_pressed()

    def current_entry_pressed(self):
        B = float(self.buffer_entry.get())
        current = float(self.current_entry.get())
        instrument.set_current(current, B)

    def vlimit_entry_pressed(self):
        B = float(self.buffer_entry.get())
        vlimit = float(self.vlimit_entry.get())
        instrument.set_vlimit(vlimit, B)

    def dwell_time_entry_pressed(self):
        B = float(self.buffer_entry.get())
        dwell_time = float(self.dwell_time_entry.get())
        instrument.set_dwell_time(dwell_time, B)

    def write_to_memory_clicked(self):
        self.current_entry_pressed()
        self.vlimit_entry_pressed()
        self.dwell_time_entry_pressed()

    def program_mode_clicked(self, mode):

        if mode == "cont.":
            mode2 = 'continuous'
            instrument.set_program_mode(mode2)
        else:
            instrument.set_program_mode(mode)

    def program_on_helper(self):
        self.btn_program_on['state'] = 'disabled'
        self.btn_program_off['state'] = 'active'
       # self.btn_stop['state'] = 'active'
       # self.btn_send['state'] = 'disabled'
        instrument.trigger()

    def program_off_helper(self):
        self.btn_program_on['state'] = 'active'
        self.btn_program_off['state'] = 'disabled'
        #self.btn_stop['state'] = 'active'
        #self.btn_send['state'] = 'disabled'
        instrument.terminate_current()
        instrument.kill()

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
        instrument.set_current(new)

    def subtract_value_from_current(self):
        step_size = self.subtract_value.get()
        old = float(self.current_entry.get())

        # TODO: make it so the addition/subtraction occurs at desired location

        #location = float(self.buffer_entry.get())
        #data = instrument.get_data(location)
        #old = data[0]

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
        instrument.set_current(new)

    def pulse_generator(self):

        amplitude = float(self.pulse_height_entry.get())
        pulse = float(self.pulse_length_entry.get())
        pause = float(self.pause_length_entry.get())
        mode = (self.pulse_mode.get())

        if mode == 'single':
            PM = 'single'
            instrument.make_square_wave(amplitude, pause, pulse, PM)
            instrument.kill()

        elif mode == 'repeater':
            PM = 'continuous'
            instrument.make_square_wave(amplitude, pause, pulse, PM)
            instrument.kill()

    def send_pulse_helper(self):
        mode = self.pulse_mode.get()
        instrument.initialize_current()

        if mode == 'single':
            instrument.trigger()

        elif mode == 'repeater':
            self.btn_program_on['state'] = 'disabled'
            self.btn_program_off['state'] = 'active'
            instrument.trigger()

    def sine_generator(self):
        period = float(self.sine_period_entry.get())
        amplitude = float(self.sine_height_entry.get())
        points = float(self.number_samples_entry.get())

        instrument.make_sine_wave(amplitude, period, points)

    def send_sine_helper(self):
        instrument.set_program_mode('continuous')
        self.btn_program_on['state'] = 'disabled'
        self.btn_program_off['state'] = 'active'
        instrument.trigger()

    def ramp_generator(self):
        period = float(self.ramp_period_entry.get())
        I_max = float(self.ramp_height_entry.get())
        points = float(self.number_samples_entry2.get())

        instrument.make_ramp_wave(I_max, period, points)

    def reset_all_helper(self):
        instrument.reset_all_memory()


# %%
if __name__ == "__main__":

    interface220 = Interface()

    interface220.mainloop()

