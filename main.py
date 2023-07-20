import requests
import json
import re

def main():


    familyListObject, individualsList = familyHelper("Porter-22228", "Porter-20216", "ThomasPorter_HaroldPorter.json")
    printUnionFamilyList(familyListObject,individualsList, "PorterAncestors.json")

def familyHelper(genStart, genEnd, fullSiblings=False):

    meAncestors = getAncestors(genEnd)
    familyListObject, individualsList = parseAncestors(meAncestors)
    print("FamilyListOBject: "  + str(familyListObject))
    familyListObject, individualsList = findFamiliesForIndis(familyListObject, individualsList)
    return familyListObject, individualsList

def findFamiliesForIndis(familyListObject, individiualsList):

    #Initialize all to empty fams
    for i in individiualsList:
        i['fams'] = []

    #remove fams with empty parents
    newFamilyListObject = familyListObject
    familyListObject = []
    for fam in newFamilyListObject:
        if fam['husb'] != "0" or fam['wife'] != '0':
            familyListObject.append(fam)
            


    for indi in individiualsList:
        foundFam = False
        for fam in familyListObject:
            if indi['id'] in fam['children']:
                indi['famc'] = fam['id']
            if indi['id'] in fam['husb'] or indi['id'] in fam['wife']:
                foundFam = True
                
                if 'fams' in indi:
                    indi['fams'].append(fam['id'])
                    
        if not foundFam:
            print("Indi family not found for: " + str(indi))
    return familyListObject,individiualsList 

def printUnionFamilyList(topDownList, bottomUpList, dataOutFName):

    print("Descendants of Thomas")
    for item in topDownList:
        print(item)

    print("Ancestors of Blair")
    for item in bottomUpList[0]:
        print(item)

    dupBottomUpList = bottomUpList


    returnedData = {
            "fams": topDownList,
            "indis": bottomUpList,
    }

    
    returnedData = json.loads(str(returnedData).replace("\'", "\""))
    writeJSONToFile(returnedData, dataOutFName)




def createSmallFamily(inputFamiliesList, currentFamIter, currentUnknownPersonIter, possiblePersonsIDs, person):

    currentFamIter += 1
    #Just the Definites
    if  str(person["Mother"]) == "0" and str(person["Father"]) == "0" and str(person['Mother']) in possiblePersonsIDs and str(person['Father']) in possiblePersonsIDs:
        currentUnknownPersonIter += 2
        newFam = {
                "id":  str(currentFamIter) ,
                "husb": str(person["Father"]),
                "wife": str(person["Mother"]) ,
                "children": [ str(person["Id"]) ]
        }

        inputFamiliesList.append(newFam)

        return inputFamiliesList, currentFamIter, currentUnknownPersonIter
    
    else:

        newFam = {
                "id":  str(currentFamIter) ,
                "children": [ str(person["Id"]) ]
        }

        #Just The Mother
        if str(person["Mother"]) != "0" and str(person['Mother']) in possiblePersonsIDs :
            newFam["wife"] = str(person["Mother"])
        else:
            # if str(person["Mother"]) not in possiblePersonsIDs:
            #     newFam["wife"] = "0" 
            # else:
            #     currentUnknownPersonIter += 1
            #     newFam["wife"] =  str(currentUnknownPersonIter)
            currentUnknownPersonIter += 1
            newFam["wife"] =  str(currentUnknownPersonIter)

        
        #Just The Father
        if str(person["Father"]) != "0" and str(person['Father']) in possiblePersonsIDs :
            newFam["husb"] = str(person["Father"])
        else:
            # if str(person["Father"]) not in possiblePersonsIDs:
            #     newFam["husb"] = "0" 
            # else:
            #     currentUnknownPersonIter += 1
            #     newFam["husb"] =  str(currentUnknownPersonIter)
            currentUnknownPersonIter += 1
            newFam["husb"] =  str(currentUnknownPersonIter)

        inputFamiliesList.append(newFam)

        return inputFamiliesList, currentFamIter, currentUnknownPersonIter
    

