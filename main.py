from random import random, randint, choice
from copy import deepcopy
from symbolic import sample, Computer, diff, gencode, mutate, cross

a = sample()
b = sample()

def noise(data, p=0.1):
	result = []
	for d in data:
		if random() < p:
			result.append(0)
		else:
			result.append(d)
	return result

def randata(length=256):
	return [randint(0,255) for i in range(length)]

class Pool:
	def __init__(self):
		self.population = []
		self.best = None
		self.bestscore = None

	def runOnce(self):
		if len(self.population) == 0:
			agentcode = gencode()
		else:
			agentcode = self.population.pop(0)

		totalscore = 0
		TRIES = 10
		for i in range(TRIES):
			a = Computer(agentcode)#XXX same code?
			b = Computer(agentcode)

			data = randata(16)

			a.input = deepcopy(data)

			LIMIT = 1000
			a.run(LIMIT)

			b.input = noise(a.output, 0)
			b.run(LIMIT)

			score = diff(b.output, data)

			totalscore += score

		averagescore = totalscore/TRIES
		#print(averagescore)
		if self.bestscore is None or averagescore < self.bestscore:

			self.best = agentcode
			self.bestscore = averagescore

			print("NEW BEST!", self.bestscore, self.best)
			print(b.output)
			print(data)
			for i in range(5):
				if len(self.population) == 0:
					other = gencode()
				else:
					other = choice(self.population)
				self.population.append(mutate(cross(agentcode, other)))

			self.population = self.population[-100:]

			self.population.append(agentcode)

	def run(self):
		while self.bestscore is None or self.bestscore > 0:
			self.runOnce()

pool = Pool()
pool.run()

"""
for i in range(100):
	a.run()
	b.input = noise(a.output)
	a.output = []

	b.run()
	a.input = noise(b.output)
	b.output = []
"""
