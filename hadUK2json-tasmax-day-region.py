import netCDF4
import numpy as np
import json
from datetime import datetime, timedelta

epoc = datetime(1800,1,1,0,0,0)
startDate = 14610 #year 2000

#filename = 'sun_hadukgrid_uk_region_mon-20y_198101-200012'
filename = 'tasmax_hadukgrid_uk_region_day_19600101-20211231'

print("Reading .nc file...")
f = netCDF4.Dataset(filename + '.nc')

print(f)
print(f.variables.keys())

md = {}
for x,y in vars(f).items():
    md[x] = y

dims ={}
for d in f.dimensions.keys():
    dims[d] = {'name' : str(f.dimensions[d].name), 'size' : f.dimensions[d].size }
md['dimensions'] = dims

vvars = {}
for k in f.variables.keys():
    locals()[k] = f.variables[k]
    vvars[k] = {'dtype' : str(f.variables[k].dtype), 'dimensions' : str(f.variables[k].dimensions), 'attributes' : f.variables[k].__dict__}
md['variables'] = vvars

rn=[]
for x in region:
    rn.append(int(x))
md['region'] = rn

rn=[]
for x in geo_region:
    rn.append(''.join(x[:].astype(str)).rstrip())
md['geo_region'] = rn

#print("{}".format(time[:]))
# rn=[]
# for x in time[startDate:]:
#     rn.append(int(x))
# md['time'] = rn
md['time']  = 'Not required'


rn = []
for i, x in enumerate(time_bnds[startDate:]):
    ro = {}
    ro['band'] = i
    ro['start'] = int(x[0:1])
    ro['end'] = int(x[1:])
    ro['day'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%d')
    ro['month'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%m')
    ro['year'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%Y')
    rn.append(ro)
md['time_bnds'] = rn
#print(rn)

rn=[]
for i, x in enumerate(tasmax[startDate:]):
    ro = {}
    ro['time_bnd'] = i
    sn = []
    for ii, y in enumerate(x, start = 1):
        so = {}
        #print("{}".format(y))
        so['region'] = ii
        if y is np.ma.masked:
            so['hours'] = 0
        else:
            so['hours'] = y
        sn.append(so)
    ro['regions'] = sn
    rn.append(ro)
    # print(x)
md['tasmax'] = rn
#print(rn)

#print(json.dumps(md, indent=4))
f.close()

print("Writing .json file....")
with open(filename + '.json', 'w', encoding='utf-8') as f:
    json.dump(md, f, ensure_ascii=False, check_circular=True)