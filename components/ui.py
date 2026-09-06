import streamlit as st


def inject_css():

    st.markdown(
        """
        <style>

        /* -----------------------------
           Global
        ----------------------------- */

        .block-container {
            max-width: 900px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        .app-header {
            padding: 0.5rem 0 1.5rem 0;
        }

        .app-title {
            font-size: 2rem;
            font-weight: 700;
        }

        .app-subtitle {
            font-size: 0.95rem;
            opacity: 0.65;
            margin-top: 0.2rem;
        }

        /* -----------------------------
           Welcome
        ----------------------------- */

        .welcome-card {
            padding: 1.5rem;
            border-radius: 20px;
            border: 1px solid rgba(128,128,128,0.25);
            margin-bottom: 1.5rem;
        }

        .welcome-card h1 {
            margin: 0.2rem 0;
        }

        .small-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            opacity: 0.55;
        }

        /* -----------------------------
           Journey
        ----------------------------- */

        .journey-item {
            text-align: center;
            font-size: 0.78rem;
        }

        .journey-icon {
            font-size: 1.6rem;
            margin-bottom: 0.25rem;
        }

        /* -----------------------------
           Mobile
        ----------------------------- */

        @media (max-width: 600px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .app-title {
                font-size: 1.6rem;
            }

            h1 {
                font-size: 1.6rem !important;
            }

            h2 {
                font-size: 1.35rem !important;
            }

            h3 {
                font-size: 1.15rem !important;
            }

            button {
                min-height: 45px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
