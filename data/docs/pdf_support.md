# PDF Support

Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.

## Use Cases
- Analyzing financial reports and understanding charts/tables
- Extracting key information from legal documents
- Translation assistance for documents
- Converting document information into structured formats

## Requirements

| Requirement | Limit |
|------------|--------|
| Maximum request size | 32 MB |
| Maximum pages per request | 600 (100 for models with a 200k-token context window) |
| Format | Standard PDF (no passwords/encryption) |

## How to Send PDFs

Three ways to provide PDFs to Claude:
1. As a URL reference to a PDF hosted online
2. As a base64-encoded PDF in document content blocks
3. By a file_id from the Files API

## How PDF Support Works

1. The system converts each page of the document into an image
2. Text from each page is extracted and provided alongside each page's image
3. Claude analyzes both text and images to understand the document
4. Claude responds referencing both textual and visual content

PDF support relies on Claude's vision capabilities and is subject to the same limitations as other vision tasks.

## Cost Estimation
- Text token costs: Each page typically uses 1,500-3,000 tokens depending on content density
- Image token costs: Each page is converted into an image with standard image-based cost calculations
- No additional PDF fees beyond standard token pricing

## Best Practices
- Place PDFs before text in requests
- Use standard fonts
- Ensure text is clear and legible
- Rotate pages to proper upright orientation
- Use logical page numbers in prompts
- Split large PDFs into chunks when needed
- Enable prompt caching for repeated analysis

## Supported Platforms
PDF support is available via direct API access, Google Vertex AI, and Amazon Bedrock. All active models support PDF processing.
