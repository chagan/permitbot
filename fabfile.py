from fabric.api import local
from permitbot import *

def large_permits(days=1):
	find_high(days=days)

def demos(days=1):
	find_demo(days=days)

def summary(days=30):
	get_summary(days=days)