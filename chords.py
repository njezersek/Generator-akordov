import itertools
from types import SimpleNamespace

names = ['c','cis','d','dis','e','f','fis','g','gis','a','b','h']

nameToId = lambda name: names.index(str.lower(name))
idToName = lambda id: names[id]
shift = lambda note, delta: (note + delta) % len(names)

strings = [*map(nameToId, ['e', 'a', 'd', 'g', 'h', 'e'])]
frets = 12
chordRoot = nameToId('F')
chordShape = [0, 4, 7]
chordNotes = [shift(chordRoot, d) for d in chordShape]

deltaStrings = [
	[d for d in range(frets) if shift(string,d) in chordNotes] 
	for string in strings
]

def score(grip):
	barre = min(grip)
	start = min(filter(lambda x: x != 0, grip))
	end = max(grip)
	fingers = len(strings) - grip.count(barre) + (1 if barre != 0 else 0)
	span = end - start + 1
	score = fingers + span
	return SimpleNamespace(grip=grip, barre=barre, score=score, start=start, end=end)

chords = [score(grip) for grip in itertools.product(*deltaStrings)]

chords = sorted(filter(lambda c: c.score < 10, chords), key=lambda c: c.score)

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
	print()


for c in chords[:5]:
	showChord(c)