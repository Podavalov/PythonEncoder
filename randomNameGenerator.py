import random
import string

def generate_random_name(length=10):
    first_char = random.choice(string.ascii_letters)
    other_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))
    return first_char + other_chars

def create_rename_mapping(old_names, name_length=10):
    mapping = {}
    used_new_names = set()

    for old in old_names:
        while True:
            new_name = generate_random_name(name_length)
            if new_name not in used_new_names:
                used_new_names.add(new_name)
                mapping[old] = new_name
                break

    return mapping