def createIndividual(inputIndisList, person, numPersons=None, unknownPersonIter=None):

    #Create Unknown Parent first
    if unknownPersonIter is not None:
        if numPersons==1: 
            if person['Mother'] == 0:
                    indi = {
                            "id":  str(unknownPersonIter) ,
                            "firstName": str("Unknown") ,
                            "lastName": str("Person") ,
                            #"sex": str(person['Gender']), 
                            "husb": str(person['Father'])
                    }
            elif person['Father'] == 0:
                    indi = {
                            "id":  str(unknownPersonIter) ,
                            "firstName": str("Unknown") ,
                            "lastName": str("Person") ,
                            #"sex": str(person['Gender']), 
                            "wife": str(person['Mother'])
                    }
            inputIndisList.append(indi)
        else: 
            indi = {
                    "id":  str(unknownPersonIter-1) ,
                    "firstName": str("Unknown") ,
                    "lastName": str("Person") ,
                    #"sex": str(person['Gender']), 
                    "husb": str(person['Father'])
            }
            inputIndisList.append(indi)
            indi = {
                    "id":  str(unknownPersonIter) ,
                    "firstName": str("Unknown") ,
                    "lastName": str("Person") ,
                    #"sex": str(person['Gender']), 
                    "wife": str(person['Mother'])
            }
            inputIndisList.append(indi)

    
    if "FirstName" in person:
        if person['Gender'] == "Male":
            if len(person['Spouses']) > 0:
                firstSpouse = getListOfKeys(person['Spouses'])[0]
                indi = {
                        "id":  str(person["Id"]) ,
                        "firstName": str(person["FirstName"]) ,
                        "lastName": str(person["LastNameAtBirth"]) ,
                        "sex": str(person['Gender']), 
                        "wife": str(person['Spouses'][firstSpouse]['Id'])
                        
                }
            else:
                indi = {
                        "id":  str(person["Id"]) ,
                        "firstName": str(person["FirstName"]) ,
                        "lastName": str(person["LastNameAtBirth"]) ,
                        "sex": str(person['Gender']), 
                }
        else:
            if len(person['Spouses']) > 0:
                firstSpouse = getListOfKeys(person['Spouses'])[0]
                indi = {
                        "id":  str(person["Id"]) ,
                        "firstName": str(person["FirstName"]) ,
                        "lastName": str(person["LastNameAtBirth"]) ,
                        "sex": str(person['Gender']),                        
                        "husb": str(person['Spouses'][firstSpouse]['Id'])

                }
            else:
                indi = {
                        "id":  str(person["Id"]) ,
                        "firstName": str(person["FirstName"]) ,
                        "lastName": str(person["LastNameAtBirth"]) ,
                        "husb": str(person['Gender']), 
                }

    else:
        indi = {
                "id":  str(person["Id"]) ,
                "firstName": "InvestigateFName" ,
                "lastName": "investigateLName" ,
                "sex": "Male" 
        }
        print("Error on: " + str(person))

    if person["BirthDate"] != "" and person["DeathDate"] != "":
        #Birth
        birthdate = person["BirthDate"]
        reBirth = re.search("(.*)-(.*)-(.*)", birthdate)
        reBirthYear = reBirth.group(0)
        reBirthMonth = reBirth.group(1)
        reBirthDay = reBirth.group(2)


        indi["birth"] = {
            "date": {
            }
        }
        indi["birth"]["date"]["year"] = str(reBirthYear)
        if reBirthMonth != "00":
            indi["birth"]["date"]["month"] = reBirthMonth
        if reBirthDay != "00":
            indi["birth"]["date"]["day"] = reBirthDay

        #Death
        deathdate = person["DeathDate"]
        reDeath = re.search("(.*)-(.*)-(.*)", deathdate)
        reDeathYear = reDeath.group(0)
        reDeathMonth = reDeath.group(1)
        reDeathDay = reDeath.group(2)


        indi["death"] = {
            "confirmed": "true",
            "date": {
            }
        }
        indi["death"]["date"]["year"] = str(reDeathYear)
        if reDeathMonth != "00":
            indi["death"]["date"]["month"] = reDeathMonth
        if reDeathDay != "00":
            indi["death"]["date"]["day"] = reDeathDay

    elif person["BirthDate"] != "" and person["DeathDate"] == "":
        #Birth
        birthdate = person["BirthDate"]
        reBirth = re.search("(.*)-(.*)-(.*)", birthdate)
        reBirthYear = reBirth.group(0)
        reBirthMonth = reBirth.group(1)
        reBirthDay = reBirth.group(2)


        indi["birth"] = {
            "date": {
            }
        }
        indi["birth"]["date"]["year"] = str(reBirthYear)
        if reBirthMonth != "00":
            indi["birth"]["date"]["month"] = reBirthMonth
        if reBirthDay != "00":
            indi["birth"]["date"]["day"] = reBirthDay

        #Death
        indi["death"] = {"confirmed": "true"}
    elif person["BirthDate"] == "" and person["DeathDate"] != "":
        #Death
        indi["death"] = {
            "confirmed": "true",

        }
        

    inputIndisList.append(indi)

    return inputIndisList 
    

