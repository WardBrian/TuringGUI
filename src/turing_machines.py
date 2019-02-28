MAX_STEPS = 200000  # constant for how long to run before giving up


class turing_machine:
    """This class serves as an object-oriented version of Howard Struabing's Turing Machine Simulator.
    Construct an instance with the name of a configuration file to create a turing machine
    """

    def __init__(self, configuration_file, input="", bidirectional=True):
        """ Initialize a TM

        Args:
        configuration_file -- a string containing the name of the config file
        input -- the tape contents. DEFAULT: "". Can be updated later with set_input_string()
        bidirectional -- a boolean informing the simulator whether it is a 1 or 2 way tape. DEFAULT: True
        """
        self.file = configuration_file
        self.two_way = bidirectional
        self.next_state_dict = self.read_transition_table(self.file)
        self.inputstring = input
        self.reset_config()

    # data setters, getters, and manipulators
    def set_input_string(self, string):
        """Set the tape contents of the machine. Also refreshes the configuration, and returns the initial configuration (see reset_config())"""
        self.inputstring = string
        return self.reset_config()

    def set_bidirectional(self, value):
        """Set the tape contents of the machine. Also refreshes the configuration, and returns the initial configuration (see reset_config())"""
        self.two_way = value
        return self.reset_config()

    def reset_config(self):
        """Refresh the configuration of the machine so it is ready for a fresh run

        Returns:
        In single tape mode: a tuple (T,s,e,p,q) of the initial configuration of the TM, where T is a list containing the tape, s,e, and p are indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        In two tape mode: a tuple (T,s,e,p,q) with the same meanings, except T,s,e, and p are tuples with two values, for tape 1 and tape 2
        """
        self.config = None
        self.config_list = None
        if self.two_way:
            table = [' '] * 10000 + list(self.inputstring) + [' '] * (10000 - len(self.inputstring))
            self.config = (table, 10000, 10000 + len(self.inputstring) - 1, 10000, 0)
        else:
            table = list(self.inputstring) + [' '] * (20000 - len(self.inputstring))
            self.config = (table, 0, len(self.inputstring) - 1, 0, 0)
        self.step = 0

        self.config_list = [self.config]
        return self.config

    def go_back_to_step(self, n):
        """Given a step, reset the machine back to that steps

        Assumption: n < self.step, zero-indexed
        """
        if n == 0:
            self.reset_config()
            return self.config
        self.step = n
        self.config = self.config_list[n]
        self.config_list = list(self.config_list[:n + 1])
        return self.config

    def previous_config(self):
        """Go back one step in the machine. If already in initial step, do nothing

        Returns:
        In one tape mode: a tuple (T,s,e,p,q) of the instantaneous configuration of the TM, where T is a list containing the tape, s,e, and p are indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        In two tape mode: a tuple (T,s,e,p,q) with the same meanings, except T,s,e, and p are tuples with two values, for tape 1 and tape 2
        """
        if (len(self.config_list) > 1):
            self.config = self.config_list[-2]
            self.config_list = list(self.config_list[:-1])
            self.step -= 1

        return self.config

    def next_config(self):
        """Go forward one step in the machine

        Returns:
        In one tape mode: a tuple (T,s,e,p,q) of the instantaneous configuration of the TM, where T is a list containing the tape, s,e, and p are indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        In two tape mode: a tuple (T,s,e,p,q) with the same meanings, except T,s,e, and p are tuples with two values, for tape 1 and tape 2
        """
        (tape, start, end, current, state) = self.config
        tape = list(tape)  # copy the tape
        table = self.next_state_dict
        symbol = tape[current]
        if (state, symbol) in table:
            (newstate, newsymbol, direction) = table[(state, symbol)]
            tape[current] = newsymbol
            newcurrent = min(max(current + direction, 0), 20000 - 1)  # keep it on our finite tape
            if current < start and tape[current] != ' ':
                newstart = current
            else:
                newstart = start
            if current > end and tape[current] != ' ':
                newend = current
            else:
                newend = end
        elif state >= 0:
            newstate = -2
            newcurrent = current
            newstart = start
            newend = end
        else:
            newstate = state
            newcurrent = current
            newstart = start
            newend = end
        newconfig = (tape, newstart, newend, newcurrent, newstate)
        self.config_list.append(newconfig)
        self.config = newconfig
        self.step += 1

        return self.config

    # useful methods in running or displaying the machine
    def run_tm_iter(self):
        """A generator function for the configurations of the TM. This effectively recreates the original simulator if used in a for-loop with a print function"""
        while self.config[4] >= 0:
            if self.step > MAX_STEPS:
                break
            self.next_config()
            yield self.config

    def format_current_config(self):
        """Returns a multi-line string of the current configuration"""
        return self.format_config(self.config)

    def format_config(self, config):
        """Returns a multi-line string of the given configuration

        Arg:
        In one tape mode: a configuration tuple (T,s,e,p,q), where T is a list containing the tape, s,e, and p are indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        In two tape mode: a tuple (T,s,e,p,q) with the same meanings, except T,s,e, and p are tuples with two values, for tape 1 and tape 2
        """
        string = 'State: ' + str(config[4]) + '\n'
        tape = config[0]
        lowindex = min(config[1], config[3])
        highindex = max(config[2] + 1, config[3] + 1)
        for j in range(lowindex, highindex):
            if tape[j] == ' ':
                string += 'B'
            else:
                string += str(tape[j])
        string += '\n'
        for j in range(lowindex, highindex):
            if config[3] == j:
                string += '^'
            else:
                string += ' '
        string += '\n'
        return string

    # technical method to load the data
    def read_transition_table(self, filename):
        """Read the configuration file into a dictionary for the simulator to use.

        Based on the code in Howard Straubing's original simulator
        Returns:
        a dictionary of key-value pairs (q,c):(q',c',D) where D is -1 or 1, for left and right, tape symbols c, c' are characters, states q,q' are integers.
        In two-tape mode, c,c',and D are tuples containing two values corresponding to tape 1 and tape 2's characters/directions. D can also be 0
        """
        f = open(filename, 'r')
        d = {}
        for line in f:
            seq = line.split()
            if (len(seq) > 0) and (seq[0][0] != '#'):
                state = int(seq[0])
                newstate = int(seq[2])

                sym = seq[1]
                sym = sym.replace('B', ' ')
                newsym = seq[3]
                newsym = newsym.replace('B', ' ')

                if seq[4] == 'L':
                    direction = -1
                else:
                    direction = 1
                d[(state, sym)] = (newstate, newsym, direction)
        f.close()
        return d


