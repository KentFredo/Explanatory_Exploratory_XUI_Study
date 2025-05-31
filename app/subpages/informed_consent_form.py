import streamlit as st
import time

# Scroll-to-top JavaScript (executes when modal is opened)
st.markdown("""
    <script>
        function scrollToTop() {
            window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
""", unsafe_allow_html=True)

# Informed Consent Modal


@st.dialog("Informed Consent Form")
def show_informed_consent_modal():
    # Call the scroll function on modal open
    st.components.v1.html("<script>scrollToTop();</script>", height=0)

    # Apply custom CSS for wider content and smaller text
    st.markdown("""
        <style>
        .element-container:has(> .stDialog) .stDialog {
            width: 95vw !important;
            max-width: 1100px !important;
        }
        .consent-text {
            font-size: 0.8em;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="consent-text"> 
    
    ##### Introduction  
    You are invited to take part in a research study conducted as part of a Master’s thesis. The study explores how medical professionals interact with two different **explainable user interfaces (XUIs)** designed to present predictions from a machine learning model that estimates **sepsis-related mortality risk** in ICU patients.

    We are interested in your **feedback, impressions, and thought process** as you engage with the patient data and the interfaces.

    ##### Purpose of the Study  
    The aim of this study is to evaluate how different interface types support clinical decision-making and to gather user-centered insights that can guide the design of future explainable AI tools in healthcare.

    ##### Study Procedures  
    - You will participate in a **single session lasting approximately 90 minutes**.  
    - You will work with **six shown ICU patient cases**—three in each of the two user interfaces (explanatory and exploratory).  
    - For each case, you will:
        - Review raw patient data.  
        - Estimate the patient’s mortality risk.  
        - Rate your certainty in the prognosis. 
        - Repeat the process with the XUI. 
    - You will also complete brief standardized questionnaires on:  
        - System Usability (SUS)  
        - Perceived task load (NASA-TLX)  
        - Explanation Satisfaction  
        - Trust Evaluation  
    - During the session, your **voice will be recorded** as part of a **think-aloud protocol** to capture your reasoning while using the interfaces. The recordings will be transcribed and then permanently deleted.

    ##### Voluntary Participation and Right to Withdraw  
    Your participation is entirely voluntary.  
    You are free to withdraw from the study at any time or to decline to answer any specific question, without providing any reason or facing any consequences.

    ##### Confidentiality  
    - No personally identifying information (such as your name, email, or contact details) will be collected.  
    - Audio recordings will only be used for transcription and qualitative analysis. Once transcribed, the original recordings will be permanently deleted.  
    - All data collected will be stored and analyzed in **anonymized form**, ensuring that individual participants cannot be identified in any publications or reports.

    ##### Potential Risks and Benefits  
    - **Risks**: The study involves minimal risk. You may experience slight fatigue due to the session duration.  
    - **Benefits**: While there is no direct personal benefit, your participation will help improve clinical decision support tools and contribute to research on explainable AI in critical care.

    ---

    ##### Consent  
    By clicking the button below, you confirm that:  
    - You have read and understood the above information.  
    - You agree to participate voluntarily.  
    - You understand that your voice will be recorded for transcription purposes and that no identifying information will be stored.
    </div>
    """, unsafe_allow_html=True)

    if st.button("I agree and give my informed consent to participate", icon=":material/check:"):
        st.session_state.consent_given = True
        st.toast('Informed Consent has been given!',
                 icon=':material/how_to_reg:')
        time.sleep(2)
        st.rerun()
