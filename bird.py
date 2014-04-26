import math
import pygame
import sys
import numpy as np
from scipy.stats import norm
from vect import Vector as vc

class BirdAI:
	def __init__(self):
		self.setGoal({"cruise": True})

	def updateAI(self, bird, interval, viscosity=0.):
		if "cruise" in self.goal:
			bird.accelerate(0.3)
			bird.turn(0.)
		if "target" in self.goal:
			(tx, ty) = self.goal["target"]
			(x, y) = bird.pos
			ang = math.atan2(tx - x, ty - y)
			if ang > 0: bird.turn(-1.)
			elif ang < 0: bird.turn(1.)
			mag = math.hypot(tx - x, ty - y)
			bird.accelerate(mag / 100.)
			#print ang

	def manualControl(self, bird):
		k = pygame.key.get_pressed()
		if (k[pygame.K_UP]): bird.accelerate(1.)
		elif (k[pygame.K_DOWN]): bird.accelerate(-1.)
		else: bird.accelerate(0.)
		if (k[pygame.K_LEFT]): bird.turn(1.)
		elif (k[pygame.K_RIGHT]) : bird.turn(-1.)
		else: bird.turn(0.)	

	def setGoal(self, goal):
		self.goal = goal

# Set up our colors
black = (0, 0, 0)

mackingbirdMean = {"beakLength": 9., 
		"neckWidth": 4.5, 
		"buttWidth": 4.5, 
		"tailWidth": 6, 
		"tailLength": 6., 
		"length": 18., 
		"majorSpan": 15., 
		"minorSpan": 12.,
		"wingWidth": 5.,
		"restingSpeed": .03,
		"brakingStrength": 0.,
		"flapStrength": 0.008,
		"flapBreadth": math.pi/3.,
		"featheriness": .005,
		"maxFlapFrequency": 0.005,
		"maxTurnSpeed": 0.001,
		"flapRampUp": .03,
		"bodyColor": (221., 177., 227.),
		"wingColor": (24., 38., 199.)}

mackingbirdStd = {"beakLength": 0.9, 
		"neckWidth": .45, 
		"buttWidth": .45, 
		"tailWidth": .6, 
		"tailLength": .6, 
		"length": 1.8, 
		"majorSpan": 1.5, 
		"minorSpan": 1.2,
		"wingWidth": .5,
		"restingSpeed": .003,
		"brakingStrength": 0.,
		"flapStrength": 0.0008,
		"flapBreadth": math.pi/30.,
		"featheriness": .0005,
		"maxFlapFrequency": .0005,
		"maxTurnSpeed": 0.0001,
		"flapRampUp": .003,
		"bodyColor": (50., 50., 50.),
		"wingColor": (50., 50., 50.)}

