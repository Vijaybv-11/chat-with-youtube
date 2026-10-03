
import youtube_transcript_api as yt
from requests.exceptions import RequestException


class TranscriptError(Exception):
    def __init__(self, message, code="transcript_error"):
          super().__init__(message)
          self.code = code

ERROR_MESSAGES = (
    (yt.InvalidVideoId, "invalid_video_id",
    "The video ID is invalid. Please check your input."),

    (yt.TranscriptsDisabled, "transcripts_disabled",
    "Captions are disabled for this video. Please try another video."),

    (yt.NoTranscriptFound, "language_unavailable",
    "No captions were found in the requested language. Try another language."),

    (yt.VideoUnavailable, "video_unavailable",
    "This video is unavailable. Check that it exists and is publicly accessible."),

    (yt.AgeRestricted, "age_restricted",
    "This app cannot retrieve captions for age- restricted videos."),

    (yt.VideoUnplayable, "video_unplayable",
    "YouTube cannot play this video for this request. Try another video."),

    (yt.RequestBlocked, "request_blocked",
    "YouTube is blocking requests from this app's network. Please try later."),

    (yt.NotTranslatable, "not_translatable",
    "This transcript does not support translation."),

    (yt.TranslationLanguageNotAvailable,
    "translation_unavailable",
    "Translation into the selected language is unavailable."),

    (yt.YouTubeRequestFailed, "youtube_request_failed",
    "The request to YouTube failed. Please try again later."),

    (RequestException, "network_error",
    "Could not connect to YouTube. Check your connection and try again."),
)



def convert_transcript_error(error):
    for error_type, code, message in ERROR_MESSAGES:
        if isinstance(error, error_type):
            return TranscriptError(message, code)

    return TranscriptError(
        "Could not retrieve captions for this video. Try again later or use another video.",
        code="retrieval_failed",
    )
   


    