# QuickNews Bot - Render Deployment Guide

This guide will help you deploy your Instagram news bot on Render.com as a background worker.

## Prerequisites

1. A Render.com account (https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

I've already added the necessary files to your project:
- `requirements.txt`: Lists all Python dependencies
- `render.yaml`: Configuration for Render deployment
- `Procfile`: Tells Render how to run your application

## Step 2: Create a Git Repository

```bash
# Initialize a git repository if you haven't already
git init
git add .
# DO NOT COMMIT YOUR .env FILE WITH SENSITIVE INFORMATION
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Initial commit for Render deployment"
```

Create a new repository on GitHub or GitLab and push your code:

```bash
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## Step 3: Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" and select "Blueprint"
3. Connect your Git repository
4. Render will detect the `render.yaml` file and set up your service
5. Click "Apply" to create the services defined in the YAML file

## Step 4: Set Environment Variables

Your `.env` file contains sensitive information that should be set as environment variables in Render:

1. Go to your worker service in the Render dashboard
2. Go to "Environment" tab
3. Add the following environment variables:
   - `IG_USERNAME`
   - `IG_PASSWORD`
   - `NEWS_API_KEY`
   - `FLASK_SECRET_KEY`

## Step 5: Monitor Your Deployment

After deploying, you can monitor your worker in the Render dashboard:
- View logs to ensure your bot is running correctly
- Check the scheduler is working as expected

## Troubleshooting

If your bot isn't working as expected:
1. Check the logs for any errors
2. Ensure all environment variables are set correctly
3. Verify that your bot can connect to Instagram (Render IPs might be blocked)

## Important Notes

- Render's free tier has limitations. For a continuously running worker, you'll need a paid plan.
- Instagram might detect bot activity from cloud services. Be cautious and follow Instagram's terms of service.
- Your bot will restart whenever you push changes to your repository.
