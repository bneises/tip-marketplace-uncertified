import boto3
import json
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--marketplace-path", help="Email for new Username On Siemplify")
args = parser.parse_args()

MARKETPLACE_PATH = args.marketplace_path #"/opt/siemplify/siemplify_server/Marketplace/"
MARKETPLACE_JSON_FILE_PATH = os.path.join(MARKETPLACE_PATH, "marketplace.json")

def get_commercial_integrations():
    s3 = boto3.client(
        's3',
        aws_access_key_id="",
        aws_secret_access_key="", )

    with open('commerical_markeplace.json', 'wb') as f:
        s3.download_fileobj('siemplify-marketplace', 'Marketplace/marketplace.json', f)
    with open('commerical_markeplace.json','r') as file:
        content = file.read()
        jsonObject = json.loads(content)
        integrationSet = set()

    for item in jsonObject:
        integrationSet.add(item["Identifier"])
    return integrationSet

def check_integrations_with_commercial(commercial_integrations):
    with open(MARKETPLACE_JSON_FILE_PATH, 'r') as f:
        content = f.read()
        uncertified_integrations_json = json.loads(content)

    for item in uncertified_integrations_json:
        identifier = item["Identifier"]
        if (identifier in commercial_integrations):
            raise Exception(identifier + ' integration already exist in the commercial marketplace.')
def main():
    integrationSet = get_commercial_integrations()

    check_integrations_with_commercial(integrationSet)

if __name__ == '__main__':
    main()


