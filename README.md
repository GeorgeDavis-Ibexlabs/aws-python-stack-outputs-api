# aws-python-stack-outputs-api

#### Serverless Framework Python HTTP API on AWS

This template deploys a simple HTTP API with backend logic running on Python + AWS Lambda and API Gateway using the Serverless Framework. It captures the HTTP request body and pushes a Slack notification to the pre-configured Slack endpoint and channel.

## Usage

### Deployment

```
$ serverless deploy
```

After deploying, you should see output similar to:

```bash
Deploying aws-python-http-api-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-http-api-project-dev (140s)

endpoint: POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/
functions:
  hello: aws-python-http-api-project-dev-hello (2.3 kB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can call the created application via HTTP:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/
```

Which should result in response similar to the following (removed `input` content for brevity):

```
Success
```