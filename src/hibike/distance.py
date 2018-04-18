from math import pi,sin,cos,acos

def dis(lat1,long1,lat2,long2):
        '''Calculates the distance from a second airport and returns it as a float'''
        
        r_earth=6378.1
        theta1=long1*(2*pi)/360
        theta2=long1*(2*pi)/360
        phi1=(90-lat1)*(2*pi)/360
        phi2=(90-lat2)*(2*pi)/360
        distance=acos(sin(phi1)*sin(phi2)*cos(theta1-theta2)+cos(phi1)*cos(phi2))*r_earth
        return distance

