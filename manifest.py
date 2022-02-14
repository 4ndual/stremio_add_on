import json
import logging
import boto3
from boto3.dynamodb.conditions import Attr

logger=logging.getLogger()
logger.setLevel(logging.INFO)

MANIFEST = {
    'id': 'test',
    'version': '1.0.0',

    'name': '4ndual watchlist',
    'description': 'list imdb 4ndual Addon',

    'types': ['movie'],

    'catalogs': [
            {'type': 'movie', 'id': 'test'},
    ],
    'resources': ['catalog'],
    "idPrefixes": ['test'],
}



dynamodbTableName="watchlist"
dynamodb=boto3.resource("dynamodb")
table=dynamodb.Table(dynamodbTableName)


getmethod="GET"
postmethod="POST"
deletemethod="DELETE"
patchmethod="PATCH"
health="/manifest.json"

def lambda_handler(event, context):
    logger.info(event)
    httpMethod=event["httpMethod"]
    path=event["path"]

    if httpMethod==getmethod and path==health:
        
        response=buildResponse(200, MANIFEST)
        
    elif httpMethod==getmethod and path=='/catalog/movie/test.json' or path=='/catalog/series/test.json' :
        type=path.split("/")[2]
        id=path.split("/")[3]
  
        response=addon_catalog(type, id)
    #
    else:
        print(path)
        response=buildResponse(200)
    
    
    return response
    
def buildResponse(statusCode,body=None):
    response={
        'statusCode': statusCode,
        'headers':{
            'Content-Type':'application/json',
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Headers':'*'
        }
    }
    
    
    response["body"]=json.dumps(body)
    
    return response
    
def addon_catalog(type, id):
    if type not in MANIFEST['types']:
        return buildResponse(404)

    CATALOG=getmovies()

    catalog = CATALOG[type] if type in CATALOG else []

    metaPreviews = {
        'metas': [
            {
                'id': item['imdbid'],
                'type': type,
                'name': item['name'],
                'genres': item['genre'],
                'poster': ""
            } for item in catalog["Items"]
        ]
    }
    
    return buildResponse(200,metaPreviews)
    
def getmovies():

    try:
        response=table.scan()
        result=response["Items"]
        
        while "lastEvalutatedKey" in response:
            response=table.scan(ExclusiveStartKey=response["lastEvalutatedKey"])
            result.extend(response["Items"])
        CATALOG={
            "movie":response
        }
        return CATALOG
    except:
        logger.exception("your exception here")
    pass
