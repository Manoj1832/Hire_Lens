"""
Dashboard Page
Shows HR round schedule and candidate information
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="HR Dashboard - HireLens",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .dashboard-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .schedule-item {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="dashboard-header">📊 HR Dashboard</h1>', unsafe_allow_html=True)

# Check if candidate passed the test
if 'test_passed' not in st.session_state or not st.session_state.get('test_passed', False):
    st.warning("⚠️ You must pass the skills assessment test (7/10) to access the HR round schedule.")
    st.info("Please complete the test first.")
    if st.button("📝 Take Test"):
        st.switch_page("pages/test_interface.py")
    st.stop()

# Get candidate information
candidate_info = {}
if 'resume_data' in st.session_state:
    candidate_info = st.session_state.resume_data

# Main dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 👤 Candidate Information")
    
    if candidate_info:
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown(f"**Name:** {candidate_info.get('name', 'N/A')}")
            st.markdown(f"**Email:** {candidate_info.get('email', 'N/A')}")
            st.markdown(f"**Phone:** {candidate_info.get('mobile_number', 'N/A')}")
            st.markdown(f"**Experience:** {candidate_info.get('total_experience', 0)} years")
        
        with info_col2:
            if candidate_info.get('college_name'):
                colleges = candidate_info.get('college_name', [])
                if isinstance(colleges, list):
                    st.markdown(f"**College:** {', '.join(colleges)}")
                else:
                    st.markdown(f"**College:** {colleges}")
            
            if candidate_info.get('degree'):
                degrees = candidate_info.get('degree', [])
                if isinstance(degrees, list):
                    st.markdown(f"**Degree:** {', '.join(degrees)}")
                else:
                    st.markdown(f"**Degree:** {degrees}")
            
            if candidate_info.get('skills'):
                skills = candidate_info.get('skills', [])
                st.markdown(f"**Skills:** {', '.join(skills[:10])}")
                if len(skills) > 10:
                    st.markdown(f"*+{len(skills) - 10} more skills*")
    
    st.markdown("---")
    
    # HR Round Schedule
    st.markdown("### 📅 HR Round Schedule")
    
    # Generate sample schedule (in production, this would come from a database)
    if 'hr_schedule' not in st.session_state:
        # Create sample schedule
        base_time = datetime.now() + timedelta(days=1)
        st.session_state.hr_schedule = [
            {
                "date": (base_time + timedelta(days=i)).strftime("%Y-%m-%d"),
                "time": "10:00 AM",
                "duration": "45 minutes",
                "type": "Technical Interview",
                "interviewer": "John Smith",
                "status": "Scheduled"
            }
            for i in range(3)
        ]
    
    schedule = st.session_state.hr_schedule
    
    for i, slot in enumerate(schedule):
        with st.expander(f"📅 {slot['date']} at {slot['time']} - {slot['type']}"):
            st.markdown(f"**Date:** {slot['date']}")
            st.markdown(f"**Time:** {slot['time']}")
            st.markdown(f"**Duration:** {slot['duration']}")
            st.markdown(f"**Type:** {slot['type']}")
            st.markdown(f"**Interviewer:** {slot['interviewer']}")
            st.markdown(f"**Status:** {slot['status']}")
            
            if slot['status'] == 'Scheduled':
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"✅ Confirm", key=f"confirm_{i}"):
                        slot['status'] = 'Confirmed'
                        st.success("Interview confirmed!")
                        st.rerun()
                with col_btn2:
                    if st.button(f"❌ Reschedule", key=f"reschedule_{i}"):
                        st.info("Please contact HR to reschedule.")
    
    # Add new schedule slot (admin function)
    with st.expander("➕ Add Interview Slot"):
        with st.form("add_slot_form"):
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                slot_date = st.date_input("Date", min_value=datetime.now().date())
                slot_time = st.time_input("Time")
            with col_form2:
                slot_type = st.selectbox("Type", ["Technical Interview", "HR Interview", "Final Round"])
                slot_duration = st.selectbox("Duration", ["30 minutes", "45 minutes", "60 minutes"])
            
            interviewer = st.text_input("Interviewer Name")
            
            if st.form_submit_button("Add Slot"):
                new_slot = {
                    "date": slot_date.strftime("%Y-%m-%d"),
                    "time": slot_time.strftime("%I:%M %p"),
                    "duration": slot_duration,
                    "type": slot_type,
                    "interviewer": interviewer,
                    "status": "Scheduled"
                }
                st.session_state.hr_schedule.append(new_slot)
                st.success("Interview slot added!")
                st.rerun()

with col2:
    st.markdown("### 📈 Test Performance")
    
    if 'test_score' in st.session_state:
        score = st.session_state.test_score
        total = 10
        percentage = (score / total) * 100
        
        st.metric("Test Score", f"{score}/{total}")
        st.metric("Percentage", f"{percentage:.1f}%")
        
        # Progress bar
        st.progress(percentage / 100)
        
        if score >= 7:
            st.success("✅ Passed - Eligible for HR Round")
        else:
            st.error("❌ Not Passed")
    
    st.markdown("---")
    
    st.markdown("### 📋 Quick Actions")
    
    if st.button("📝 View Resume", use_container_width=True):
        if 'resume_data' in st.session_state:
            st.json(st.session_state.resume_data)
        else:
            st.info("No resume data available")
    
    if st.button("🔄 Retake Test", use_container_width=True):
        st.session_state.test_passed = False
        st.switch_page("pages/test_interface.py")
    
    if st.button("📄 Download Resume Data", use_container_width=True):
        if 'resume_data' in st.session_state:
            import json
            json_str = json.dumps(st.session_state.resume_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="resume_data.json",
                mime="application/json"
            )
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Information")
    st.info("""
    **Next Steps:**
    1. Review your interview schedule
    2. Confirm your preferred time slot
    3. Prepare for the interview
    4. Contact HR for any queries
    """)

