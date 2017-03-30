import requests, os, sys
import json
import csv
from collections import namedtuple

# Readme
# This script lets you update Mandrill Templates. You can specify a folder
# with all the Templates you want to update as html + a CSV file containing
# the metadata of the Templates. The filename must match the slug of the Template
# you want to update. The script will push the HTML + the Metadata
# to the Mandrill API thereby updating (read: OVERWRITING) the Templates
# with the data you provide.

# You can specify some things here:

# Adjust the API Key
api_key = ""
# Change Endpoint if necessary
# https://mandrillapp.com/api/docs/templates.JSON.html#method=update
endpoint = "https://mandrillapp.com/api/1.0/templates/update.json"

# Specify the directory that contains the Template Html Code you want to update.
# Name the Files after the respective Slug of the Template! The Html in the File
# will overwrite the Html Code of the Template that matches the Slug!
template_directory = "../uploadThese"

# Specify the name of the file that contains the Metadata of the templates, i.e.:
# Subject header, From header, To header, labels
meta_path = "../metadata"
meta_filename = "metadata.csv"

FROM_EMAIL = "from_email"
FROM_NAME = "from_name"
SUBJECT = "subject"
LABELS = "labels"


def remove_file_ending(filename):
    if (filename.endswith(".html", 0, len(filename))):
        return filename[0:len(filename) - 5]
    else:
        return filename


def add_metadata(payload, meta, slug):
    if meta is None:
        return payload

    print("With metadata: [", end="")
    if (FROM_EMAIL in meta and meta[FROM_EMAIL]):
        print(FROM_EMAIL + ": \'" + str(meta[FROM_EMAIL]) + "\'", end="")
        payload.update({FROM_EMAIL: meta["from_email"]})

    if (FROM_NAME in meta and meta[FROM_NAME]):
        print(FROM_NAME + ": \'" + str(meta[FROM_NAME]) + "\'", end="")
        payload.update({FROM_NAME: meta[FROM_NAME]})

    if (SUBJECT in meta and meta[SUBJECT]):
        print(SUBJECT + ": \'" + str(meta[SUBJECT]) + "\'", end="")
        payload.update({SUBJECT: meta[SUBJECT]})

    if (LABELS in meta and meta[LABELS]):
        print(LABELS + ": \'" + str(meta[LABELS]) + "\'", end="")
        payload.update({LABELS: meta[LABELS]})

    print("]", end="")

    return payload


def prepare_json(api_key, template, slug, meta):
    payload = {
        "key": api_key,
        "name": slug,
        "code": template
    }

    payload = add_metadata(payload, meta, slug)

    return json.dumps(payload)


def read_template(template_directory, template_filename):
    with open(os.path.join(template_directory, template_filename), 'r') as template_file:
        template = template_file.read()
        return template


def process_meta_file(meta_path, meta_filename):
    with open(os.path.join(meta_path, meta_filename), 'r') as meta_file:
        reader = csv.reader(meta_file)

        meta_dict = {}

        for rows in reader:
            labels = []
            for i in [4, 5, 6, 7]:
                label = rows[i]
                if label:
                    labels.append(label)

            meta_dict.update({rows[0]: {SUBJECT: rows[1], FROM_EMAIL: rows[2], FROM_NAME: rows[3], LABELS: labels}})

        return meta_dict


def process_template_files(template_directory):
    error_counter = 0;

    list = []

    for template_file in os.listdir(template_directory):
        if not (template_file.endswith('.html')):
            error_counter += 1
        list.append(template_file)

    if (error_counter > 0):
        sys.exit(
            "Some Templates don't have .html ending or some non-template files existant in " + template_directory + ". Aborting...")
    else:
        return list


def print_welcome_message(template_files):
    print("")
    print("This script updates Templates for Mandrill API key " + api_key)
    print("")
    print("Usage: The script expects the template .html files in the subdirecotry \"" + template_directory + "\" folder.")
    print("The filenames must match the slugs of the respective template.")
    print("The script also expects the template metadate in \"" + meta_path + "/" + meta_filename + "\".")
    print("")
    print("The following templates will be updated:")
    print("-----------------")
    for template_file in template_files:
        print(template_file)
    print("-----------------")
    print("")
    try:
        input("Press enter continue or ctl+c to abort...")
        return
    except KeyboardInterrupt:
        print("Aborted.")
        sys.exit()


def push_files_to_mandrill(template_files, metainformations):
    successes = 0

    print("")
    print("Pushing files:")
    print("=================")

    for template_file in template_files:
        print("Updating " + template_file + "...", end="")

        slug = remove_file_ending(template_file)
        template = read_template(template_directory, template_file)
        meta = None
        if (slug in metainformations):
            meta = metainformations[slug]
        else:
            print("Not adding any metadata."),
        payload = prepare_json(api_key, template, slug, meta)

        response = requests.post(endpoint, payload)

        if response is None:
            print("Error: Response is null. Nothing updated.")
        else:
            if response.status_code != 200:
                print("Error: Status Code is " + str(response.status_code))
                print("Response JSON is " + str(response.json()))
            if response.status_code == 200:
                successes += 1
                print("success")

    print("=================")
    print("")
    return successes


def main():
    templates = process_template_files(template_directory)

    metainformation = process_meta_file(meta_path, meta_filename)

    print_welcome_message(templates)

    successfully_pushed_files = push_files_to_mandrill(templates, metainformation)

    errors = len(templates) - successfully_pushed_files

    print("Successfully pushed {0} templates. Errors: {1}".format(successfully_pushed_files, errors))


if __name__ == "__main__":
    main()
