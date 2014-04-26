import pygame

class Controller:

	def __init__(self):
		self.controls = {}
		self.lines = []
		# initialize font
		self.infoFont = pygame.font.SysFont("monospace", 15)

	def handleEvent(self, event):
		for key in self.controls:
			(keyup,keydown,upFunc,downFunc,formatFunc,param)=self.controls[key]
			if event.key == keyup:
				param = upFunc(param)
			elif event.key == keydown:
				param = downFunc(param)
			self.controls[key]=(keyup,keydown,upFunc,downFunc,formatFunc,param)

	def draw(self, window):
		self.makeControlLines()
		y = 10
		for line in self.lines:
			label = self.infoFont.render(line, 1, (255,255,0))
			window.blit(label, (10, y))
			y += 15
		self.lines = [] #TODO: WARNING: THIS IS LAZY array rebuilding

	def makeControlLines(self):
		for key in self.controls:
			(keyup,keydown,upFunc,downFunc,formatFunc,param)=self.controls[key]
			self.lines.append(formatFunc(param))

	def addLine(self, line):
		self.lines.add(line)

	def getParam(self, key):
		(keyup,keydown,upFunc,downFunc,formatFunc,param)=self.controls[key]
		return param
