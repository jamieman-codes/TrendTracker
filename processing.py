import json
import matplotlib
import matplotlib.pyplot as plt
import tweepy
import requests
from time import sleep
from datetime import datetime

auth = tweepy.OAuthHandler('', '') #Add in own twitter app tokens here
auth.set_access_token('', '')
api = tweepy.API(auth)

def getWOEID(location):
    '''
    Gets the WOEID of a location that Twitter has trends for, closest to the given location
    '''
    location.replace(' ','+') #Replaces spaces in the locations for + so the URL can be formed properly
    completed = False
    attempts = 0
    while not completed:
        try:
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + location) #Gets the lat and long from google maps
            if jsonCheck(response) == True:
                lat= response.json()['results'][0]['geometry']['location']['lat']
                long= response.json()['results'][0]['geometry']['location']['lng']
                return api.trends_closest(lat, long)[0]['woeid'], lat, long #Returns the WOEID of the closest place with trend data
        except IndexError:
            sleep(1) #Sometimes google doesnt return any data, so the request must be sent again
            attempts += 1
            if attempts == 5: #Let it attempt to collect the data twice
                return False

def jsonCheck(response):
    '''
    Checks if the data returned from Google is a json
    There is multiple ways it can do this so all must be checked
    '''
    if 'application/json' in response.headers['Content-Type'] or 'application/javascript' in response.headers['Content-Type'] or 'text/javascript' in response.headers['Content-Type']:
        return True

def getTrendsTwitter(location):
    '''
    Collects the twitter trends from a given WOEID Location
    '''
    trends = api.trends_place(location) #Gets the WOEID
    trendData = {}
    for trend in trends[0]['trends']: 
        if trend['tweet_volume'] != None: #Remove any trends with no information on how many tweets there was
            trendData[trend['name']] = trend['tweet_volume']    
    return trendData
 
def getTrendsGoogleTime(keywordList, timeframe, location = ''):
    '''
    Gather the interest over time trends from Google
    '''
    requestsPayload = {'comparisonItem' : [], 'category' : 0} #Forming the request payload that contains the information about the trends i want to have returned
    for keyword in keywordList:
        requestsPayload['comparisonItem'].append({'keyword': keyword, 'time': timeframe, 'geo': location}) #IF there is more then one trend they must be in the same payload so google can compare the,
    tokenPayload = {'hl' : 'en',
               'tz' : 0,
               'req' : json.dumps(requestsPayload),
               'property': ''} #Form the rest of the payload
    response = requests.get('https://trends.google.com/trends/api/explore', params=tokenPayload) #Send the request to google
    if jsonCheck(response) == True:
        content = json.loads(response.text[4:]) #Trim the excess characters off the response so that it can be interpreted by python properly
        for widgetTemp in content['widgets']:
            if widgetTemp['id'] == 'TIMESERIES': #Selects the interest over time widget
                widget = widgetTemp
        reqJson = json.dumps(widget['request'])
        timePayload = {'req': reqJson,
            'token': widget['token'],
            'tz': 360} #Form the payload that will be sent to gather the trends
        timeResponse = requests.get('https://trends.google.com/trends/api/widgetdata/multiline', params= timePayload) 
        if jsonCheck(timeResponse) == True:
            return json.loads(timeResponse.text[5:])['default']['timelineData'] #Return the interest over time data

def getTrendsGoogleLocation(keyword, location, timeframe = 'today 5-y'):
    '''
    Gather the interest via location trends from Google and return them
    '''
    requestsPayload = json.dumps({'comparisonItem' : [{'keyword': keyword, 'time': timeframe, 'geo': location}], 'category' : 0})#Program will only display 1 trend via location so a list is not needed
    tokenPayload = {'hl' : 'en',
               'tz' : 0,
               'req' : requestsPayload,
               'property': ''
               } #Create payload to use in request
    response = requests.get('https://trends.google.com/trends/api/explore', params=tokenPayload) #Send payload to get widgets 
    if jsonCheck(response) == True:
        content = json.loads(response.text[4:]) #Trim characters
        fristToken = True
        for widgetTemp in content['widgets']:
            if widgetTemp['id'] == 'GEO_MAP' and fristToken: #Checking the widget is correct
                widget = widgetTemp
                fristToken = False
        if location == '': #If the user doesnt set a location this is set to avoid errors
            widget['request']['resolution'] = 'COUNTRY' 
        requestsPayload = json.dumps(widget['request'])  
        locationPayload = {'req' :  requestsPayload,
                           'token' : widget['token'],
                           'tz' : 360} #Create the location payload
        locationResponse = requests.get('https://trends.google.com/trends/api/widgetdata/comparedgeo', params=locationPayload) #Send request
        if jsonCheck(locationResponse) == True:
            return json.loads(locationResponse.text[5:])['default']['geoMapData']
    
