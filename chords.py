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

class Chord:
	def __init__(self, grip, bass):
		tones = [shift(s,t) for t, s in zip(grip, strings)]

		# ugotovi koliko strun (od nizkih naprej) mora biti prostih, da bo v basu pravi ton
		self.free = 100
		if bass in tones: self.free = tones.index(bass) 
		
		# izračunaj na katero prečko se splača postaviti barre
		self.barre = min(grip) 
		
		# odstrani prijeme na prostih strunah
		self.grip = (self.barre,)*self.free + grip[self.free:] 
		self.tones = tones[self.free:]
		
		# izračunaj razdaljo med prvim in zadnjim prstom
		self.start = min(filter(lambda x: x != 0, self.grip + (100,)))	
		self.end = max(self.grip)
		self.span = self.end - max(self.start, self.barre) + 1

		# koliko prstov je uporabljenih
		self.fingers = len(strings) - self.grip.count(self.barre) + (1 if self.barre != 0 else 0) 

		self.score = max(0,self.span-2)**2 + self.start + max(0,self.fingers-2)**2 + max(0, self.free)*2 - len(set(self.tones))
	
	def __eq__(self, o: object) -> bool:
		return self.__hash__() == o.__hash__()

	def __hash__(self) -> int:
		return hash(self.grip)

def getChords(root, shape, bass):
	notes = [shift(root, d) for d in shape] # note v akordu glede na obliko

	# možne prečke za vsako struno
	deltaStrings = [
		[d for d in range(frets) if shift(string,d) in notes] 
		for string in strings
	]

	# vse možne kombinacije prijemov in njihova ocena
	chords = list(set([Chord(grip, bass) for grip in itertools.product(*deltaStrings)]))

	# prijemi urejeni po oceni in filtrirani najslabši
	chords = sorted(filter(lambda c: c.score < 50, chords), key=lambda c: c.score)

	return chords

def showChord(chord):
	lines = []
	start = chord.start if chord.start > 2 else 1
	end = max(chord.end, start+4)
	lines.append("    E A D G H E  ")
	lines.append("   "+" X"*chord.free)
	for fr in range(start, end+1):
		if chord.barre == fr:
			line = "OOOOOOOOOOOOO"
		else:
			line = "_"
			for s in chord.grip:
				if s == fr: line += "O_"
				else: line += "__"
		lines.append(f"{fr:2} {line}")
	lines.append(", ".join(map(idToName, chord.tones)))
	lines.append(f"span: {chord.span}")
	lines.append(f"start: {chord.start}")
	lines.append(f"fingers: {chord.fingers}")
	lines.append(f"score: {100 - chord.score}")

	return lines


def decodeChord(s):
	m = re.findall(r"^([cdefgabhCDEFGABH])(is|IS|s|S|es|ES)?(|dim|Dim|DIM|sus|Sus|SUS)?(maj|Maj|MAJ)?(\d)?\/?([cdefgahCDEFGAH])?(is|IS|s|S|es|ES)?$", s)[0]

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

	for row in zip(*[showChord(c) for c in chords[:5]]):
		for line in row:
			print(f"{line:20s}", end='')
		print()
	print()