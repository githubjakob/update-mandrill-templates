# update-mandrill-templates

Python script to update Mandrill Email Templates plus its metadata in your Mandrill Account according to local HTML files/metadata as CSV.

The script will push the HTML + the Metadata to the Mandrill API thereby updating (read: OVERWRITING) the Templates in your Account with the data you provide.

## Usage

The script uses the Mandrill template `slug` to identify templates. Make sure the name of the HTML files matches the `slug` of your template.

You need to specify in the script:
* the folder which contains the HTML of the Templates you want to update 
* path of the CSV file which contains the metadata of the Templates (Format of the CSV should be: `slug,subject,from_email,from_name,label1,label2,label3,label4`)
* your Mandrill API key

Run with `python3 updateMandrillTemplates.py`.

