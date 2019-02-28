try:  # python 3: default
    import tkinter as tk
    from tkinter import filedialog
except ImportError:  # python 2
    import Tkinter as tk
    import tkFileDialog as filedialog

import os, graphviz

WIDTH = 250
HEIGHT = 75
DIMENSIONS = str(WIDTH) + "x" + str(HEIGHT)
CWD = os.getcwd()


class GrapherGUI():
    """A basic GUI wrapper for the Turing Machine Grapher"""

    def __init__(self, master):
        self.main = master
        self.main.title("Turing Machine Grapher")
        self.main.geometry(DIMENSIONS)

        ### RIGHT FRAME: EDITOR
        self.buttonGraph = tk.Button(self.main, width=10, text="Graph", command=self.graphTM)
        self.buttonGraph.pack(pady=5, expand=1)

    def graphTM(self):
        """Get a TM specification file from the user, and graph it"""
        tmFileName = filedialog.askopenfilename(
            initialdir=CWD, title="Select TM File", filetypes=[("TM files", "*.tm"), ("all", "*.*")])
        if tmFileName == '':
            return
        tmgraphdict = GrapherGUI.make_state_dict(tmFileName)
        file = os.path.basename(tmFileName)[:-3]
        GrapherGUI.generate_graph(tmgraphdict, file)

    @staticmethod
    def generate_graph(dict, file="turing_machine"):
        """Take the dictionary from make_state_dict(), turn it into a Digraph object and render"""
        d = dict
        g = graphviz.Digraph(graph_attr={"dpi": "300"})
        for key in d:
            state = str(key[0])
            newstate = str(key[1])
            if newstate == '-1':
                newstate = 'Accept'
            if newstate == '-2':
                newstate = 'Reject'
            if newstate == '-3':
                newstate = 'Halt'
            val = d[key]
            sym = str(val[0])
            newsym = str(val[1])
            direction = val[2]
            comma = ', ' if newsym else ''
            g.edge(state, newstate, label="< " + sym + " &#8594; " + newsym + comma + direction + ">")  #use HTML labels
        g.render(file, directory='img', format="png", cleanup=True, view=True)

    @staticmethod
    def make_state_dict(filename):
        """Turn a configuration file into a state-state dictionary. Used in generating images of the TM.
        Returns:
        a dictionary with key-value pairs (q,q'):(C,C',D,X) where q,q' are states, C, C' are the lists of input and output symbols, D is direction, and X is a flag for coloring
        """
        f = open(filename, 'r')
        d = {}
        for line in f:
            seq = line.split()
            if (len(seq) > 0) and (seq[0][0] != '#'):
                state = int(seq[0])
                sym = seq[1]
                if sym == 'B':
                    sym = "&#9633;"  # a square character
                newstate = int(seq[2])
                newsym = seq[3]
                direction = seq[4]
                if newsym == 'B':
                    newsym = "&#9633;"
                if newsym == sym:
                    newsym = ''
                k = (state, newstate)
                if k in d:
                    cur = tuple(d[k])
                    if (cur[0] != sym):
                        sym = cur[0] + ', ' + sym
                    if not (cur[1] == newsym):
                        newsym = cur[1] + ', ' + newsym
                    if not (cur[2] == direction):
                        direction = cur[2] + ', ' + direction
                d[k] = (sym, newsym, direction)
        f.close()
        return d


root = tk.Tk()
try:  # do a fancy icon if available
    img = tk.Image("photo", file="favicon.gif")
    root.call('wm', 'iconphoto', root._w, img)
except Exception:
    pass
grapher_gui = GrapherGUI(root)
root.mainloop()
