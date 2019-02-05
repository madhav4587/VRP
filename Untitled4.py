#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# %load test_address.txt
60
Hyderabad
Calicut| 20
Kochi| 50
Chennai| 40
Mumbai| 35
Kolkata| 20


# In[31]:



import googlemaps
import json
import io
import requests
from datetime import datetime
from operator import itemgetter
import gmplot
import webbrowser
import os
requests.packages.urllib3.disable_warnings()

# Current Time
now = datetime.now()

print "Current Time"
print "============"
print now

# Read Address File
address = []
demand = []
visited = []
C = 0
with open("test_address.txt") as f:
    # First line is Vehicle Capacity
    C = int(f.readline())
    # Other lines are "Address|Demand"
    # First address will be of Depot Address with 0 demand
    data = f.readlines()
    for line in data:
        # Extract Address & Demands
        [adr,dem] = line.strip("\n").split("|")
        address.append(adr)
        demand.append(int(dem))
        visited.append(False)

N = len(address)

print "\nDelivery Information"
print "===================="
print "\nDepot Address = ", address[0]
print "\nVehicle Capacity = ", C

print "\nDelivery Address"
print "================"
print "No of Addresses = ", N-1, "\n"

for x in range(1,N):
    print x, address[x]

# Google Maps API
api_key = 'AIzaSyCYPyNLAA25ZGbe7-gzuipegly6Zjfp6Ko'
gmaps = googlemaps.Client(key= api_key)

# Set Origins and Destinations equal to Address to get Distance Matrix
origins = address
destinations = address
                  
now = datetime.now()
# Get Distance Matrix
matrix = gmaps.distance_matrix(origins, destinations,
                                            mode="driving",
                                            language="en",
                                            avoid="tolls",
                                            units="imperial"
                                            )

print matrix

# Sample write Output in seprate file
with open('json_output.txt','w') as f:
    f.write(unicode(json.dumps(matrix,ensure_ascii=False)))

# Mile list containing mile matrix
print "matrix"+str(matrix)
mile = []
for i in range(N):
    temp = []
    for j in range(N):
        val = matrix['rows'][i]['elements'][j]['distance']['text']
        [m, unit] = val.strip("\n").split(" ")
        if unit != "mi":
            m = 0
        m = int(str(m).replace(',', ''))
        temp.append(float(m))
    mile.append(temp)

# Make the Matrix Symmetric 
for i in range(N):
    for j in range(N):
        val = max(mile[i][j], mile[j][i])
        mile[i][j] = val;
        mile[j][i] = val;

# Calculate the Savings (It will calculate only upper Half as it will be symmetric)
savings_list = []
for i in range (0,N-2):
    for j in range (i, N-1):
        if i != j:
            # Saving = Ci0 + C0j - Cij
            val = mile[i+1][0] + mile[0][j+1] - mile[i+1][j+1]
            savings_list.append([i+1,j+1,val])

# Sort savings pair in Descending Order
sorted_list = sorted(savings_list, key = itemgetter(2), reverse = True)

# Function to calculate the Route Cost
def route_cost(route):
    cost = 0
    cost = cost + mile[0][route[0]]

    for x in range(1,len(route)):
        cost = cost + mile[route[x-1]][route[x]]
    cost = cost + mile[route[len(route)-1]][0]
    return cost

##################################################
# Customized Clarke & Wright's Savings Algorithm
##################################################

