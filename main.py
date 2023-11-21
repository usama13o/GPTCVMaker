

import streamlit as st
import openai
import subprocess
import PyPDF2

# Set up OpenAI API key
# openai.api_key = ''

# Define the Streamlit app
@st.cache
def generate_cover_letter(job_description, cv_file, tone,template):
    # Read the CV file

    pdf_reader = PyPDF2.PdfReader(cv_file)
    cv_text = ""
    for page in pdf_reader.pages:
        cv_text += page.extract_text()
    # print(cv_text)
    
    # Generate prompts for GPT-4 model based on the selected tone
    if tone == "Professional":
        prompt = f"As a recruiter, I am writing a professional cover letter for the job with the following description:\n\n{job_description}\n\nBased on the CV provided, I would like to highlight the following experiences and projects:\n\n{cv_text}\n\nUse the following latex template to generate the cover letter in latex:\n\n{template}\n\n"
    elif tone == "Friendly":
        prompt = f"As a recruiter, I am writing a friendly cover letter for the job with the following description:\n\n{job_description}\n\nBased on the CV provided, I would like to highlight the following experiences and projects:\n\n{cv_text}\n\nUse the following latex template to generate the cover letter in latex:\n\n{template}\n\n"
    else:
        prompt = f"As a recruiter, I am writing a neutral cover letter for the job with the following description:\n\n{job_description}\n\nBased on the CV provided, I would like to highlight the following experiences and projects:\n\n{cv_text}\n\nUse the following latex template to generate the cover letter in latex:\n\n{template}\n\n"
    # Call the OpenAI API to generate the cover letter using the prompt
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You're an expert at matching people to jobs and wrting cover letters. Reply only in LaTeX format. Without any introduction.Don't Make stuff up Use the CV for the cover letter."},
                  {"role": "user", "content": prompt},
                  ],
        max_tokens=4096,
        # temperature=0.7,
        n=1,
        stop=None,
        # temperature=0.7
    )
    
    # Extract the generated cover letter from the API response
    print(response.choices[0].message.content)
    cover_letter = response.choices[0].message.content
    #remove ''' at the beginning and end of the cover letter
    cover_letter = cover_letter[3+5:-3]
    return cover_letter

# Define the layout of the app
def app():
    st.title("Cover Letter Generator")
    
    # Input fields
    job_description = st.text_area("Job Description", height=200)
    cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Neutral"])
    #pull template from  file .tex and put it in the text area
    with open(r"cover_letter.tex", "r") as f:
        template = f.read()
        st.text_area("Template for CV", value=template, height=200)
    openai.api_key = st.text_input("OpenAI API Key", type="password")

    # Generate cover letter button
    if st.button("Generate Cover Letter"):
        if job_description and cv_file:
            cover_letter = generate_cover_letter(job_description, cv_file, tone,template)
            
            # Save the cover letter as a LaTeX file
            print("################### Save the cover letter as a LaTeX file ###################")
            with open(r"cover_letter_uz.tex", "w") as f:
                f.write(cover_letter)
            
            # Generate PDF from LaTeX
            print("################### Generate PDF from LaTeX ###################")
            subprocess.run(["xelatex","-interaction=batchmode", r"cover_letter_uz.tex"])
            # subprocess.run(["dvipdf", "cover_letter.dvi"])
            
            # Provide a download link/button for the user
            with open(r"cover_letter_uz.pdf", "rb") as f:
                st.download_button("Download Cover Letter", f, file_name="cover_letter_uz.pdf")
            
            st.success("Cover letter generated successfully!")
            print("################### Open PDF file ###################")
            #open pdf file windows 
            subprocess.run(["start", r"cover_letter_uz.pdf"], shell=True)
        else:
            st.warning("Please provide both the job description and CV file.")

# Run the app
if __name__ == "__main__":
    app()