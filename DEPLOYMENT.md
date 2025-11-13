# Deploying HireLens on Render

This guide will help you deploy the HireLens Streamlit application on Render.

## Prerequisites

1. A GitHub account with this repository
2. A Render account (sign up at https://render.com)

## Deployment Methods

### Method 1: Using Render Blueprint (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Go to Render Dashboard**:
   - Visit https://dashboard.render.com
   - Click "New +" and select "Blueprint"

3. **Connect your repository**:
   - Select your GitHub repository
   - Render will automatically detect the `render.yaml` file

4. **Deploy**:
   - Click "Apply" to deploy
   - Render will automatically build and deploy your application

### Method 2: Manual Deployment

1. **Go to Render Dashboard**:
   - Visit https://dashboard.render.com
   - Click "New +" and select "Web Service"

2. **Connect your repository**:
   - Connect your GitHub account
   - Select the repository containing this project

3. **Configure the service**:
   - **Name**: `hirelens` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r Automation/requirements.txt && python -m spacy download en_core_web_sm && python -m nltk.downloader words stopwords
     ```
   - **Start Command**: 
     ```bash
     cd Automation && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
     ```
   - **Plan**: Select "Free" (or upgrade for production)

4. **Environment Variables** (optional):
   - `PYTHON_VERSION`: `3.10.12`
   - `PORT`: `8501` (Render sets this automatically, but you can specify it)

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your application
   - The first deployment may take 5-10 minutes

## Important Notes

### Build Process
- The build process downloads the spaCy model (`en_core_web_sm`) and NLTK data
- This may take several minutes during the first build
- Subsequent deployments will be faster if dependencies are cached

### Free Tier Limitations
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to a paid plan for production use

### Troubleshooting

1. **Build fails with spaCy model error**:
   - Ensure the build command includes: `python -m spacy download en_core_web_sm`
   - Check that `spacy` is in `requirements.txt`

2. **Application doesn't start**:
   - Verify the start command uses `$PORT` environment variable
   - Check that `app.py` is in the `Automation` directory
   - Review build logs in Render dashboard

3. **Import errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check that the working directory is set correctly

## Post-Deployment

After successful deployment:
1. Your application will be available at: `https://your-service-name.onrender.com`
2. The first load may take longer due to model initialization
3. Monitor logs in the Render dashboard for any issues

## Updating the Application

1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Manual redeploy is also available in the Render dashboard

## Support

For issues specific to:
- **Render**: Check Render documentation at https://render.com/docs
- **Streamlit**: Check Streamlit documentation at https://docs.streamlit.io
- **Application**: Review application logs in Render dashboard

