def pretty_snakecase(name):
    # Make a prettier version of the capsule name, for display purposes
    name = (name
            .replace('_', ' ')
            .replace('-', ' ')
            .strip()
            .title())
    name = ''.join([c for c in name
                    if c.isalnum() or c == ' '])
    return name
