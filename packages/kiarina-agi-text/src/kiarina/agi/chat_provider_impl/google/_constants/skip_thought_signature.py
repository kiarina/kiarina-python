SKIP_THOUGHT_SIGNATURE = "skip_thought_signature_validator"
"""
Documented sentinel that makes Gemini skip thought signature validation for a
function call part. Signatures are not kept in `AIMessage`, so replayed function
calls carry this instead.

https://cloud.google.com/vertex-ai/generative-ai/docs/thought-signatures
"""
