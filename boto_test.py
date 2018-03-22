import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('askMBTA')

# table.put_item(
# Item={
#     'userID': "1234",
#     'home': "none",
#     'work': "none",
#     'stopid' : "1233",
#     'trainStopId':"none",
#     'route': "none"
# })

res = table.update_item(
    Key={
        'userID': 'amzn1.ask.account.a123'
    },
    UpdateExpression='SET stopid2 = :val1',
    ExpressionAttributeValues={
        ':val1': 1416
    }
)

print (res)