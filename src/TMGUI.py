try:  # python 3: default
    import tkinter as tk
    from tkinter import ttk, scrolledtext, filedialog
except ImportError:  # python 2
    import Tkinter as tk
    import ttk, ScrolledText as scrolledtext, tkFileDialog as filedialog

from turing_machines import *
import os

WIDTH = 1280
HEIGHT = 690
DIMENSIONS = str(WIDTH) + "x" + str(HEIGHT) + "+10+10"
CWD = os.getcwd()


class TMGUI:
    """A GUI for simulating Turing Machines"""

    def __init__(self, master):
        self.tm = None
        self._jobs = []

        self.main = master
        self.main.title("Turing Machine Simulator")
        self.main.geometry(DIMENSIONS)

        ### RIGHT FRAME: EDITOR
        self.frameEditor = tk.Frame(self.main)
        self.labelEditor = tk.Label(self.frameEditor, text="Editor")
        self.labelEditor.grid(row=0, column=1)
        self.textEditor = scrolledtext.ScrolledText(self.frameEditor, height=35, width=40, wrap=tk.WORD)
        self.textEditor.grid(row=1, column=0, columnspan=3, pady=5, sticky='news')

        self.buttonSave = tk.Button(self.frameEditor, width=10, relief='groove', text="Save", command=self.saveTM)
        self.buttonSave.grid(row=2, column=2, padx=20, pady=5)

        self.buttonLoad = tk.Button(self.frameEditor, width=10, relief='groove', text="Load", command=self.loadTM)
        self.buttonLoad.grid(row=2, column=0, padx=20, pady=5)

        self.frameEditor.grid(row=0, column=3, padx=15, pady=10, sticky='news')

        default_resize(self.frameEditor)

        ### LEFT FRAME: Simulator
        self.frameSim = tk.Frame(self.main)
        self.labelSim = tk.Label(self.frameSim, text="Simulator")
        self.labelSim.grid(row=0, column=0, columnspan=3)

        self.frameInput = tk.Frame(self.frameSim)
        tk.Label(self.frameInput, text="Tape Input: ").pack(side='left')
        self.tape_input = tk.StringVar()
        self.tape_input.trace("w", self.setTape)
        self.textTapeInput = tk.Entry(self.frameInput, textvariable=self.tape_input, width=25)
        self.textTapeInput.pack(side='right')
        self.frameInput.grid(row=1, column=0, columnspan=3, pady=10)

        self.tabsSim = ttk.Notebook(self.frameSim)
        self.frameTape = tk.Frame(self.tabsSim)
        self.frameText = tk.Frame(self.tabsSim)
        self.tabsSim.add(self.frameTape, text='  Tape  ')
        self.tabsSim.add(self.frameText, text='  Text  ')
        self.tabsSim.grid(row=2, column=0, columnspan=3)

        # Check boxes
        self.frameCheck = tk.Frame(self.frameSim)
        self.bidirectional = tk.BooleanVar()
        self.checkbox2Way = tk.Checkbutton(
            self.frameCheck, text="Bidirectional", var=self.bidirectional, onvalue=True, offvalue=False)
        self.checkbox2Way.select()
        self.checkbox2Way.grid(row=0, sticky='w')
        self.two_tape = tk.BooleanVar()
        self.checkbox2Tape = tk.Checkbutton(
            self.frameCheck, text="Two Tape", var=self.two_tape, onvalue=True, offvalue=False)
        self.checkbox2Tape.grid(row=1, sticky='w')
        self.two_tape.trace("w", self.setTwoTape)
        self.bidirectional.trace("w", self.setBidirectional)
        self.frameCheck.grid(row=3, column=2)

        # Controls
        self.frameRun = tk.Frame(self.frameSim)
        self.buttonRun = tk.Button(self.frameRun, width=10, relief='groove', text="Run", command=self.runTM)
        self.buttonRun.grid(row=0, column=0, pady=5, padx=5)
        self.buttonStop = tk.Button(self.frameRun, width=10, relief='groove', text="Stop", command=self.stopTM)
        self.buttonStop.grid(row=0, column=1, pady=5, padx=5)
        self.buttonReset = tk.Button(self.frameRun, width=10, relief='groove', text="Reset", command=self.resetTM)
        self.buttonReset.grid(row=1, column=1, pady=5, padx=5)
        self.frameDelay = tk.Frame(self.frameRun)
        tk.Label(self.frameDelay, text="Delay (s)").pack(side='left', padx=3)
        self.textDelay = tk.Entry(self.frameDelay, relief='groove', width=4)
        self.textDelay.insert(0, "0.1")
        self.textDelay.pack(side='right')
        self.frameDelay.grid(row=1, column=0, pady=5, padx=5)
        self.frameRun.grid(row=3, column=0)

        self.frameStep = tk.Frame(self.frameSim)
        self.buttonStep = tk.Button(self.frameStep, width=10, relief='groove', text="Step", command=self.stepTM)
        self.buttonStep.grid(row=0, pady=5)
        self.buttonStepBack = tk.Button(
            self.frameStep, width=10, relief='groove', text="Step Back", command=self.stepBackTM)
        self.buttonStepBack.grid(row=1, pady=5)
        self.frameStep.grid(row=3, column=1)

        # Tape frame
        self.canvasSimOut = tk.Canvas(self.frameTape, bg="#c4c4c4", width=852, height=500)
        self.drawFirstTape()
        self.canvasSimOut.pack(expand=1, fill='both')

        # Text Frame
        self.textSimOut = scrolledtext.ScrolledText(self.frameText, state='disabled', height=10, width=55, wrap=tk.WORD)
        self.textSimOut.pack(expand=1, fill='both')

        self.frameSim.grid(row=0, column=0, rowspan=10, padx=15, pady=10, sticky="news")

        default_resize(self.frameSim)
        self.frameSim.grid_rowconfigure(0, weight=0)
        self.frameSim.grid_rowconfigure(1, weight=0)
        ### Seperate the two sides
        ttk.Separator(master, orient='vertical').grid(column=1, row=0, rowspan=21, sticky='nsew', padx=5)

    # Editor Buttons
    def loadTM(self):
        """Load a TM from a specification file into the editor and simulator"""
        tmFileName = filedialog.askopenfilename(
            initialdir=CWD, title="Select TM File", filetypes=[("TM files", "*.tm"), ("all", "*.*")])
        if tmFileName == '':
            return
        tmFile = open(tmFileName, "r")
        self.textEditor.delete('1.0', 'end')
        self.textEditor.insert(0.0, tmFile.read())
        tmFile.close()
        self.tm = None
        if self.two_tape.get():
            self.tm = two_tape_TM(tmFileName, input=self.textTapeInput.get())
        else:
            self.tm = turing_machine(tmFileName, input=self.textTapeInput.get(), bidirectional=self.bidirectional.get())
        self.resetTM()

    def saveTM(self):
        """Save a TM to a specification file from the editor and load it into the simulator"""
        tmFileName = filedialog.asksaveasfilename(
            initialdir=CWD,
            title="Select save directory",
            filetypes=[("TM files", "*.tm"), ("all", "*.*")],
            defaultextension=[("TM files", "*.tm"), ("all", "*.*")])
        if tmFileName == '':
            return
        tmFile = open(tmFileName, "w")
        tmFile.write(self.textEditor.get(0.0, 'end'))
        tmFile.close()
        self.tm = None
        if self.two_tape.get():
            self.tm = two_tape_TM(tmFileName, input=self.textTapeInput.get())
        else:
            self.tm = turing_machine(tmFileName, input=self.textTapeInput.get(), bidirectional=self.bidirectional.get())
        self.resetTM()

    # Simulator Buttons
    def runTM(self):
        """Run the TM continuouslyself.
        Completely run a machine and enqueue all of the updates to be displayed (with optional delay)
        """
        if self.tm != None:
            self._jobs = []  # store the "after" IDS so we can cancel it
            try:
                delay = float(self.textDelay.get())
            except ValueError:
                delay = 0.1  # a reasonable default value
                self.textDelay.delete(0, "end")
                self.textDelay.insert(0, "0.1")
            if delay == 0:  # don't bother with the waiting at all then
                for config in self.tm.run_tm_iter():
                    self.writeOutText(config)
                    c = config
                self.drawOutMachine(c)
            else:
                delay *= 1000  # convert to miliseconds
                delay = int(delay)
                count = 0
                for config in self.tm.run_tm_iter():
                    count += 1
                    step = self.tm.step
                    self._jobs.append(self.main.after(delay * count, self.drawOutMachine, config, step))
                    self._jobs.append(self.main.after(delay * count, self.writeOutText, config, step))

    def stepTM(self):
        """Step the TM forward once"""
        if self.tm != None:
            config = self.tm.next_config()
            self.drawOutMachine(config)
            self.writeOutText(config)

    def stepBackTM(self):
        """Step the TM backward once"""
        if self.tm != None:
            config = self.tm.previous_config()
            self.drawOutMachine(config)
            self.writeOutText("Stepping Back\n")
            self.writeOutText(config)

    def resetTM(self):
        """Reset the TM to an unrun state"""
        self.lastRunStep = 0
        self.stopTM()
        if self.bidirectional.get():
            self.drawFirstTape()
        if self.two_tape.get():
            self.drawSecondTape()
        self.drawOutMachine(self.tm.config)

        self.textSimOut.config(state='normal')
        self.textSimOut.delete(1.0, 'end')
        self.writeOutText(self.tm.config)
        self.textSimOut.config(state='disabled')

    def stopTM(self):
        """Stop the continuous run of the TM
        Cancels all tk.after()-scheduled updates and rewinds underlying the machine to the last displayed state.
        """
        if self.tm != None:
            for job in self._jobs:
                self.main.after_cancel(job)
            self.tm.go_back_to_step(self.lastRunStep)
        self._jobs = []

    # Callbacks
    def setTape(self, *args):
        """Callback for when tape input is changed.
        Inform the TM and reset the run.
        """
        if self.tm != None:
            self.tm.set_input_string(self.textTapeInput.get())
            self.resetTM()

    def setBidirectional(self, *args):
        """Callback for when the bidirectional option is changed.
        Inform the TM, reset the run, and disable the other checkbox
        """
        if self.tm != None:
            self.tm.set_bidirectional(self.bidirectional.get())
            self.resetTM()
        else:
            if self.bidirectional.get():
                self.drawFirstTape()
            else:
                self.canvasSimOut.delete('left')

        if (self.bidirectional.get()):
            self.checkbox2Tape.configure(state='normal')
        else:
            self.checkbox2Tape.configure(state='disabled')

    def setTwoTape(self, *args):
        """Callback for when the two tape option is changed.
        Inform the TM, reset the run, and disable the other checkbox
        """
        if self.tm != None:
            file = self.tm.file
            self.tm = None
            if self.two_tape.get():
                self.tm = two_tape_TM(file, input=self.textTapeInput.get())
            else:
                self.tm = turing_machine(file, input=self.textTapeInput.get(), bidirectional=self.bidirectional.get())
            self.resetTM()
        else:
            if self.two_tape.get():
                self.drawSecondTape()
            else:
                self.canvasSimOut.delete('twotape')
        if (not self.two_tape.get()):
            self.checkbox2Way.configure(state='normal')
        else:
            self.checkbox2Way.configure(state='disabled')

    # Drawing functions
    def drawFirstTape(self):
        """Helper function to draw the first tape on the canvas"""
        starty = 150
        for i in range(17):
            if i < 8:
                self.canvasSimOut.create_rectangle(50 * i + 2, starty, 50 * i + 52, starty + 50, fill="", tag="left")
            elif i > 8:
                self.canvasSimOut.create_rectangle(50 * i + 2, starty, 50 * i + 52, starty + 50, fill="")
        # draw highlighted square last to make sure sides are properly colored
        i = 8
        self.canvasSimOut.create_rectangle(50 * i + 2, starty, 50 * i + 52, starty + 50, fill="white", outline="red")

    def drawSecondTape(self):
        """Helper function to draw the second tape on the canvas"""
        starty = 300
        for i in range(17):
            if i != 8:
                self.canvasSimOut.create_rectangle(50 * i + 2, starty, 50 * i + 52, starty + 50, fill="", tag="twotape")
        # draw highlighted square last to make sure sides are properly colored
        i = 8
        self.canvasSimOut.create_rectangle(
            50 * i + 2, starty, 50 * i + 52, starty + 50, fill="white", outline="red", tag="twotape")

    def drawOutMachine(self, config, step=None):
        """Draw out the given configuration of the machine on the canvas."""
        if step == None:
            step = self.tm.step
        self.canvasSimOut.delete('text')
        state_text = "State: "
        state = config[4]
        if state < 0:
            if state == -1:
                state_text += 'Accept'
            elif state == -2:
                state_text += 'Reject'
            else:
                state_text += 'Halt'
        else:
            state_text += str(state)

        self.canvasSimOut.create_text(125, 100, text=state_text, font="Times 20", tag='text')
        self.canvasSimOut.create_text(725, 100, text="Step: " + str(step), font="Times 20", tag='text')
        starty = 150
        if not self.two_tape.get():
            self.canvasSimOut.delete('twotape')
            tape = config[0]
            position = config[3] - 8
            if not self.bidirectional.get():
                self.canvasSimOut.delete('left')
                for i in range(8):
                    if (position + i) >= 0:
                        self.canvasSimOut.create_rectangle(
                            50 * i + 2, starty, 50 * i + 52, starty + 50, fill="", tag='left')
                # draw highlighted square last to make sure sides are properly colored
                i = 8
                self.canvasSimOut.create_rectangle(
                    50 * i + 2, starty, 50 * i + 52, starty + 50, fill="white", outline="red")
            for j in range(17):
                if (position + j) < 0 or (position + j) >= 20000:
                    continue
                text = tape[position + j] if tape[position + j] != " " else ""
                self.canvasSimOut.create_text(50 * j + 27, starty + 25, text=text, font="Times 20", tag='text')
        else:
            tape1 = config[0][0]
            tape2 = config[0][1]
            position1 = config[3][0] - 8
            position2 = config[3][1] - 8
            for j in range(17):
                if (position1 + j) < 20000:
                    text1 = tape1[position1 + j] if tape1[position1 + j] != " " else ""
                    self.canvasSimOut.create_text(50 * j + 27, starty + 25, text=text1, font="Times 20", tag='text')
                if (position2 + j) < 20000:
                    text2 = tape2[position2 + j] if tape2[position2 + j] != " " else ""
                    self.canvasSimOut.create_text(50 * j + 27, starty + 175, text=text2, font="Times 20", tag='text')

    def writeOutText(self, config, step=None):
        """Write out the given configuration of the machine in the text output."""
        if step == None:
            step = self.tm.step
        self.lastRunStep = step
        self.textSimOut.config(state='normal')
        if (type(config) != str):
            self.textSimOut.insert('end', "Step: " + str(step) + '\n')
            self.textSimOut.insert('end', self.tm.format_config(config))
            if config[4] < 0:
                if config[4] == -1:
                    result = 'Accept'
                elif config[4] == -2:
                    result = 'Reject'
                else:
                    result = 'Halt'
                self.textSimOut.insert('end', result + '\n')
                self.textSimOut.insert('end', str(step) + ' steps' + '\n')
                tape = ''
                if not self.two_tape.get():
                    for j in range(config[1], config[2] + 1):
                        tape += config[0][j]
                    self.textSimOut.insert('end', tape + '\n')
                else:
                    for j in range(config[1][0], config[2][0] + 1):
                        tape += config[0][0][j]
                    self.textSimOut.insert('end', tape + '\n')
                    tape = ''
                    for j in range(config[1][1], config[2][1] + 1):
                        tape += config[0][1][j]
                    self.textSimOut.insert('end', tape + '\n')

        else:
            self.textSimOut.insert('end', config)
        self.textSimOut.config(state='disabled')
        self.textSimOut.yview(tk.END)


def default_resize(frame):
    """When given a frame, sets all the row and column weights in the grid to 1.
    This means the frame resizes evenly with the window.
    """
    (rows, columns) = frame.grid_size()
    for i in range(rows):
        frame.grid_rowconfigure(i, weight=1)
    for i in range(columns):
        frame.grid_columnconfigure(i, weight=1)


root = tk.Tk()
try:  # do a fancy icon if available
    img = tk.Image("photo", file="favicon.gif")
    root.call('wm', 'iconphoto', root._w, img)
except Exception:
    pass
tm_gui = TMGUI(root)
root.minsize(width=WIDTH, height=HEIGHT)
default_resize(root)
root.grid_columnconfigure(2, weight=2)
root.mainloop()
