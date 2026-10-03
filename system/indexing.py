#  Document ingestion getting the transcript from youtube video and storing it 
from system.transcript import get_video_transcript,extract_video_id



def build_index(video_id,language):
    from system.splitters import split_text
    from system.embedding import generate_embeddings
    transcript=get_video_transcript(video_id,language)
    chunks=split_text(text=transcript)
    vector_store=generate_embeddings(chunks)
    return vector_store



if __name__ == "__main__":
    video_id = extract_video_id("https://youtu.be/WX4_jsFhd-I?si=L_qoLrankbZY2uve")
    v_s=build_index(video_id,"en")
    from system.answering import answer_question
    answer=answer_question(v_s,"Does this video contain about movie uncharted and what's the overall rating?")
    print(answer) 


       

