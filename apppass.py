import re

def check_password_validity(password, min_length, max_length, invalid_chars):
    # Check password length
    if len(password) < min_length or len(password) > max_length:
        return "NotValid: Password length should be between {} and {} characters.".format(min_length, max_length)

    # Check for at least one number
    if not any(char.isdigit() for char in password):
        return "NotValid: Password must contain at least one number."

    # Check for at least two uppercase letters
    if len(re.findall(r'[A-Z]', password)) < 2:
        return "NotValid: Password must contain at least two uppercase letters."

    # Check for invalid characters
    if any(char in password for char in invalid_chars):
        return "NotValid: Password contains invalid characters."

    # Password is valid
    return "Valid"


# Admin form (VF) to set password requirements
def admin_form():
    min_length = int(input("Enter minimum password length: "))
    max_length = int(input("Enter maximum password length: "))
    invalid_chars = input("Enter invalid characters (if any): ")
    return min_length, max_length, invalid_chars


# User form (CP) to check password validity
def user_form():
    password = input("Enter password: ")
    return password


# Main program
if __name__ == "__main__":
    # Admin form to set password requirements
    print("Admin Form (VF)")
    min_length, max_length, invalid_chars = admin_form()

    # User form to check password validity
    print("\nUser Form (CP)")
    password = user_form()

    # Check password validity
    result = check_password_validity(password, min_length, max_length, invalid_chars)
    print("\nResult: {}".format(result))
