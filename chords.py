import itertools
from types import SimpleNamespace

names = ['c','cis','d','dis','e','f','fis','g','gis','a','b','h']

shapes = {
	'dur': [0,4,7],
	'mol': [0,3,7],
	'dim': [0,3,6],
	'dur7': [0,4,7,10],
	'mol7': [0,3,7,11],
	'dim7': [0,3,6,9],
}

nameToId = lambda name: names.index(str.lower(name))
idToName = lambda id: names[id]
shift = lambda note, delta: (note + delta) % len(names)

strings = [*map(nameToId, ['e', 'a', 'd', 'g', 'h', 'e'])]
frets = 12


def getChords(root, shape):
	chordRoot = nameToId(root)
	chordShape = shapes.get(shape)
	chordNotes = [shift(chordRoot, d) for d in chordShape] # note v akordu glede na obliko

	# možne prečke za vsako struno
	deltaStrings = [
		[d for d in range(frets) if shift(string,d) in chordNotes] 
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
	print("    E D A G H E  ")
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


while True:
	root = input("Root note: ")
	shape = input("Type: ")

	chords = getChords(root, shape)

	for c in chords[:5]:
		showChord(c)
	
	print()