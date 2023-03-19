.PHONY: files-to-ses-template
files-to-ses-template: ## Add html and txt files to SES templates
	@python .scripts/files_to_ses_template.py

.PHONY: create-template
create-template: ## Create template in SES
	@aws ses create-template --cli-input-json file://ses_template.json

