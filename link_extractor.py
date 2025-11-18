from langchain_community.document_loaders import SeleniumURLLoader
from youtube_transcript_api import YouTubeTranscriptApi
import re

def links_extractor(query:str):
    """
    Checks if a URL is the only (or primary) content in the user's input.
    """

    # Search the input string for the pattern
    URL_PATTERN = r'https?://(?:[-\w./?=+]|(?:%[\da-fA-F]{2}))+'
    match = re.findall(URL_PATTERN, query)

    if match:
        return match
    
    return None

def text_extraction_from_link(link:str):
    text = None
    if "www.youtube.com" in link:
        video_ID = link.split("=")[-1]
        extractor = YouTubeTranscriptApi()
        transcript_object = list(extractor.fetch(video_id=video_ID, languages=["en", "hindi"]))
        text = " ".join(chunk.text for chunk in transcript_object)
    elif "youtu.be" in link:
        video_ID = link.split("youtu.be/")[-1].split("?")[0]
        extractor = YouTubeTranscriptApi()
        transcript_object = list(extractor.fetch(video_id=video_ID, languages=["en", "hindi"]))
        text = " ".join(chunk.text for chunk in transcript_object)
    else:
        loader = SeleniumURLLoader(urls=[link,])
        text = loader.load()
        text = text[0].page_content

    return text


if __name__ == "__main__":
    text = """
            summarize this one https://www.youtube.com/watch?v=BaM7OCEm3G0 print(response)

            """

    print(text_extraction_from_link(text))
