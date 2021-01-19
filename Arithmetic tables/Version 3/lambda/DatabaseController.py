import boto3
from decimal import Decimal

class DatabaseController:
    def __init__(self):
        self.table_name = 'user'
        self.aws_access_key_id = 'AKIASP6ELZ6M2ZTGJVEL'
        self.aws_secret_access_key = '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'
        self.region_name = 'us-east-1'

    def connect_database(self):
        try:
            return boto3.resource('dynamodb', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)
        except Exception as e:
            print("Error connecting to the database: {}".format(e))

    def create_table_users(self, dynamodb=None):
        dynamodb = self.connect_database()
        
        try:
            table = dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'userId',
                        'KeyType': 'HASH'  
                    },
                    {   
                        'AttributeName': 'name',
                        'KeyType': 'RANGE'  
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'userId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            return table.table_status

        except Exception as e:
            return e
        
    def find_user(self, user_id, name):
        dynamodb = self.connect_database()
        try:
            table = dynamodb.Table(self.table_name)
            response = table.get_item(
                Key={   
                        'userId': user_id,
                        'name': name
                    }
            )
            return response['Item']
        except Exception as e:
            print("Error getting user from the database.: {}".format(e))

    def insert_user(self, user_id, name):
        dynamodb = self.connect_database()
        if self.find_user(user_id, name) == None:
            try:
                table = dynamodb.Table(self.table_name)
                response = table.put_item(
                    Item={  
                            'userId': user_id,
                            'name': name,
                            'total_score': 0
                        }
                )
                return response
            except Exception as e:
                print("Error putting user to the database.: {}".format(e))
        else:
            print("The user already exists.")

    def delete_user(self, user_id, name):
        dynamodb = self.connect_database()
        if self.find_user(name):
            try:
                table = dynamodb.Table(self.table_name)
                response = table.delete_item(
                    Key={
                    'userId': user_id,
                    'name': name
                    },
                )
                return response
            except Exception as e:
                print("Error deleting user from the database.: {}".format(e))
        else:
            print("The user does not exist.")

    def update_score(self,  user_id, name, add_score):
        dynamodb = self.connect_database()
        if self.find_user(user_id, name):
            try:
                table = dynamodb.Table(self.table_name)
                response = table.update_item(
                    Key={
                        'userId': user_id,
                        'name': name
                    },
                    UpdateExpression="set total_score = total_score + :t",
                    ExpressionAttributeValues={
                    ':t': Decimal(add_score)
                    },
                    ReturnValues="UPDATED_NEW"
                )
                return response
            except Exception as e:
                print("Error updating user in the database.: {}".format(e))
        else:
            print("The user already exists.")
