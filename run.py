#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import listdir
from subprocess import call

FILTER_DATE = '2018-10-06'
FOLDER_NAME = 'pages_reduzido'

for f in listdir(FOLDER_NAME):
	call(['py', '-3', 'fb-scrap.py', FOLDER_NAME+'/'+f, FILTER_DATE])