def parseAncestors(apiResponse):

    currentFamIter = 1
    currentUnknownPersonIter = 999
    familyList = []
    indisList = []

    apiResponse = getJSONObject(apiResponse)
    #Create a list of all posible iDs
    allPersonIds = []
    for resp in apiResponse[0]["ancestors"]:
        allPersonIds.append(str(resp["Id"]))

    for resp in apiResponse[0]["ancestors"]:
        
        ancId = str(resp["Id"])
        wikitreeId= str(resp["Name"])
        
        newResp = getAspectsOfPerson(wikitreeId)
        newResp = getJSONObject(newResp)[0]["person"]
        print(newResp)
        familyList, currentFamIter, newUnknownPersonIter = createSmallFamily(familyList, currentFamIter, currentUnknownPersonIter, allPersonIds, resp)
        if currentUnknownPersonIter < newUnknownPersonIter:
            indisList = createIndividual(indisList, newResp, numPersons=newUnknownPersonIter-currentUnknownPersonIter, unknownPersonIter=newUnknownPersonIter)
            currentUnknownPersonIter = newUnknownPersonIter
        else:

            indisList = createIndividual(indisList, newResp)
               

    return familyList, indisList


def parseDescendants(apiResponse):

    apiResponse = getJSONObject(apiResponse)

    return apiResponse
        


def getDecendants(profileID):

    treeDepth = 20 
    url = "https://api.wikitree.com/api.php?action=getDescendants&key=" + profileID + "&fields=Id,Derived.LongNamePrivate,LastNameAtBirth,FirstName,Name,Father,Mother,Children" + "&depth=" + str(treeDepth)
    headers = ''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return None

def getAncestors(profileID):

    #Gets the pretty data for the tree 

    treeDepth = 10 
    url = "https://api.wikitree.com/api.php?action=getAncestors&key=" + profileID + "&fields=Id,FirstName,LastNameAtBirth,Derived.LongNamePrivate,Name,Father,Mother"+ "&depth=" + str(treeDepth)
    headers = ''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return None

def getAspectsOfProfile(profileID):
    
    url = "https://api.wikitree.com/api.php?action=getProfile&key=" + profileID + "&fields=Id,FirstName,LastNameAtBirth,LongNamePrivate,Name,Gender,Spouses,Father,Mother,BirthDate,DeathDate"
    headers = ''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return None

def getAspectsOfPerson(profileID):
    
    url = "https://api.wikitree.com/api.php?action=getPerson&key=" + profileID + "&fields=Id,FirstName,LastNameAtBirth,LongNamePrivate,Name,Gender,Spouses,Father,Mother,BirthDate,DeathDate"
    headers = ''
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return None




def prettyPrint(inputJSONStr):

    obj = json.loads(inputJSONStr)
    strObj = json.dumps(obj, indent=4)
    print(strObj)

def getJSONObject(inputJSONStr):

    obj = json.loads(inputJSONStr)

    return obj

def writeJSONToFile(data, dataFileName):
    with open(dataFileName, 'w', encoding='utf-8') as f:
        #a = json.dumps(data, sort_keys=True,indent=2)
        #f.write(a)
        json.dump(data, f, ensure_ascii=False,indent=2)
        #return json.dumps(self, default=lambda o: o.__dict__,    sort_keys=True, indent=4)

def getListOfKeys(dict):
    list = []
    for key in dict.keys():
        list.append(key)
         
    return list

    



main()
