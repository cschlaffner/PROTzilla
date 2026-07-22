import plotly
import plotly.express as px

PLOT_COLOR_SEQUENCE = [
    "#4A536A",
    "#CE5A5A",
    "#87A8B9",
    "#A7A1B2",
    "#F1A765",
    "#8E3F25",
]
"""List of colors to use in plots."""

PLOT_PRIMARY_COLOR = PLOT_COLOR_SEQUENCE[0]
"""First color in list. Conventionally used for visualizing outliers."""

PLOT_SECONDARY_COLOR = PLOT_COLOR_SEQUENCE[1]
"""Second color in list."""


def rgb_to_hex(rgb):
    # Convert RGB tuples back to hex color strings
    return f"#{''.join(f'{c:02x}' for c in rgb)}"


def interpolate_color(color_a, color_b, t):
    """
    Interpolate between two RGB color strings based on a float t between 0 and 1.

    :param color_a: RGB color string in the format "#RRGGBB".
    :param color_b: RGB color string in the format "#RRGGBB".
    :param t: A float between 0 and 1 representing the interpolation factor.

    :return: Interpolated color as an RGB string in the format "#RRGGBB".
    """
    if not 0 <= t <= 1:
        raise ValueError("Interpolation factor t must be between 0 and 1")

    # Convert hex color strings to RGB tuples
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    rgb_a = hex_to_rgb(color_a)
    rgb_b = hex_to_rgb(color_b)

    # Interpolate each color channel
    interpolated_rgb = tuple(int(a + (b - a) * t) for a, b in zip(rgb_a, rgb_b))

    return rgb_to_hex(interpolated_rgb)

ALL_PLOTLY_COLORSCALES = px.colors.named_colorscales()
ALL_PLOTLY_COLORSCALES_WITH_REVERSED = ALL_PLOTLY_COLORSCALES + [i + "_r" for i in ALL_PLOTLY_COLORSCALES]
ALL_PLOTLY_DIVERGING_COLORSCALES_WITH_REVERSED = list(filter(lambda x: not x.startswith("_") and not x.startswith("swatches"), dir(plotly.colors.diverging)))
