---
name: AI Engine Contribution
about: Propose or implement support for a new AI engine/provider
title: '[AI ENGINE] '
labels: ai-engine, enhancement
assignees: ''
---

## AI Engine Information

**Provider Name**: [e.g., Google Gemini, Ollama, OpenAI, etc.]  
**API Documentation**: [Link to official API docs]  
**Pricing Model**: [Free tier available? Pay-per-use? Self-hosted?]

## Motivation
Why should converSQL support this AI engine?
- What unique capabilities does it offer?
- What use cases does it enable?
- Who would benefit from this integration?

## Implementation Status
- [ ] Proof of concept completed
- [ ] Adapter class implemented
- [ ] Configuration added
- [ ] Error handling implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Ready for review

## Technical Details

### API Access
- **Authentication Method**: [API Key, OAuth, Self-hosted, etc.]
- **Rate Limits**: [If applicable]
- **Model Options**: [List available models]
- **Recommended Model**: [For SQL generation]

### Sample Code
If you've started implementation, share a code snippet:

```python
class NewEngineAdapter:
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        # Initialization code
        pass
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        # Implementation
        pass
```

## Configuration Requirements

What environment variables or configuration will users need?

```bash
# .env additions
NEW_ENGINE_API_KEY=xxx
NEW_ENGINE_MODEL=model-name
NEW_ENGINE_ENDPOINT=https://...  # If applicable
```

## Testing Plan

How will this be tested?
- [ ] Unit tests for adapter
- [ ] Integration tests with real API
- [ ] Mock tests for CI/CD
- [ ] Manual testing completed

## Documentation Plan

What documentation needs to be created/updated?
- [ ] Add setup instructions to docs/
- [ ] Update AI_ENGINES.md guide
- [ ] Add example queries
- [ ] Update README.md
- [ ] Add troubleshooting section

## Dependencies

Will this require new dependencies?

```python
# requirements.txt additions
new-ai-library==1.0.0
```

## Challenges and Considerations

Are there any challenges or special considerations?
- API limitations
- Cost concerns
- Performance characteristics
- Error handling nuances
- Model-specific quirks

## Comparison with Existing Engines

How does this compare to existing supported engines (Bedrock, Claude)?

| Feature | Bedrock | Claude | New Engine |
|---------|---------|--------|------------|
| Cost | $$$ | $$ | ? |
| Speed | Fast | Very Fast | ? |
| Accuracy | High | Very High | ? |
| Self-hosted | No | No | ? |

## Questions for Review

Any specific questions for maintainers?
1. ...
2. ...

## Willingness to Maintain

- [ ] I'm willing to maintain this adapter
- [ ] I can provide ongoing support
- [ ] I'll respond to related issues
- [ ] I need help with maintenance

## Additional Resources

- Link to example implementations
- Link to relevant research/benchmarks
- Link to community discussions
- Other helpful resources

---

**Contribution Checklist** (for implementers):
- [ ] Forked repository
- [ ] Created feature branch
- [ ] Implemented adapter following patterns in src/ai_service.py
- [ ] Added tests
- [ ] Updated documentation
- [ ] Tested locally
- [ ] Ready to submit PR

**See [AI Engine Development Guide](docs/AI_ENGINES.md) for detailed implementation instructions.**
