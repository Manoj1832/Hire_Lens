# Quick Start: Deploy to Render

## Fastest Way to Deploy

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Render deployment files"
   git push
   ```

2. **Deploy on Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Click "Apply"

That's it! Render will automatically:
- Install dependencies from `Automation/requirements.txt`
- Download spaCy model (`en_core_web_sm`)
- Download NLTK data
- Start your Streamlit app

## What Was Created

- `render.yaml` - Render Blueprint configuration
- `Automation/build.sh` - Build script (optional, commands are in render.yaml)
- `DEPLOYMENT.md` - Detailed deployment guide
- Updated `Automation/Procfile` - For compatibility

## Your App URL

After deployment, your app will be available at:
`https://hirelens.onrender.com` (or your custom name)

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Ensure all dependencies are in `Automation/requirements.txt`
3. Verify Python version (3.10.12) matches `Automation/runtime.txt`

For more details, see `DEPLOYMENT.md`.

