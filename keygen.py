import re
import ctypes

flagPattern = "\[ebx\+([\s\S]+)\]"
operationPattern = "eax,([\s\S]+)"
file = open("code.txt", 'r', encoding='utf-8')

listOfLines = []
operation2Flag = []

flag = [0xf2, 0x6e, 0xd1, 0xb1, 0x7e, 0x8b, 0x3e, 0x8e, 0xb1, 0x67, 0x6e, 0xe2, 0xf7, 0xa8, 0x3d, 0xce, 0x2f, 0xb0,
        0xec, 0x0]

for i in range(len(flag)):
    operation2Flag.append([])  # operation2Flag recorded in a matrix
for eachline in file:
    listOfLines.append(eachline)


def jump_over_trash_code(listOfLines,index):
    if "push" not in listOfLines[index]:
        pass
    else:
        stack=[]
        while True:
            if "push" in listOfLines[index]:  # jump over trash codes
                stack.append(1)
            elif "pop" in listOfLines[index]:
                stack.pop()
            else:
                pass
            index += 1

            if not stack and "push" not in listOfLines[index]:
                break
    return index


def parse_operation_by_section(listOfLines,index,flagSectionIndex):
    index = jump_over_trash_code(listOfLines, index)

    if "mov" in listOfLines[index]:  # operation always ends with a "mov"
        index += 1
        return index

    else:
        if "add" in listOfLines[index]:
            num = re.findall(operationPattern, listOfLines[index])[0]
            if 'h' in num:
                num = num.replace('h', '').strip()
            operation2Flag[flagSectionIndex].append("+" + str(int(num, 16)))
            index += 1
            return parse_operation_by_section(listOfLines,index,flagSectionIndex)

        elif "sub" in listOfLines[index]:
            num = re.findall(operationPattern, listOfLines[index])[0]
            if 'h' in num:
                num = num.replace('h', '').strip()
            operation2Flag[flagSectionIndex].append("-" + str(int(num, 16)))
            index += 1
            return parse_operation_by_section(listOfLines,index,flagSectionIndex)

        elif "xor" in listOfLines[index]:
            num = re.findall(operationPattern, listOfLines[index])[0]
            if 'h' in num:
                num = num.replace('h', '').strip()
            operation2Flag[flagSectionIndex].append("^" + str(int(num, 16)))
            index += 1
            return parse_operation_by_section(listOfLines,index,flagSectionIndex)

        else:
            print("Unknown command: ")
            print(listOfLines[index])
            index += 1
            return parse_operation_by_section(listOfLines,index,flagSectionIndex)


numberOfLines = len(listOfLines)
index = 0

while index < numberOfLines:
    if "movzx" not in listOfLines[index]:
        index += 1
    else:  # The operation always start with a "movzx" providing a section index of flag
        msg = re.findall(flagPattern, listOfLines[index])[0]
        if 'h' in msg:
            msg = msg[:-1]

        flagSectionIndex = int(msg, 16) - 1
        index += 1

        index=parse_operation_by_section(listOfLines,index,flagSectionIndex)

for i in range(len(operation2Flag)):
    operation2Flag[i].reverse()
    for each_op in operation2Flag[i]:
        if each_op[0] == '-':
            flag[i] = flag[i] + int(each_op[1:])
        elif each_op[0] == '+':
            flag[i] = flag[i] - int(each_op[1:])
        elif each_op[0] == '^':
            flag[i] = ctypes.c_ubyte(flag[i]).value ^ ctypes.c_ubyte(int(each_op[1:])).value

print(flag)
for i in flag:
    print(chr(ctypes.c_ubyte(i).value), end='')
