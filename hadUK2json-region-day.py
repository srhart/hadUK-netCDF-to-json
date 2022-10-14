import netCDF4
import numpy as np
import json
from datetime import datetime, timedelta

epoc = datetime(1800,1,1,0,0,0)
startDate = datetime(2020,1,1,0,0,0)
startH = (startDate - epoc).days * 24
startRow = None
timeData = []
jsonData = None
drnd = 4
vvars = {}

jsonFilename = 'hadukgrid_uk_region_day_from_'+startDate.strftime('%Y%m%d')+'.json'
files = []
file = 0
files.append({'fname':'tasmax_hadukgrid_uk_region_day_19600101-20211231.nc','dim':'tasmax','lname':'Max Temperature C','obsvar':'tmx'})
files.append({'fname':'tasmin_hadukgrid_uk_region_day_19600101-20211231.nc','dim':'tasmin','lname':'Min Temperature C','obsvar':'tmn'})
files.append({'fname':'rainfall_hadukgrid_uk_region_day_18910101-20211231.nc','dim':'rainfall','lname':'Rainfall mm','obsvar':'rnfl'})


def readFile(filename):
    global startRow
    print("Reading file {}".format(filename))
    try:
        f = netCDF4.Dataset(filename)
        # print(f)
        for k in f.variables.keys():
            globals()[k] = f.variables[k]
            vvars[k] = {'dtype' : str(f.variables[k].dtype), 'dimensions' : str(f.variables[k].dimensions), 'attributes' : f.variables[k].__dict__}
    
        for i, x in enumerate(time[:]):
            if (int(x)) >= startH:
                startRow = i
                break
        print("Set start row = {} (for days after {})".format(startRow,(epoc + timedelta(hours=int(x))).strftime('%d-%b-%Y')))
    
    except FileNotFoundError:
        print("File {} not found".format(filename))
        return -1

    return f


def initFile(f):

    global startRow, timeData
    jsonData = {}

    fdata = [{"id":x+1,"name":'unknown'} for x in range(region.size)]
    rgn = 0
    for x in geo_region:
        fdata[rgn]["name"] = format(''.join(x[:].astype(str)).rstrip())
        rgn += 1

    jsonData['geo_region'] = fdata

    #print("{}".format(time[:]))
    # rn=[]
    # for x in time[startDate:]:
    #     rn.append(int(x))
    # md['time'] = rn
    jsonData['time']  = 'Not required'

    for i, x in enumerate(time_bnds[startRow:]):
        ro = {}
        # ro['band'] = i
        # ro['start'] = int(x[0:1])
        # ro['end'] = int(x[1:])
        ro['day'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%d')
        ro['month'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%m')
        ro['year'] = (epoc + timedelta(hours=int(x[0:1]))).strftime('%Y')
        timeData.append(ro)
    jsonData['time_bnds'] = 'Not required'
    #print(tb)
    return jsonData


def updateFile(jsonData, f, observation, obsname, obskey):
    fdata=[]
    if 'observations' in jsonData:
        print("Adding {} observations".format(obsname))
        for i, x in enumerate(observation[startRow:]):
            regions = (jsonData['observations'][i]['regions'])
            for ii, y in enumerate(x):
                if y is np.ma.masked:
                    regions[ii][obskey] = 0
                else:
                    regions[ii][obskey] = round(y,drnd)
        pass
    else:
        print("Creating {} observations".format(obsname))
        for i, x in enumerate(observation[startRow:]):
            ro = {}
            ro['time'] = timeData[i]
            sn = []
            for ii, y in enumerate(x):
                so = {}
                so['region'] = ii + 1 
                if y is np.ma.masked:
                    so[obskey] = 0
                else:
                    so[obskey] = round(y,drnd)
                sn.append(so)
            ro['regions'] = sn
            fdata.append(ro)
            # print(x)
        jsonData['observations'] = fdata
                
    return jsonData

for file in files:
    filename = file['fname']
    f = readFile(filename)
    if f == -1:
        continue
    if jsonData == None:
        jsonData = initFile(f)
    jsonData = updateFile(jsonData, f, eval(file['dim']), file['lname'], file['obsvar'])
    f.close()

print("Writing .json file....")
with open(jsonFilename, 'w', encoding='utf-8') as f:
    json.dump(jsonData, f, ensure_ascii=False, check_circular=True)