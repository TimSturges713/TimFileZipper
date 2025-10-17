"""
filename: lz77.py

@author: Timothy Sturges

The compression and decompression functions of my personal implementation
of the LZ77 algorithm in Python.
"""

import struct
from collections import deque

WINDOW_SIZE = 255
LOOK_AHEAD = 18                 # size of lookahead
SEARCH_BUFFER = 255 - 18       # size of the search buffer
MAX_CANDIDATES = 64
MIN_MATCH = 3





def longestMatch(data, searchStart, prefix_table, pos, lookAhead):
    
    prefix = data[pos: pos + MIN_MATCH]

    if len(prefix) < MIN_MATCH:
        return (0 << 16) | (0 << 8) | lookAhead[0]

    bestLen = 0
    bestOffset = 0

    if prefix in prefix_table:
        candidates = prefix_table[prefix]
        while candidates and candidates[-1] < searchStart:
            candidates.pop()
    

        tried = 0
        for candidate in candidates:

            if tried >= MAX_CANDIDATES:
                break
            tried += 1
            max_len = min(len(lookAhead), len(data) - pos, pos - candidate)
            i = 0
            while i < max_len and data[candidate + i] == data[pos + i]:
                i += 1      # length of match
            if i > bestLen:
                bestLen = i
                bestOffset = pos - candidate
                if bestLen == len(lookAhead):
                    break
    
    if bestLen == 0:
        return (0 << 16) | (0 << 8) | lookAhead[0]
    elif bestLen + pos < len(data):
        return (bestOffset << 16) | (bestLen << 8) | data[pos + bestLen]
    else:
        return (0 << 16) | (0 << 8) | (0)



             




def compress(filename):
    with open(filename, "rb") as file:
        data = file.read()
        data = memoryview(data)
    pointers = []
    prefix_table = {}
    pos = 0

    while pos < len(data):
        lookAhead = data[pos: min(pos + LOOK_AHEAD, len(data))]
        searchStart = max(0, pos - SEARCH_BUFFER)
        searchBuffer = data[searchStart: pos]

        matchPointer = longestMatch(data, searchStart, prefix_table, pos, lookAhead)
        pointers.append(matchPointer)

        if (matchPointer >> 8) & 0xFF == 0:
            move = 1
        else:
            move = ((matchPointer >> 8) & 0xFF) + 1
            
        
        for k in range(pos, min(pos + move, len(data) - (MIN_MATCH - 1))):
            key = bytes(data[k: k + MIN_MATCH])
            dq = prefix_table.setdefault(key, deque())
            dq.appendleft(k)

            while dq and dq[-1] < k - SEARCH_BUFFER:
                dq.pop()
            
            if len(dq) > (SEARCH_BUFFER // 4):
                dq.pop()

        pos += move 
    
    return pointers
        



"""
Decompresses a textfile using the LZ77 algorithm.
"""
def decompress(pointers):
    finalAnswer = bytearray()

    for pointer in pointers:
        offset = pointer >> 16
        length = (pointer >> 8) & 0xFF
        nextChar = pointer & 0xFF
          
        if offset > 0 and length > 0:
            start = len(finalAnswer) - offset
            for i in range(length):
                finalAnswer.append(finalAnswer[start + i])
                
        
        if(nextChar != 0):
            finalAnswer.append(nextChar)
        
    return finalAnswer.decode('latin1')

def decompressionProcessing(filename):
    with open(filename, "rb") as f:
                pointers = []
                while True:
                    chunk = f.read(3)
                    if not chunk:
                        break             
                    if len(chunk) != 3:
                        raise EOFError(f"Incomplete token: expected 3 bytes, got {len(chunk)}")
                    offset, length, next_byte = struct.unpack(">BBB", chunk)
                    pointer = (offset << 16) | (length << 8) | next_byte
                    pointers.append(pointer)    
                englishAnswer = decompress(pointers)
            
                try:
                    with open(filename[:len(filename)-4] + ".txt", "w", newline="") as write:
                        write.write(englishAnswer)
                except:
                    f = open(filename[:len(filename)-4] + ".txt", "x")
                    f.close()
                    with open(filename[:len(filename)-4] + ".txt", "w", newline="") as write:
                        write.write(englishAnswer)

def compressionProcessing(filename):
    pointers = compress(filename)
    name = filename[:len(filename)-4]
    try:
        with open(name + ".tim", "wb") as write:
            for pointer in pointers:
                offset = pointer >> 16
                length = (pointer >> 8) & 0xFF
                next_char = pointer & 0xFF
                write.write(struct.pack(">BB", offset, length))
                write.write(struct.pack("B", next_char))  
    except: 
        f = open(name + ".tim", "x")
        f.close()
        with open(name + ".tim", "wb") as write:
            for pointer in pointers:
                offset = pointer >> 16
                length = (pointer >> 8) & 0xFF
                next_char = pointer & 0xFF
                write.write(struct.pack(">BB", offset, length))
                write.write(struct.pack("B", next_char))   

def main():
    print("Welcome to the text file compression software!")
    while True:
        compOrDecomp = input("Do you want to compress (0) or decompress (1) a text file? Enter 0 or 1, or -1 to quit:")
        if compOrDecomp == "-1":
            return
        if compOrDecomp == "0":
            while True:
                try:
                    while True:
                        filename = input("Enter the path of the text file to compress, or -1 to quit:")
                        if filename[len(filename)-4:] == ".txt":
                            break
                        elif filename == "-1":
                            return
                        else:
                            print("Please enter a valid .txt file path")
                    compressionProcessing(filename)
                    break
                except:
                    print("Please try a valid .txt file path")
                    continue
            print("Compressed into " + filename[:len(filename)-4] + ".tim successfully!")
            return
        if compOrDecomp == "1": 
            while True:
                try:
                    while True:
                        filename = input("Enter the path of the .tim file to decompress, or -1 to quit:")
                        if filename[len(filename)-4:] == ".tim":
                            break
                        elif filename == "-1":
                            return
                        else:
                            print("Please enter a valid .tim file path")
                    decompressionProcessing(filename)
                    break
                except:
                    print("Please try a valid .tim file path")
                    continue
                
            
            print("Decompressed into " + filename[:len(filename)-4] + ".txt successfully!")
            return
        else:
            print("Please enter a valid option.")
            continue

if __name__ == "__main__":
    main()