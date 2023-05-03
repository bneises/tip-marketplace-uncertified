from SiemplifyAction import *
import json, requests

INTEGRATION_NAME = "Spell Checker"

def main():
    siemplify = SiemplifyAction()


    siemplify.end('Spell Checker is connected', True)


if __name__ == "__main__":
    main()