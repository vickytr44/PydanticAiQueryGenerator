import matplotlib.pyplot as plt

def generate_chart_image(data, x_col, y_col, chart_type="bar", filename="output_chart.pdf"):
    if x_col not in data.columns or y_col not in data.columns:
        raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in data.")

    plt.figure(figsize=(8, 5))

    if chart_type == "bar":
        grouped = data.groupby(x_col)[y_col].sum()
        grouped.plot(kind="bar", color="skyblue")
    elif chart_type == "line":
        data.plot(x=x_col, y=y_col, kind="line", marker='o')
    elif chart_type == "pie":
        grouped = data.groupby(x_col)[y_col].sum()
        grouped.plot(kind="pie", autopct="%1.1f%%", ylabel='')
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    plt.title(f"{y_col} by {x_col}")

    if chart_type != "pie":
        plt.xlabel(x_col)
        plt.ylabel(y_col)

    plt.tight_layout()
    plt.savefig(f"C:\\PydanticAiReporting\\FileStorage\\{filename}")
    plt.close()

    return filename