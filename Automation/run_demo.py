#!/usr/bin/env python
"""
Simple demo script to run the resume parser
"""
import sys
import os
from pprint import pprint

# Add the current directory to the path so we can import from local source
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyresparser import ResumeParser

def main():
    # Use the sample resume that comes with the project
    resume_file = 'OmkarResume.pdf'
    
    if not os.path.exists(resume_file):
        print(f"Error: Resume file '{resume_file}' not found!")
        print("Please make sure you're running this from the pyresparser directory.")
        return
    
    print("=" * 60)
    print("Resume Parser Demo")
    print("=" * 60)
    print(f"\nExtracting data from: {resume_file}\n")
    
    try:
        parser = ResumeParser(resume_file)
        data = parser.get_extracted_data()
        
        print("\n" + "=" * 60)
        print("Extracted Resume Data:")
        print("=" * 60)
        pprint(data)
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

