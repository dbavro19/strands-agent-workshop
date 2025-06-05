#RAG
#Memory
#Code Interpreter
#from strands_tools import python_repl #Linux
#import python_repl_windows #If running on personal windows laptop
from strands_tools import retrieve

import boto3
import random
import string
import os


#STEPS
#Create S3 Bucket
def create_unique_s3_bucket():

    s3 = boto3.client('s3')
    bucket_name = 'aws-strands-agent-training' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    s3.create_bucket(Bucket=bucket_name)
    return bucket_name

#Copy pets-kb-files to s3 bucket


def copy_pets_kb_files_to_s3(bucket_name):
    """
    Dynamically uploads all files from the pets-kb-files directory to the specified S3 bucket.
    Each file is uploaded with its original filename as the S3 key.
    
    Args:
        bucket_name (str): Name of the S3 bucket to upload files to
    """
    s3 = boto3.client('s3')
    
    # Path to the pets-kb-files directory
    kb_files_dir = os.path.join(os.path.dirname(__file__), 'rag_dataset')
    
    # Get list of all files in the directory
    files = os.listdir(kb_files_dir)
    
    # Upload each file individually
    for filename in files:
        file_path = os.path.join(kb_files_dir, filename)
        if os.path.isfile(file_path):
            print(f"Uploading {filename} to S3...")
            s3.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=filename
            )
    
    print(f"Successfully uploaded {len(files)} files to {bucket_name}")


bucket_name = create_unique_s3_bucket()
copy_pets_kb_files_to_s3(bucket_name)


