# README

In this video, I will demonstrate how to train a model and deploy it using AWS SageMaker. The process is broken down into three steps:

## Step 1: Training the Model
1. Obtain the MNIST dataset from an AWS S3 bucket.
2. Utilize supervised classification techniques to train the XGBoost model using the acquired dataset.
3. Store the trained model for future use.

## Step 2: Deploying the Model
1. Upload the trained model to an AWS S3 bucket.
2. Retrieve a Docker container to host the model.
3. Create a model within AWS SageMaker.
4. Configure an endpoint for the model.
5. Deploy the endpoint.
6. Monitor the endpoint status.
7. Conduct a test of the endpoint to ensure proper functionality.

## Step 3: Creating the UI
1. Create an UI using Streamlit to access the endpoint.
2. Send requests from the UI and display the received response.