"""Visualization functions for the dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import networkx as nx
import streamlit as st
from config import PLOTLY_TEMPLATE


def create_zipf_plot(data_df):
    """Create Zipf's law visualization."""
    fig_zipf = go.Figure()
    
    # Add actual data
    fig_zipf.add_trace(go.Scatter(
        x=data_df['rank'][:1000],
        y=data_df['count'][:1000],
        mode='markers',
        name='Dane rzeczywiste',
        marker=dict(
            size=6,
            color=data_df['rank'][:1000],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Ranga")
        ),
        hovertemplate='<b>%{text}</b><br>Ranga: %{x}<br>Częstotliwość: %{y}<extra></extra>',
        text=data_df['word'][:1000]
    ))
    
    # Add ideal Zipf line
    x_ideal = np.array(range(1, 1001))
    y_ideal = data_df.iloc[0]['count'] / x_ideal
    
    fig_zipf.add_trace(go.Scatter(
        x=x_ideal,
        y=y_ideal,
        mode='lines',
        name='Idealne prawo Zipfa',
        line=dict(color='rgba(255, 75, 75, 0.8)', width=2, dash='dash')
    ))
    
    fig_zipf.update_layout(
        xaxis_type="log",
        yaxis_type="log",
        xaxis_title="Ranga słowa (skala logarytmiczna)",
        yaxis_title="Częstotliwość (skala logarytmiczna)",
        height=600,
        hovermode='closest',
        template=PLOTLY_TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    
    return fig_zipf


def create_top_words_bar_chart(data_df, top_n):
    """Create bar chart for top N words."""
    top_data = data_df.head(top_n)
    
    fig_bar = px.bar(
        top_data,
        x='word',
        y='count',
        color='count',
        color_continuous_scale='Plasma',
        labels={'word': 'Słowo', 'count': 'Liczba wystąpień'},
        hover_data={'rank': True}
    )
    
    fig_bar.update_layout(
        height=500,
        template=PLOTLY_TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45,
        showlegend=False,
        font=dict(size=12)
    )
    
    return fig_bar


def create_network_graph(bigram_counts, top_connections, min_connection_freq):
    """Create network graph for word connections."""
    # Get top connections
    top_bigrams = bigram_counts.most_common(top_connections)
    
    # Filter by minimum frequency
    filtered_bigrams = [(w1, w2, count) for (w1, w2), count in top_bigrams if count >= min_connection_freq]
    
    if not filtered_bigrams:
        return None, None
    
    # Create network graph
    G = nx.Graph()
    
    for w1, w2, count in filtered_bigrams:
        G.add_edge(w1, w2, weight=count)
    
    # Calculate node positions using spring layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Prepare edge traces
    edge_traces = []
    
    for edge in G.edges():
        w1, w2 = edge
        weight = G[w1][w2]['weight']
        
        x0, y0 = pos[w1]
        x1, y1 = pos[w2]
        
        # Normalize edge width based on weight
        max_weight = max([G[e[0]][e[1]]['weight'] for e in G.edges()])
        edge_width = 0.5 + (weight / max_weight) * 5
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=edge_width,
                color='rgba(102, 126, 234, 0.4)'
            ),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Prepare node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Node size based on degree
        degree = G.degree(node)
        node_size.append(10 + degree * 2)
        
        # Hover text
        connections = list(G.neighbors(node))
        hover_text = f"<b>{node}</b><br>"
        hover_text += f"Połączenia: {degree}<br>"
        hover_text += f"Sąsiedzi: {', '.join(connections[:5])}"
        if len(connections) > 5:
            hover_text += f"... (+{len(connections) - 5})"
        
        node_text.append(hover_text)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color='#667eea',
            line=dict(width=2, color='#764ba2')
        ),
        text=[node for node in G.nodes()],
        textposition="top center",
        textfont=dict(size=10, color='white'),
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    )
    
    # Create figure
    fig_network = go.Figure(data=edge_traces + [node_trace])
    
    fig_network.update_layout(
        title=f"Top {len(filtered_bigrams)} połączeń słów (min. częstotliwość: {min_connection_freq})",
        showlegend=False,
        hovermode='closest',
        height=800,
        template=PLOTLY_TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig_network, G
