# Vision

Claude's vision capabilities allow it to understand and analyze images, opening up exciting possibilities for multimodal interaction.

## How to use vision

Use Claude's vision capabilities through:
- claude.ai: Upload an image like you would a file, or drag and drop an image directly into the chat window.
- The Console Workbench: A button to add images appears at the top right of every User message block.
- API request: Include images in your API calls using base64 encoding, URL references, or the Files API.

## Basics and limits

You can include multiple images in a single request: up to 20 for claude.ai, and up to 600 for API requests (100 for models with a 200k-token context window). Claude analyzes all provided images when formulating its response. This can be helpful for comparing or contrasting images.

If you submit an image larger than 8000x8000 px, it is rejected. If you submit more than 20 images in one API request, this limit is 2000x2000 px.

## Image format support

Claude currently supports JPEG, PNG, GIF, and WebP image formats:
- image/jpeg
- image/png
- image/gif
- image/webp

## Image size limits

- API: Maximum 5 MB per image
- claude.ai: Maximum 10 MB per image

## Ensuring image quality

When providing images to Claude, keep the following in mind for best results:
- Image format: Use a supported image format: JPEG, PNG, GIF, or WebP.
- Image clarity: Ensure images are clear and not too blurry or pixelated.
- Text: If the image contains important text, make sure it's legible and not too small.

## Limitations

While Claude's image understanding capabilities are cutting-edge, there are some limitations:
- People identification: Claude cannot be used to name people in images and refuses to do so.
- Accuracy: Claude may hallucinate or make mistakes when interpreting low-quality, rotated, or very small images under 200 pixels.
- Spatial reasoning: Claude's spatial reasoning abilities are limited. It may struggle with tasks requiring precise localization or layouts.
- Counting: Claude can give approximate counts of objects in an image but may not always be precisely accurate.
- AI generated images: Claude does not know if an image is AI-generated and may be incorrect if asked.
- Inappropriate content: Claude does not process inappropriate or explicit images that violate the Acceptable Use Policy.
- Healthcare applications: While Claude can analyze general medical images, it is not designed to interpret complex diagnostic scans.
- Image generation: Claude is an image understanding model only. It can interpret and analyze images, but it cannot generate, produce, edit, manipulate, or create images.
