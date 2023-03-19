import json

with open(
    "./email_template/build_production/transaction_summary_with_data.html", "r"
) as html_file:
    html_content = html_file.read()

with open(
    "./email_template/build_production/transaction_summary_with_data.txt", "r"
) as txt_file:
    text_content = txt_file.read()

with open("ses_template.json", "r") as template_json_file:
    template_data = json.load(template_json_file)

template_data["Template"]["HtmlPart"] = html_content
template_data["Template"]["TextPart"] = text_content

with open("ses_template.json", "w") as updated_template_json_file:
    json.dump(template_data, updated_template_json_file)
