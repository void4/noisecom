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
		self.senders = []
		self.receivers = []
		self.best = None
		self.bestscore = None

	def runOnce(self):
		if len(self.senders) == 0:
			sender = gencode()
		else:
			sender = self.senders.pop(0)

		if len(self.receivers) == 0:
			receiver = gencode()
		else:
			receiver = self.receivers.pop(0)

		DATALEN = 8
		LIMIT = DATALEN*20
		NOISE = 0.1

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
		#print(len(self.senders), len(self.receivers))
		if self.bestscore is None or averagescore <= self.bestscore:

			self.best = [sender, receiver]
			self.bestscore = averagescore

			print("NEW BEST!", self.bestscore, "\n", self.best[0], "\n", self.best[1])
			print(b.output)
			print(data)
			for i in range(1):
				other = gencode() if len(self.senders) == 0 else choice(self.senders)
				self.senders.append(mutate(cross(sender, other)))

				other = gencode() if len(self.receivers) == 0 else choice(self.receivers)
				self.receivers.append(mutate(cross(receiver, other)))

				# Crisscross sender with receivers
				other = gencode() if len(self.senders) == 0 else choice(self.senders)
				self.senders.append(mutate(cross(receiver, other)))

				other = gencode() if len(self.receivers) == 0 else choice(self.receivers)
				self.receivers.append(mutate(cross(sender, other)))

			self.senders = self.receivers[-200:]
			self.receivers = self.receivers[:-200:]

			self.senders.append(sender)
			self.receivers.append(receiver)

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
