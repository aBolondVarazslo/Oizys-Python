from main import *
from nulldel import *

def handle_lines(lines_deque):
    while lines_deque:
        handle_line(lines_deque.popleft().strip(), lines_deque)

def handle_line(line, lines_deque):
    if line.startswith("#") or not line or line == "done":
        return

    if line == "else:":
        raise ValueError("Unexpected 'else' without matching 'if'")

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
            raise ValueError(f"'{const_name}' is a reserved keyword and cannot be used for variables or constants")

        tokens = tokenize(expr)
        value = evaluate(tokens)
        constants[const_name] = value
        print(f"{const_name} (constant) = {value}")

    elif line.startswith("null "):
        var_name = line[len("null "):].strip()
        reset_variable(var_name, variables, constants)

    elif line.startswith("del "):
        var_name = line[len("del "):].strip()
        delete_variable(var_name, variables, constants)

    elif line.startswith("if ") and line.endswith(":"):
        condition_expr = line[3:-1].strip()
        condition_tokens = tokenize(condition_expr)
        condition_result = evaluate(condition_tokens)

        if_block = read_block(lines_deque)

        else_block = []

        if lines_deque and lines_deque[0].strip() == "else:":
            lines_deque.popleft()
            else_block = read_block(lines_deque)

        chosen_block = if_block if condition_result else else_block

        for blk_line in chosen_block:
            handle_line(blk_line, lines_deque)

    elif line.startswith("out "):
        expr = line[len("out "):].strip()
        tokens = tokenize(expr)
        value = evaluate(tokens)
        print(value)

    elif line == "CLEAR":
        print("\033[2J\033[H", end="")

    elif line == "RESET":
        variables.clear()
        constants.clear()
        print("\033[2J\033[H", end="")
        print("Environment reset")

    elif line.startswith("while ") and line.endswith(":"):
        condition_expr = line[6:-1].strip()
        loop_block = read_block(lines_deque)

        while True:
            condition_tokens = tokenize(condition_expr)
            condition_result = evaluate(condition_tokens)

            if not condition_result:
                break

            for blk_line in loop_block:
                handle_line(blk_line, lines_deque)

    else:
        equal_pos = line.find('=')

        if equal_pos != -1 and not (
            (equal_pos + 1 < len(line) and line[equal_pos + 1] == '=') or
            (equal_pos > 0 and line[equal_pos - 1] in ('!', '<', '>'))
        ):
            var_name = line[:equal_pos].strip()
            expr = line[equal_pos + 1:].strip()

            if not var_name.isalpha():
                raise ValueError("Invalid variable name")

            if var_name in keywords:
                raise ValueError(f"'{var_name}' is a reserved keyword and cannot be used for variables or constants")

            if var_name in constants:
                raise ValueError(f"'{var_name}' is a constant and cannot be changed")

            tokens = tokenize(expr)
            value = evaluate(tokens)
            variables[var_name] = value
            print(f"{var_name} = {value}")

        else:
            tokens = tokenize(line)
            result = evaluate(tokens)

def read_block(lines_deque):
    block_lines = []
    depth = 0

    while lines_deque:
        line = lines_deque.popleft()
        stripped = line.strip()

        if stripped.startswith("if ") and stripped.endswith(":"):
            depth += 1
            block_lines.append(stripped)
            continue

        if stripped.startswith("while ") and stripped.endswith(":"):
            depth += 1
            block_lines.append(stripped)
            continue

        if stripped == "done":
            if depth == 0:
                return block_lines
            else:
                depth -= 1
                block_lines.append(stripped)
                continue

        if depth == 0 and stripped in ("else:", "else"):
            lines_deque.appendleft(stripped)
            return block_lines

        block_lines.append(stripped)

    raise ValueError("Expected 'done' to close block but reached end of input")