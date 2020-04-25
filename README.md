Mazie, the Maze Evaluator
=====

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
