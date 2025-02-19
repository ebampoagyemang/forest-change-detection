import streamlit as st
import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
import folium
from PIL import Image

def process_images(image1_path, image2_path, output_dir):
    """Process two temporal forest images and generate change detection analysis"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read images
    with rasterio.open(image1_path) as src1:
        image1 = src1.read(1)
        meta1 = src1.meta.copy()
        
    with rasterio.open(image2_path) as src2:
        image2 = src2.read(1)
        meta2 = src2.meta
    
    # Resample image2 to match image1's dimensions
    image2_resampled = np.empty_like(image1)
    reproject(
        source=image2,
        destination=image2_resampled,
        src_transform=meta2['transform'],
        src_crs=meta2['crs'],
        dst_transform=meta1['transform'],
        dst_crs=meta1['crs'],
        resampling=Resampling.bilinear
    )
    
    # Calculate difference and apply thresholds
    difference = image1 - image2_resampled
    threshold = st.slider('Change Detection Threshold', 5, 20, 10)
    
    forest_loss = difference < -threshold
    forest_regrowth = difference > threshold
    unchanged = (difference >= -threshold) & (difference <= threshold)
    
    # Create change map
    change_map = np.zeros_like(difference)
    change_map[forest_loss] = 1
    change_map[forest_regrowth] = 2
    
    # Calculate areas
    pixel_area = meta1['transform'][0] * -meta1['transform'][4]
    forest_loss_area = np.sum(forest_loss) * pixel_area
    forest_regrowth_area = np.sum(forest_regrowth) * pixel_area
    unchanged_area = np.sum(unchanged) * pixel_area
    
    # Create custom colormap
    colors = ['red', 'gray', 'green']
    n_bins = 3
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
    
    # Generate visualization
    plt.figure(figsize=(12, 8))
    plt.imshow(change_map, cmap=cmap)
    plt.colorbar(ticks=[0, 1, 2], 
                label='Change Type',
                boundaries=np.arange(4)-0.5)
    plt.title('Forest Change Detection Map')
    
    # Add legend
    legend_elements = [plt.Rectangle((0,0),1,1, fc='red', label='Forest Loss'),
                      plt.Rectangle((0,0),1,1, fc='gray', label='Unchanged'),
                      plt.Rectangle((0,0),1,1, fc='green', label='Forest Regrowth')]
    plt.legend(handles=legend_elements, loc='lower right')
    
    # Save the plot
    plot_path = os.path.join(output_dir, 'change_detection_map.png')
    plt.savefig(plot_path)
    st.pyplot(plt)
    
    # Generate summary statistics
    total_area = forest_loss_area + forest_regrowth_area + unchanged_area
    loss_percentage = (forest_loss_area / total_area) * 100
    regrowth_percentage = (forest_regrowth_area / total_area) * 100
    unchanged_percentage = (unchanged_area / total_area) * 100
    
    # Display results
    st.subheader('Change Detection Analysis Results')
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Area Statistics (m²)")
        st.write(f"Forest Loss Area: {forest_loss_area:.2f}")
        st.write(f"Forest Regrowth Area: {forest_regrowth_area:.2f}")
        st.write(f"Unchanged Area: {unchanged_area:.2f}")
        
    with col2:
        st.write("### Percentage Distribution")
        st.write(f"Forest Loss: {loss_percentage:.2f}%")
        st.write(f"Forest Regrowth: {regrowth_percentage:.2f}%")
        st.write(f"Unchanged: {unchanged_percentage:.2f}%")
    
    # Generate and save report
    report_path = os.path.join(output_dir, 'change_detection_report.txt')
    with open(report_path, 'w') as f:
        f.write("Forest Change Detection Analysis Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Image 1: {os.path.basename(image1_path)}\n")
        f.write(f"Image 2: {os.path.basename(image2_path)}\n\n")
        f.write("Area Statistics (m²):\n")
        f.write(f"Forest Loss Area: {forest_loss_area:.2f}\n")
        f.write(f"Forest Regrowth Area: {forest_regrowth_area:.2f}\n")
        f.write(f"Unchanged Area: {unchanged_area:.2f}\n\n")
        f.write("Percentage Distribution:\n")
        f.write(f"Forest Loss: {loss_percentage:.2f}%\n")
        f.write(f"Forest Regrowth: {regrowth_percentage:.2f}%\n")
        f.write(f"Unchanged: {unchanged_percentage:.2f}%\n")
    
    return plot_path, report_path

def main():
    st.title("Forest Change Detection Analysis")
    st.write("Upload two temporal forest images to detect changes in forest cover.")
    
    # File upload
    image1_path = st.text_input("Path to first image (GeoTiff)", "C:/Users/bampo/OneDrive/Desktop/RAINFOREST BUILDER/selected images/17-04-2024.tif")
    image2_path = st.text_input("Path to second image (GeoTiff)", "C:/Users/bampo/OneDrive/Desktop/RAINFOREST BUILDER/selected images/25-06-2024.tif")
    output_dir = st.text_input("Results output directory", "C:/Users/bampo/OneDrive/Desktop/RAINFOREST BUILDER/results/new_results")
    
    if st.button("Process Images"):
        try:
            plot_path, report_path = process_images(image1_path, image2_path, output_dir)
            st.success(f"Analysis complete! Results saved to {output_dir}")
            
            # Display download buttons for results
            with open(report_path, "r") as f:
                st.download_button(
                    label="Download Report",
                    data=f.read(),
                    file_name="forest_change_report.txt",
                    mime="text/plain"
                )
                
            with open(plot_path, "rb") as f:
                st.download_button(
                    label="Download Map",
                    data=f.read(),
                    file_name="forest_change_map.png",
                    mime="image/png"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()