total_route = []
# Count will keep track of address remaining to include in the route
count = N-1
while count > 0:
    x = 0
    # starts with empty route
    route = []
    route_demand = 0
    # Passthrough the Savings list
    while x < len(sorted_list):
        if not route:
            # Route is Empty
            p = sorted_list[x][0]
            q = sorted_list[x][1]
            
            # if nodes are not included in any route
            if visited[p] == False and visited[q] == False:
                # Calculate Total Demand of the Route
                total_demand = demand[p] + demand[q]
                if total_demand <= C:
                    # Add this pair in Route
                    route_demand = total_demand
                    route.append(p)
                    route.append(q)
                    # Make the nodes as visited
                    visited[p] = True
                    visited[q] = True
                    #print "Deleting = ", sorted_list[x]
                    del sorted_list[x]
                    x = x - 1
                    count = count - 2
        else:
            # Route is Present
            p = sorted_list[x][0]
            q = sorted_list[x][1]

            # Check left element of pair with first element of route
            # If it matches then check whether right element is not present in the route
            # if it satisfy this condition then we can add the new node q in the route if demand is satisfied
            # for example, Route is 1-5 and pair is [1,2,20] then we can add 2nd node before 1 as 2-1-5 in the route
            if p == route[0]:
                if q not in route: 
                    total_demand = route_demand + demand[q]
                    if total_demand <= C:
                        if visited[q] == False:
                            route.insert(0, q)
                            visited[q] = True
                            route_demand = total_demand
                            #print "Deleting = ", sorted_list[x]
                            del sorted_list[x]
                            x = -1
                            count = count - 1

            # Check left element of pair with last element of route
            # If it matches then check whether right element is not present in the route
            # if it satisfy this condition then we can add the new node q in the route if demand is satisfied
            # for example, Route is 1-5 and pair is [5,4,20] then we can add 4th node after 5 as 1-5-4 in the route
            elif p == route[len(route)-1]:
                if q not in route:
                    total_demand = route_demand + demand[q]
                    if total_demand <= C:
                        if visited[q] == False:
                            route.append(q)
                            visited[q] = True
                            route_demand = total_demand
                            #print "Deleting = ", sorted_list[x]
                            del sorted_list[x]
                            x = -1
                            count = count - 1

            # Check right element of pair with first element of route
            # If it matches then check whether left element is not present in the route
            # if it satisfy this condition then we can add the new node p in the route if demand is satisfied
            # for example, Route is 1-5 and pair is [3,1,20] then we can add 3rd node before 1 as 3-1-5 in the route
            elif q == route[0]:
                if p not in route:
                    total_demand = route_demand + demand[p]
                    if total_demand <= C:
                        if visited[p] == False:
                            route.insert(0, p)
                            visited[p] = True
                            route_demand = total_demand
                            #print "Deleting = ", sorted_list[x]
                            del sorted_list[x]
                            x = -1
                            count = count - 1

            # Check right element of pair with last element of route
            # If it matches then check whether left element is not present in the route
            # if it satisfy this condition then we can add the new node p in the route if demand is satisfied
            # for example, Route is 1-5 and pair is [4,5,20] then we can add 4th node after 5 as 1-5-4 in the route
            elif q == route[len(route)-1]:
                if p not in route:
                    total_demand = route_demand + demand[p]
                    if total_demand <= C:
                        if visited[p] == False:
                            route.append(p)
                            visited[p] = True
                            route_demand = total_demand
                            #print "Deleting = ", sorted_list[x]
                            del sorted_list[x]
                            x = -1
                            count = count - 1
        x = x + 1
    # One Route is calculated and No more demand can be satisfied due to capacity constraint
    # Add the Route, Cost and Demand in the list
    total_route.append([route,route_cost(route),route_demand])

    # Special Case only 1 Node is left in the Route
    if count == 1:
        for x in range(1,N):
            # Find which node is remaining
            if visited[x] == False:
                # Add the Node in the route
                route = [x]
                route_demand = demand[x]
                count = count - 1
                total_route.append([route,route_cost(route),route_demand])





mymap = gmplot.GoogleMapPlotter(17.4548873,78.1374796, 13 ) 

lat = []
lng = []
color = ["yellow", "blue", "magenta", "cyan", "green", "black", "white"]

print address[0], address[1], address[2]

for x in range(0,N):
    val1, val2 = mymap.geocode(address[x], api_key)
    lat.append(val1)
    lng.append(val2)

print "\n\n\n\n\n"+str(lat)+str(lng)
mymap.marker(lat[0], lng[0], "red")

# Print the Route Information
print "\nRoutes"
print "======"
i = 1
for r in total_route:
    print i
    print "route = ",r[0]
    print "route cost = ",r[1], "miles"
    print "demand = ", r[2]
    print ""
    print "\t\t", address[0]
    print "\t\t   |"
    for x in r[0]:
        print "\t\t", address[x]
        print "\t\t   |"
    print "\t\t", address[0]
    print ""
    i = i + 1

# i = 0
# for r in total_route:
#     lat_list = [lat[0]]
#     lng_list = [lng[0]]
#     for x in r[0]:
#         mymap.marker(lat[x], lng[x], color[i%7])
#         lat_list.append(lat[x])
#         lng_list.append(lng[x])
#     lat_list.append(lat[0])
#     lng_list.append(lng[0])
#     path = [lat_list, lng_list]
#     mymap.plot(path[0], path[1], color[i%7], edge_width=5)
#     i = i + 1

mymap.draw("mymap.html")

filename = 'G:\mymap.html'
# webbrowser.open_new_tab(filename)

print "Shortest Path Calculation for Package Delivery Completed Successfully\n"


import gmaps
from datetime import datetime
origin = destination = (17.4548873,78.1374796)
gmaps.configure(api_key=api_key)
fig = gmaps.figure()
now = datetime.now()

stroke_color_arr = ["red", "blue", "yellow", "white", "violet"]
a = 0
for r in total_route:
    waypoints = []
    for x in r[0]:
        waypoints.append((lat[x],lng[x]))
    print str(waypoints)+"\n"
    layer = gmaps.directions.Directions(origin, destination,waypoints = waypoints,optimize_waypoints=True,mode='car',api_key=api_key,departure_time = now,stroke_color=stroke_color_arr[a])
    fig.add_layer(layer)
    a = a+1
fig

    
    



# In[ ]:




