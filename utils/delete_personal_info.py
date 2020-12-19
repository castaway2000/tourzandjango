import boto3

s3 = boto3.client("s3")
all_objects = s3.list_objects_v2(Bucket='tourzan', Prefix='users/', MaxKeys=1000)
docs = []
next_token = all_objects['NextContinuationToken']
marker = len(all_objects['Contents'])
count = all_objects['KeyCount']

contents = all_objects['Contents']
while next_token:
    print(next_token, count)
    for i in contents:
        if '/docs/' in i['Key']:
            docs.append(i['Key'])
        if '/webcam_images/' in i['Key']:
            docs.append(i['Key'])
        if '/license/' in i['Key']:
            docs.append(i['Key'])
    objects = s3.list_objects_v2(Bucket='tourzan', Prefix='users/', ContinuationToken=next_token)
    if 'NextContinuationToken' in objects.keys():
        next_token = objects['NextContinuationToken']
    else:
        break
    count += len(objects['Contents'])
    contents = objects['Contents']
print(len(docs))

for doc in docs:
    s3.delete_object(Bucket='tourzan', Key=doc)
    print(doc)