class Bird:
	# Current design params:
	# beakLength, neckWidth, buttWidth, tailWidth, length, 
	# majorSpan, minorSpan, wingWidth, restingSpeed, brakingStrength, 
	# flapStrength, flapBreadth, featherin i       i
	def __init__(self, species, colors=[(0,0,0),(0,0,0)]):
		# Save design params
		self.species = species
		# Set state variables
		self.pos = (0., 0.)
		self.vel = (0., 0.)
		self.acc = (0., 0.)
		self.ang = 0.
		self.avl = 0.
		self.aac = 0.
		self.majorAng = 0.
		self.minorAng = 0.
		self.flapAngle = 0.
		self.targetFlapFrequency = 0.
		self.flapFrequency = 0.
		# Generate vertices
		self.bodyVerts = self.genBodyVerts()
		self.wingVerts = self.genWingVerts(self.bodyVerts)

	def turn(self, power):
		if abs(power) > 1: power = power/abs(power) # scale to +/-1
		self.avl = power*self.species["maxTurnSpeed"]

	def accelerate(self, power):
		if power > 1: power = power/abs(power) # scale to +/-1
		if power == 0:
			self.targetFlapFrequency = 0.
			self.flapFrequency = 0.
		else:
			self.targetFlapFrequency = power*self.species["maxFlapFrequency"]

	def getBirdState(self):
		return (self.pos, self.vel, self.acc,
			self.ang, self.avl, self.aac, self.majorAng,
			self.minorAng,self.flapAngle,
			self.targetFlapFrequency, self.flapFrequency)

	def setBirdState(self, state):
		(self.pos, self.vel, self.acc,
			self.ang, self.avl, self.aac, self.majorAng,
			self.minorAng,self.flapAngle,
			self.targetFlapFrequency, self.flapFrequency) = state

	def turnAndShift(self, pts, loc, rot):
		(lx, ly) = loc
		npts = []
		mc = math.cos(rot)
		ms = math.sin(rot)
		return [(px * mc + py * ms + lx, px * -ms + py * mc + ly)
				for (px, py) in pts]

	def genBodyVerts(self):
		s = self.species
		nose = (0, s["length"]/2 + s["beakLength"])
		lShd = (-s["neckWidth"]/2, s["length"]/2)
		rShd = ( s["neckWidth"]/2, s["length"]/2)
		lBtt = (-s["buttWidth"]/2, -s["length"]/2)
		rBtt = ( s["buttWidth"]/2, -s["length"]/2)
		lTal = (-s["tailWidth"]/2, -s["tailLength"]-s["length"]/2)
		rTal = ( s["tailWidth"]/2, -s["tailLength"]-s["length"]/2)
		return [nose, lShd, lBtt, lTal, rTal, rBtt, rShd]

	def genWingVerts(self, bodyVerts):
		s = self.species
		[nose, lShd, lBtt, lTal, rTal, rBtt, rShd] = bodyVerts
		# Unpack relevant vertices
		(lsx, lsy) = lShd
		(rsx, rsy) = rShd
		(lbx, lby) = lBtt
		(rbx, rby) = rBtt
		lmTx = lsx - s["majorSpan"]*math.cos(self.majorAng)
		lmTy = lsy - s["majorSpan"]*math.sin(self.majorAng)
		lmTp = (lmTx, lmTy)
		rmTx = rsx + s["majorSpan"]*math.cos(self.majorAng)
		rmTy = rsy - s["majorSpan"]*math.sin(self.majorAng)
		rmTp = (rmTx, rmTy)
		lTip = (lmTx - s["minorSpan"]*math.cos(self.minorAng),
			lmTy + s["minorSpan"]*math.sin(self.minorAng))
		rTip = (rmTx + s["minorSpan"]*math.cos(self.minorAng),
			rmTy + s["minorSpan"]*math.sin(self.minorAng))
		lmBp = (lmTx, lmTy - s["wingWidth"])
		rmBp = (rmTx, rmTy - s["wingWidth"])
		return [lShd, lmTp, lTip, lmBp, lBtt, rBtt, rmBp, rTip, rmTp, rShd]

	def draw(self, window):
		bC = self.species["bodyColor"]
		wC = self.species["wingColor"]
		#print bC, wC
		pygame.draw.polygon(window, bC, 
			self.turnAndShift(self.bodyVerts, self.pos, self.ang))
		pygame.draw.polygon(window, wC, 
			self.turnAndShift(self.wingVerts, self.pos, self.ang))

	#TODO: There are two customizable parameters here: the flapAngles,
	# and the resting speed of the unflapped wings
	def update(self, interval, viscosity=0.):
		s = self.species
		#
		(ax, ay) = self.acc
		(sx, sy) = self.vel
		(px, py) = self.pos
		(dx, dy) = (math.sin(self.ang), math.cos(self.ang))
		(fx, fy) = (0, 0) # Directional force added
		# Ramp up to target flap frequency for believable effect
		self.flapFrequency = self.flapFrequency + \
			(self.targetFlapFrequency-self.flapFrequency)/(1+s["flapRampUp"])
		# Update the flapping
		if (self.flapFrequency > 0.): # flap and accelerate
			self.flapAngle = self.flapAngle + interval*self.flapFrequency
			self.majorAng = s["flapBreadth"]*math.sin(self.flapAngle)
			self.minorAng = s["flapBreadth"]*math.cos(self.flapAngle)
			fmag = s["flapStrength"]*self.flapFrequency
			fx = fmag*dx*interval
			fy = fmag*dy*interval
		elif (self.flapFrequency == 0.): # glide
			self.majorAng = self.majorAng / (1+s["restingSpeed"])
			self.minorAng = self.minorAng / (1+s["restingSpeed"])
			self.flapAngle = self.flapAngle / (1+s["restingSpeed"])
		else: # decellerate
			fx = -s["brakingStrength"]*sx*interval
			fy = -s["brakingStrength"]*sy*interval
		# Viscosity affects acceleration proportional to speed
		ax = fx - viscosity*sx*interval
		ay = fy - viscosity*sy*interval
		self.acc = (ax, ay)
		# Adjust for air turning in speed
		sx = sx + ax*interval
		sy = sy + ay*interval
		#speedAngle = math.atan2(sx, sy)
		speedMag = math.hypot(sx, sy)
		sx = (1-s["featheriness"])*sx+s["featheriness"]*speedMag*dx
		sy = (1-s["featheriness"])*sy+s["featheriness"]*speedMag*dy
		self.vel = (sx, sy)
		self.pos = (px + sx*interval, py + sy*interval)
		# Update the angle
		self.avl = self.avl + interval*self.aac
		self.ang = self.ang + interval*self.avl
		# Rebuild wings
		self.wingVerts = self.genWingVerts(self.bodyVerts)


