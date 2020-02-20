from random import choice, randint
#https://esolangs.org/wiki/Symbolic_Brainfuck
CELL = 256

REGISTERNAMES = "αßπσ"#"µδφε"
ALLCOMMANDS = "><+²-½↨⌂.," + REGISTERNAMES

class Computer:

	def __init__(self, code=None):
		self.ip = 0
		self.code = gencode() if code is None else code
		self.pointer = 0
		self.data = [0 for i in range(256)]
		self.registers = [0 for i in range(len(REGISTERNAMES))]

		self.input = []
		self.output = []

	def run(self, limit=None):

		steps = 0

		jmpmap = {}
		jmplst = []
		for ci, c in enumerate(self.code):
			if c == "[":
				jmplst.append(ci)
			elif c == "]":
				if len(jmplst) == 0:
					break
				matching = jmplst.pop(-1)
				jmpmap[ci] = matching
				jmpmap[matching] = ci + 1

		while steps < limit:

			if self.ip >= len(self.code):
				break

			cmd = self.code[self.ip]

			jump = False

			if cmd == ">":
				self.pointer = (self.pointer + 1) % CELL#LENMEM
			elif cmd == "<":
				self.pointer = (self.pointer - 1) % CELL
			elif cmd == "+":
				self.data[self.pointer] = (self.data[self.pointer] + 1) % CELL
			elif cmd == "²":
				self.data[self.pointer] = (self.data[self.pointer] << 1) % CELL
			elif cmd == "-":
				self.data[self.pointer] = (self.data[self.pointer] - 1) % CELL
			elif cmd == "½":
				self.data[self.pointer] = (self.data[self.pointer] >> 1) % CELL
			elif cmd == ".":
				self.output.append(self.data[self.pointer])
			elif cmd == ",":
				if len(self.input) > 0:
					self.data[self.pointer] = self.input.pop(0)
			elif cmd == "[":
				try:
					if self.data[self.pointer] == 0:
						self.ip = jmpmap[self.ip]
						jump = True
				except KeyError:
					pass
					#break
			elif cmd == "]":
				try:
					if self.data[self.pointer] != 0:
						self.ip = jmpmap[self.ip]
						jump = True
				except KeyError:
					pass
					#break
			elif cmd == "↨":
				self.data[self.pointer] = self.pointer
			elif cmd == "⌂":
				self.pointer = self.data[self.pointer]
			elif cmd in REGISTERNAMES:
				ri = REGISTERNAMES.find(cmd)
				#print(pointer)
				self.registers[ri], self.data[self.pointer] = self.data[self.pointer], self.registers[ri]

			if not jump:
				self.ip += 1

			steps += 1

		return steps

CODELEN = 140
STEPS = 250

def gencode(length=CODELEN):
	code = "".join([choice(ALLCOMMANDS+"[]") for i in range(length)])

	"""
	lcode = list(code)

	numpairs = randint(0, len(code)//2//10)
	for pair in range(numpairs):
		closing = randint(numpairs-pair, len(code)-1)
		opening = randint(0, closing-1)
		if lcode[opening] in "[]" or lcode[closing] in "[]":
			continue
		lcode[opening] = "["
		lcode[closing] = "]"

	code = "".join(lcode)
	"""

	return code


#state = state[0] + [c for c in state[1]]
from collections import Counter

c = Counter()
o = Counter()

def diff(a, b):
	la = len(a)
	lb = len(b)

	maxi = a if la > lb else b
	mini = a if la <= lb else b

	delta = 0

	for ci, c in enumerate(mini):
		delta += abs(maxi[ci]-c)#square?

	ldelta = abs(lb-la)
	#print(delta, ldelta)
	return (1+delta) * (1+ldelta*256**2)#*len(maxi))

def diff01(a, b):
	la = len(a)
	lb = len(b)

	maxi = a if la > lb else b
	mini = a if la <= lb else b

	delta = 0

	for ci, c in enumerate(mini):
		if c != maxi[ci]:
			delta += 1

	ldelta = abs(lb-la)
	#print(delta, ldelta)
	return (1+delta) * (1+ldelta)#*len(maxi))

def cross(a,b):
	ml = min(len(a), len(b))

	crossover = randint(0, ml-1)

	first = randint(0,1)

	a, b = [a,b][first], [a,b][1-first]

	return a[:crossover] + b[crossover:]

lowestscore = None
lowest = None

pop = []
best = []
rnd = 0
spl = 0
err = 0

def sample():
	global pop, rnd, spl
	if randint(0,100) < 25 and len(best) > 0:
		spl += 1
		return Computer(mutate(choice(best)))
	elif randint(0,100) < 75 and len(pop) > 0:
		spl += 1
		return Computer(pop.pop(0))
	else:
		rnd += 1
		return Computer(gencode())

def mutate(code):
	m = ""
	for c in code:
		r = randint(0,100)
		if r == 0:
			m += choice(ALLCOMMANDS)
		elif r == 1:
			pass
		elif r == 2:
			m += c + choice(ALLCOMMANDS)
		else:
			m += c
	return m

def merge(code):
	global best, rnd, pop, spl, lowest, lowestscore
	if randint(0,100) < 10 and len(best) > 0:
		other = choice(best)
	elif randint(0,100) < 25 and len(pop) > 0:
		other = choice(pop)
	else:
		other = gencode()
	#other = mutate(other)
	#code = mutate(code)
	return mutate(cross(other, code))

def train(targetstring):
	global best, rnd, pop, spl, err, lowest, lowestscore
	try:
		while True:
			comp = sample()
			if (rnd+spl)%3000 == 0:
				print(lowestscore, len(pop), len(best), rnd, spl, err)

			try:
				steps = comp.run(STEPS)
			except UnicodeError:#(KeyError, IndexError):
				err += 1
				continue

			target = [ord(c) for c in targetstring]#code[1]]
			score = diff(target, comp.output)
			#print(score)
			if lowestscore is None or score < lowestscore*1.1:
				for i in range(3):
					pop.append(merge(comp.code))
				for i in range(1):
					pop.append(comp.code)
				best.append(comp.code)
				best = best[-10:]
				pop = pop[-100:]

			if lowestscore is None or score < lowestscore:
				lowestscore = score
				lowest = comp.code
				print("CODE", comp.code)
				print("OUTP", "".join([chr(c) for c in comp.output]))
				print(lowestscore)

			#if 1000 > steps > 500:
			c[steps] += 1
			o[len(comp.output)] += 1
			#print(state)
			#print(steps)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	train("Targetstring")

"""
print(c)
print(o)
print(o[256])
"""
