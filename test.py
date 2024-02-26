import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc, html
import datetime

today_date = datetime.date.today().strftime("%Y-%m-%d")

combined_df = pd.read_csv(f"daily_prices/{today_date}.csv", index_col=0)
combined_df = combined_df.sort_values(by='Avg Price', ascending=False)

# Sort the index alphabetically
sorted_vegetables = sorted(combined_df.index)

# Define your Dash app
app = dash.Dash(__name__)

# Define the app layout with a date picker, letter selector, and the graph
app.layout = html.Div([
    dcc.DatePickerSingle(
        id='date-picker',
        date=today_date,
        display_format='YYYY-MM-DD'
    ),
    dcc.Dropdown(
        id='commodity-selector',
        options=[{'label': vegetable, 'value': vegetable} for vegetable in sorted_vegetables],
        value=[],
        multi=True,
        placeholder="Select commodities"
    ),
    dcc.Graph(id='price-graph'),
    html.Div(id='date-validation-message', children='')  # Add this element
])

# Define the callback function to update the chart
@app.callback(
    dash.dependencies.Output('price-graph', 'figure'),
    dash.dependencies.Output('date-validation-message', 'children'),  # Add this output
    [dash.dependencies.Input('commodity-selector', 'value'),
     dash.dependencies.Input('date-picker', 'date')]
)
def update_graph(selected_commodities, selected_date):
    # Construct the filename based on the selected date
    selected_filename = f"daily_prices/{selected_date}.csv"

    try:
        # Try to read the selected CSV file into a DataFrame
        selected_df = pd.read_csv(selected_filename, index_col=0)
        selected_df = selected_df.sort_values(by='Avg Price', ascending=False)
    except FileNotFoundError:
        # If the file is not found, return an empty figure and a validation message
        return go.Figure(), "Invalid date selected. No data available."

    fig = go.Figure()

    if selected_commodities:
        # If multiple commodities are selected, create line charts for each selected commodity
        for selected_letter in selected_commodities:
            selected_vegetable = selected_df.loc[selected_letter]
            nepali_name = selected_df.loc[selected_letter, 'Nepali']
            fig.add_trace(go.Scatter(x=selected_vegetable.index, y=selected_vegetable.values, mode='lines+markers', name=f"{selected_letter} ({nepali_name}"))

        fig.update_layout(
            yaxis_title='Price',
            autosize=True,
            width=1500,
            height=750,
            template="plotly_dark",
            title="Selected Commodities Prices",
        )
    else:
        # If no commodities are selected, create a custom vertical line chart
        customdata = list(zip(selected_df['Nepali'], selected_df['Min Price'], selected_df['Avg Price'], selected_df['Max Price']))
        custom_hovertemplate = '<b>%{x}</b><br>नेपाली: %{customdata[0]}<br>Min Price: %{customdata[1]}<br>Avg Price: %{customdata[2]}<br>Max Price: %{customdata[3]}'
        
        for index, row in selected_df.iterrows():
            # Create a vertical line for each vegetable
            fig.add_trace(go.Bar(
                x=[index],
                y=[row['Max Price'] - row['Min Price']],
                base=[row['Min Price']],
                name=f"{index} ({row['Nepali']}",
                marker_color='#B0E0E6',  # You can customize the color as needed
                customdata=[[row['Nepali'], row['Min Price'], row['Avg Price'], row['Max Price']]],
                hovertemplate=custom_hovertemplate
            ))

        fig.update_layout(
            yaxis_title='',
            autosize=True,
            width=1500,
            height=750,
            template="plotly_dark",
            title="Vegetable Prices (Min, Avg, and Max)",
        )
    
    fig.update_xaxes(showticklabels=False)

    return fig, ""  # Clear the validation message if data is found

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
