import streamlit as st


def show_in_between_instruction():
    # Disable scrolling on the main app containers
    st.markdown(
        """
        <style>
        .stMainBlockContainer {
            padding-top: 60px !important;
        }
        html, body, [data-testid="stAppViewContainer"], .block-container {
            overflow: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Using a parent container that is positioned relative so our arrow/text are relative to it.
    if st.session_state.study_xui_selection is None and (not st.session_state.explanatory_xui_study_finished or not st.session_state.exploratory_xui_study_finished):

        st.markdown(
            """
            <style>
                /* Parent container now does not force 100vh */
                .parent-container {
                    position: relative;
                    width: 100%;
                    /* Let its height adjust with content */
                    min-height: 300px;
                }
                /* Arrow and text positioned relative to the parent container */
                .arrow-text-container {
                    position: absolute;
                    top: 1.5rem; /* distance from the parent's top edge */
                    left: -2.5rem; /* adjust as needed */
                    display: flex;
                    align-items: center; 
                    gap: 0.75rem;
                    animation: arrowAnimation 1s infinite ease-in-out;
                }
                .fancy-arrow {
                    font-size: 3rem;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
                }
                .instruction-text {
                    font-size: 1.5rem;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
                }
                @keyframes arrowAnimation {
                    0% { transform: translateX(0); }
                    50% { transform: translateX(10px); }
                    100% { transform: translateX(0); }
                }
            </style>
            <div class="parent-container">
                <div class="arrow-text-container">
                    <div class="fancy-arrow">&#11013;</div>
                    <div class="instruction-text">Select a User Interface</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.session_state.current_patient_index < 3:
            text = "Load Patient Data"
        elif not st.session_state.explanatory_xui_study_finished or not st.session_state.exploratory_xui_study_finished:
            text = "Evaluate the User Interface"
        else:
            text = "Compare both User Interfaces"
        st.markdown(
            f"""
            <style>
                .parent-container {{
                    position: relative;
                    width: 100%;
                    min-height: 300px;
                }}
                .arrow-text-container {{
                    position: absolute;
                    top: 19.5rem; /* adjust vertical placement relative to parent */
                    left: -2.5rem;
                    display: flex;
                    align-items: center; 
                    gap: 0.75rem;
                    animation: arrowAnimation 1s infinite ease-in-out;
                }}
                .fancy-arrow {{
                    font-size: 3rem;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
                }}
                .instruction-text {{
                    font-size: 1.5rem;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
                }}
                @keyframes arrowAnimation {{
                    0% {{ transform: translateX(0); }}
                    50% {{ transform: translateX(10px); }}
                    100% {{ transform: translateX(0); }}
                }}
            </style>
            <div class="parent-container">
                <div class="arrow-text-container">
                    <div class="fancy-arrow">&#11013;</div>
                    <div class="instruction-text">{text}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
