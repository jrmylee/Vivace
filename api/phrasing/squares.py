import numpy as np
#least squares solution of one line segment
#return a=slope, b=y-intercept, e=square error
def lscoefs(xarr,yarr):
    n = len(xarr)
    fit1 = np.polyfit(xarr, yarr, 2)
    a, b, c = fit1[0], fit1[1], fit1[2]
    e = 0
    for i in range(n):
        poly_val = a*xarr[i] ** 2 + b*xarr[i] + c 
        e += (yarr[i] - poly_val)**2
    return (a,b,c,e)

#precompute all least squares coefs for all pairs of points i <= j
#result is a list of lists, one per j, each entry in sublist is a 
#tuple for an i
#each tuple is the ls coefs a, b and the error, for that segment (i,j)
def precompute(n,xarray,yarray):
    result = [[(0,0,0,10000)], [(0,0,0,1000), (0,0,0,1000)]]
    for j in range(2,n):
        jres = []
        for i in range(0,j+1):
            if n - j >= 2:
                a,b,c,e = lscoefs(xarray[i:j+1],yarray[i:j+1])     
                jres = jres + [(a,b,c,e)]
        if len(jres) > 0:
            result = result + [jres]
    return (result)       

#estimate variance of y array to use in computing segment penalty in
#finding opt solution
def estvariance(n,yarray):
    meany = sum(yarray)/n
    sqrdiffy = [(y-meany)*(y-meany) for y in yarray]
    yvar = sum(sqrdiffy)/n
    return yvar
    
    
#dynamic programming solution using precomputed results
def findopt(n,preresult,C):
    optresult = []  
    for j in range(len(preresult)):
        beste = 9e999
        besti = -1
        jpre = preresult[j]   #list of tuples (a,b,c) for i=0,1,...,j
        #for each possible start i, up to j
        for i in range(0,j+1):
            #get the error assuming using opt to to i-1, and new fit for i..j,
            #with penalty per segment, C
            if (i > 0):
                e = jpre[i][3] + optresult[i-1][0] + C
            else:
                e = jpre[i][3] + C
            #find i with smallest error            
            if (e < beste):
                beste = e
                besti = i
        #create opt entry for j, consisting of min error and list of of (i,j) 
        #this is this a list of (i,j) segments for this j, consisting of
        #the current best (i,j) appended to list from opt[besti-1]
        if (besti > 0):
            optresult = optresult + [[beste, optresult[besti-1][1] + [(besti,j)]]] 
        else:
            optresult = optresult + [[beste, [(besti,j)]]]
    return optresult[n-2]
    
#constuct fitted line from optimum solution 
def constructfit(n,xarray,yarray,preresult,opt):
    yfit = []
    optintervals = opt[1]    #list of tuples (opt has error and list of tuples)
    #for each segment    
    phrases = []
    for interval in optintervals:
        i=interval[0]        #get the segment
        j=interval[1]
        phrases.append((i, j))
        a = preresult[j][i][0]    #get the ls coeffs for the segment
        b = preresult[j][i][1]
        c = preresult[j][i][2]
        xarr = xarray[i:j+1]
        yfit = yfit + [a*x**2 + b*x + c for x in xarr]   #build up fit
    return yfit, phrases
    
    
#segmented least squares
def segls(n,xarray,yarray,Cfactor):
    preresult = precompute(n,xarray,yarray)  #precompute ls coefs and errors
    yvar = estvariance(n,yarray)
    C = Cfactor * yvar                       #penalty for adding segments
    opt = findopt(n,preresult,C)             #optimum solution
    yfit, phrases = constructfit(n,xarray,yarray,preresult,opt)   #compute fit  
    return yfit, phrases