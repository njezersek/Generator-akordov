import itertools
import re
from types import SimpleNamespace

names = ['c','cis','d','dis','e','f','fis','g','gis','a','b','h']

nameToId = lambda name: names.index(name.lower())
idToName = lambda id: names[id]
shift = lambda note, delta: (note + delta) % len(names)

strings = [*map(nameToId, ['e', 'a', 'd', 'g', 'h', 'e'])]
frets = 12


def getChords(root, shape):
	notes = [shift(root, d) for d in shape] # note v akordu glede na obliko

	# možne prečke za vsako struno
	deltaStrings = [
		[d for d in range(frets) if shift(string,d) in notes] 
		for string in strings
	]

	def score(grip):
		barre = min(grip)
		start = min(filter(lambda x: x != 0, grip))
		end = max(grip)
		fingers = len(strings) - grip.count(barre) + (1 if barre != 0 else 0)
		span = end - max(start, barre+1) + 1
		score = 10*max(0,span-3) + start + 10*max(0,fingers-4)
		return SimpleNamespace(grip=grip, barre=barre, score=score, start=start, end=end, span=span, fingers=fingers)

	# vse možne kombinacije prijemov in njihova ocena
	chords = [score(grip) for grip in itertools.product(*deltaStrings)]

	# prijemi urejeni po oceni in filtrirani najslabši
	chords = sorted(filter(lambda c: c.score < 50, chords), key=lambda c: c.score)

	return chords

def showChord(chord):
	start = chord.start if chord.start > 2 else 1
	end = max(chord.end, start+4)
	print("    E A D G H E  ")
	for fr in range(start, end+1):
		if chord.barre == fr:
			line = "XXXXXXXXXXXXX"
		else:
			line = "_"
			for s in chord.grip:
				if s == fr: line += "X_"
				else: line += "__"
		print(f"{fr:2} {line}")
	print(f"span: {chord.span}, start: {chord.start}, fingers: {chord.fingers}, score: {chord.score} \n")


def decodeChord(s):
	m = re.findall(r"^([cdefgahCDEFGAH])(is|IS|s|S|es|ES)?(|dim|Dim|DIM|sus|Sus|SUS)?(maj|Maj|MAJ)?(\d)?\/?([cdefgahCDEFGAH])?$", s)[0]

	root = names.index(m[0].lower())
	modificators = {'is': 1, 'es': -1, 's': -1}
	d = modificators.get(m[1].lower(), 0)
	root = shift(root, d)

	shape = set()
	if m[2].lower() == 'dim': shape = {0, 3, 6}
	elif m[2].lower() == 'sus': shape = {0, 5, 7}
	else:
		if str.isupper(m[0]): shape = {0,4,7}
		else: shape = {0,3,7}

	intervals = {'2': 1, 'maj2': 2, '3': 3, 'maj3': 4, '4': 5, '5': 7, '6': 8, 'maj6': 9, '7': 10, 'maj7': 11}

	shape.add(intervals.get((m[3]+m[4]).lower(), 0))

	return root, shape


while True:
	s = input("Enter chord name: ")

	root, shape = decodeChord(s)

	chords = getChords(root, shape)

	for c in chords[:5]:
		showChord(c)
	
	print()