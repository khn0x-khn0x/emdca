import boto3

class UserService:
    def save(self):
        try:
            boto3.client("s3")
        except Exception:
            raise ValueError()

