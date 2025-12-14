from main import *
from nulldel import *
from help import GENERAL_HELP, HELP


# * =========================
# * TOP-LEVEL LINE DISPATCH
# * =========================

# * Processes all lines in a script or REPL buffer
def handle_lines(lines_deque):
    while lines_deque:
        handle_line(lines_deque.popleft().strip(), lines_deque)


# * Handles a single line of input
def handle_line(line, lines_deque):
    # * Ignore comments, blank lines, and block terminators
    if line.startswith("#") or not line or line == "done":
        return

    # * Guard against invalid standalone else
    if line == "else:":
        raise ValueError("Unexpected 'else' without matching 'if'")

    # * =========================
    # * CONSTANT DEFINITION
    # * =========================
    if line.startswith("const "):
        rest = line[len("const "):].strip()

        if "=" not in rest:
            raise ValueError("Expected '=' in constant definition")

        const_name, expr = rest.split("=", 1)
        const_name = const_name.strip()
        expr = expr.strip()

        if not const_name.isalpha():
            raise ValueError("Invalid constant name")

        if const_name in keywords:
            raise ValueError(f"'{const_name}' is a reserved keyword")

        value = evaluate(tokenize(expr))
        constants[const_name] = value
        print(f"{const_name} (constant) = {value}")

    # * =========================
    # * VARIABLE MANAGEMENT
    # * =========================
    elif line.startswith("null "):
        reset_variable(line[5:].strip(), variables, constants)

    elif line.startswith("del "):
        delete_variable(line[4:].strip(), variables, constants)

    # * =========================
    # * CONDITIONALS
    # * =========================
    elif line.startswith("if ") and line.endswith(":"):
        condition = evaluate(tokenize(line[3:-1].strip()))
        if_block = read_block(lines_deque)

        else_block = []
        if lines_deque and lines_deque[0].strip() == "else:":
            lines_deque.popleft()
            else_block = read_block(lines_deque)

        for blk_line in (if_block if condition else else_block):
            handle_line(blk_line, lines_deque)

    # * =========================
    # * OUTPUT
    # * =========================
    elif line.startswith("out "):
        print(evaluate(tokenize(line[4:].strip())))

    # * =========================
    # * ENVIRONMENT CONTROL
    # * =========================
    elif line == "CLEAR":
        print("\033[2J\033[H", end="")

    elif line == "RESET":
        variables.clear()
        constants.clear()
        print("\033[2J\033[H", end="")
        print("Environment reset")

    # * =========================
    # * HELP SYSTEM
    # * =========================
    elif line == "help":
        print(GENERAL_HELP)

    elif line.startswith("help "):
        topic = line[5:].strip()
        print(HELP.get(topic, f"No help for '{topic}'"))

    # * =========================
    # * LOOPS
    # * =========================
    elif line.startswith("while ") and line.endswith(":"):
        condition_expr = line[6:-1].strip()
        loop_block = read_block(lines_deque)

        while evaluate(tokenize(condition_expr)):
            for blk_line in loop_block:
                handle_line(blk_line, lines_deque)

    # * =========================
    # * ASSIGNMENT OR EXPRESSION
    # * =========================
    else:
        equal_pos = line.find('=')

        # * Assignment (but not comparison)
        if equal_pos != -1 and not (
            (equal_pos + 1 < len(line) and line[equal_pos + 1] == '=') or
            (equal_pos > 0 and line[equal_pos - 1] in ('!', '<', '>'))
        ):
            var_name = line[:equal_pos].strip()
            expr = line[equal_pos + 1:].strip()

            if not var_name.isalpha():
                raise ValueError("Invalid variable name")
            if var_name in keywords:
                raise ValueError(f"'{var_name}' is a reserved keyword")
            if var_name in constants:
                raise ValueError(f"'{var_name}' is a constant")

            value = evaluate(tokenize(expr))
            variables[var_name] = value
            print(f"{var_name} = {value}")

        else:
            # * Expression with no side effects
            evaluate(tokenize(line))


# * =========================
# * BLOCK PARSING
# * =========================
# * Reads an indented-style block terminated by 'done'
def read_block(lines_deque):
    block_lines = []
    depth = 0

    while lines_deque:
        stripped = lines_deque.popleft().strip()

        # * Nested blocks increase depth
        if stripped.startswith(("if ", "while ")) and stripped.endswith(":"):
            depth += 1
            block_lines.append(stripped)
            continue

        # * Block termination
        if stripped == "done":
            if depth == 0:
                return block_lines
            depth -= 1
            block_lines.append(stripped)
            continue

        # * Allow else to be handled by parent
        if depth == 0 and stripped in ("else:", "else"):
            lines_deque.appendleft(stripped)
            return block_lines

        block_lines.append(stripped)

    raise ValueError("Expected 'done' to close block")
