# Image Upload Guidelines for DigitalHome

This document provides recommendations for uploading product and category images to ensure optimal display quality and performance across all pages and devices.

## Recommended Image Sizes

### Product Images
- **Optimal Size**: `600x600px` (1:1 square ratio)
- **Maximum Size**: 800px (automatically resized)
- **File Size**: 100-300KB
- **Formats**: JPG (85-90% quality) or WebP
- **Background**: White or transparent
- **Used On**: Product listings, product detail (related products), cart, order confirmation

**Why 600x600px?**
- Displays sharply on desktop (100% scaling) and mobile
- Scales perfectly to tablet (200px containers) and mobile (160px containers)
- Maintains image quality without excess file size
- Optimal for `object-fit: contain` display

### Category Images
- **Optimal Size**: `400x200px` (2:1 landscape ratio)
- **Maximum Size**: Automatically resized
- **File Size**: 40-100KB
- **Formats**: JPG or WebP
- **Background**: Can be transparent or colored
- **Used On**: Home page category cards

**Why 400x200px?**
- Displays perfectly in full-width category cards (200px height)
- Professional landscape format showing category more clearly
- Scales well on responsive tablets and mobile
- Optimal file size for home page performance
- Fills card without stretching or cropping

### Product Detail Main Image
- **Optimal Size**: `800x800px` (1:1 square ratio)
- **Maximum Size**: 1000px (automatically resized)
- **File Size**: 200-500KB
- **Formats**: JPG or WebP
- **Used On**: Product detail page - main product view

**Why 800x800px?**
- Fills the 400px+ desktop detail containers
- Provides better zoom and detail viewing experience
- Professional presentation for featured products

### Other Image Types
| Location | Recommended Size | Max File Size |
|----------|-----------------|---------------|
| Hero/Banner Slides | 1200x600px (2:1) | 500KB |
| Product Review Images | 300x300px | 150KB |
| Cart Items | 200x200px | 80KB |
| Thumbnails | 150x150px | 50KB |

---

## Automatic Image Processing

Your application automatically:

1. **Resizes Images**: All images are resized to optimal dimensions while preserving aspect ratio
2. **Converts Formats**: RGBA/PNG images are converted to RGB for better compatibility
3. **Compresses Quality**: JPG files saved at 85% quality, PNG at 90% for file size optimization
4. **Centers Images**: Smaller images are centered in square canvases (white background)
5. **Adds Padding**: 10px padding prevents images from touching container edges

### Upload Image Types

The system recognizes these image types during upload:

```
'product'      → 600x600px (product listings, hero sections)
'category'     → 400x200px (category cards - landscape 2:1 ratio)
'detail'       → 800x800px (product detail pages)
'cart'         → 200x200px (shopping cart)
'recommended'  → 300x300px (recommended products section)
```

---

## Best Practices

### Image Quality
✅ **DO:**
- Use high-quality source images (at least 800x800px)
- Choose clear, well-lit product photos
- Ensure uniform white or light gray background
- Use natural colors without heavy filters

❌ **DON'T:**
- Upload low-resolution images (less than 400x400px)
- Use compressed JPG images with visible artifacts
- Include distracting backgrounds or watermarks
- Use extremely bright or dark lighting

### File Format Selection
- **JPG**: Best for product photos with solid backgrounds (smaller file size)
- **WebP**: Better quality at smaller file size (modern browsers only)
- **PNG**: Use only for logos/icons with transparency needed

### Naming Conventions
- Use descriptive filenames: `product-name-white.jpg` instead of `IMG_0001.jpg`
- Avoid special characters (system auto-sanitizes, but clarity helps)
- Include product/category name when possible

### Image Content
- **Products**: Show item clearly with minimal background
- **Categories**: Use representative product image or category icon
- **Consistency**: Keep similar products with consistent lighting/angles

---

## File Size Reference

After automatic optimization (approximate):

| Type | Unoptimized | Optimized | Savings |
|------|------------|-----------|---------|
| 600x600 JPG (85%) | 250KB | 80-150KB | 50-70% |
| 400x400 JPG (85%) | 150KB | 50-100KB | 50-70% |
| 800x800 JPG (85%) | 400KB | 150-300KB | 50-70% |
| 600x600 PNG | 500KB | 100-200KB | 60-80% |

---

## Responsive Display

Your images automatically adjust for different screen sizes:

### Product Images
| Device | Container Size | Display |
|--------|---------------|---------|
| Desktop | 250px | Full image, centered |
| Tablet (768px) | 200px | Full image, centered |
| Mobile (576px) | 160px | Full image, centered |

### Category Cards
| Device | Container Size | Display |
|--------|---------------|---------|
| Desktop | 180px | Full image, centered |
| Tablet | 144px | Full image, centered |
| Mobile | 108px | Full image, centered |

---

## Troubleshooting

### Image Appears Cropped
- ❌ **Problem**: Image is cut off or squeezed
- ✅ **Solution**: Ensure image is square (1:1) with white/transparent background. The system displays full images with `object-fit: contain`

### Image File Too Large
- ❌ **Problem**: Upload takes too time
- ✅ **Solution**: Pre-compress using:
  - Photoshop: Export as JPG, quality 85-90%
  - Online tools: TinyPNG, Compressor.io
  - Free tools: ImageMagick, FFmpeg

### Image Quality Lost
- ❌ **Problem**: Image appears blurry after upload
- ✅ **Solution**: 
  - Upload high-quality source (800x800px minimum)
  - Use JPG quality 90%+ for source file
  - Avoid over-compressed PNGs

### Image Won't Upload
- ❌ **Problem**: File rejected or upload fails
- ✅ **Solutions**:
  - Check file format (JPG, PNG, GIF only)
  - Verify file size under 16MB
  - Try different filename without special characters
  - Clear browser cache and retry

---

## Recommended Tools for Image Preparation

### Free Online Tools
- **TinyPNG/TinyJPG**: https://tinypng.com - Compression
- **Compressor.io**: https://compressor.io - Advanced compression
- **Pixlr**: https://pixlr.com - Image editing
- **Canva**: https://canva.com - Design and resizing

### Desktop Applications
- **ImageMagick** (Free, CLI): Batch resizing and optimization
- **FFmpeg** (Free, CLI): Video and image processing
- **GIMP** (Free): Full image editing
- **Photoshop** (Paid): Professional image editing

### Command Line Resizing (ImageMagick)
```bash
# Resize product image to 600x600
magick convert input.jpg -resize 600x600 -gravity center -extent 600x600 -quality 85 product.jpg

# Resize category image to 400x200 (landscape 2:1)
magick convert input.jpg -resize 400x200 -gravity center -extent 400x200 -quality 85 category.jpg
```

---

## Implementation Details

### Image Processing Flow
1. Admin uploads image via web form
2. Image saved with timestamp filename
3. Image type parameter determines target size:
   - Products: 600x600px
   - Categories: 400x200px (landscape)
   - etc.
4. Image aspect ratio preserved, centered in container
5. Format converted (RGBA→RGB) and optimized
6. File saved with quality compression

### Display CSS
All images use `object-fit: contain` which:
- Shows the entire image without cropping
- Centers image in container
- Maintains aspect ratio
- Applies responsive padding to prevent edge crowding

---

## Questions or Issues?

If you encounter issues with image uploads:
1. Check this guide for size/format recommendations
2. Try uploading a different image to test
3. Check browser console for error messages
4. Clear browser cache and cookies
5. Try different file format (JPG → PNG or vice versa)

---

**Last Updated**: December 4, 2025  
**Version**: 1.0
