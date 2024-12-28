import os.path
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')  # Use TkAgg backend for interactive plots

extra = False
other_view = True
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
stop_words = [
    "a", "an", "the", "in", "on", "at", "to", "by", "with", "from", "about", "of",
    "and", "or", "but", "if", "because",
    "he", "she", "it", "they", "we", "I", "you", "me", "him", "her", "them",
    "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did",
    "not", "very", "so", "then", "there",
    "this", "that", "these", "those", "which", "who", "whom","my", "people", "for"
]
# Word you do not want to see in results
words_to_remove = []
stop_words += words_to_remove


def clean_date_string(date_string):
    # Remove ordinal suffixes (st, nd, rd, th)
    for suffix in ["st", "nd", "rd", "th"]:
        if suffix in date_string:
            num = -1
            for a in range(date_string.count(suffix)):
                num = date_string.index(suffix, num + 1)
                if num > 0 and date_string[num - 1].isdigit():
                    date_string = date_string[:num] + date_string[num:].replace(suffix, "")
    return date_string


def format_date(date):
    date = date.replace(":", "")
    formated_date = ""
    # Clean and parse each date string
    cleaned_date = clean_date_string(date)
    try:
        date_object = datetime.strptime(cleaned_date, "%A, %B %d %Y")
    except ValueError:
        date_object = datetime.strptime(cleaned_date, "%A %B %d %Y")
    # Format to MM/DD/YY
    formated_date = date_object.strftime("%y/%m/%d")
    return formated_date


def read_file(file_name):
    file = open(file_name, 'r', encoding="utf8")
    lines = file.readlines()

    # Local vars for the loop
    current = ""
    hit_extra = False

    for line in lines:
        line = line.lower().rstrip()

        # If we hit 2023 start appending the year
        if line == "2023":
            hit_extra = True
            if not extra:
                break
            continue

        if ":" in line and any(elem.lower() in line for elem in days):
            if hit_extra:
                line += " 2023"
            else:
                line += " 2024"
            line = format_date(line)
            happy[line] = []
            current = line
        else:
            happy[current].append(line)


def popular_phrases(data):
    # 1. Combine all words for global analysis
    all_words = [word for words in data.values() for word in words]
    word_counts = Counter(all_words)

    # 2. Most popular words
    top_words = word_counts.most_common(40)

    a = 0
    while a < len(top_words):
        if a < len(top_words):
            if any(elem.lower() in top_words[a][0] for elem in words_to_remove):
                top_words.pop(a)
            else:
                a += 1

    print("\nTop Phrases:")
    for word, count in top_words:
        print(f"  {word}: {count}")

    # 3. Word trends over time
    word_trends = {}
    for date, words in data.items():
        counts = Counter(words)
        for word, count in counts.items():
            if word not in word_trends:
                word_trends[word] = []
            word_trends[word].append((date, count))

    # Number of words to visualize
    top_words_count = 30

    # Create subplots
    fig, axes = plt.subplots(top_words_count, 1, figsize=(10, 6), sharex=True)

    # Ensure axes is iterable, even if there's only one subplot
    if top_words_count == 1:
        axes = [axes]

    # Visualize top 3 words
    for i, (word, _) in enumerate(top_words[:top_words_count]):
        trend = sorted(word_trends[word], key=lambda x: datetime.strptime(x[0], "%y/%m/%d"))
        dates = [datetime.strptime(t[0], "%y/%m/%d") for t in trend]
        counts = [t[1] for t in trend]
        axes[i].plot(dates, counts, marker='o', label=word)
        axes[i].set_ylabel(f"{word}({_})", rotation=0, labelpad=80)
        # axes[i].legend()

    # Set common labels
    plt.xlabel("Date")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


def analyze_and_report(data):
    # 1. Combine all words for global analysis
    all_phrases = [word for words in data.values() for word in words]
    all_words = []
    for num in range(len(all_phrases)):
        all_words += all_phrases[num].split(" ")

    word_counts = Counter(all_words)

    # 2. Most popular words
    top_words = word_counts.most_common(100)
    a = 0
    while a < len(top_words):
        if a < len(top_words):
            if any(elem.lower() == top_words[a][0] for elem in stop_words):
                top_words.pop(a)
            else:
                a += 1

    print("Top Words:")
    for word, count in top_words:
        print(f"  {word}: {count}")

    # 3. Most active dates
    date_activity = {date: len(words) for date, words in data.items()}
    most_active_dates = sorted(date_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nMost Active Dates:")
    for date, count in most_active_dates:
        print(f"  {date}: {count} words")

    # 4. Word trends over time
    word_trends = {}
    for date, phrase in data.items():
        words = []
        for num in range(len(phrase)):
            words += phrase[num].split(" ")
        counts = Counter(words)
        for word, count in counts.items():
            if word not in word_trends:
                word_trends[word] = []
            word_trends[word].append((date, count))
    if other_view:
        for a in range(int(len(top_words)/ 40 + 1)):
            # Number of words to visualize
            top_words_count = 40

            # Create subplots
            fig, axes = plt.subplots(top_words_count, 1, figsize=(10, 6), sharex=True)

            # Ensure axes is iterable, even if there's only one subplot
            if top_words_count == 1:
                axes = [axes]

            # Visualize top 3 words
            num =0
            for i, (word, _) in enumerate(top_words[a*10:(a+4)*10]):
                if any(elem.lower() not in word for elem in days):
                    trend = sorted(word_trends[word], key=lambda x: datetime.strptime(x[0], "%y/%m/%d"))
                    dates = [datetime.strptime(t[0], "%y/%m/%d") for t in trend]
                    counts = [t[1] for t in trend]

                    axes[i+num].plot(dates, counts, marker='o', label=word)
                    # axes[i].set_title(f"{word} Trend")
                    axes[i+num].set_ylabel(f"{word}({_})", rotation=0, labelpad=80)
                    # axes[i].legend()
                else:
                    num-=1
            plt.xlabel("Date")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
    else:
        # 5. Visualize trends for top words
        for word, _ in top_words:  # Visualize top 3 words
            trend = sorted(word_trends[word], key=lambda x: datetime.strptime(x[0], "%y/%m/%d"))
            dates = [datetime.strptime(t[0], "%y/%m/%d") for t in trend]
            counts = [t[1] for t in trend]
            plt.plot(dates, counts, marker='o', label=word)

        plt.title("Word Trends Over Time")
        plt.ylabel("Count")
        plt.legend()
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # 6. Summary report
    print("\nSummary Report:")
    print(f"  Total unique words: {len(word_counts)}")
    print(f"  Total words used: {sum(word_counts.values())}")
    print(f"  Most used word: '{top_words[0][0]}' ({top_words[0][1]} times)")
    print(f"  Most active day: {most_active_dates[0][0]} ({most_active_dates[0][1]} words)")


if __name__ == "__main__":
    global happy
    happy = {}
    file_name = os.path.expanduser("~/Documents/Jack/happy-stats-2024.txt")
    read_file(file_name)

    # create report with how popular days are and most popular words
    analyze_and_report(happy)
    # Most popular phrases
    popular_phrases(happy)
