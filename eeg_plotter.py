import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import sys
import os
from pathlib import Path
import dash
from dash import dcc, html, Input, Output



class EEGPlotter:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = None
        self.channels = []
        self.sample_rate = 200
        
    def parse_eeg_csv(self):
        """Parse EEG/ECG CSV"""
        print(f"Loading {self.csv_file}...")
        
        # Read the raw file to find the header
        with open(self.csv_file, 'r') as f:
            lines = f.readlines()
        
        # Extract metadata
        metadata = {}
        header_line_idx = -1
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Extract sample frequency from metadata
            if 'Sample_Frequency_(Hz)' in line:
                try:
                    self.sample_rate = float(line.split(',')[1])
                    metadata['sample_rate'] = self.sample_rate
                except:
                    pass
            
            # Find the actual header line
            if line.startswith('Time,') or line.startswith('Time\t'):
                header_line_idx = i
                break
                
        if header_line_idx == -1:
            raise ValueError("Could not find header line starting with 'Time'")
        
        # Read the CSV starting from the header
        self.data = pd.read_csv(self.csv_file, skiprows=header_line_idx, low_memory=False)
        
        # Clean column names
        self.data.columns = [col.replace('**', '').replace(':', '_').strip() 
                           for col in self.data.columns]
        
        # Filter out system/trigger columns
        exclude_cols = ['Trigger', 'Time_Offset', 'ADC_Status', 'ADC_Sequence', 
                       'Event', 'X3_', 'Comments', 'CMF']
        
        self.channels = [col for col in self.data.columns 
                        if col != 'Time' and col not in exclude_cols and col.strip()]
        
        
        return metadata
    
    def create_interactive_plot(self, max_channels=30):
        """Create an interactive multichannel plot"""

        # Categorize channels
        channel_categories = self.categorize_channels()

        # Create ordered channel list
        ordered_channels = (channel_categories['eeg'] +
                            channel_categories['ecg'] +
                            channel_categories['reference'])
        
        channels_to_plot = ordered_channels[:max_channels] if max_channels else ordered_channels
        n_channels = len(channels_to_plot)
        
        if n_channels == 0:
            raise ValueError("No valid channels found to plot")
        

        subplot_titles = []
        for ch in channels_to_plot:
            if ch in channel_categories['ecg']:
                subplot_titles.append(f"{ch} (mV) - ECG")
            elif ch in channel_categories['reference']:
                subplot_titles.append(f"{ch} (Reference)")
            else:
                subplot_titles.append(f"{ch} (μV) - EEG")
        
        # Create subplots with shared x-axis
        fig = make_subplots(
            rows=n_channels, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.015,
            subplot_titles=subplot_titles,
            specs=[[{"secondary_y": False}] for _ in range(n_channels)]
        )
        
        # Color palette for channels
        colors = px.colors.qualitative.Set1 + px.colors.qualitative.Set2
        
        # Add traces for each channel
        for i, channel in enumerate(channels_to_plot):
            if channel in self.data.columns:
                color = colors[i % len(colors)]
                
                fig.add_trace(
                    go.Scatter(
                        x=self.data['Time'],
                        y=self.data[channel],
                        mode='lines',
                        name=channel,
                        line=dict(color=color),
                        hovertemplate=f'<b>{channel}</b><br>' +
                                    'Time: %{x:.4f}s<br>' +
                                    'Amplitude: %{y:.1f}μV<extra></extra>',
                        showlegend=False
                    ),
                    row=i+1, col=1
                )
                
                # Update y-axis for this subplot
                if channel in channel_categories['ecg']:
                    fig.update_yaxes(
                        title_text="mV",
                        row=i+1, col=1,
                        showgrid=True,
                        gridcolor='lightcoral',
                        gridwidth=0.5,
                        zeroline=True,
                        zerolinecolor='black',
                        zerolinewidth=0.5
                    )
                elif channel in channel_categories['reference']:
                    fig.update_yaxes(
                        title_text="μV (Ref)",
                        row=i+1, col=1,
                        showgrid=True,
                        gridcolor='lightgray',
                        gridwidth=0.5,
                        zeroline=True,
                        zerolinecolor='black',
                        zerolinewidth=0.5
                    )
                else:
                    fig.update_yaxes(
                    title_text="μV",
                    row=i+1, col=1,
                    showgrid=True,
                    gridcolor='lightblue',
                    gridwidth=0.5,
                    zeroline=True,
                    zerolinecolor='blue',
                    zerolinewidth=0.5,
                )
        
        # Update layout for better interaction
        fig.update_layout(
            title={
                'text': f'EEG/ECG Multi-Channel <br><sub>File: {Path(self.csv_file).name} | {len(self.channels)} channels | {self.sample_rate}Hz</sub>',
                'x': 0.5,
                'y': 0.99,
                'yanchor': 'top',
                'xanchor': 'center',
                'font': {'size': 16},

            },
            height=150 * n_channels + 100,  # Dynamic height based on channels
            showlegend=False,
            hovermode='x unified',
            dragmode='pan',  # Default mode
            
            # X-axis configuration
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                type='linear',
            ),
            
            # Styling
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=10),

            # Add custom buttons for interaction modes
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"dragmode": "pan"}],
                            label="Pan",
                            method="relayout"
                        ),
                        dict(
                            args=[{"dragmode": "zoom"}],
                            label="Zoom",
                            method="relayout"
                        ),
                        dict(
                            args=[{
                                "dragmode": "select",
                                "selectdirection": "horizontal",
                            }],
                            label="Select",
                            method="relayout"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0,
                    xanchor="left",
                    y=1.02,
                    yanchor="top"
                ),
            ]
        )

        
        # Configure all x-axes to be linked for zooming
        for i in range(2, n_channels + 1):
            fig.update_xaxes(
                showgrid=True,
                gridcolor='lightgray',
                matches='x', 
                row=i, col=1)
            
        fig.update_xaxes(
            title_text="Time (seconds)",
            row=n_channels,
            col=1
        )

        
        return fig
    
    def create_dash_app(self, port=8050, debug=False):
        app = dash.Dash(__name__)
     
        fig = self.create_interactive_plot()
        app.layout = html.Div(
            children=[
                html.H1("Data Explorer", style={"textAlign": "center", "marginBottom": "-5px",}),
                dcc.Graph(id="eeg-plot", figure=fig),
                html.Div(id="selection-output",)
            ],
            style={"marginTop": "2px"}
        )

        @app.callback(
            Output("selection-output", "children"),
            Input("eeg-plot", "selectedData"),
            prevent_initial_call=True
        )

        def update_output(selected_data):
            update_fig = fig
            if not selected_data:
                return "No region selected."

            elif "range" in selected_data and "x" in selected_data["range"]:
                xmin, xmax = selected_data["range"]["x"]
                return f"Selected time window: {xmin:.2f}–{xmax:.2f} seconds"
        
        return app
        
    def categorize_channels(self):
        eeg_channels = []
        ecg_channels = []
        reference_channels = []

        for channel in self.channels:
            if any(x in channel for x in ['X1_LEOG', 'X2_REOG']):
                ecg_channels.append(channel)
            elif 'CM' in channel:
                reference_channels.append(channel)
            else:
                eeg_channels.append(channel)
        
        return {
            'eeg': eeg_channels,
            'ecg': ecg_channels,
            'reference': reference_channels,
        }

    



def main():
    """Main function to run the EEG/ECG plotter"""
    print("\nEEG/ECG Multichannel Data Explorer")
    print("=" * 35)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("No CSV file provided.")
    else:
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            print(f"Error: File '{csv_file}' not found!")
            return
    
    try:
        # Create plotter and load data
        plotter = EEGPlotter(csv_file)
        metadata = plotter.parse_eeg_csv()
        
        print(f"Opening plot in browser...")
        app = plotter.create_dash_app()
        app.run(debug=True, port=8060) 
        
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()