from SiemplifyAction import *

from jinja2 import Template, Environment
INTEGRATION_NAME = "TemplateEngine"

def main():
    siemplify = SiemplifyAction()


    siemplify.end('Siemplify is connected', True)


if __name__ == "__main__":
    main()