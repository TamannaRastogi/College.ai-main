import streamlit as st
import sqlite3
import random
import string
from httpx_oauth.clients.google import GoogleOAuth2
# Database initialization
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')
conn.commit()

st.title("College.ai")


import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2



client_id = "client_id"
client_secret = "client_secent"
redirect_url = "xxx"  # Your redirect URL

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)


async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    return await client.get_access_token(code, redirect_url)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_logged_in_user_email():
    try:
        query_params = st.query_params()
        code = query_params.get('code')
        if code:
            token = asyncio.run(get_access_token(client, redirect_url, code))
            st.experimental_set_query_params()

            if token:
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_email)
                    st.session_state.email = user.email
                    return user.email
        return None
    except:
        pass

def show_login_button():
    # Define the HTML for the button
    authorization_url = asyncio.run(client.get_authorization_url(
        redirect_url,
        scope=["email", "profile"],
        extras_params={"access_type": "offline"},
    ))
    button_html = f'<a href="{authorization_url}" target="_self" style="text-decoration: none;"><button style="background-color: #2F80ED; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; cursor: pointer;">Login via Google</button></a>'
    st.markdown(button_html, unsafe_allow_html=True)

# Function to generate OTP

def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

# Function to send OTP (dummy implementation)
def send_otp(email, otp):
    # Dummy implementation, replace with actual email sending logic
    st.write(f"An OTP has been sent to {email}. Your OTP is: {otp}")


def main():
   
    st.write("<h1><center> Authentication Portal</center></h1>", unsafe_allow_html=True)
    
    
    if "logged_in" not in st.session_state:
        form_type = st.selectbox('login/Signup',['Login','Sign Up','Forgot Password'])
        
        if form_type == "Login":
           
            form = st.form(key="login_form")
            form.subheader("Login")

            user = form.text_input("Username")
            password = form.text_input("Password", type="password")

            if form.form_submit_button("Login"):
               
                # Check if username and password are correct
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, password))
                result = c.fetchone()
                if result:
                    st.session_state["user"] = user
                    st.session_state["logged_in"] = True
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password")
            
            get_logged_in_user_email()
            show_login_button()

        elif form_type == "Sign Up":
            form = st.form(key="signup_form")
            form.subheader("Sign Up")

            new_user = form.text_input("New Username")
            new_password = form.text_input("New Password", type="password")
            email = form.text_input("Email")

            if form.form_submit_button("Sign Up"):
                # Add user to database
                c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                          (new_user, new_password, email))
                conn.commit()
                st.success("Account created successfully! Please login.")
                #st.balloons()
            get_logged_in_user_email()
            show_login_button()

        elif form_type == "Forgot Password":
            form = st.form(key="forgot_password_form")
            form.subheader("Forgot Password")

            email = form.text_input("Enter Email")

            if form.form_submit_button("Send OTP"):
                # Check if email exists in database
                c.execute("SELECT * FROM users WHERE email=?", (email,))
                result = c.fetchone()
                if result:
                    otp = generate_otp()
                    send_otp(email, otp)
                    st.success("OTP sent successfully! Check your email.")
                else:
                    st.error("Email not found in database")

    else:
        st.subheader("Logged in")
        st.write("You are logged in as:", st.session_state["user"])

        if st.button("Logout"):
            del st.session_state["logged_in"]
            del st.session_state["user"]
            st.success("Logged out successfully!")


if __name__ == "__main__":
    main()