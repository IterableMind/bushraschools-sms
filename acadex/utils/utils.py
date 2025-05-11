# app/utils.py
def generate_username(teacher_name):
    """
    Generates a username for the teacher.
    Format: teachername@acadex.com
    """
    return teacher_name.replace(' ', '').lower() + '@bushra'

