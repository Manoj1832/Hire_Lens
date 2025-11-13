"""
Streamlit UI for Resume Parser
Upload a resume and extract key information
"""
import streamlit as st
import sys
import os
import io
import subprocess
from pathlib import Path
from pprint import pprint

# Add the current directory to the path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Check for spaCy model
def check_spacy_model():
    """Check if en_core_web_sm model is installed"""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        return True
    except (OSError, IOError):
        return False

def download_spacy_model():
    """Download the spaCy model"""
    try:
        import spacy
        # Use spacy's download command
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.PIPE)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

# Check and handle spaCy model
if not check_spacy_model():
    st.warning("⚠️ spaCy model 'en_core_web_sm' not found. Attempting to download...")
    
    with st.spinner("Downloading spaCy model (this may take a few minutes)..."):
        success, error = download_spacy_model()
        if success:
            st.success("✅ Model downloaded successfully! Please refresh the page.")
            st.rerun()
        else:
            st.error("❌ Failed to download model automatically.")
            if error:
                st.code(error)
            st.info("""
            **Please run this command in your terminal:**
            ```
            python -m spacy download en_core_web_sm
            ```
            Or if using the virtual environment:
            ```
            ..\\venv\\Scripts\\python.exe -m spacy download en_core_web_sm
            ```
            After downloading, refresh this page.
            """)
            st.stop()

try:
    from pyresparser import ResumeParser
