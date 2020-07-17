import json
import os
import base64
import pack 
import sock 

# import requests
config = {}

if 'TCP_IP' in os.environ:
    config['TCP_IP'] = os.environ['TCP_IP']
else:
    config['TCP_IP'] = '79.79.1.47'    

if 'TCP_PORT' in os.environ:
    config['TCP_PORT'] = int(os.environ['TCP_PORT'])
else:
    config['TCP_PORT'] = 2022

if 'TIMEOUT' in os.environ:
    config['TIMEOUT'] = int(os.environ['TIMEOUT'])
else:
    config['TIMEOUT'] = 20


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
    print (event)
    json_event = event
    method = json_event['httpMethod']
    path = json_event['path']
    ret = 'nothing'

    dryrun = True
    confirm = False

    params = event['queryStringParameters']

    if params is not None:
        if 'dryrun' in params:
            dryrun = True
        elif 'confirm' in params:
            confirm = True
            dryrun = False

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

            print (packet)

            if dryrun:
                # Return TCP packet bytes
                packet =  pack.dump_bstring(packet)
                ret = {
                    "statusCode": 200,
                    "body": json.dumps({
                        "packet": packet,
                    })
                }
            elif confirm:
                # Send Request
                print ("SENDING PACKET")
                resp = sock.send_packet_recv_timeout(config['TCP_IP'], config['TCP_PORT'], packet, config['TIMEOUT'])
                print ("SERVER RETURNS:", resp)
                (goodResponse, response) = pack.decode_response(resp)
                print ("SERVER RESPONSE", goodResponse, response)

                if goodResponse:
                    statusCode = 200
                else:
                    statusCode = 401
                ret = {
                    "statusCode": statusCode,
                    "body": json.dumps({
                        "commsStatus": response,
                    })
                }
                
        '''
        except Exception as e:
            print (e)
            ret = 'exception'
            #raise e
        '''   

    # Forward order to server

    return ret
