from typing import Dict
from operator import itemgetter
from wordcloud import WordCloud


def get_wordcloud_data(transcript_text: str) -> Dict[str, int]:
    wordcloud_data = WordCloud().process_text(transcript_text)
    data = []
    for word, count in wordcloud_data.items():
        data.append({"text": word, "count": count})

    data.sort(key=itemgetter("count"), reverse=True)
    return data[:20]