except ImportError as e:
    st.error(f"Error: Could not import ResumeParser. {str(e)}")
    st.info("Make sure you're running from the pyresparser directory and that the package is properly set up.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Resume Parser - HireLens",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📄 Resume Parser</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload a resume to extract key information automatically</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool extracts the following information from resumes:
    - **Personal Details**: Name, Email, Phone
    - **Skills**: Technical and professional skills
    - **Experience**: Work experience and total years
    - **Education**: Degree and college name
    - **Career**: Designation and company names
    """)
    
    st.header("📋 Supported Formats")
    st.markdown("""
    - PDF files (.pdf)
    - Word documents (.docx)
    - DOC files (requires textract)
    """)
    
    st.header("🔧 Instructions")
    st.markdown("""
    1. Click "Browse files" to upload a resume
    2. Wait for processing (may take a few seconds)
    3. View extracted information below
    """)

# File uploader
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=['pdf', 'docx', 'doc'],
    help="Upload a PDF or Word document resume"
)

if uploaded_file is not None:
    # Display file info
    file_details = {
        "Filename": uploaded_file.name,
        "FileType": uploaded_file.type,
        "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
    }
    
    with st.expander("📎 File Information", expanded=False):
        st.json(file_details)
    
    # Process the file
    if st.button("🔍 Extract Resume Data", type="primary", use_container_width=True):
        with st.spinner("Processing resume... This may take a few seconds."):
            try:
                # Save uploaded file temporarily
                file_extension = Path(uploaded_file.name).suffix
                temp_file_path = f"temp_resume{file_extension}"
                
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse resume
                parser = ResumeParser(temp_file_path)
                data = parser.get_extracted_data()
                
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                # Store in session state
                st.session_state['resume_data'] = data
                st.session_state['file_processed'] = True
                
                # Generate MCQ questions from extracted skills
                try:
                    from mcq_generator import generate_mcq_from_skills
                    skills = data.get('skills', [])
                    if skills:
                        questions = generate_mcq_from_skills(skills, num_questions=10)
                        st.session_state['test_questions'] = questions
                    else:
                        st.warning("No skills found in resume. Generic questions will be used.")
                        from mcq_generator import generate_mcq_from_skills, GENERIC_QUESTIONS
                        import random
                        questions = random.sample(GENERIC_QUESTIONS, min(10, len(GENERIC_QUESTIONS)))
                        st.session_state['test_questions'] = questions
                except Exception as e:
                    st.warning(f"Could not generate test questions: {e}")
                
                st.success("✅ Resume processed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing resume: {str(e)}")
                st.exception(e)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
    
    # Display results if available
    if 'resume_data' in st.session_state and st.session_state.get('file_processed', False):
        data = st.session_state['resume_data']
        
        st.markdown("---")
        st.markdown("## 📊 Extracted Information")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Experience", f"{data.get('total_experience', 0)} years" if data.get('total_experience') else "N/A")
        
        with col2:
            st.metric("Number of Pages", data.get('no_of_pages', 'N/A'))
        
        with col3:
            skills_count = len(data.get('skills', [])) if data.get('skills') else 0
            st.metric("Skills Found", skills_count)
        
        with col4:
            companies_count = len(data.get('company_names', [])) if data.get('company_names') else 0
            st.metric("Companies", companies_count)
        
        # Personal Information
        st.markdown("### 👤 Personal Information")
        personal_col1, personal_col2 = st.columns(2)
        
        with personal_col1:
            st.markdown(f"**Name:** {data.get('name', 'Not found')}")
            st.markdown(f"**Email:** {data.get('email', 'Not found')}")
        
        with personal_col2:
            st.markdown(f"**Mobile Number:** {data.get('mobile_number', 'Not found')}")
        
        # Skills
        if data.get('skills'):
            st.markdown("### 🛠️ Skills")
            skills_list = data.get('skills', [])
            # Display skills as chips/badges
            skills_text = ", ".join([f"`{skill}`" for skill in skills_list[:30]])  # Limit to first 30
            if len(skills_list) > 30:
                skills_text += f" *(+{len(skills_list) - 30} more)*"
            st.markdown(skills_text)
        
        # Experience
        if data.get('total_experience') or data.get('experience'):
            st.markdown("### 💼 Experience")
            exp_col1, exp_col2 = st.columns(2)
            
            with exp_col1:
                if data.get('total_experience'):
                    st.markdown(f"**Total Experience:** {data.get('total_experience')} years")
            
            with exp_col2:
                if data.get('designation'):
                    designations = data.get('designation', [])
                    if isinstance(designations, list):
                        st.markdown(f"**Designations:** {', '.join(designations)}")
                    else:
                        st.markdown(f"**Designations:** {designations}")
            
            if data.get('company_names'):
                companies = data.get('company_names', [])
                if isinstance(companies, list):
                    st.markdown(f"**Companies:** {', '.join(companies)}")
                else:
                    st.markdown(f"**Companies:** {companies}")
        
        # Education
        if data.get('degree') or data.get('college_name'):
            st.markdown("### 🎓 Education")
            edu_col1, edu_col2 = st.columns(2)
            
            with edu_col1:
                if data.get('degree'):
                    degrees = data.get('degree', [])
                    if isinstance(degrees, list):
                        st.markdown(f"**Degree:** {', '.join(degrees)}")
                    else:
                        st.markdown(f"**Degree:** {degrees}")
            
            with edu_col2:
                if data.get('college_name'):
                    colleges = data.get('college_name', [])
                    if isinstance(colleges, list):
                        st.markdown(f"**College:** {', '.join(colleges)}")
                    else:
                        st.markdown(f"**College:** {colleges}")
        
        # Raw JSON data (expandable)
        with st.expander("📋 View Raw JSON Data"):
            st.json(data)
        
        # Download button for JSON
        import json
        json_str = json.dumps(data, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name=f"resume_data_{uploaded_file.name.split('.')[0]}.json",
            mime="application/json"
        )
        
        st.markdown("---")
        
        # Start Test Button
        if 'test_questions' in st.session_state and st.session_state['test_questions']:
            st.markdown("### 📝 Next Step: Skills Assessment Test")
            st.info("""
            **Ready to take the skills assessment test?**
            - 10 multiple choice questions based on your resume skills
            - 10 seconds per question
            - Proctoring enabled (camera and audio monitoring)
            - Minimum score required: 7/10 to pass
            - Passing the test makes you eligible for HR round scheduling
            """)
            
            col_test1, col_test2 = st.columns([1, 1])
            with col_test1:
                if st.button("📝 Start Skills Assessment Test", type="primary", use_container_width=True):
                    st.switch_page("pages/test_interface.py")
            with col_test2:
                if st.button("📊 Go to Dashboard", use_container_width=True):
                    st.switch_page("pages/dashboard.py")
        
        # Clear button
        if st.button("🔄 Process Another Resume"):
            st.session_state.pop('resume_data', None)
            st.session_state.pop('file_processed', None)
            st.session_state.pop('test_questions', None)
            st.rerun()

else:
    # Show example or instructions when no file is uploaded
    st.info("👆 Please upload a resume file to get started.")
    
    # Show sample resume option
    sample_resume_path = "OmkarResume.pdf"
    if os.path.exists(sample_resume_path):
        st.markdown("---")
        st.markdown("### 🧪 Try with Sample Resume")
        if st.button("📄 Use Sample Resume (OmkarResume.pdf)", use_container_width=True):
            try:
                with st.spinner("Processing sample resume... This may take a few seconds."):
                    parser = ResumeParser(sample_resume_path)
                    data = parser.get_extracted_data()
                    
                    st.session_state['resume_data'] = data
                    st.session_state['file_processed'] = True
                    st.session_state['sample_used'] = True
                    
                    # Generate MCQ questions from extracted skills
                    try:
                        from mcq_generator import generate_mcq_from_skills
                        skills = data.get('skills', [])
                        if skills:
                            questions = generate_mcq_from_skills(skills, num_questions=10)
                            st.session_state['test_questions'] = questions
                        else:
                            from mcq_generator import generate_mcq_from_skills, GENERIC_QUESTIONS
                            import random
                            questions = random.sample(GENERIC_QUESTIONS, min(10, len(GENERIC_QUESTIONS)))
                            st.session_state['test_questions'] = questions
                    except Exception as e:
                        st.warning(f"Could not generate test questions: {e}")
                    
                    st.success("✅ Sample resume processed successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error processing sample resume: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built with ❤️ using pyresparser | HireLens"
    "</div>",
    unsafe_allow_html=True
)

