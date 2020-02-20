from random import random, randint, choice
from copy import deepcopy
from symbolic import sample, Computer, diff, gencode, mutate, cross, diff01

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

def randata(length=256, upper=255):
	return [randint(0, upper) for i in range(length)]

class Pool:
	def __init__(self):
		self.population = []

	def runOnce(self):
		POPLEN = 100
		SURVIVE = 20

		DATALEN = 8
		NOISE = 0.5
		LIMIT = DATALEN*20/(1-NOISE)

		for i in range(POPLEN-len(self.population)):
			self.population.append([gencode(), gencode(), 10**10])

		for i in range(POPLEN):
			sender = self.population[i][0]
			receiver = self.population[i][1]

			totalscore = 0
			TRIES = 10
			for i in range(TRIES):
				a = Computer(sender)
				#XXX use same code? well, if it's the same code, it can't differentiate
				# between being sender or receiver, unless it creates noise detector
				b = Computer(receiver)

				data = randata(DATALEN)

				a.input = deepcopy(data)
				a.run(LIMIT)

				b.input = noise(a.output, NOISE)
				b.run(LIMIT)

				score = diff01(b.output, data)

				totalscore += score

			averagescore = totalscore/TRIES
			#print(averagescore)
			self.population[i][2] = averagescore

		self.population = sorted(self.population, key=lambda x:x[2])

		print(self.population[0][2])
		newpopulation = []

		for i in range(SURVIVE):
			for j in range(POPLEN//SURVIVE-1):
				other = [gencode(), gencode()] if len(self.population) == 0 else choice(self.population)
				newsender = mutate(cross(self.population[i][0], other[0]))
				newreceiver = mutate(cross(self.population[i][1], other[1]))
				newpopulation.append([newsender, newreceiver, 10**10])

		for i in range(SURVIVE):
			newpopulation.append([gencode(), gencode(), 10**10])

		#print(len(newpopulation))
		self.population = newpopulation


	def run(self):
		while True:#self.population[0][2] > 0
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
