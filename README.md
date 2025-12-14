# Oizys Programming Language

A basic interpreted programming language designed for learning and experimentation.

## Features

- Define variables and constants
- Basic arithmetic and logical expressions
- `if` statements with `done` block termination
- `null` to reset variables, `del` to delete them
- Basic error handling for invalid syntax or usage
- `while` loop functionality
- `CLEAR` and `RESET` to clear terminal and reset environment respectively

## Installation

Requires Python 3.x. Clone the repository and run the interpreter:

```bash
git clone https://github.com/yourusername/Oizys-Python
cd Oizys-Python
python MAIN/interpreter.py {path-to-oizys-script}
```

## Limitations

- No `elif` support yet
- No functions
- No complex parsing (indentation not enforced)
- Blocks must end with `done` keyword
