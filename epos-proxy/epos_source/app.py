import json
import pack
import os
import base64
import sock

# import requests
config = {}

if 'TCP_IP' in os.environ:
    config['TCP_IP'] = os.environ['TCP_IP']
else:
    config['TCP_IP'] = '79.79.1.47'    

if 'TCP_PORT' in os.environ:
    config['TCP_PORT'] = os.environ['TCP_PORT']
else:
    config['TCP_PORT'] = 2022


def lambda_handler(event, context):
    """
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # Validate the event
    # Method can only be a POST and Path /order
    json_event = event
    method = json_event['httpMethod']
    path = json_event['path']
    ret = 'nothing'

    if (method == 'POST') and (path == '/order'):
        # extract Order details
        #try:
        if 'body' in event and event['body'] is not None:
            body = event['body']
            # Check to see if data is Base64 encode
            if (event['isBase64Encoded'] == True):
                body = base64.b64decode(body)   

            order = json.loads(body)
            packet = pack.create_epos_packet(order)
            ret =  pack.dump_bstring(packet)

            # Send Request
            #response = sock.send_packet_recv(config['TCP_IP'], config['TCP_PORT'], packet)
            #print (response)
        '''
        except Exception as e:
            print (e)
            ret = 'exception'
            #raise e
        '''   

    # Forward order to server


    return {
        "statusCode": 200,
        "body": json.dumps({
            "packet": ret,
        }),
    }
