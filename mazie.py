# Maze Evaluator
#
# Processes cells and doors, and determines whether
# maze completion is possible

import os
import re
import sys

DEFAULT_FN = "layout.txt"

START = None
END = None

cells = dict()
doors = dict()
force_close, force_open = [], []
force_cells = list()
force_not_cells = list()
evals = list()

# List of tuples of open/closed doors
results_pass = list()
fail_count = 0

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def door_criteria(cells, doors):
    """Use this function to filter for specific scenarios"""
    c_cnts = {k:len(v.connections) for k,v in cells.items()}
    d_cnts = {k:int(v.open) for k,v in doors.items()}
    return True

def report(filename, results):
    """Create a report file"""
    def gen_line(title, data, delim=" "):
        """Generate a line for reporting"""
        res = "{}({}):".format(title, len(data)).ljust(13) + delim.join(data) + "\n"
        return res

    with open(filename, "w") as fout:
        for result in results:
            opened, closed, path = result
            fout.write(gen_line("Open", opened))
            fout.write(gen_line("Closed", closed))
            fout.write(gen_line("Path", path, " -> "))
            fout.write("\n")

def read_layout(filename):
    """Read layout from file"""
    global START, END

    with open(filename, "r") as fin:
        lines = fin.readlines()

    for line in lines:
        line = line.strip()
        # Set start and end points
        if line.startswith("START "):
            START = line[6:]
            continue
        if line.startswith("END "):
            END = line[4:]
            continue
        if line.startswith("CLOSE "):
            force_close.append(line[6])
            continue
        if line.startswith("OPEN "):
            force_open.append(line[5])
            continue
        if line.startswith("CONTAINS "):
            cellnames = line.split()[1:]
            for name in cellnames:
                force_cells.append(name)
            continue
        if line.startswith("OMITS "):
            cellnames = line.split()[1:]
            for name in cellnames:
                force_not_cells.append(name)
            continue
        if line.startswith("? "):
            evals.append(line[2:])
            continue

        # Set cell/door relationship
        match = re.match(r"(\w)\s+(\w+)\s+(\w+)", line)
        if not match:
            continue
        doorname = match.group(1)
        node1_name = match.group(2)
        node2_name = match.group(3)

        door = doors.setdefault(doorname, Door(doorname))

        node1 = cells.setdefault(node1_name, Cell(node1_name))
        cells[node1_name].doors.add(door)

        node2 = cells.setdefault(node2_name, Cell(node2_name))
        cells[node2_name].doors.add(door)

        door.set_cells(node1, node2)

class Door:
    """A door (edge) object"""
    def __init__(self, name):
        """Create a Door object"""
        self.name = name
        self.r1 = None
        self.r2 = None
        self.open = False

    def set_cells(self, r1, r2):
        """Set the cells connected to this object"""
        self.r1 = r1
        self.r2 = r2

    def other(self, ra):
        """Given one cell, return this door's other cell"""
        if ra == self.r1:
            return self.r2
        if ra == self.r2:
            return self.r1
        print("ERROR: cell {} not connected to this door ({})!".format(self.name, ra.name))
        print("r1 = {}, r2 = {}".format(self.r1.name, self.r2.name))
        sys.exit(1)

class Cell:
    """A cell (node) object"""
    def __init__(self, name):
        """Create a Cell object"""
        self.name = name
        self.doors = set()
        self.prev = None

    @property
    def connections(self):
        """Return cells connected to this cell through open doors"""
        result = list()
        for door in self.doors:
            if not door.open:
                continue
            result.append(door.other(self))
        return result

if len(sys.argv) < 2:
    print("Reading default layout file: " + DEFAULT_FN)
    filename = DEFAULT_FN
else:
    filename = sys.argv[1]

if not os.path.isfile(filename):
    print("ERROR: Could not find file " + filename)
    sys.exit(1)

read_layout(filename)

amt_tests = 2 ** len(doors)
invalid_count = 0
skip_count = 0

# Set upper-case vars so layout file can use
# eval statements such as "A.open != B.open"
for k,v in doors.items():
    exec(k + " = v")

for i in range(amt_tests):
    if i % 1117 == 0:
        print("\rRunning test {} of {}...".format(i+1, amt_tests), end="")

    skip = False

    # Reset cells
    for cell in cells.values():
        cell.prev = None
    # Set door states
    for door in doors.values():
        idx = letters.index(door.name)
        bitmask = 0x1 << idx
        door.open = bool(bitmask & i)
        if door.open and door.name in force_close or \
           not door.open and door.name in force_open:
            skip = True

    if skip:
        skip_count += 1
        continue

    visited = set()
    candidates = [cells[START]]
    found_soln = False
    path = list()

    while candidates:
        cell = candidates.pop(0)
        visited.add(cell)
        adjs = [c for c in cell.connections
                if c not in visited and c not in candidates]
        for adj in adjs:
            candidates.append(adj)
            adj.prev = cell
            if adj == cells[END] and not found_soln:
                found_soln = True
                cc = cells[END]
                while cc:
                    path.insert(0, cc.name)
                    cc = cc.prev

    open_doors = sorted([d.name for d in doors.values() if d.open])
    closed_doors = sorted([d.name for d in doors.values() if not d.open])
    data = (open_doors, closed_doors, path)

    # Preserve the "open" symbol's Python definition
    py_open = open

    filter_pass = True
    open = len(open_doors)
    closed = len(closed_doors)
    path = len(path)

    for statement in evals:
        if not eval(statement):
            filter_pass = False
            break
    if filter_pass:
        for cell in force_cells:
            if cell not in data[2]:
                filter_pass = False
                break
    if filter_pass:
        for cell in force_not_cells:
            if cell in data[2]:
                filter_pass = False
                break

    open = py_open

    # Implicit requirement that all cells are visited
    if len(visited) == len(cells) and filter_pass:
        results_pass.append(data)
    else:
        fail_count += 1

print("\rRunning test {0} of {0}...".format(amt_tests), end="")

print("{} passing, {} invalid, {} skipped".format(len(results_pass), fail_count, skip_count))
report("pass.txt", results_pass)
