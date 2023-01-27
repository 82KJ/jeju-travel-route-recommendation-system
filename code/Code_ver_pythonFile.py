import requests
import json
import time
import sys
import csv
from copy import deepcopy

class TouristAttraction:
    def __init__(self, name, address, priority, stayTime):
        self.name = name
        self.address = address
        self.priority = priority
        self.stayTime = stayTime

def generateGraph(attrList):
    attrCnt = len(attrList)
    graph = [[0 for _ in range(attrCnt)] for _ in range(attrCnt)]
    for i in range(attrCnt):
        origins = attrList[i].address
        for j in range(attrCnt):
            if i == j:
                continue
            destinations = attrList[j].address
            url = (
                "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&mode=transit&origins="
                + origins
                + "&destinations="
                + destinations
                + "&region=KR&key=AIzaSyBT0UwFPLEkNNQf6o41xzSaH03twY6Aczw"
            )
            response = requests.request("GET", url, headers={}, data={})
            data = json.loads(response.text)
            
            if data["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
                graph[i][j] = 0
            else:
                duration = data["rows"][0]["elements"][0]["duration"]["text"]

                hour = 0
                minute = 0
                temp = ''
                for x in duration:
                    if x == 'h':
                        hour = temp
                        temp = ''
                    elif x == 'm':
                        minute = temp
                        temp = ''
                    elif x.isdigit():
                        temp += x
                hour = int(hour)
                minute = int(minute) + 60 * hour

                graph[i][j] = minute
            
    return graph

def getShortestInBF(totalList, graph):
    attrCnt = len(totalList)
    minTime = sys.maxsize
    path = [0]
    minPath = []

    def find_path(here, visited, duration):
        nonlocal minTime, minPath, path, attrCnt
        if visited == (1 << attrCnt) - 1:
            temp = duration + graph[here][0]
            if minTime > temp:
                minTime = temp
                minPath = deepcopy(path)
                minPath.append(0)
            return

        for i in range(attrCnt):
            if visited & (1 << i) == 0:
                path.append(i)
                find_path(i, visited | (1 << i), duration + graph[here][i])
                del path[-1]

    find_path(0, 1 << 0, 0)
    
    for attr in totalList:
        minTime += attr.stayTime

    return minPath, minTime

def getShortestInDP(totalList, graph):
    attrCnt = len(totalList)
    memo = [[sys.maxsize] * (1 << attrCnt) for row in range(attrCnt)]
    minPath = []

    def getMinTime(start, visited, list):
        nonlocal memo, graph, attrCnt
        if visited == (1 << attrCnt) - 1:
            memo[start][visited] = graph[start][0]
            return graph[start][0]

        if memo[start][visited] != sys.maxsize:
            return memo[start][visited]

        for i in range(1, attrCnt):
            if visited & (1 << i):
                continue
            memo[start][visited] = min(
                memo[start][visited],
                getMinTime(i, visited | (1 << i), list) + graph[start][i],
            )

        return memo[start][visited]

    def getShortest(here, visited):
        nonlocal memo, minPath, attrCnt, graph
        minPath.append(here)

        if visited == (1 << attrCnt) - 1:
            minPath.append(0)
            return
        nextvalue = [sys.maxsize, 0]
        for i in range(attrCnt):
            if visited & (1 << i):
                continue
            if (graph[here][i] + memo[i][visited | (1 << i)]) < nextvalue[0]:
                nextvalue[0] = graph[here][i] + memo[i][visited | (1 << i)]
                nextvalue[1] = i

        getShortest(nextvalue[1], visited | (1 << nextvalue[1]))

    minTime = getMinTime(0, 1 << 0, totalList)
    getShortest(0, 1 << 0)
    for attr in totalList:
        minTime += attr.stayTime

    return minPath, minTime


def getShortestIn2opt(totalList, graph):
    def calcTime(path):
        total = 0
        for x in path:
            total += x.stayTime
        for i in range(len(path) - 1):
            total += graph[totalList.index(path[i])][totalList.index(path[i + 1])]
        total += graph[totalList.index(path[-1])][0]
        return total

    def swapPath(path, left, right):
        reversedPath = []

        for i in range(0, left):
            reversedPath.append(path[i])
        for i in range(left, right + 1):
            reversedPath.append(path[(left + right) - i])
        for i in range(right + 1, len(path)):
            reversedPath.append(path[i])

        return reversedPath

    attrCnt = len(totalList)
    org = calcTime(totalList)
    orgPath = totalList
    best = org
    bestPath = totalList
    while True:
        for i in range(attrCnt - 1):
            if i == 0:
                continue
            for j in range(i, attrCnt - 1):
                if i == j:
                    continue
                pathTemp = swapPath(orgPath, i, j)
                temp = calcTime(pathTemp)
                if temp < best:
                    best = temp
                    bestPath = pathTemp

        if best < org:
            org = best
            orgPath = bestPath
        else:
            minPath = []
            for i in bestPath:
                minPath.append(totalList.index(i))
            minPath.append(0)
            return minPath, best


def print_path(totalList, path):
    for x in path:
        print(totalList[x].name, end= " ")


def getCombinations(arr, r):    
    res = []
    if r == 0:
        return [[]]
    
    for i in range(0, len(arr)):
        ele = arr[i]
        rest_arr = arr[i+1:]
        for combi in getCombinations(rest_arr, r-1):
            res.append([ele]+combi)
    return res


def getCandidateIdxList(touristAttractionList, cnt, graph):
    idx_list = [ i for i in range(1,cnt)]
    candidateIdxList = []
    for i in range(1, cnt-1):
        combination_list = getCombinations(idx_list,i)
        for x in combination_list:
            candidateIdxList.append(list(x))
    
    for a in candidateIdxList:
        prior = 0
        for b in a:
            prior += touristAttractionList[b].priority
        a.append(prior)
    
    candidateIdxList.sort(key=lambda x:-x[-1])
    
    newTouristAttracionList = []
    for candidate in candidateIdxList:
        candidate.pop()
        candidate.insert(0,0)
        tempList = []
        for idx in candidate:
            tempList.append(touristAttractionList[idx])
        
        newTouristAttracionList.append(tempList)
    
    newGraphList = []
    for candidateIdx in candidateIdxList:
        newGraph = [[0 for _ in range(len(candidateIdx))] for _ in range(len(candidateIdx))]
        for i in range(len(candidateIdx)):
            for j in range(len(candidateIdx)):
                if i == j : continue
                newGraph[i][j] = graph[candidateIdx[i]][candidateIdx[j]]
        newGraphList.append(newGraph)
    
    return newTouristAttracionList, newGraphList


#===================================================================================
# Body

# 1. Read CSV file & Save nameList, addressList
csvReader = csv.reader(open("allAttr.csv", "r", encoding="utf-8"))
nameList = []
addressList = []

for row in csvReader:
    nameList.append(row[0])
    addressList.append(row[1])


# 2-1. 지정된 Input 사용하기 --> 지정된 testcase를 바로 실행합니다. 
# Input을 직접 입력을 원하시면, 해당 영역을 주석지정하시고 2-2의 주석을 해제해주세요
startIndex = 302  #제주다이브 게스트하우스
attrIndexList = [712, 529, 270, 369, 391, 989] # 서귀포자연휴양림, 천제연폭포, 갯깍주상절리, 정방폭포, 이중섭거주지, 오설록티뮤지엄
attrPriorityList = [3, 1, 5, 1, 2, 5]
attrStaytimeList = [200, 20, 20, 20, 30, 60]
allocationTime = 600
attrList = []

csvReader = csv.reader(open("allAttr.csv", "r", encoding="utf-8"))
rowCnt = 1
inputCnt = 0
for row in csvReader:
    if rowCnt in attrIndexList:
        attrList.append(
            TouristAttraction(
                row[0], row[1].replace(" ", "%20"), attrPriorityList[inputCnt], attrStaytimeList[inputCnt]
            )
        )
        inputCnt += 1
    if rowCnt == startIndex:
        startPoint = TouristAttraction(row[0], row[1].replace(" ", "%20"), sys.maxsize, 0)
    rowCnt += 1
totalList = [startPoint]
totalList.extend(attrList)


# 2-2. Input 직접 입력하기 --> 직접 입력을 원하시면 주석을 해제해주세요
# search_name = ""
# attrList = []
# while True:
#     search_name = input("시작 관광지, 숙박지 이름을 입력하세요 : ")
#     is_answer_true = False
#     is_search_true = False
    
#     for idx, name in enumerate(nameList):
#         if search_name == name:
#             is_search_true = True
#             print(f"{name} : {addressList[idx]}")
#             answer = input("해당 지점을 시작 지점을 지정하시겠습니까? (y/n) ")
            
#             if answer == "y":
#                 startPoint = TouristAttraction(name, addressList[idx].replace(" ", "%20"), sys.maxsize, 0)
#                 is_answer_true = True
#                 break
            
#             else:
#                 break
#     if is_search_true == False:
#         print("해당 지점은 존재하지 않습니다. 다시 검색해 주시기 바랍니다")
#         continue
    
#     if is_answer_true == True :
#         break
                
# while True:
#     search_name = input("\n관광지 이름을 입력하세요 : ")
#     is_search_true = False

#     for idx, name in enumerate(nameList):
#         if search_name == name:
#             is_search_true = True

#             print(f"{name} : {addressList[idx]}")
#             answer = input("해당 관광지를 추가하시겠습니까 ? (y/n) ")
            
#             if answer == "y":
#                 priority = int(input("관광지 우선 순위를 입력하세요 : "))
#                 stayTime = int(input("관광지에서 머무를 시간을 입력하세요 : "))
#                 attrList.append(TouristAttraction(name, addressList[idx].replace(" ", "%20"), priority, stayTime))
#                 break
            
#             else:
#                 break
#     if is_search_true == False:
#         print("해당 지점은 존재하지 않습니다. 다시 검색해 주시기 바랍니다")
#         continue
    
#     if answer == "n": continue
    
#     continuing = input("관광지를 더 추가하시겠습니까 ? (y/n)")
    
#     if continuing == "n":
#         break

# totalList = [startPoint]
# totalList.extend(attrList)

# allocationTime = int(input("전체 제한 시간을 입력하세요 : "))


# 3. Get Graph
for i in totalList:
    print(i.name, end = " ")

start = time.time()
graph = generateGraph(totalList)
end = time.time()
print(f"\ngraph construction time : {end - start:.5f} sec\n")

print(graph)

# 4. Apply Brute Force
print("\n\nBrute Force:")
start = time.time()
bfPath, bf = getShortestInBF(totalList, graph)
end = time.time()
print_path(totalList, bfPath)
print(f"\n전체시간 : {bf}")
print(f"{end - start:.5f} sec\n")


# 5. Apply Dynamic Programming
print("Dynamic Programming:")
start = time.time()
dpPath, dp = getShortestInDP(totalList, graph)
end = time.time()
print_path(totalList, dpPath)
print(f"\n전체시간 : {dp}")
print(f"{end - start:.5f} sec\n")


# 6. Apply 2-opt
print("2-opt heuristic:")
start = time.time()
optPath, opt = getShortestIn2opt(totalList, graph)
end = time.time()
print_path(totalList,optPath)
print(f"\n전체시간 : {opt}")
print(f"{end - start:.5f} sec\n")
print(f"2-opt 오차: {opt - bf}\n")

# 7. Get Result
print(f"할당된 시간: {allocationTime}분\n")
if allocationTime >= bf:
    print("모든 관광지 탐색 가능")
else:
    print("모든 관광지 탐색 불가능")

print("가장 짧은 경로 :", end=" ")
for idx in bfPath:
    print(totalList[idx].name, end=" ")
print(f"\n총 소요 시간 : {bf}분")

# 8. if dp time > alloc time --> Get New Path
if dp > allocationTime:
    candidateList, newGraph = getCandidateIdxList(totalList, len(totalList), graph)
    
    graph_idx = 0
    for candidate in candidateList:
        minPath, minTime = getShortestInDP(candidate, newGraph[graph_idx])
        if minTime <= allocationTime:
            print("\n모든 관광지 탐색 가능")
            print("가장 짧은 경로 :", end=" ")
            for idx in minPath:
                print(candidate[idx].name, end=" ")
            print(f"\n총 소요 시간 : {minTime}분")
            break
        graph_idx += 1

# 9. if bf time > alloc time --> Get New Path
if bf > allocationTime:
    candidateList, newGraph = getCandidateIdxList(totalList, len(totalList), graph)
    
    graph_idx = 0
    for candidate in candidateList:
        minPath, minTime = getShortestInBF(candidate, newGraph[graph_idx])
        if minTime <= allocationTime:
            print("\n모든 관광지 탐색 가능")
            print("가장 짧은 경로 :", end=" ")
            for idx in minPath:
                print(candidate[idx].name, end=" ")
            print(f"\n총 소요 시간 : {minTime}분")
            break
        graph_idx += 1

# 10. if 2opt time > alloc time --> Get New Path
if opt > allocationTime:
    candidateList, newGraph = getCandidateIdxList(totalList, len(totalList), graph)
    
    graph_idx = 0
    for candidate in candidateList:
        minPath, minTime = getShortestIn2opt(candidate, newGraph[graph_idx])
        if minTime <= allocationTime:
            print("\n모든 관광지 탐색 가능")
            print("가장 짧은 경로 :", end=" ")
            for idx in minPath:
                print(candidate[idx].name, end=" ")
            print(f"\n총 소요 시간 : {minTime}분")
            break
        graph_idx += 1