def trendsGraphTwitLine(location):
    '''
    Generates a live line graph with multiple data plots on one graph based on twitter trends of a given location
    '''
    plt.cla()
    location, lat, long = getWOEID(location)
    fig = plt.figure(1) #Creating the frame and varibles
    plt.ylabel('Tweet Freq')
    n = 0
    numOfTrends = 1
    trendData = dict()
    trendDataTemp = getTrendsTwitter(location) #Collects the trends from the twitter api and adds them into the dict 
    for trend in trendDataTemp: 
        trendData[trend] = [[trendDataTemp[trend]], [n], numOfTrends]
        numOfTrends += 1
    for x in trendData:
        plt.scatter(trendData[x][1], trendData[x][0], label = trendData[x][2])   
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=10, mode="expand", borderaxespad=0.)    
    return fig, n, trendData, location, numOfTrends, lat, long
    
def updateTwitGraph(n, trendData, location, numOfTrends):
    plt.cla()
    fig = plt.figure(1)
    trendDataTemp = getTrendsTwitter(location) #Get the new trends
    for x in trendDataTemp: 
        if x in trendData.keys(): #If the trend is current add the new value to the list
            trendData[x][0].append(trendDataTemp[x])
            trendData[x][1].append(n)
        else:
            trendData[x] = [[trendDataTemp[x]], [n], numOfTrends] #If the trend is new add it too the dict
            numOfTrends += 1
    for x in trendData: 
        plt.plot(trendData[x][1], trendData[x][0], '.-', label = trendData[x][2])    
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=10, mode="expand", borderaxespad=0.)
    return fig, n, trendData, numOfTrends
  
def locationBarGraph(kw, location):
    '''
    Displays a bar graph of the populuarity of a keyword in different locations
    '''
    trendData = getTrendsGoogleLocation(kw, location)
    trendDataFormatted = {}
    for trend in trendData:
        trendDataFormatted[trend['geoName']] = trend['value'][0]
    fig = plt.figure(1)
    plt.bar(range(len(trendDataFormatted)), trendDataFormatted.values(), align='center')
    plt.xticks(range(len(trendDataFormatted)), trendDataFormatted.keys())   
    plt.title('Popularity of "' +kw +'" ')
    fig.autofmt_xdate() 
    return fig, trendDataFormatted


def timeLineGraph(kw_list, location, tf): #2004-01-01 <-min value
    '''
    Creates a line graph based on the trends over time from google
    '''
    fig = plt.figure(1)
    dateformat = '%d %b %Y'
    trendDataFormatted = dict()
    trendDataTemp = getTrendsGoogleTime(kw_list, tf, location)
    for data in trendDataTemp:
        if type(data['formattedAxisTime']) != float:
            if len(data['formattedAxisTime']) < 7:
                dateformat = '%d %b'
            data['formattedAxisTime'] = datetime.strptime(data['formattedAxisTime'], dateformat)
            data['formattedAxisTime'] = matplotlib.dates.date2num(data['formattedAxisTime'])        
    for keyword in range(len(kw_list)): 
        trendDataFormatted[kw_list[keyword]] = {}
        for data in trendDataTemp:
            trendDataFormatted[kw_list[keyword]][data['formattedAxisTime']] = data['value'][keyword]
    for trend in trendDataFormatted:
        plt.plot_date(trendDataFormatted[trend].keys(), trendDataFormatted[trend].values(), '.-', label = trend)
    fig.autofmt_xdate()
    plt.legend()
    plt.title('Popularity over time') 
    return fig, trendDataFormatted

if __name__ == '__main__':
    fig, a = locationBarGraph('Jonty', '')
    plt.show()
