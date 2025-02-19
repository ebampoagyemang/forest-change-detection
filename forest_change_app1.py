{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c1e58f3f-eb9b-490c-907c-d062b3529f57",
   "metadata": {},
   "outputs": [],
   "source": [
    "# forest_change_app.py\n",
    "import streamlit as st\n",
    "import rasterio\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "st.title(\"Forest Change Detection\")\n",
    "\n",
    "uploaded_file1 = st.file_uploader(\"Upload the first image\", type=[\"tif\"])\n",
    "uploaded_file2 = st.file_uploader(\"Upload the second image\", type=[\"tif\"])\n",
    "\n",
    "if uploaded_file1 and uploaded_file2:\n",
    "    with rasterio.open(uploaded_file1) as src1:\n",
    "        image1 = src1.read(1)\n",
    "        meta1 = src1.meta\n",
    "\n",
    "    with rasterio.open(uploaded_file2) as src2:\n",
    "        image2 = src2.read(1)\n",
    "        meta2 = src2.meta\n",
    "\n",
    "    # Resample image2 to match image1's dimensions\n",
    "    image2_resampled = np.empty_like(image1)\n",
    "    reproject(\n",
    "        source=image2,\n",
    "        destination=image2_resampled,\n",
    "        src_transform=meta2['transform'],\n",
    "        src_crs=meta2['crs'],\n",
    "        dst_transform=meta1['transform'],\n",
    "        dst_crs=meta1['crs'],\n",
    "        resampling=Resampling.bilinear\n",
    "    )\n",
    "\n",
    "    difference = image1 - image2_resampled\n",
    "    threshold = 10\n",
    "    forest_loss = difference < -threshold\n",
    "    forest_regrowth = difference > threshold\n",
    "    unchanged = (difference >= -threshold) & (difference <= threshold)\n",
    "\n",
    "    change_map = np.zeros_like(difference)\n",
    "    change_map[forest_loss] = 1\n",
    "    change_map[forest_regrowth] = 2\n",
    "\n",
    "    plt.imshow(change_map, cmap='viridis')\n",
    "    plt.colorbar(label='Change Type')\n",
    "    plt.title('Forest Change Detection Map')\n",
    "    st.pyplot(plt)\n",
    "\n",
    "    pixel_area = meta1['transform'][0] * -meta1['transform'][4]\n",
    "    forest_loss_area = np.sum(forest_loss) * pixel_area\n",
    "    forest_regrowth_area = np.sum(forest_regrowth) * pixel_area\n",
    "    unchanged_area = np.sum(unchanged) * pixel_area\n",
    "\n",
    "    st.write(f\"Forest Loss Area: {forest_loss_area} m²\")\n",
    "    st.write(f\"Forest Regrowth Area: {forest_regrowth_area} m²\")\n",
    "    st.write(f\"Unchanged Area: {unchanged_area} m²\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
