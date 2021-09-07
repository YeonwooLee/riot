#cl_collector
import requests
import json
import operator
import datetime
import time
from skimage import io # 미니맵 처리
#from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import smtplib # 메일을 보내기 위한 라이브러리 모듈
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 
import smtplib
import imaplib
import poplib
import email
from email.mime.text import MIMEText
import random
import telegram


class LolCollector:
	def getKey(self):
		


