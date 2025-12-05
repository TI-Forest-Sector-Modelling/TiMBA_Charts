import seaborn as sns


def generate_color_palette(palette_name: str, n_colors: int):
    try:
        palette = sns.color_palette(palette_name, n_colors=n_colors)
    except IndexError:
        palette = sns.color_palette("Spectral", as_cmap=True, n_colors=n_colors)
    return palette.as_hex()

