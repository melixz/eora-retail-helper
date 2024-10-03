import re
from collections import Counter
import html

used_urls_global = set()


def remove_extra_digits_around_links(formatted_answer):
    formatted_answer = re.sub(
        r'\d+\s*(<a href="[^"]+">\[\d+\]</a>)', r"\1", formatted_answer
    )
    return formatted_answer


def validate_formatting(text):
    text = re.sub(r"\s*\[\d+\]\s*", lambda match: match.group().strip(), text)
    text = re.sub(
        r"(\d\.\s*)([a-zа-яё])", lambda m: m.group(1) + m.group(2).upper(), text
    )
    return text


def extract_keywords(text):
    words = re.findall(r"\w+", text.lower())
    return Counter(words)


def add_links_to_sentences(sentences, context_with_urls, used_urls):
    global used_urls_global
    new_urls = []
    new_sentences = []

    for idx, sentence in enumerate(sentences):
        if len(new_urls) >= 3:
            break

        max_similarity = 0
        best_url = None
        sentence_keywords = extract_keywords(sentence)

        for content, url in context_with_urls:
            content_keywords = extract_keywords(content)
            common_words = sentence_keywords & content_keywords
            similarity = sum(common_words.values())
            if similarity > max_similarity and url not in used_urls_global:
                max_similarity = similarity
                best_url = url

        if best_url and max_similarity > 0 and best_url not in new_urls:
            escaped_url = html.escape(best_url, quote=True)
            if f"<code>[{len(new_urls) + 1}]</code>" not in sentence:
                sentence = f"{sentence} <code>[{len(new_urls) + 1}]</code>"
            new_urls.append((len(new_urls) + 1, escaped_url))
            used_urls_global.add(best_url)

        new_sentences.append(sentence)

    return new_sentences, new_urls


def format_answer(answer, context_with_urls, used_urls):
    sentences = re.split(r"(?<=[.!?])\s+", answer)
    new_sentences, new_urls = add_links_to_sentences(
        sentences, context_with_urls, used_urls
    )

    formatted_answer = " ".join(new_sentences)
    formatted_answer = remove_extra_digits_around_links(formatted_answer)
    formatted_answer = validate_formatting(formatted_answer)
    formatted_answer = re.sub(r"\*\*(.*?)\*\*", r"\1", formatted_answer)
    formatted_answer = re.sub(r"<b>(.*?)</b>", r"\1", formatted_answer)

    for i, url in new_urls:
        formatted_answer = formatted_answer.replace(
            f"<code>[{i}]</code>", f'<a href="{url}">[{i}]</a>'
        )

    return formatted_answer
