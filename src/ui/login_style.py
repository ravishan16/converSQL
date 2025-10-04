import streamlit as st


def load_login_css():
    st.markdown(
        """
    <style>
    :root {
        --color-background: #FAF6F0;
        --color-background-alt: #FDFDFD;
        --color-text-primary: #3A3A3A;
        --color-text-secondary: #7C6F64;
        --color-accent-primary: #DDBEA9;
        --color-accent-primary-darker: #B45F4D;
        --color-border-light: #E4C590;
    }

    .footer-links {
        margin-top: 1rem;
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .footer-links a {
        color: var(--color-accent-primary-darker);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .footer-links a:hover {
        color: #d89c7f;
    }

    .login-wrapper {
        max-width: 560px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.75rem;
    }

    .login-hero {
        text-align: center;
        padding: 1.5rem 1rem 0 1rem;
        margin: 0;
    }

    .login-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .login-logo img {
        width: clamp(280px, 70vw, 460px);
        height: auto;
        filter: drop-shadow(0 12px 28px rgba(180, 95, 77, 0.18));
    }

    .login-logo--fallback {
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: 0.06em;
        color: var(--color-text-primary, #3A3A3A);
    }

    .login-tagline {
        color: var(--color-text-secondary, #7C6F64);
        font-size: 1.05rem;
        margin: 0.25rem 0 0 0;
    }

    .login-card {
        width: 100%;
        background: linear-gradient(140deg, var(--color-background-alt, #FDFDFD) 0%, var(--color-background, #FAF6F0) 100%);
        border: 1px solid var(--color-border-light, #E4C590);
        border-radius: 18px;
        padding: 2.5rem 2.25rem;
        text-align: center;
        box-shadow: 0 18px 40px rgba(180, 95, 77, 0.18);
    }

    .login-card h3 {
        color: var(--color-text-primary, #3A3A3A);
        font-weight: 500;
        margin-bottom: 0.85rem;
        letter-spacing: 0.01em;
    }

    .login-card p {
        color: var(--color-text-secondary, #7C6F64);
        margin-bottom: 1.75rem;
        line-height: 1.65;
    }

    .login-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        width: min(320px, 100%);
        margin: 0 auto 1.75rem auto;
        padding: 0.9rem 1.5rem;
        border-radius: 999px;
        border: 1px solid var(--color-accent-primary-darker, #B45F4D);
        background: linear-gradient(120deg, var(--color-accent-primary, #DDBEA9) 0%, var(--color-accent-primary-darker, #B45F4D) 100%);
        color: var(--color-background-alt, #FDFDFD);
        font-weight: 600;
        text-decoration: none;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 12px 24px rgba(180, 95, 77, 0.22);
    }

    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 30px rgba(180, 95, 77, 0.28);
    }

    .login-button--disabled {
        cursor: not-allowed;
        opacity: 0.7;
        background: linear-gradient(120deg, rgba(221, 190, 169, 0.6) 0%, rgba(180, 95, 77, 0.6) 100%);
        box-shadow: none;
    }

    .login-details {
        margin-top: 1.25rem;
        background: rgba(221, 190, 169, 0.18);
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid rgba(228, 197, 144, 0.55);
        text-align: left;
    }

    .login-details strong {
        color: var(--color-text-primary, #3A3A3A);
    }

    .login-divider {
        width: 100%;
        margin: 0 auto 1.75rem auto;
        border-bottom: 1px solid rgba(228, 197, 144, 0.5);
    }

    </style>
    """,
        unsafe_allow_html=True,
    )
