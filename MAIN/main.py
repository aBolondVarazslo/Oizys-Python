# * =========================
# * TOKENISER
# * =========================
# * Converts a raw input string into a list of tokens that the parser can consume.
# * This includes numbers, identifiers, operators, comparisons, strings, etc.
def tokenize(expr):
    tokens = []                 # * Final list of tokens
    number = ''                 # * Buffer for multi-digit numbers
    identifier = ''             # * Buffer for variable/keyword names
    in_string = False           # * Are we currently inside a string literal?
    string_delim = ''           # * Which quote opened the string (' or ")
    string_buffer = ''          # * Contents of the string literal
    i = 0                       # * Manual index to allow lookahead

    while i < len(expr):
        char = expr[i]

        # * =========================
        # * STRING HANDLING
        # * =========================
        if in_string:
            if char == '\\':  # * Escape sequence inside string
                i += 1
                if i < len(expr):
                    string_buffer += expr[i]
                else:
                    raise ValueError("Unfinished escape sequence in string")

            elif char == string_delim:
                # * Closing quote: emit full string token
                tokens.append(string_delim + string_buffer + string_delim)
                string_buffer = ''
                in_string = False

            else:
                # * Regular character inside string
                string_buffer += char

        # * =========================
        # * NON-STRING CONTEXT
        # * =========================
        else:
            # * Digits form integer literals
            if char.isdigit():
                if identifier:
                    tokens.append(identifier)
                    identifier = ''
                number += char

            # * Letters form identifiers / keywords
            elif char.isalpha():
                if number:
                    tokens.append(number)
                    number = ''
                identifier += char

            # * Operators and punctuation
            elif char in "+-*/()^!<>=":
                # * Flush any buffered number or identifier
                if number:
                    tokens.append(number)
                    number = ''
                if identifier:
                    tokens.append(identifier)
                    identifier = ''

                # * Handle multi-character operators (==, !=, <=, >=)
                if char in ('=', '!', '<', '>') and i + 1 < len(expr):
                    next_char = expr[i + 1]
                    two_char = char + next_char

                    if two_char in ('==', '!=', '<=', '>='):
                        tokens.append(two_char)
                        i += 1

                    elif char == '!':
                        # * Support chained factorial operators (!!!)
                        count = 1
                        while i + 1 < len(expr) and expr[i + 1] == '!':
                            count += 1
                            i += 1
                        tokens.append('!' * count)

                    else:
                        tokens.append(char)

                elif char == '!':
                    # * Standalone factorial handling
                    count = 1
                    while i + 1 < len(expr) and expr[i + 1] == '!':
                        count += 1
                        i += 1
                    tokens.append('!' * count)

                else:
                    tokens.append(char)

            # * String literal start
            elif char in ('"', "'"):
                if number:
                    tokens.append(number)
                    number = ''
                if identifier:
                    tokens.append(identifier)
                    identifier = ''

                in_string = True
                string_delim = char
                string_buffer = ''

            # * Whitespace ends current token
            elif char.isspace():
                if number:
                    tokens.append(number)
                    number = ''
                if identifier:
                    tokens.append(identifier)
                    identifier = ''

            # * Any other character is invalid
            else:
                raise ValueError(f"Invalid character: {char}")

        i += 1

    # * Unterminated string literal
    if in_string:
        raise ValueError("Unterminated string literal")

    # * Flush remaining buffers
    if number:
        tokens.append(number)
    if identifier:
        tokens.append(identifier)

    return tokens


# * =========================
# * GLOBAL STATE
# * =========================
# * Runtime storage for variables and constants
variables = {}
constants = {}

# * Reserved keywords that cannot be used as identifiers
keywords = {
    "and", "or", "not",
    "if", "else", "while", "for",
    "null", "del", "done",
    "CLEAR", "RESET", "help"
}


# * =========================
# * PARSER (RECURSIVE DESCENT)
# * =========================

