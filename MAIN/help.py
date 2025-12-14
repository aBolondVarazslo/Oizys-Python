GENERAL_HELP = """Oizys — minimal interpreted language

Statements:
  x = expr          assign variable
  const x = expr    define constant
  null x            reset variable
  del x             delete variable

Control flow:
  if condition:
    ...
    done

  else:
    ...
    done

  while condition:
    ...
    done

Output & environment:
  out expr           print expression
  RESET              clear variables/constants
  CLEAR              clear screen
  exit               quit interpreter

Expressions:
  +  -  *  /  ^      arithmetic
  !  !!  !!!         factorials
  == != < > <= >=    comparisons
  and or not         logic"""

HELP = {
    # * If
    "if": """Usage:
  if condition:
    ...
    done
  
Example:
  if 3 > 2:
    out "3 is greater than 2"
    done
    """,



    # * Else
    "else": """Usage:
  if condition:
    ...
    done
  else:
    ...
    done

Example:
  if 2 > 3:
    out "2 is bigger than 3"
    done
  else:
    out "3 is bigger than 2"
    """,



    # * While
    "while": """Usage:
  while condition:
    ...
    done

Example:
  a = 0
  while a > 5:
    a = a + 5
    done
    """,


    # * Delete
    "del": """Usage:
  del variable

Example:
  a = 2
  del a
  """,


    #* Null
    "null": """Usage:
  null variable

Example:
  null a
  """,


    # * Output
    "out": """Usage:
  out variable
  out constant
  
Example:
  a = 5
  out a
  out "Example"
  """,

    # * Constant
    "const": """Usage:
  const variable = value

Example:
  const a = 5
  """
}