# files necessary for the project

```
# File config.ini
[slack]
client_id: 
client_secret: 
verification_token: 
oauth_secret: 
[forecast.io]
secret_key: 
```

```
# zappa_settings.json

generate with zappa init

example:

{
  "prod": {
    "app_function": "app.app",
    "aws_region": "us-east-1",
    "exclude": [
      "__pycache__",
      ".git/*",
      ".gitignore",
      ".python-version",
      "LICENSE",
      "README.md",
      "requirements.txt",
      "zappa_settings.json"
    ],
    "keep_warm": true,
    "keep_warm_expression": "rate(5 minutes)",
    "memory_size": 128,
    "profile_name": "default",
    "project_name": "....",
    "runtime": "python3.6",
    "s3_bucket": ".....",
    "timeout_seconds": 30
  }
}

```