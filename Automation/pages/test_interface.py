"""
Test Interface Page
MCQ test with proctoring
"""
import streamlit as st
import time
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from proctoring import ProctoringSystem
import cv2

st.set_page_config(
    page_title="Skills Assessment Test",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 10
if 'test_completed' not in st.session_state:
    st.session_state.test_completed = False
if 'proctoring' not in st.session_state:
    st.session_state.proctoring = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

st.markdown("""
    <style>
    .test-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .timer-box {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .violation-alert {
        background-color: #ffcccc;
        border: 2px solid #ff0000;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load questions from session state
if not st.session_state.questions and 'test_questions' in st.session_state:
    st.session_state.questions = st.session_state.test_questions

if not st.session_state.questions:
    st.error("No questions available. Please go back and extract a resume first.")
    st.stop()

questions = st.session_state.questions
total_questions = len(questions)

# Header
st.markdown('<h1 class="test-header">📝 Skills Assessment Test</h1>', unsafe_allow_html=True)

# Proctoring section
col1, col2 = st.columns([2, 1])

with col1:
    if not st.session_state.test_started:
        st.info("""
        **Test Instructions:**
        - You have 10 seconds to answer each question
        - Proctoring will monitor your camera and audio
        - Multiple persons detected will result in violation
        - You need to score at least 7/10 to pass
        - Click 'Start Test' when ready
        """)
        
        if st.button("🎬 Start Test", type="primary", use_container_width=True):
            # Initialize proctoring
            st.session_state.proctoring = ProctoringSystem()
            if st.session_state.proctoring.start_monitoring():
                st.session_state.test_started = True
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.session_state.time_remaining = 10
                st.session_state.question_start_time = time.time()
                st.rerun()
            else:
                st.error("Could not initialize camera. Please allow camera access and try again.")
    
    elif not st.session_state.test_completed:
        # Show current question
        q_idx = st.session_state.current_question
        question_data = questions[q_idx]
        
        # Initialize question start time if not set
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()
        
        # Calculate time remaining based on elapsed time
        elapsed_time = time.time() - st.session_state.question_start_time
        time_remaining = max(0, int(10 - elapsed_time))
        
        # Update session state
        st.session_state.time_remaining = time_remaining
        
        # Timer display with color coding
        if time_remaining > 0:
            timer_color = "#ff4444" if time_remaining <= 3 else "#ff8800" if time_remaining <= 5 else "#1f77b4"
            st.markdown(
                f'<div class="timer-box" style="background-color: {timer_color};">⏱️ Time Remaining: {time_remaining} seconds</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="timer-box" style="background-color: #ff0000;">⏱️ Time\'s Up!</div>', 
                unsafe_allow_html=True
            )
        
        # Question
        st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"### Question {q_idx + 1} of {total_questions}")
        st.markdown(f"**{question_data['question']}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Options
        selected_option = st.radio(
            "Select your answer:",
            options=question_data['options'],
            key=f"q_{q_idx}",
            index=None
        )
        
        # Navigation buttons
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("⏭️ Next Question", disabled=(selected_option is None), use_container_width=True):
                # Save answer
                st.session_state.answers[q_idx] = {
                    'selected': question_data['options'].index(selected_option) if selected_option else None,
                    'correct': question_data['correct']
                }
                
                # Move to next question or complete
                if q_idx < total_questions - 1:
                    st.session_state.current_question += 1
                    st.session_state.question_start_time = time.time()
                    st.session_state.time_remaining = 10
                    st.session_state.last_timer_update = time.time()  # Reset timer update
                else:
                    st.session_state.test_completed = True
                st.rerun()
        
        with col_btn2:
            if st.button("✅ Submit Test", use_container_width=True):
                # Save current answer if selected
                if selected_option is not None:
                    st.session_state.answers[q_idx] = {
                        'selected': question_data['options'].index(selected_option),
                        'correct': question_data['correct']
                    }
                st.session_state.test_completed = True
                st.rerun()
        
        # Auto-advance when timer reaches 0
        if time_remaining <= 0:
            # Auto-submit current question (save None if no answer selected)
            st.session_state.answers[q_idx] = {
                'selected': question_data['options'].index(selected_option) if selected_option else None,
                'correct': question_data['correct']
            }
            
            # Move to next or complete
            if q_idx < total_questions - 1:
                st.session_state.current_question += 1
                st.session_state.question_start_time = time.time()
                st.session_state.time_remaining = 10
                st.session_state.last_timer_update = time.time()  # Reset timer update
                st.rerun()
            else:
                st.session_state.test_completed = True
                st.rerun()
        
        # Auto-refresh timer - rerun every second to update display
        if 'last_timer_update' not in st.session_state:
            st.session_state.last_timer_update = time.time()
        
        # Only rerun if at least 1 second has passed
        time_since_update = time.time() - st.session_state.last_timer_update
        if time_remaining > 0 and time_since_update >= 1.0:
            st.session_state.last_timer_update = time.time()
            st.rerun()
    
    else:
        # Test completed - show results
        st.success("✅ Test Completed!")
        
        # Calculate score
        correct = 0
        total = len(st.session_state.answers)
        for q_idx, answer_data in st.session_state.answers.items():
            if answer_data['selected'] == answer_data['correct']:
                correct += 1
        
        score = correct
        percentage = (correct / total_questions) * 100
        passed = correct >= 7
        
        # Display results
        st.markdown("### 📊 Test Results")
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric("Score", f"{correct}/{total_questions}")
        
        with col_res2:
            st.metric("Percentage", f"{percentage:.1f}%")
        
        with col_res3:
            status = "✅ PASSED" if passed else "❌ FAILED"
            st.metric("Status", status)
        
        # Show detailed results
        with st.expander("View Detailed Results"):
            for q_idx in range(total_questions):
                q = questions[q_idx]
                answer_data = st.session_state.answers.get(q_idx, {})
                selected_idx = answer_data.get('selected')
                correct_idx = answer_data.get('correct')
                
                st.markdown(f"**Question {q_idx + 1}:** {q['question']}")
                for i, opt in enumerate(q['options']):
                    marker = ""
                    if i == correct_idx:
                        marker = "✓ (Correct)"
                    if selected_idx == i:
                        if i == correct_idx:
                            marker = "✓ (Your Answer - Correct)"
                        else:
                            marker = "✗ (Your Answer - Wrong)"
                    st.markdown(f"  {chr(65+i)}. {opt} {marker}")
                st.markdown("---")
        
        # Proctoring violations
        if st.session_state.proctoring:
            violations = st.session_state.proctoring.get_violations_summary()
            if violations['total_violations'] > 0:
                st.warning(f"⚠️ Proctoring Violations Detected: {violations['total_violations']}")
                st.json(violations)
        
        # Next steps
        if passed:
            st.success("🎉 Congratulations! You passed the test. You are eligible for the HR round.")
            if st.button("📊 Go to Dashboard", type="primary", use_container_width=True):
                st.session_state.test_passed = True
                st.session_state.test_score = score
                st.switch_page("pages/dashboard.py")
        else:
            st.error("❌ You did not pass the test. Minimum score required: 7/10")
            st.info("You can try again later.")
            if st.button("🔄 Retake Test", use_container_width=True):
                # Reset test state
                st.session_state.test_started = False
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.session_state.test_completed = False
                st.session_state.time_remaining = 10
                st.rerun()
        
        # Stop proctoring
        if st.session_state.proctoring:
            st.session_state.proctoring.stop_monitoring()

with col2:
    # Proctoring camera feed
    if st.session_state.test_started and st.session_state.proctoring and not st.session_state.test_completed:
        st.markdown("### 📹 Proctoring Monitor")
        
        # Get frame from proctoring system
        frame, status = st.session_state.proctoring.get_frame()
        
        if frame is not None:
            # Convert BGR to RGB for Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Show status
            if status:
                if status['multiple_faces']:
                    st.error(f"⚠️ Multiple faces detected: {status['faces_detected']}")
                elif not status['face_detected']:
                    st.warning("⚠️ No face detected")
                else:
                    st.success("✅ Monitoring active")
        
        # Proctoring status display (timer is handled in main column)

