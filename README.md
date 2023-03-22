# transactions to email
This repository is an AWS Lambda project in Python designed to process financial transactions stored in CSV files. When a CSV file is uploaded to an Amazon S3 bucket, the Lambda is triggered to process the transactions, generate a summary, and send an email to the user using the Amazon Simple Email Service (SES).

The main Lambda code is located in the **`transaction_processor/app.py`** file. Although it does not use a specific framework, the project has been optimized to ensure high performance and efficiency in Lambda execution.

The general flow of the process is as follows:

1. A CSV file is uploaded to an S3 bucket.
2. The Lambda is triggered based on this event in S3.
3. The code in **`transaction_processor/app.py`** reads and processes the transactions from the CSV file.
4. A summary of the transactions is created, including debit and credit totals, as well as a monthly breakdown.
5. The transaction summary is sent to the user via email using Amazon SES.

The repository also includes GitHub Actions workflows for running tests and automatically deploying the Lambda to AWS when a push is made to the main branch.

The project is designed to be scalable, easy to maintain, and highly efficient in Lambda execution.

### ****Deployment Guide****

Follow these steps to deploy the **`transaction-processor`** application:

1. **Add the required variables and secrets to the GitHub repository:**
    
    Navigate to your GitHub repository, then go to **`Settings > Secrets > Actions`**, and add the following variables and secrets:
    
    - **`AWS_REGION`** (variable)
    - **`AWS_ACCOUNT_ID`** (variable)
    - **`AWS_ACCESS_KEY_ID`** (secret)
    - **`AWS_SECRET_ACCESS_KEY`** (secret)
2. **Attach necessary policies to the AWS account:**
    
    Ensure the AWS account associated with the **`AWS_ACCESS_KEY_ID`** and **`AWS_SECRET_ACCESS_KEY`** has the necessary permissions to interact with AWS services such as AWS Lambda, Amazon S3, Amazon SES, and Amazon ECR.
    
3. **Attach necessary policies to the AWS services:**
    
    Make sure the AWS services you are using have the necessary permissions to interact with each other. For example, the Lambda function should have permissions to access the S3 bucket and send emails using Amazon SES.
    
4. **Use the Makefile commands for SES template:**
    
    Run the following commands to create and upload the SES template:
    
    ```
    make files-to-ses-template
    make create-template
    ```
    
5. **Add a file to the S3 bucket:**
    
    After deploying the application, upload a CSV ([test.csv](https://github.com/miltonparedes/transaction-processor/blob/main/test.csv)) file containing the transactions to the S3 bucket created during the deployment process. This will trigger the Lambda function to process the transactions and send the email summary.
    

After completing these steps, the GitHub Actions workflow will automatically deploy the application to AWS Lambda when you push changes to the main branch.
