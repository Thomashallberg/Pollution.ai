import matplotlib.pyplot as plt
import numpy as np
import rasterio


with rasterio.open("stockholm_no2.tiff") as dataset:
    no2 = dataset.read(1)
    data_mask = dataset.read(2)

masked_no2 = np.where(data_mask > 0, no2, np.nan)

print("Shape:", masked_no2.shape)
print("Minimum NO2:", np.nanmin(masked_no2))
print("Maximum NO2:", np.nanmax(masked_no2))
print("Mean NO2:", np.nanmean(masked_no2))

plt.figure(figsize=(10, 7))

image = plt.imshow(
    masked_no2,
    origin="upper",
)

plt.colorbar(image, label="NO₂")
plt.title("Sentinel-5P NO₂ over Stockholm")
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.tight_layout()
plt.show()