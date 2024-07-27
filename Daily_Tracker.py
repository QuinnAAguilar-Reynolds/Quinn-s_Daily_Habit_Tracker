from shiny import App, render, ui, input, output
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Functions
def load_data(file_path):
    """Load CSV data into a DataFrame."""
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        data = pd.DataFrame(columns=['Date', 'Task', 'Duration'])
    return data

def add_entry(file_path, date, task, duration):
    """Add a new entry to the CSV file."""
    data = load_data(file_path)
    new_entry = pd.DataFrame([[date, task, duration]], columns=['Date', 'Task', 'Duration'])
    data = pd.concat([data, new_entry], ignore_index=True)
    data.to_csv(file_path, index=False)

def plot_data(file_path):
    """Generate a plot of the data from the CSV file."""
    data = load_data(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    data['Duration'] = pd.to_numeric(data['Duration'], errors='coerce')

    plt.figure(figsize=(10, 6))
    for task in data['Task'].unique():
        task_data = data[data['Task'] == task]
        plt.plot(task_data['Date'], task_data['Duration'], label=task, marker='o')

    plt.xlabel('Date')
    plt.ylabel('Duration (minutes)')
    plt.title('Chore Adherence Over Time')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.read()).decode()

# Shiny app
def app_ui():
    return ui.page_fluid(
        ui.input_file("file", "Upload CSV File"),
        ui.input_text("date", "Date (YYYY-MM-DD)"),
        ui.input_text("task", "Task"),
        ui.input_numeric("duration", "Duration (minutes)", min=0),
        ui.action_button("add", "Add Entry"),
        ui.output_ui("data_table"),
        ui.output_ui("plot")
    )

def server(input, output, session):
    file_path = "data.csv"

    @output()
    @render.ui
    def data_table():
        data = load_data(file_path)
        if not data.empty:
            return ui.table(data)
        return ui.p("No data available.")

    @output()
    @render.ui
    def plot():
        if input.file():
            img_data = plot_data(file_path)
            return ui.img(src=f"data:image/png;base64,{img_data}")
        return ui.p("Upload a CSV file to see the plot.")

    @input.add("add")
    def handle_add_entry():
        add_entry(file_path, input.date(), input.task(), float(input.duration()))
        output.data_table.update()
        output.plot.update()

app = App(app_ui, server)

# Run the app
run_app(app)