class BirdFactory:
	def __init__(self, speciesMean=mackingbirdMean, speciesStd=mackingbirdStd):
		self.speciesMean = speciesMean
		self.speciesStd = speciesStd

	def getPercentile(self, bird):
		#return sum([norm.ppf(birdMean, loc=normMean, scale=normStd) \
		#	for birdMean, normMean, normStd in 
		#	zip(bird.species, self.speciesMean, self.speciesStd)])
		N = 0
		ptot = 0.
		for key in bird.species:
			try:
				float(bird.species[key])
			except TypeError, t:
				continue # Don't bother with no-floats
			pt = bird.species[key] 
			loc=self.speciesMean[key]
			scale=self.speciesStd[key]
			# quickie normPdf
			#normPdf = lambda x, m, s: exp(-(x-m)**2/2)/sqrt(2*pi)
			if scale != 0:
				ptot += norm.cdf((pt-loc)/scale)
				N += 1
			#print pt, loc, scale, ptot
		return ptot/N
	def createBird(self, size = 1., pos=(0., 0.)):
		species = self.speciesMean.copy()
		clmpLow = lambda c: 0. if c < 0. else c
		for key in species:
			try:
				meanList = self.speciesMean[key]
				stdList = self.speciesStd[key]
				rndList = [np.random.normal(mean, std) \
					for mean, std in zip(meanList, stdList)]
				if key.endswith("Color"):
					# special clause for color
					clmpColor = lambda c: 255. if c > 255 else c
					rndList = [clmpColor(clmpLow(c)) for c in rndList]
				else:
					rndList = [clmpLow(c) for c in rndList]
				#print rndList
				species[key] = tuple(rndList)
			except TypeError, t:
				mean = self.speciesMean[key]
				std = self.speciesStd[key]
				if std == 0.:
					rnd = mean
				else:
					rnd = np.random.normal(mean, std)
				species[key] = clmpLow(rnd)
		b = Bird(species)
		b.pos = pos
		b.species["percentile"]=self.getPercentile(b)
		return b

if __name__ == "__main__":
	pygame.init()
	# create the screen
	window = pygame.display.set_mode((640, 480))
	# Event Handler method
	def handleEvents():
		# what key buttons do you want to monitor?
		# up, down, left, right, escape
		key_esc = 27
		# Handle events
		for event in pygame.event.get():
			if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == key_esc): 
				sys.exit(0) 
	# Create a bird
	b = BirdFactory().createBird(10.)
	b.pos = startPos = (320, 240)
	# set up time
	lastTick = lastChange = pygame.time.get_ticks()
	period = 1500.
	while (True):
		# Update interval
		newTick = pygame.time.get_ticks()
		interval = newTick - lastTick
		lastTick = newTick
		if newTick > lastChange + period:
			lastChange = newTick
			b = BirdFactory().createBird(10.)
			b.pos = startPos
			b.ang = math.pi
			b.accelerate(0.5)
		# handle events
		handleEvents()
		# Update the bird
		b.update(interval, 0.001)
		# Clear screen
		window.fill(black)
		# Draw bird
		b.draw(window)
		pygame.display.flip()