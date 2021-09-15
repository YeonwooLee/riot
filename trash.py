import datetime

def time_to_millisecond(year,month,day,time):
	'''
	dt_obj = datetime.strptime('25.8.2021 22:00:00,00',
	                           '%d.%m.%Y %H:%M:%S,%f')
	                         '''

	dt_obj = datetime.datetime.strptime("{}.{}.{} {}:00:00,00".format(day,month,year,time),'%d.%m.%Y %H:%M:%S,%f')
	millisec = dt_obj.timestamp() * 1000

	return millisec


print(time_to_millisecond(2021,12,25,22))