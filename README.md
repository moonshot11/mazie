Mazie, the Maze Evaluator
=====

Given a specification for a maze (comprised of cells, and doors connecting them), Mazie determines all possible states with doors open and closed, and if the maze is solvable, it prints the shortest possible path from the start to finish. Cells are described using alphanumerical characters (no spaces!), and doors are described using **upper case letters only**.

Usage
-----

Create a text file to define doors (edges) and cells (nodes)

`A kitchen living_room`

Creates a "door" named A that connects the kitchen and living room. Cells are created automatically.

- Doors must be a single, upper-case letter. Limit of 26, do not skip letters of the alphabet.
- Cells cannot have spaces

You must also add start and end points:

```
START kitchen
END office
```

You can force doors to be open or closed:

```
OPEN A
CLOSE B
```

You can create dynamic statements using `open`, `closed`, and `path` to reference the number of open and closed doors, and the length of the shortest path. Start the line with a `?` followed by a space.

```
# Check only for shortest paths greater than 4 in length
? path > 4

# Check for solutions where exactly there doors are closed
? open == 3
```

You can refer to a specific door's state with `<door name>.open`.

```
# Only one of A and B can be open
? A.open != B.open

# Only one of C, D, and E can be open
sum( [C.open, D.open, E.open] ) == 1
```

You can use `CONTAINS` and `OMITS` to require whether certain cells are in the shortest path:

```
# Requires the living room to be in the shortest path
CONTAINS living_room foyer

# Requires that the office and hall are NOT in the shortest path
OMITS office hall
```

Mazie has an implicit requirement that all cells must be visited.
