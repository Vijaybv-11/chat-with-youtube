import youtube_transcript_api as yt
from system.transcripterror_handler import (
      TranscriptError,
      convert_transcript_error,
  )
import re
from urllib.parse import urlparse, parse_qs
from requests.exceptions import RequestException



#  Document ingestion getting the transcript from youtube video and storing it 
def get_video_transcript(video_id, language="en"):
    fetched = fetch_transcript(video_id, language)
    return " ".join(snippet.text for snippet in fetched)



def list_language(video_id):
    try:
        transcript_list = yt.YouTubeTranscriptApi().list(video_id)
        languages = []

        for transcript in transcript_list:
            languages.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
            })

        return languages
    except (yt.YouTubeTranscriptApiException, RequestException) as error:
        raise convert_transcript_error(error) from error


def extract_video_id(url_or_id):
      value = url_or_id.strip()

      if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
          return value

      url = urlparse(value if "://" in value else "https://" + value)
      parts = url.path.strip("/").split("/")
      video_id = ""

      if url.hostname == "youtu.be" and len(parts) == 1:
          video_id = parts[0]

      elif url.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
          if url.path == "/watch":
              video_id = parse_qs(url.query).get("v", [""])[0]
          elif len(parts) == 2 and parts[0] in ("shorts", "embed", "live"):
              video_id = parts[1]

      if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
          return video_id

      raise TranscriptError("Enter a valid YouTube URL or video ID.", code="invalid_url")


def fetch_transcript(video_id,language):
    try:
        transcript_list = yt.YouTubeTranscriptApi().list(video_id)
        try:
            fetched = transcript_list.find_transcript([language]).fetch()
        except yt.NoTranscriptFound:
            fetched = fetch_translated_or_original(transcript_list, language)

        if not any(snippet.text.strip() for snippet in fetched):
            raise TranscriptError(
                "This video's captions contain no usable text.",
                code="empty_transcript",
            )

        return fetched
    except (yt.YouTubeTranscriptApiException,
            RequestException) as error:
          raise convert_transcript_error(error) from error


def fetch_translated_or_original(transcript_list, language):
    # manual transcripts first, auto-generated after
    candidates = sorted(
        transcript_list,
        key=lambda transcript: transcript.is_generated)

    # translate() only builds the request, nothing is downloaded until fetch()
    for transcript in candidates:
        try:
            translated = transcript.translate(language)
        except (yt.NotTranslatable, yt.TranslationLanguageNotAvailable):
            continue

        # YouTube often blocks translated captions, so falling back if it fails
        try:
            return translated.fetch()
        except (yt.YouTubeTranscriptApiException, RequestException):
            break

    # if no translation, using  the best transcript in its original language
    return candidates[0].fetch()
