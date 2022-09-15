from pyexpat import model, native_encoding
from mpcpy import variables
from mpcpy import units

setpoint = variables.Static('setpoint',20,units.degC)
print(setpoint)

setpoint.display_data()

setpoint.get_base_data()

setpoint.set_display_unit(units.degF)
setpoint.display_data()

import pandas as pd
data = [0,5,10,15,20]
index=pd.date_range(start='1/1/2017',periods=len(data),freq='H')
ts=pd.Series(data=data,index=index,name='power_data')

power_data=variables.Timeseries('power_data',ts,units.Btuh)
print(power_data)

power_data.display_data()

power_data.get_base_data()

power_data.set_display_unit(units.kW)
power_data.display_data()

from mpcpy import exodata
weather = exodata.WeatherFromEPW('~/research/MPCPy/doc/userGuide/tutorial/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw')
variable_map = {'Qflow_csv':('Qflow',units.W)}
control=exodata.ControlFromCSV('~/research/MPCPy/doc/userGuide/tutorial/ControlSignal.csv',variable_map,tz_name=weather.tz_name)

start_time='1/1/2017'
final_time='1/3/2017'
weather.collect_data(start_time,final_time)
control.collect_data(start_time,final_time)

control.display_data()

from mpcpy import systems
measurements = {'Tzone':{},'Qflow':{}}
measurements['Tzone']['Sample']=variables.Static('sample_rate_Tzone',3600,units.s)
measurements['Qflow']['Sample']=variables.Static('sample_rate_Qflow',3600,units.s)

moinfo=('/home/guokaichen/research/MPCPy/doc/userGuide/tutorial/Tutorial.mo','Tutorial.RC',{})

emulation=systems.EmulationFromFMU(measurements,
                                   moinfo=moinfo,
                                   weather_data=weather.data,
                                   control_data=control.data,
                                   tz_name=weather.tz_name)

emulation.collect_measurements('1/1/2017','1/2/2017')

emulation.display_measurements('Measured')

from mpcpy import models
parameters = exodata.ParameterFromCSV('/home/guokaichen/research/MPCPy/doc/userGuide/tutorial/Parameters.csv')
parameters.collect_data()
parameters.display_data()

model=models.Modelica(models.JModelicaParameter,
                      models.RMSE,
                      emulation.measurements,
                      moinfo=moinfo,
                      parameter_data=parameters.data,
                      weather_data=weather.data,
                      control_data=control.data,
                      tz_name=weather.tz_name)

model.simulate('1/1/2017','1/2/2017')
model.display_measurements('Simulated')
model.parameter_estimate('1/1/2017','1/2/2017',['Tzone'])

model.validate('1/1/2017','1/2/2017','validate_tra',plot=1)
print("%.3f" % model.RMSE['Tzone'].display_data())

start_time_val='1/2/2017'
final_time_val='1/3/2017'
emulation.collect_measurements(start_time_val,final_time_val)

model.measurements=emulation.measurements
model.validate(start_time_val,final_time_val,'validate_val',plot=1)
print('%.3f' % model.RMSE['Tzone'].display_data())

for key in model.parameter_data.keys():
    print(key,'%.2f' % model.parameter_data[key]['Value'].display_data())

from mpcpy import optimization
variable_map={'Qflow_min':('Qflow','GTE',units.W),
              'Qflow_max':('Qflow','LTE',units.W),
              'T_min':('Tzone','GTE',units.degC),
              'T_max':('Tzone','LTE',units.degC)}

constraints=exodata.ConstraintFromCSV('/home/guokaichen/research/MPCPy/doc/userGuide/tutorial/Constraints.csv',
                                      variable_map,
                                      tz_name=weather.tz_name)

constraints.collect_data('1/1/2017','1/3/2017')
constraints.display_data()

opt_problem = optimization.Optimization(model,
                                        optimization.EnergyMin,
                                        optimization.JModelica,
                                        'Qflow',
                                        constraint_data= constraints.data)

opt_problem.optimize('1/2/2017','1/3/2017')

opt_problem.get_optimization_statistics()

opt_problem.display_measurements('Simulated')

model.control_data['Qflow'].display_data().loc[pd.to_datetime('1/2/2017 06:00:00'):pd.to_datetime('1/3/2017 06:00:00')]

model.simulate('1/2/2017','1/3/2017')

model.display_measurements('Simulated')

opt_problem.optimize('1/2/2017','1/3/2017',res_control_step=1.0)

model.control_data['Qflow'].display_data().loc[pd.to_datetime('1/2/2017 06:00:00'):pd.to_datetime('1/3/2017 06:00:00')]
model.simulate('1/2/2017','1/3/2017')
model.display_measurements('Simulated')
