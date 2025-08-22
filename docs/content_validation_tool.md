# MCP Content Validation Tool

The MCP Content Validation Tool provides comprehensive content quality assessment and improvement recommendations for various types of content including presentations, documents, webpages, and reports.

## Features

### Core Validation Capabilities

- **Readability Assessment**: Evaluates content readability using multiple metrics
- **Completeness Analysis**: Checks if content covers all intended objectives
- **Accuracy Verification**: Validates factual accuracy and consistency
- **Engagement Evaluation**: Assesses content engagement and audience appeal
- **Accessibility Review**: Ensures content meets accessibility standards
- **SEO Optimization**: Evaluates search engine optimization factors
- **Visual Element Assessment**: Reviews visual presentation and structure

### Content Types Supported

- Presentations
- Documents
- Webpages
- Reports
- Marketing materials
- Technical documentation

### Validation Rules

The tool applies a comprehensive set of validation rules:

1. **Readability Rules**
   - Sentence length and complexity
   - Word choice and vocabulary level
   - Paragraph structure and flow

2. **Completeness Rules**
   - Objective coverage
   - Key message delivery
   - Required sections and components

3. **Accuracy Rules**
   - Factual consistency
   - Data validation
   - Source verification

4. **Engagement Rules**
   - Audience appropriateness
   - Content structure
   - Visual appeal

5. **Accessibility Rules**
   - Language clarity
   - Structure and navigation
   - Inclusive language

6. **SEO Rules**
   - Keyword usage
   - Meta information
   - Content optimization

## Usage

### Basic Validation

```python
from mcp_server_openai.tools.mcp_content_validation import validate_content_quality

result = await validate_content_quality(
    content="Your content here...",
    content_type="presentation",
    target_audience="Professionals",
    objectives=["Inform", "Educate"],
    key_messages=["Key point 1", "Key point 2"]
)
```

### Advanced Validation with Custom Rules

```python
result = await validate_content_quality(
    content="Your content here...",
    content_type="document",
    target_audience="General audience",
    objectives=["Provide overview"],
    key_messages=["Basic information"],
    validation_rules=["readability", "completeness"],
    custom_thresholds={"readability": 0.6, "completeness": 0.5},
    include_suggestions=True
)
```

### MCP Tool Registration

The tool automatically registers with MCP servers and provides these endpoints:

- `mcp_content_validation_validate_content`: Main validation function
- `mcp_content_validation_get_history`: Retrieve validation history
- `mcp_content_validation_get_result`: Get specific validation results

## API Reference

### ValidationRequest

```python
class ValidationRequest:
    content: str                    # Content to validate
    content_type: str              # Type of content
    target_audience: str           # Target audience
    objectives: List[str]          # Content objectives
    key_messages: List[str]        # Key messages to convey
    validation_rules: Optional[List[str]]  # Specific rules to apply
    custom_thresholds: Optional[Dict[str, float]]  # Custom thresholds
    include_suggestions: bool      # Include improvement suggestions
```

### ValidationResponse

```python
class ValidationResponse:
    status: str                    # Validation status
    message: str                   # Status message
    validation_id: str             # Unique validation ID
    overall_score: float           # Overall quality score (0-1)
    passed_rules: int              # Number of passed rules
    failed_rules: int              # Number of failed rules
    warning_rules: int             # Number of warning rules
    content_metrics: ContentMetrics  # Detailed metrics
    validation_results: List[ValidationResult]  # Rule results
    recommendations: List[str]     # Improvement suggestions
    timestamp: datetime            # Validation timestamp
```

### ContentMetrics

```python
class ContentMetrics:
    word_count: int                # Total word count
    sentence_count: int            # Total sentence count
    paragraph_count: int           # Total paragraph count
    readability_score: float       # Readability score (0-1)
    content_structure_score: float # Structure quality (0-1)
    visual_element_score: float    # Visual quality (0-1)
    accessibility_score: float     # Accessibility score (0-1)
    seo_score: float              # SEO optimization (0-1)
    overall_quality_score: float   # Overall quality (0-1)
```

