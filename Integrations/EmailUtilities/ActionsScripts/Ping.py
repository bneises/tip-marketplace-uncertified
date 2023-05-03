from SiemplifyAction import *
import json, requests

INTEGRATION_NAME = "Email Utilities"

def main():
    siemplify = SiemplifyAction()


    siemplify.end('Siemplify is connected', True)


if __name__ == "__main__":
    main()