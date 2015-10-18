#!/usr/bin/python

import script as s
import sys
import re

def parse(path):
    f = open(path, 'r')

    script = s.Script()

    # Get characters!
    for line in f:
        if line.strip() == "CAST": break
    print "Cast:"
    for line in f:
        if ("STAR TREK" in line):
            break
        line = line.strip()
        if line == "": continue

        chars = re.split("\s\s+", line)
        for char in chars:
            if char == "Non-Speaking":continue # Special case!!!
            script.addCharacter(char)
            print "Character:", char

    # Get sets!
    for line in f:
        if line.strip() == "SETS": break
    print "Sets:"
    for line in f:
        if ("STAR TREK" in line):
            break
        line = line.strip()
        if line == "": continue

        sets = re.split("\s\s+", line)
        for setting in sets:
            if script.addSetting(setting):
                print "Set:", setting

    # Get scenes!
    scenetexts = []
    curscene = []
    for line in f:
        if line.strip() == "THE END" or re.match("^\d+.*$", line):
            if "CONTINUED" in line or "ANGLE" in line: # Don't split up scenes.
                continue
            if not ("INT." in line or "EXT." in line):
                continue
            scenetexts.append(curscene)
            curscene = []
            if line.strip() == "THE END":
                break

        curscene.append(line)

    scenetexts = scenetexts[1:] # Remove some crap.

    seenchars = set()

    for text in scenetexts:
        descr = text[0].strip()
        setting = script.getSetting(descr)
        print descr, "==>", setting.name
        scene = s.Scene(text[0])
        scene.setSetting(setting)

        actuallines = []
        lastline = (0,"")
        for line in text[1:]:
            tabs = 0
            for rune in line:
                if rune == "\t":
                    tabs += 1
                else:
                    break
            line = line.strip()
            if tabs == 0 or line == "":
                continue

            if tabs == lastline[0]:
                lastline = (tabs, lastline[1] + " " + line)
            else:
                actuallines.append(lastline)
                lastline = (tabs, line)
        if lastline[0] != 0:
            actuallines.append(lastline)

        curchar = None
        for line in actuallines:
            tabs, line = line
            
            if tabs == 1: # Stage direction
                scene.addDirection(s.StageDirection(line))
            elif tabs == 3: # Dialog
                scene.addDirection(s.Dialog(curchar, line))
            elif tabs == 4: # Stage direction for character
                scene.addDirection(s.StageDirection(line, character=curchar))
            elif tabs == 5: # Character
                curchar = script.getCharacter(line)
                if not line in seenchars:
                    print line, "==>", curchar.name
                    seenchars.add(line)
            else:
                pass # Eh, this probably shouldn't happen. Whatever.

        script.addScene(scene)
    return script

if __name__=="__main__":

    if len(sys.argv) != 2:
        print "USAGE: ./star-trek-parse <scriptpath>"
        exit(1)

    print "Parsing script from %s" % sys.argv[1]
    script = parse(sys.argv[1])

    print "Scene 1:"
    scene1 = script.scenes[0]
    for action in scene1.directions:
        if isinstance(action, s.Dialog):
            print "%s: %s" % (action.character.name, action.text)
