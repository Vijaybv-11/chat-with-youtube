import groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class GenerationError(Exception):
    def __init__(self, message, code="generation_error"):
        super().__init__(message)
        self.code = code


ERROR_MESSAGES = (
    (groq.AuthenticationError, "invalid_api_key",
    "The Groq API key is missing or invalid. Check GROQ_API_KEY in your .env file."),

    (groq.RateLimitError, "rate_limited",
    "The free-tier rate limit was reached. Wait a minute and try again."),

    (groq.InternalServerError, "model_busy",
    "The model is busy right now. Try again in a few seconds."),

    (groq.APIConnectionError, "network_error",
    "Could not reach Groq. Check your internet connection."),
)

# errors where trying another model can help
FALLBACK_ERRORS = (groq.InternalServerError, groq.RateLimitError, groq.APIConnectionError)


def get_llm():
    primary = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=2)
    # qwen's free tier allows 1000 output tokens per minute,
    # so max_tokens must stay below that or every request is rejected
    fallback = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.2, max_retries=2, max_tokens=800)
    return primary.with_fallbacks([fallback], exceptions_to_handle=FALLBACK_ERRORS)


def generate(final_prompt):
    try:
        answer = get_llm().invoke(final_prompt)
        return answer.content
    except groq.APIError as error:
        for error_type, code, message in ERROR_MESSAGES:
            if isinstance(error, error_type):
                raise GenerationError(message, code) from error
        raise GenerationError("Could not generate an answer. Try again.") from error
