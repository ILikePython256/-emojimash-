import operator
import sys
import copy


class chars:
    number = "๐ข"
    string = "๐ค"
    true = "๐น"
    false = "๐ท"
    null = "๐ซ"
    string_escape = "โ"
    string_escapes = {
        "โ": "โ",
        "๐ค": "๐ค",
        "โฉ": "\n",
        "โก": "\t",
        "\n": "",
    }
    math = "๐งฎ"
    math_ops = {
        "โ": (operator.add, 2),
        "โ": (operator.sub, 2),
        "โ": (operator.mul, 2),
        "โ": (operator.floordiv, 2),
        "โ": (operator.mod, 2),
        "โคด": (operator.pow, 2),
        "โบ": (operator.pow, 2),
        "๐ฐ": (operator.eq, 2),
        "๏ผ": (operator.eq, 2),
        "โช": (operator.lt, 2),
        "โฉ": (operator.gt, 2),
        "โฎ": (operator.le, 2),
        "โญ": (operator.ge, 2),
        "โ ": (operator.ne, 2),
        "๐": (operator.neg, 1),
        "โผ": (operator.not_, 1),
        "๐ข": (int, 1),
        "๐ค": (str, 1),
        "โ": (bool, 1),
        "๐": (list, 1),
    }
    makelist = "๐"
    makedict = "๐"
    getitem = "๐"
    print = "๐จ"
    print_nl = "๐ "  # Print with newline
    delete = "๐"
    comment = "๐ฌ"
    label = "๐ท"
    goto = "๐ "
    gotoif = "๐"
    copy = "๐"
    no_op = "\n\t "
    input = "โจ"
    length = "๐"
    pop = "๐"
    stack = "๐"
    setitem = "๐"
    swap = "๐"
    callfunc = "๐ธ"
    return_ = "๐"
    eraseitem = "๐"
    globaldict = "๐"
    append = "๐งฑ"


def lexify(text):
    inp = list(text.replace("\uFe0F", ""))  # Fe0F == Variation Selector-16
    code = []
    labels = {}
    while inp:
        symbol = inp.pop(0)
        symname = [i for i in dir(chars) if getattr(chars, i) == symbol]
        if symname:
            symname = symname[0].rstrip("_")  # For things like return_
        else:
            symname = None
        # print(symbol, symname)
        if symname == "string":
            buffer = ""
            while (char := inp.pop(0)) != chars.string:
                if char == chars.string_escape:
                    char2 = inp.pop(0)
                    if char2 in chars.string_escapes:
                        buffer += chars.string_escapes[char2]
                    else:
                        buffer += char + char2
                else:
                    buffer += char
            code.append(("push", buffer))
        elif symname == "math":
            op = inp.pop(0)
            if op in chars.math_ops:
                code.append(("math", op))
            else:
                print(f"error: unknown math op '{op}'")
                sys.exit()
        elif symname in ("makelist", "makedict", "getitem", "copy", "length",
                         "stack", "print", "print_nl", "delete", "input",
                         "pop", "setitem", "swap", "return", "eraseitem",
                         "globaldict", "append"):
            code.append((symname,))
        elif symname in ("comment", "label", "goto", "gotoif", "number",
                         "callfunc"):
            ind = inp.index(symbol)
            buffer = "".join(inp[:ind])
            inp = inp[ind+1:]
            if symname == "label":
                labels[buffer] = len(code)
            if symname in ("goto", "gotoif", "callfunc"):
                code.append((symname, buffer))
            if symname == "number":
                code.append(("push", int(buffer)))
        elif symname in ("true", "false", "null"):
            code.append(("push", {
                "true": True,
                "false": False,
                "null": None
            }[symname]))
        elif symbol not in chars.no_op:
            print(f"error: unknown char '{symbol}' ({symname=})")
            sys.exit()

    return code, labels


def run(code, labels):
    pc = 0
    stack = []
    funcstack = []
    globaldict = {}
    while pc < len(code):
        cmd, *args = code[pc]
        if cmd == "push":
            stack.append(args[0])
        elif cmd == "math":
            op, numargs = chars.math_ops[args[0]]
            items = [stack.pop() for _ in range(numargs)][::-1]
            stack.append(op(*items))
        elif cmd == "makelist":
            if type(stack[-1]) is int:
                num = stack.pop()
                stack.append([stack.pop() for _ in range(num)][::-1])
        elif cmd == "makedict":
            if type(stack[-1]) is list and type(stack[-2]) is list:
                stack.append(dict(zip(stack.pop(), stack.pop())))
        elif cmd == "getitem":
            ind = stack.pop()
            stack.append(stack[-1][ind])
        elif cmd == "print":
            print(stack[-1], end="")
        elif cmd == "print_nl":
            print(stack[-1])
        elif cmd == "delete":
            stack.pop()
        elif cmd == "goto":
            pc = labels[args[0]]-1
        elif cmd == "gotoif":
            if stack.pop():
                pc = labels[args[0]]-1
        elif cmd == "copy":
            stack.append(copy.deepcopy(stack[-1]))
        elif cmd == "input":
            stack.append(input())
        elif cmd == "length":
            stack.append(len(stack[-1]))
        elif cmd == "pop":
            if type(stack[-1]) is str:
                stack.append(stack[-1][0])
                stack[-2] = stack[-2][1:]
            else:
                stack.append(stack[-1].pop(0))
        elif cmd == "stack":
            stack.append(copy.deepcopy(stack))
        elif cmd == "setitem":
            ind = stack.pop()
            stack[-1][ind] = stack.pop()
        elif cmd == "swap":
            N = stack.pop()
            stack[-N], stack[-1] = stack[-1], stack[-N]
        elif cmd == "callfunc":
            funcstack.append(pc)
            pc = labels[args[0]]-1
        elif cmd == "return":
            if funcstack:
                pc = funcstack.pop()
            else:
                return
        elif cmd == "eraseitem":
            ind = stack.pop()
            del stack[-1][ind]
        elif cmd == "globaldict":
            stack.append(globaldict)
        elif cmd == "append":
            item = stack.pop()
            stack[-1].append(item)
        pc += 1


if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <file>")
    sys.exit(1)
elif len(sys.argv) == 1:
    pass  # TODO: REPL
if sys.argv[1] == "-":
    code = sys.stdin.read()
else:
    code = open(sys.argv[1]).read()
lex = lexify(code)
# print(lex)
run(*lex)
