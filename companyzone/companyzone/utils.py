import html
import nh3 # Ammonia HTML sanitization library

def sanitize_user_input(value, allow_html=True):
    """
    Replaces characters like <, >, and & with their safe 
    HTML entity codes (&lt;, &gt;, &amp;), preventing the browser from 
    interpreting user inputs as executable code.
    """
    # This line is a safety guard to handle fields that are empty, None, or blank so your backend doesn't crash.
    # In Python, if a field is optional, empty, or has a None value 
    # (like a blank middle name or an unselected profile picture field), 
    # running a string operation on it directly will crash your server with an AttributeError.
    if not value or not isinstance(value, str):
        return value


    # return html.escape(value)

    # While html.escape is excellent for general strings, 
    # ---------------------------------------------------
    # using it on strings that get saved directly to the database can sometimes cause text formatting issues. 
    # For instance, a simple symbol like & will be transformed into &amp; 
    # inside your database row, making searching, sorting, or using that text elsewhere a bit messy.

    # The modern standard practice for sanitising API input in Python is to use nh3 or bleach. 
    # They don't distort normal symbols; instead, they selectively scan for and 
    # strip out dangerous strings like <script>, onload=, and javascript:.

    # Since bleach was recently deprecated, nh3 (powered by an incredibly fast Rust engine) is now the recommended tool.
    if allow_html:
        # Best for rich text areas / textareas (strips malicious code)
        return nh3.clean(value)
    else:
        # Best for standard text inputs (names, titles, emails)
        # Completely strips ALL HTML formatting, keeping purely text text
        return nh3.clean_text(value)