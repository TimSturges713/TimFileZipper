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


"""
Compresses a textfile using the LZ77 algorithm.

@param filename     the path of the file to compress

@return pointers    the list of the corresponding LZ77 compressed pointers to the text file
"""
def compress(filename:str):
    pointers = []               # the array of pointers to represent the compressed data (tuples)
    prefix_table = {}
    with open(filename, "rb") as file:    # open the file provided
        data = file.read()        # access all text from the file
        data = memoryview(data)        
    pos = 0
    while pos < len(data):  # while the cursor isn't out of bounds
        # Define the sliding windows
        lookAhead = data[pos : min(pos + LOOK_AHEAD, len(data))]
        searchBuffer = data[max(0, pos - SEARCH_BUFFER) : pos]

        # Find the longest match
        match = longestMatch(data, searchBuffer, lookAhead, len(searchBuffer), len(lookAhead), pos, prefix_table)
        pointers.append(match)

        # Extract offset/length/nextChar from the packed 24-bit integer
        
        offset = (match >> 16) & 0xFF
        length = (match >> 8) & 0xFF
        next_char = match & 0xFF
        

        # Slide window forward
        if length < len(lookAhead):
            pos += length + 1
        else:
            pos += length
    return pointers
            
            
            
            
"""
Finds the longest repeating subsequence present in the search buffer compared to the look ahead buffer.

@param searchBuffer     sequence of characters from file of length SEARCH_BUFFER
@param lookAhead        sequence of characters from file of length LOOK_AHEAD

@return longestSub      a tuple of format (offset, length, next char) that makes the algorithm function properly
"""
def longestMatch(data, searchBuffer: memoryview, lookAhead: memoryview, searchLen, lookLen, pos, prefix_table) -> int:
    
    if(searchLen == 0):             # if there's no search buffer yet, then there's no longest match, return pointer (0,0,char)
        return (0 << 16) | (0 << 8) | lookAhead[0]
    
    best_len = 0    # set initial len of match to 0
    best_offset = 0 # set initial offset to 0, no match yet


    for j in range(searchLen):  # iterate through the search buffer, j is how much you subtract from the pos cursor, searchLen-j, offset is j + 1
        length = 0  # initial length of matching sequence
        while (length < lookLen and     # while length of subseq is the size of look len
            (searchLen - j) + length  <= searchLen and   # while the length of the substring doesn't go past the rightmost bound of search buffer
            searchBuffer[(searchLen -j - 1)+length] == lookAhead[length]):   # keep adding length until the match ends
            length += 1     # increase length of found substring

        # Once the previous loop is done it finds the match length of that position in the search buffer and saves it

        if length > best_len:
            best_len = length
            best_offset = j + 1
        if best_len == lookLen:
            break

    
    
    if(best_len < lookLen):
        next_char = data[best_len + pos]
    else:
        next_char = 0

    if best_len == 0:
        best_offset = 0

    

    return (best_offset << 16) | (best_len << 8) | next_char


def newLongestMatch(data, searchStart, prefix_table, pos, lookAhead):
    
    prefix = data[searchStart: searchStart + MIN_MATCH]
    bestLen = 0
    bestOffset = 0

    if prefix in prefix_table:
        candidates = prefix_table[prefix]
        tried = 0
        for candidate in list(candidates):
            if candidate < searchStart:     # prune an out of searchBuffer bounds candidate for a match
                try:
                    candidates.pop()
                except IndexError:
                    pass
                continue

            if tried >= MAX_CANDIDATES:
                break
            tried += 1
            max_len = min(len(lookAhead), len(data) - pos, pos - candidate)
            while i < max_len and data[candidate + i] == data[pos + i]:
                i += 1      # length of match
            if i > bestLen:
                bestLen = i
                bestOffset = pos - candidate
                if bestLen == len(lookAhead):
                    break
    
    if bestLen == 0:
        return (0 << 16) | (0 << 8) | lookAhead[0]
    elif bestLen > 0 and bestLen + pos < len(data):
        return (bestOffset << 16) | (bestLen << 8) | lookAhead[bestLen]
    else:
        return (0 << 16) | (0 << 8) | (0)



             




def new_compress(filename):
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

        matchPointer = newLongestMatch(data, searchStart, prefix_table, pos, lookAhead)
        pointers.append(matchPointer)

        if (matchPointer >> 8) & 0xFF == 0:
            move = 1
        else:
            move = ((matchPointer >> 8) & 0xFF) + 1
            
        
        for k in range(pos, min(pos + move, n - (MIN_MATCH - 1))):
            key = bytes(data[k: k + MIN_MATCH])
            dq = prefix_table.setdefault(key, deque())
            dq.appendleft(k)

            while dq and dq[-1] < pos - SEARCH_BUFFER:
                dq.pop()
            
            if len(dq) > (SEARCH_BUFFER // 8):
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
                        filename = input("Enter the path of the text file to compress:")
                        if filename[len(filename)-4:] == ".txt":
                            break
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
                        filename = input("Enter the path of the .tim file to decompress:")
                        if filename[len(filename)-4:] == ".tim":
                            break
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