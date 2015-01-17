from math import sqrt
import copy

"""
@desc get the neighbours of a user
@param prefs user-item matrix
userid id of a user
productid id of a product
n number of neighbours
@return neighbours list
"""
def getNeighbours(prefs,userid,productid, n=5):
    orgscores = [(similarity(prefs,userid,other),other)
                for other in prefs if other != userid]
    # remove neighbours which do not have read the products[productid]
    scores = {}
    for sim, userid in orgscores:
        if productid in prefs[userid].keys():
            scores[userid] = sim
    # sort the neighbours by similarity
    scores = sorted(scores.items(), key=lambda d:d[1])
    scores.reverse()
    return scores[0:n]

"""
@desc calculate the similarity by Pearson correlation coefficient
@param prefs user-item matrix
p1 userid`
p1 the other userid
@return similarity value
"""
def similarity(prefs,p1,p2):
    #Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    #if they are no rating in common, return 0
    if len(si) == 0:
        return 0

    #sum calculations
    n = len(si)

    #sum of all preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    #Sum of the squares
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    #Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    #Calculate r (Pearson score)
    num = pSum - (sum1 * sum2/n)
    den = sqrt((sum1Sq - pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))

    if den == 0:
        return 0
    r = num/den

    # if r is negative, make it 0
    if r < 0:
        r = 0
    return r

"""
@desc convert the rating scale
@param rating rating value
@return rating value in new scale
"""
def convertScale(rating):
    scale = {
        '0': -1,
        '-5': 0.00,
        '-3': 0.25,
        '1': 0.50,
        '3': 0.75,
        '5': 1.00,
    }
    return scale[rating]

"""
@desc load the data file
@param path dir path of the datafile
return testPrefs test dataset dict
prefs dataset dict
users user list
products product list
"""
def loadDataset(path=""):
    # load the products info
    products = []
    for line in open(path+"products_list.txt"):
        line = line.strip('\n').strip()
        products.append(line)
    # load the user product rating
    testPrefs = {}
    prefs = {}
    users = []
    index = 1
    userid = 0
    for line in open(path+"products_ratings.txt"):
        line = line.strip('\n').strip()
        # odd lines are usernames
        if index % 2 == 1:
            users.append(line)
            index += 1
            continue
        # even lines are ratings
        ratings = line.split(" ")
        testRatings = {}
        allRatings = {}
        count = 0
        productid = 0
        valid = 0
        for rating in ratings:
            # use two points with smallest IDs as test dataset
            if rating != '0' and count < 2:
                testRatings[productid] = convertScale(rating)
                allRatings[productid] = convertScale(rating)
                count += 1
            else:
                if rating != '0':
                    valid = 1
                    allRatings[productid] = convertScale(rating)
            productid += 1
        if valid == 1:
            testPrefs[userid] = testRatings
        # user product rating, delete the ratings of products that user have never read
        prefs[userid] = allRatings
        userid += 1
        index += 1
    return testPrefs,prefs,users,products

"""
@desc: predict the rating possibly given by a user
@param: prefs user-item matrix
userid id of a user
productid id of a product
neighbours top N nearest to user[userid]
@return rating value
"""
def predict(prefs, userid, productid, neighbours):
    sumSim = 0
    for uid, sim in neighbours:
        sumSim += sim
    if sumSim == 0:
        return -1
    weight = {}
    rating = 0
    for uid, sim in neighbours:
        weight[uid] = sim/sumSim
        if productid in prefs[uid].keys():
            if prefs[uid][productid] != -1:
                rating += prefs[uid][productid] * weight[uid]
    return rating
"""
@desc: remove user[userid]'s ratings of two products
in prefs to generate train preferences
@param: prefs user-items matrix
userid id of a user
items items to be removed
@return: train dataset dict
"""
def generateTrainPrefs(prefs, userid, items):
    trainPrefs = copy.deepcopy(prefs)
    for key in items.keys():
        trainPrefs[userid].pop(key)
    return trainPrefs

"""
calculate root mean square error
@param predictRatings predict ratings dict
realRatings test ratings dict
@return rmse value
"""
def rmse(predictRatings, realRatings):
    predictRatingList = []
    f1=open('./predict_rating_list.txt', 'w+')
    print >>f1 ,"user_id product_id predicted_rating"
    for userid, items in predictRatings.items():
        for itemid, value in items.items():
            predictRatingList.append(value)
            print >> f1 ,userid,itemid,value 

    realRatingList = []
    f2=open('./real_rating_list.txt', 'w+')
    print >>f2 ,"user_id product_id orignal_rating"
    for userid, items in realRatings.items():
        for itemid, value in items.items():
            realRatingList.append(value)
            print >> f2 ,userid,itemid,value 
    # print zip(predictRatingList, realRatingList)
    return sqrt(sum([(f - o) ** 2 for f, o in zip(predictRatingList, realRatingList)]) / len(predictRatingList))

"""
@desc evaluation by collaborative filtering method
@param testPrefs test dataset
prefs complete dataset
neighbour_num number of neighbours
"""
def evaluation_cf(testPrefs, prefs, neighbour_num = 5):
    ratings = {}
    missUser = []
    validTestPrefs = {}
    for userid in testPrefs.keys():
        trainPrefs = generateTrainPrefs(prefs, userid, testPrefs[userid])
        ratings.setdefault(userid, {})
        for productid in testPrefs[userid].keys():
            neighbours = getNeighbours(trainPrefs, userid, productid, neighbour_num)
            ratings[userid][productid] = predict(trainPrefs, userid, productid, neighbours)
            """
some users might always get 0 similarity
in this case, they cannot get prediction
"""
            if ratings[userid][productid] == -1:
                ratings.pop(userid)
                missUser.append(userid)
                break
        validTestPrefs[userid] = testPrefs[userid]
    return rmse(ratings, validTestPrefs)

if __name__ == '__main__':
    testPrefs,prefs,users,_ = loadDataset("")
    f3=open('./rmse_result.txt', 'w+')
    print >>f3 ,"RMSE 5 neighbors", evaluation_cf(testPrefs, prefs, 5);
    print >>f3 ,"RMSE 10 neighbors",evaluation_cf(testPrefs, prefs, 10);
    
    
"""
RMSE for CF(10) method: 0.323508363794
"""