# * Parse lowest-level values: literals, variables, parentheses, unary ops
def parse_factor(tokens):
    if not tokens:
        raise ValueError("Unexpected end of input")

    token = tokens.pop(0)

    # * Block terminator (used by control flow)
    if token == "done":
        return None

    # * Unary minus
    if token == "-":
        value = parse_factor(tokens)
        if isinstance(value, (int, float)):
            return -value
        else:
            raise ValueError("Unary negative can only be applied to numbers")

    # * Parenthesised expression
    if token == "(":
        value = parse_logical_or(tokens)
        if not tokens or tokens.pop(0) != ")":
            raise ValueError("Expected ')'")
    else:
        # * Integer literal
        if token.isdigit():
            value = int(token)

        # * Variable lookup
        elif token in variables:
            value = variables[token]

        # * Constant lookup
        elif token in constants:
            value = constants[token]

        # * String literal
        elif token.startswith(("'", '"')):
            value = token[1:-1]

        else:
            raise ValueError(f"Undefined variable or invalid token: {token}")

    # * Postfix factorial operators
    while tokens and tokens[0] in ("!", "!!", "!!!"):
        op = tokens.pop(0)

        if not isinstance(value, int) or value < 0:
            raise ValueError("Factorial only works on non-negative integers")

        if op == "!":
            value = factorial(value)
        elif op == "!!":
            value = double_facorial(value)
        elif op == "!!!":
            value = triple_factorial(value)

    return value


# * Handle multiplication and division
def parse_term(tokens):
    value = parse_power(tokens)

    while tokens and tokens[0] in ("*", "/"):
        op = tokens.pop(0)
        right = parse_factor(tokens)

        if op == "*":
            value *= right
        else:
            value /= right

    return value


# * Handle addition, subtraction, and string concatenation
def parse_expression(tokens):
    value = parse_term(tokens)

    while tokens and tokens[0] in ("+", "-"):
        op = tokens.pop(0)
        right = parse_term(tokens)

        if op == "+":
            if isinstance(value, str) or isinstance(right, str):
                value = str(value) + str(right)
            else:
                value += right
        else:
            value -= right

    return value


# * Comparison operators
def parse_comparison(tokens):
    value = parse_expression(tokens)

    while tokens and tokens[0] in ("==", "!=", ">", "<", ">=", "<="):
        op = tokens.pop(0)
        right = parse_expression(tokens)

        if op == "==":
            value = value == right
        elif op == "!=":
            value = value != right
        elif op == ">":
            value = value > right
        elif op == "<":
            value = value < right
        elif op == ">=":
            value = value >= right
        elif op == "<=":
            value = value <= right

    return value


# * Exponentiation (right-associative)
def parse_power(tokens):
    value = parse_factor(tokens)

    while tokens and tokens[0] == "^":
        tokens.pop(0)
        right = parse_power(tokens)
        value = value ** right

    return value


# * =========================
# * LOGICAL OPERATORS
# * =========================

def parse_logical_not(tokens):
    if tokens and tokens[0] == "not":
        tokens.pop(0)
        return not parse_logical_not(tokens)
    return parse_comparison(tokens)


def parse_logical_and(tokens):
    value = parse_logical_not(tokens)

    while tokens and tokens[0] == "and":
        tokens.pop(0)
        value = value and parse_logical_not(tokens)

    return value


def parse_logical_or(tokens):
    value = parse_logical_and(tokens)

    while tokens and tokens[0] == "or":
        tokens.pop(0)
        value = value or parse_logical_and(tokens)

    return value


# * =========================
# * MATH UTILITIES
# * =========================

def factorial(n):
    if n in (0, 1):
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def double_facorial(n):
    if n < 0:
        raise ValueError("Double factorial not defined for negative numbers")
    if n in (0, 1):
        return 1
    result = 1
    for i in range(n, 0, -2):
        result *= i
    return result


def triple_factorial(n):
    if n < 0:
        raise ValueError("Triple factorial not defined for negative numbers")
    if n in (0, 1, 2):
        return 1
    result = 1
    for i in range(n, 0, -3):
        result *= i
    return result


# * =========================
# * EVALUATION ENTRY POINT
# * =========================
# * Evaluates a full expression and ensures no tokens remain
def evaluate(tokens):
    tokens = tokens[:]  # * Work on a copy
    result = parse_logical_or(tokens)

    if tokens:
        raise ValueError(f"Unexpected input after expression: {' '.join(tokens)}")

    # * Normalise floats that are actually integers
    if isinstance(result, float) and result.is_integer():
        return int(result)

    return result
