#!/usr/bin/python

####################################################
# Jessy Cowan-Sharp, August 2009
# References:
#   1. DBScan Algorithm, from Data Mining Textbook 
#      (Han and Kamber, Data Mining, Concepts and Techniques, 
#      Second Edition. Chapter 7 section 6.1 (pp.418)). 
#   2. see also wikipedia entry (this implementation is similar to
#      their pseudo code): http://en.wikipedia.org/wiki/DBSCAN
####################################################

# XXX TODO noise cluster is getting duplicates added. the initial
# cluster member is getting repeated sometimes-- it's because the
# point in 'for point in points' is of course a copy. fuckers.

# very code-like pseudo-code
# DBSCAN
# for point in points:
#    if point is visited:
#        continue
#    mark point as visited
#    neighbours = immediate_neighbours(point, epsilon)
#    if len(neighbours) > min_pts:
#        cluster = new_cluster()
#        append point to cluster
#        for n in neighbours:
#            cluster.append(all_neighbours(n))
#    else:
#        mark point as NOISE
#
# def all_neighbours(n, epsilon, cluster):
#     for point in points:
#         if point has not been visited:
#             mark point as visited
#             new_points = immediate_neighbours(point)
#             if len(new_points) > min_pts:
#                 points.append(new_points)
#         if point is not member of any cluster:
#             append point to cluster

from math import pow, sqrt

class Point(object):
    ''' internal helper class to support algorithm implementation'''
    def __init__(self,feature_vector):
        # feature vector should be something like a list or a numpy
        # array
        self.feature_vector = feature_vector
        self.cluster = None
        self.visited = False

    def __str__(self):
        return str(self.feature_vector)

def _as_points(points):
    ''' convert a list of list- or array-type objects to internal
    Point class'''
    return [Point(point) for point in points]

def as_lists(clusters):
    ''' converts the Points in each cluster back into regular feature
    vectors (lists).'''
    clusters_as_points = {}
    for cluster, members in clusters.iteritems():
        clusters_as_points[cluster] = [member.feature_vector for member in members]
    return clusters_as_points

def print_points(points):
    ''' a wierd klugey function for printing lists of points. ''' 
    s = ''
    for p in points:
        s += str(p) + '\n'
    return s[:-2]

def euclidean(x,y):
    ''' calculate the euclidean distance between x and y.'''
    # sqrt((x0-y0)^2 + ... (xN-yN)^2)
    assert len(x) == len(y)
    sum = 0.0
    for i in xrange(len(x)):
        sum += pow(x[i] - y[i],2)
    return sqrt(sum)

def immediate_neighbours(point, all_points, epsilon, distance, debug):
    ''' find the immediate neighbours of point.'''
    # XXX TODO: this is probably a stupid way to do it; if we could
    # use a grid approach it should make this much faster.
    neighbours = []
    for p in all_points:
        if p == point:
            # you cant be your own neighbour...!
            continue
        d = distance(point.feature_vector,p.feature_vector)
        if d < epsilon:
            neighbours.append(p)
    return neighbours

def add_connected(points, all_points, epsilon, min_pts, current_cluster, distance, debug):
    ''' find every point in the set of all_points which are
    density-connected, starting with the initial points list. '''
    cluster_points = []
    for point in points:
        if not point.visited:
            point.visited = True
            new_points = immediate_neighbours(point, all_points, epsilon, distance, debug)
            if len(new_points) >= min_pts:                                
                # append any new points on the end of the list we're
                # already iterating over.
                for p in new_points:
                    if p not in points:
                        points.append(p)

        # here, we separate 'visited' from cluster membership, since
        # 'visited' only helps keep track of if we've checked this
        # point for neighbours. it may or may not have been assessed
        # for cluster membership at that point.
        if not point.cluster:
            cluster_points.append(point)
            point.cluster = current_cluster
    if debug: 
        print 'Added points %s' % print_points(cluster_points)
    return cluster_points

def dbscan(points, epsilon, min_pts, distance=euclidean, debug=False):
    ''' Main dbscan algorithm function. pass in a list of feature
    vectors (most likely a list of lists or a list of arrays), a
    radius epsilon within which to search for neighbouring points, and
    a min_pts, the minimum number of neighbours a point must have
    within the radius epsilon to be considered connected. the default
    distance metric is euclidean, but another could be used as
    well. your custom distance metric must accept two equal-length
    feature vectors as input as return a distance value. pass in
    debug=True for verbose output.''' 

    assert isinstance(points, list)
    epsilon = float(epsilon)
    if not isinstance(points[0], Point):
        # only check the first list instance. imperfect, but the lists
        # could be arbitrarily long.
        points = _as_points(points)

    if debug:
        print '\nEpsilon: %.2f' % epsilon
        print 'Min_Pts: %d' % min_pts
    
    clusters = {}     # each cluster is a list of points
    clusters[-1] = [] # store all the points deemed noise here. 
    current_cluster = -1
    for point in points:
        if not point.visited:
            point.visited = True
            neighbours = immediate_neighbours(point, points, epsilon, distance, debug)
            if len(neighbours) >= min_pts:
                current_cluster += 1
                if debug: 
                    print '\nCreating new cluster %d' % (current_cluster)
                    print '%s' % str(point)
                point.cluster = current_cluster                
                cluster = [point,]
                cluster.extend(add_connected(neighbours, points, epsilon, min_pts, 
                                             current_cluster, distance, debug))
                clusters[current_cluster] = cluster
            else:
                clusters[-1].append(point)
                if debug: 
                    print '\nPoint %s has no density-connected neighbours.' % str(point.feature_vector)

    # return the dictionary of clusters, converting the Point objects
    # in the clusters back to regular lists
    return as_lists(clusters)

if __name__ == '__main__':

    import random

    epsilon = 2.0
    min_pts = 2.0
    points = []
    points.append([1,1])
    points.append([1.5,1])
    points.append([1.8,1.5])
    points.append([2.1,1])
    points.append([3.1,2])
    points.append([4.1,2])
    points.append([5.1,2])
    points.append([10,10])
    points.append([11,10.5])
    points.append([9.5,11])
    points.append([9.9,11.4])
    points.append([15.0, 17.0])
    points.append([15.0, 17.0])
    points.append([7.5, -5.0])

    clusters = dbscan(points, epsilon, min_pts, debug=True)
    print '\n========== Results of Clustering ============='
    for cluster, members in clusters.iteritems():
        print '\n--------Cluster %d---------' % cluster
        for point in members:
            print point

    points = []
    for i in xrange(100):
        points.append([random.uniform(0.0, 20.0), random.uniform(0.0, 20.0)])

    clusters = dbscan(points, epsilon, min_pts, debug=True)
    print '\n========== Results of Clustering ============='
    for cluster, members in clusters.iteritems():
        print '\n--------Cluster %d---------' % cluster
        for point in members:
            print point
