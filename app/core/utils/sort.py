import re


def sort_titles(titles):
    def key_func(title):
        split_title = re.split(r'(\d+)', title)  # split the title into a list of strings and numbers
        return [int(num) if num.isdigit() else num for num in
                split_title]  # convert numbers to int and leave strings as is

    sorted_titles = sorted(titles, key=key_func)
    return sorted_titles
