import itertools
import re
from types import SimpleNamespace

names = ['c','cis','d','dis','e','f','fis','g','gis','a','b','h']
modificators = {'is': 1, 'es': -1, 's': -1}
intervals = {'2': 1, 'maj2': 2, '3': 3, 'maj3': 4, '4': 5, '5': 7, '6': 8, 'maj6': 9, '7': 10, 'maj7': 11}

idToName = lambda id: names[id]
shift = lambda note, delta: (note + delta) % len(names)
nameToId = lambda name: shift(names.index(name[:1].lower()), modificators.get(name[1:].lower(), 0))

strings = [*map(nameToId, ['e', 'a', 'd', 'g', 'h', 'e'])]
frets = 12


def getChords(root, shape, bass):
	notes = [shift(root, d) for d in shape] # note v akordu glede na obliko

	# možne prečke za vsako struno
	deltaStrings = [
		[d for d in range(frets) if shift(string,d) in notes] 
		for string in strings
	]

	def score(grip): # girp je seznam pokritih prečk po strunah
		tones = [shift(s,t) for t, s in zip(grip, strings)]
		free = 100
		if bass in tones: free = tones.index(bass) # ugotovi koliko strun (od nizkih naprej) mora biti prostih, da bo v basu pravi ton
		barre = min(grip) # izračunaj na katero prečko se splača postaviti barre
		grip = (barre,)*free + grip[free:] # odstrani prijeme na prostih strunah
		tones = tones[free:]
		start = min(filter(lambda x: x != 0, grip + (100,)))	# na kateri prečki je prvi prst
		end = max(grip) # zadnja prečka, na kateri je prst
		fingers = len(strings) - grip.count(barre) + (1 if barre != 0 else 0) # koliko prstov je uporabljenih
		span = end - max(start, barre) + 1
		score = max(0,span-2)**2 + start + 10*max(0,fingers-4) + free - len(set(tones))
		return SimpleNamespace(grip=grip, free=free, barre=barre, score=score, start=start, end=end, span=span, fingers=fingers, tones=tones)

	# vse možne kombinacije prijemov in njihova ocena
	chords = [score(grip) for grip in itertools.product(*deltaStrings)]

	# prijemi urejeni po oceni in filtrirani najslabši
	chords = sorted(filter(lambda c: c.score < 50, chords), key=lambda c: c.score)

	return chords

def showChord(chord):
	start = chord.start if chord.start > 2 else 1
	end = max(chord.end, start+4)
	print("    E A D G H E  ")
	print("   "+" X"*chord.free)
	for fr in range(start, end+1):
		if chord.barre == fr:
			line = "OOOOOOOOOOOOO"
		else:
			line = "_"
			for s in chord.grip:
				if s == fr: line += "O_"
				else: line += "__"
		print(f"{fr:2} {line}")
	print(", ".join(map(idToName, chord.tones)))
	print(f"span: {chord.span}, start: {chord.start}, fingers: {chord.fingers}, score: {chord.score} \n")


def decodeChord(s):
	m = re.findall(r"^([cdefgahCDEFGAH])(is|IS|s|S|es|ES)?(|dim|Dim|DIM|sus|Sus|SUS)?(maj|Maj|MAJ)?(\d)?\/?([cdefgahCDEFGAH])?(is|IS|s|S|es|ES)?$", s)[0]

	root = nameToId(m[0]+m[1])

	shape = set()
	if m[2].lower() == 'dim': shape = {0, 3, 6}
	elif m[2].lower() == 'sus': shape = {0, 5, 7}
	else:
		if str.isupper(m[0]): shape = {0,4,7}
		else: shape = {0,3,7}

	shape.add(intervals.get((m[3]+m[4]).lower(), 0))

	bass = root
	if m[5] != '': bass = nameToId(m[5]+m[6])

	return root, shape, bass


while True:
	s = input("Enter chord name: ")

	root, shape, bass = decodeChord(s)
	chords = getChords(root, shape, bass)

	for c in chords[:1]:
		showChord(c)
	
	print()