class two_tape_TM:
    """This class serves as an object-oriented version of Howard Struabing's Turing Machine Simulator, but for two tapes
    """

    def __init__(self, configuration_file, input=""):
        """ Initialize a TM

        Args:
        configuration_file -- a string containing the name of the config file
        input -- the tape contents. DEFAULT: "". Can be updated later with set_input_string()
        """
        self.file = configuration_file
        self.next_state_dict = self.read_transition_table(self.file)
        self.inputstring = input
        self.reset_config()

    # data setters, getters, and manipulators
    def set_input_string(self, string):
        """Set the tape contents of the machine. Also refreshes the configuration, and returns the initial configuration (see reset_config())"""
        self.inputstring = string
        return self.reset_config()

    def reset_config(self):
        """Refresh the configuration of the machine so it is ready for a fresh run

        Returns:
        a tuple (T,s,e,p,q) of the initial configuration of the TM, where T is a tuple containing two lists containing the tapes, s,e, and p are tuples containing indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        """
        self.config = None
        self.config_list = None
        table1 = [' '] * 10000 + list(self.inputstring) + [' '] * (10000 - len(self.inputstring))
        table2 = [' '] * 20000
        self.config = ((table1, table2), (10000, 10000), (10000 + len(self.inputstring) - 1,
                                                          10000 + len(self.inputstring) - 1), (10000, 10000), 0)
        self.step = 0
        self.config_list = [self.config]
        return self.config

    def go_back_to_step(self, n):
        """Given a step, reset the machine back to that steps

        Assumption: n < self.step, zero-indexed
        """
        if n == 0:
            self.reset_config()
            return self.config
        self.step = n
        self.config = self.config_list[n]
        self.config_list = list(self.config_list[:n + 1])
        return self.config

    def previous_config(self):
        """Go back one step in the machine. If already in initial step, do nothing

        Returns:
        a tuple (T,s,e,p,q) of the instantaneous configuration of the TM, where T is a tuple containing two lists containing the tapes, s,e, and p are tuples containing indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        """
        if (len(self.config_list) > 1):
            self.config = self.config_list[-2]
            self.config_list = list(self.config_list[:-1])
            self.step -= 1

        return self.config

    def next_config(self):
        """Go forward one step in the machine

        Returns:
        a tuple (T,s,e,p,q) of the instantaneous configuration of the TM, where T is a tuple containing two lists containing the tapes, s,e, and p are tuples containing indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        """

        (tapes, starts, ends, currents, state) = self.config
        (t1, t2) = tapes
        t1 = list(t1)  # copy the lists
        t2 = list(t2)
        (s1, s2) = starts
        (e1, e2) = ends
        (c1, c2) = currents
        table = self.next_state_dict
        symbol1 = t1[c1]
        symbol2 = t2[c2]
        symbols = (symbol1, symbol2)
        if (state, symbols) in table:
            (newstate, newsymbols, directions) = table[(state, symbols)]
            t1[c1] = newsymbols[0]
            t2[c2] = newsymbols[1]
            (d1, d2) = directions
            newcurrent1 = min(max(c1 + d1, 0), 20000 - 1)  # keep it on our finite tape
            newcurrent2 = min(max(c2 + d2, 0), 20000 - 1)

            if c1 < s1 and t1[c1] != ' ':
                newstart1 = c1
            else:
                newstart1 = s1
            if c1 > e1 and t1[c1] != ' ':
                newend1 = c1
            else:
                newend1 = e1

            if c2 < s2 and t2[c2] != ' ':
                newstart2 = c2
            else:
                newstart2 = s2
            if c2 > e2 and t2[c2] != ' ':
                newend2 = c2
            else:
                newend2 = e2

        elif state >= 0:
            newstate = -2
            newcurrent1 = c1
            newcurrent2 = c2
            newstart1 = s1
            newstart2 = s2
            newend1 = e1
            newend2 = e2
        else:
            newstate = state
            newcurrent1 = c1
            newcurrent2 = c2
            newstart1 = s1
            newstart2 = s2
            newend1 = e1
            newend2 = e2

        newconfig = ((t1, t2), (newstart1, newstart2), (newend1, newend2), (newcurrent1, newcurrent2), newstate)
        self.config_list.append(newconfig)
        self.config = newconfig
        self.step += 1

        return self.config

    # useful methods in running or displaying the machine
    def run_tm_iter(self):
        """A generator function for the configurations of the TM. This effectively recreates the original simulator if used in a for-loop with a print function"""
        while self.config[4] >= 0:
            if self.step > MAX_STEPS:
                break
            self.next_config()
            yield self.config

    def format_current_config(self):
        """Returns a multi-line string of the current configuration"""
        return self.format_config(self.config)

    @staticmethod
    def format_config(config):
        """Returns a multi-line string of the given configuration

        Arg:
        a configuration tuple (T,s,e,p,q), where T is a tuple containing two lists containing the tapes, s,e, and p are tuples containing indecies corresponding to start, end, and head position on the tape contents, and q is the state (an integer)
        """
        string = 'State: ' + str(config[4]) + '\n'
        (t1, t2) = config[0]
        lowindex1 = min(config[1][0], config[3][0])
        lowindex2 = min(config[1][1], config[3][1])
        highindex1 = max(config[2][0] + 1, config[3][0] + 1)
        highindex2 = max(config[2][1] + 1, config[3][1] + 1)
        for j in range(lowindex1, highindex1):
            if t1[j] == ' ':
                string += 'B'
            else:
                string += str(t1[j])
        string += '\n'
        for j in range(lowindex1, highindex1):
            if config[3][0] == j:
                string += '^'
            else:
                string += ' '
        string += '\n'

        for j in range(lowindex2, highindex2):
            if t2[j] == ' ':
                string += 'B'
            else:
                string += str(t2[j])
        string += '\n'
        for j in range(lowindex2, highindex2):
            if config[3][1] == j:
                string += '^'
            else:
                string += ' '
        string += '\n'
        return string

    # technical method to load the data
    @staticmethod
    def read_transition_table(filename):
        """Read the configuration file into a dictionary for the simulator to use.

        Based on the code in Howard Straubing's original simulator
        Returns:
        a dictionary of key-value pairs (q,c):(q',c',D) where D is a 2-tuple of -1, 0, or 1, for left, stay, and right, tape symbols c, c' are tuples of two characters for the two tapes, states q,q' are integers.
        """
        f = open(filename, 'r')
        d = {}
        for line in f:
            seq = line.split()
            if (len(seq) > 0) and (seq[0][0] != '#'):
                state = int(seq[0])
                newstate = int(seq[2])

                sym = seq[1]
                sym = sym.replace('B', ' ')
                newsym = seq[3]
                newsym = newsym.replace('B', ' ')
                sym = tuple(sym.split(':'))
                newsym = tuple(newsym.split(':'))

                direction = tuple()
                for val in seq[4].split(':'):
                    if val == "L":
                        direction += (-1, )
                    elif val == "R":
                        direction += (1, )
                    else:
                        direction += (0, )

                d[(state, sym)] = (newstate, newsym, direction)
        f.close()
        return d
