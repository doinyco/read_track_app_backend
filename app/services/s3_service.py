import boto3
import os
from botocore.exceptions import ClientError

s3_client = boto3.client(
   "s3",
   region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def upload_book_cover(image_data, filename):
   key = f"images/{filename}"

   # Check if image already exists
   try:
       s3_client.head_object(
           Bucket=BUCKET_NAME,
           Key=key
       )

       # File exists
       return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
   
   except ClientError as e:
       error_code = e.response["Error"]["Code"]

       if error_code != "404":
           raise e

   # File does not exist, upload it
   s3_client.put_object(
       Bucket=BUCKET_NAME,
       Key=key,
       Body=image_data,
       ContentType="image/jpeg"
   )

   return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
