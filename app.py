# from click import pass_context
import streamlit as st
import pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import spacy
import pandas as pd
import re

nlp = spacy.load("en_core_web_sm")

st.markdown("""
    ## :office: Applicant Filtering System
    [![Twitter](https://img.shields.io/twitter/url?label=Twitter&style=social&url=https%3A%2F%2Ftwitter.com%2Fnainia_ayoub)](https://www.twitter.com/Ashish02lotake)
    [![Linkedin](https://img.shields.io/twitter/url?label=Linkedin&logo=linkedin&style=social&url=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fayoub-nainia%2F%3Flocale%3Den_US)](https://www.linkedin.com/in/ashish-lotake/?locale=en_US)
    [![GitHub](https://img.shields.io/twitter/url?label=Github&logo=GitHub&style=social&url=https%3A%2F%2Fgithub.com%2Fnainiayoub)](https://github.com/ashishlotake)

    It would help if you defined what skills the applicant should have. Then upload the resume and you will get the applicants who have those skills and who don't.
""")

# this code from
# https://github.com/nainiayoub/pdf-text-data-extractor/blob/main/functions.py


def convert_pdf_to_txt_pages(path):
    texts = []
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    size = 0
    c = 0
    file_pages = PDFPage.get_pages(path)
    nbPages = len(list(file_pages))
    for page in PDFPage.get_pages(path):
      interpreter.process_page(page)
      t = retstr.getvalue()
      if c == 0:
        texts.append(t)
      else:
        texts.append(t[size:])
      c = c+1
      size = len(t)
    # text = retstr.getvalue()

    # fp.close()
    device.close()
    retstr.close()
    return texts, nbPages


# capturing the content from the text files

def parse_content(text, in_skills):
    
    ##### Here skillset and phone_num are the template of what we are looking in the text
    # here we have to define what skillset do we expect the resume of applicant have 
    
    skillset = re.compile(in_skills) # eg skills for Data Science role
    
    #phone_num credit https://stackoverflow.com/a/3868861
    phone_num = re.compile(
        "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
    )
    text = text.replace("•","")
    text.strip()
    text = text.replace("\n","") # removing new lines from text  
    text = text.replace("\t","") # removing tabs from text
    text = re.sub(' +', ' ',text) ## removing all the multiple space

    doc = nlp(text)
    name = [entity.text for entity in doc.ents if entity.label_ == "PERSON"][0]
    ## in spacy "PERSON" if for name, and the first name is for applicant
    ## because it may happen that a resume have multiple names in it.
    # print(name)
    email = [str(word) for word in doc if word.like_email == True][0]
    # print(email)
    phone = str(re.findall(phone_num, text.lower()))
    skills_set = re.findall(skillset, text.lower())
    ## if may happen that a skill is mention more than once
    unique_skill_set = set(skills_set)
    names.append(name)
    emails.append(email)
    phones.append(phone)
    skills.append(unique_skill_set)
    # print("Extraction done")

in_skills = st.text_input("Accepted skills from the applicants", placeholder= "Leadership,SQL,Pyhton,Adobe,CAD,Creo,etc")
st.caption("Enter values separated by commas and please check before uploading resume.")
in_skills = in_skills.lower()
in_skills = re.sub(" +", "", in_skills)
in_skills= in_skills.replace(",","|")
st.write(in_skills)



pdf_files = st.file_uploader("Please upload multiple/single RESUME", type="pdf", accept_multiple_files=True)

if pdf_files:
    # definfing main component which is to be captured form resumes

    result_dict = {"name":[], "phone":[], "email":[], "skills":[]}
    # we will be using dict to store info for each applicant

    # we will be populating this list for all the applicants
    names = []
    phones = []
    emails = []
    skills = []
    for file in pdf_files:
        txt, npage = convert_pdf_to_txt_pages(file)
        # st.write(txt, len(txt),  type(txt[0]))
        # st.write(txt[0])
        text = txt[0]
        parse_content(text,in_skills)
        
        
    result_dict["name"] = names
    result_dict["email"] = emails
    result_dict["phone"] = phones
    result_dict["skills"] = skills

    final_df = pd.DataFrame(result_dict)

    def proper_num(x):  ## this program print number only 
        return int(re.sub('[^a-zA-Z0-9]+', '',x ))
    final_df["phone"] = final_df["phone"].apply(proper_num)


    ## filtering out those applicant which have skills
    for i in range(len(final_df)-1):
        if len(final_df.iloc[i]["skills"]) == 0:
            final_df.drop(labels=i, axis=0, inplace=True)
        else:
            pass

    st.dataframe(final_df)



    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(final_df)

    
    st.download_button("Press to Download CSV.",csv,"file.csv","text/csv",key='download-csv')

    st.caption("This app is still underprogress, it it fails/give wrong output please report bug")