## Configuration

### Default Thresholds

The tool uses configurable thresholds for different validation rules:

```python
DEFAULT_THRESHOLDS = {
    "readability": 0.7,
    "completeness": 0.8,
    "accuracy": 0.9,
    "engagement": 0.7,
    "accessibility": 0.8,
    "seo": 0.6
}
```

### Custom Thresholds

You can override default thresholds for specific rules:

```python
custom_thresholds = {
    "readability": 0.6,      # Lower threshold for technical content
    "completeness": 0.9      # Higher threshold for documentation
}
```

## Examples

### Example 1: Presentation Validation

```python
# Validate a business presentation
presentation_content = """
# Q4 Sales Report

## Executive Summary
Our Q4 performance exceeded expectations with 15% growth.

## Key Metrics
- Revenue: $2.5M (+15% YoY)
- New Customers: 150 (+25% YoY)
- Customer Satisfaction: 4.8/5.0

## Next Steps
1. Expand marketing efforts
2. Improve customer onboarding
3. Launch new product line
"""

result = await validate_content_quality(
    content=presentation_content,
    content_type="presentation",
    target_audience="Executive team",
    objectives=["Report Q4 results", "Plan Q1 strategy"],
    key_messages=["Strong performance", "Growth opportunities"]
)
```

### Example 2: Document Validation

```python
# Validate technical documentation
doc_content = """
# API Reference Guide

## Authentication
All API requests require authentication via API key.

## Endpoints
### GET /users
Retrieves a list of users.

### POST /users
Creates a new user.

## Error Handling
Standard HTTP status codes are used.
"""

result = await validate_content_quality(
    content=doc_content,
    content_type="document",
    target_audience="Developers",
    objectives=["Provide API reference", "Explain authentication"],
    key_messages=["API requires authentication", "Standard HTTP responses"],
    validation_rules=["completeness", "accuracy", "accessibility"]
)
```

## Testing

Run the test suite to verify the tool works correctly:

```bash
python scripts/test_content_validation.py
```

## Integration

### MCP Server

The tool automatically integrates with MCP servers through the `register()` function:

```python
from mcp_server_openai.tools.mcp_content_validation import register

# Register with MCP server
register(mcp_server)
```

### Standalone Usage

You can also use the tool independently:

```python
from mcp_server_openai.tools.mcp_content_validation import ContentValidator

validator = ContentValidator()
# Use validator methods directly
```

## Performance

- **Validation Time**: Typically 1-5 seconds depending on content length
- **Memory Usage**: Minimal memory footprint
- **Scalability**: Handles content up to 100,000 words efficiently
- **Caching**: Results are cached for performance optimization

## Error Handling

The tool provides comprehensive error handling:

- **Validation Errors**: Detailed error messages with suggestions
- **Input Validation**: Checks for required parameters and valid values
- **Graceful Degradation**: Continues validation even if some rules fail
- **Logging**: Comprehensive logging for debugging and monitoring

## Best Practices

1. **Set Appropriate Thresholds**: Adjust thresholds based on content type and audience
2. **Use Specific Objectives**: Define clear, measurable objectives for better validation
3. **Include Key Messages**: Specify the main points your content should convey
4. **Review Recommendations**: Always review and apply improvement suggestions
5. **Monitor Performance**: Track validation scores over time to measure improvement

## Troubleshooting

### Common Issues

1. **Low Readability Scores**
   - Simplify sentence structure
   - Use shorter words and sentences
   - Break up long paragraphs

2. **Completeness Failures**
   - Ensure all objectives are addressed
   - Include required sections
   - Add missing key messages

3. **Accessibility Issues**
   - Use clear, simple language
   - Improve content structure
   - Add descriptive headings

### Getting Help

- Check the validation results for specific failure reasons
- Review the improvement suggestions
- Adjust thresholds if needed
- Run validation on similar successful content for comparison

## Contributing

To contribute to the content validation tool:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This tool is part of the MCP Server OpenAI project and follows the same license terms.


