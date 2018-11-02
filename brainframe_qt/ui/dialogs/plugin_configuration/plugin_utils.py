def pretty_plugin_name(name):
    # Make a prettier version of the plugin name, for display purposes
    name = (name
            .replace('_', ' ')
            .replace('-', ' ')
            .strip()
            .title())
    name = ''.join([c for c in name
                    if c.isalnum() or c == ' '])
    return name
