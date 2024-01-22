import re, os
import bs4, pdf2image, weasyprint
from typing import List, Optional, Tuple


def render_song(
    output_filename: str,
    title: str,
    artist: Optional[str],
    key: Optional[str],
    sections: List[Tuple[str, str]],
):
    """
    Renders a song sheet to pdf.
    
    :param output_filename: The name of the output files, without extension.
                            '.html', '.pdf' and '_#.png' will be appended.
    :param title: The title of the song.
    :param artist: The artist or band name. May be None or empty.
    :param key: The key of the song. None or empty if Nashville numbers are
                being used.
    :param sections: A list of tuples representing the sections of the song.
                     Each tuple contains the section name and the lyrics.
                     Chords are represented by square brackets.
    """

    root_path = os.path.dirname(os.path.realpath(__file__))
    output_filename = os.path.join(
        root_path,
        output_filename
    )

    # Load HTML template for editing
    template_path = os.path.join(
        root_path,
        'song.html.template'
    )
    with open(template_path, 'r') as f:
        soup = bs4.BeautifulSoup(f.read(), 'html.parser')
    
    # Set header
    soup.find(name='title').string = title
    soup.find(id='title').string = title
    if artist:
        soup.find(id='artist').string = artist
    else:
        soup.find(id='artist').decompose()
    if key:
        write_to_tag(
            soup.find(id='key'),
            "Key: " + format_chord(key)
        )
    else:
        soup.find(id='key').decompose()
    
    # Build content
    content = "".join([
        write_section(name, lines)
        for name, lines in sections
    ])

    # Write content to template
    write_to_tag(
        soup.find(name='article'),
        content
    )

    # Write HTML to file
    htmlContent = str(soup)
    with open(output_filename + ".html", 'w') as f:
        f.write(htmlContent)



    # Create PDF
    import logging
    logging.getLogger('weasyprint').setLevel(logging.DEBUG)
    logging.getLogger('weasyprint').addHandler(logging.StreamHandler())
    html = weasyprint.HTML(
        string = htmlContent,
        base_url = root_path
    )
    html.write_pdf(
        output_filename + ".pdf"
    )
    
    # Create PNG
    imgs = pdf2image.convert_from_path(output_filename + ".pdf")
    for i, img in enumerate(imgs):
        img.save(output_filename + f"_{i}.png")

def write_to_tag(tag: bs4.Tag, content: str):
    tag.clear()
    tag.append(bs4.BeautifulSoup(content, 'html.parser'))

def write_section(name: str, lines: str) -> str:
    return f"""
        <section>
            <h2>{name}</h2>
            {"".join(write_lines(lines))}
        </section>
    """

def write_lines(lines: str) -> str:
    return "".join([
        write_line(line)
        for line in lines.split('\n')
    ])

def write_line(line: str) -> str:
    result = "<p>"
    blocks = split_chords(line)
    for chord, lyrics in blocks:
        result += "<span>"
        result += f"<span>{format_chord(chord)}</span>"
        result += f"<span>{format_lyrics(lyrics)}</span>"
        result += "</span>"
    result += "</p>"
    return result

def split_chords(line):
    """ Splits a line into chords and lyrics. """
    blocks = []
    for pair in line.split("["):
        if "]" in pair:
            chord, lyrics = pair.split("]", 1)
            blocks.append((chord, lyrics))
        else:
            blocks.append(("", pair))
    return blocks

rxExtensionNumber = re.compile(r'(?<!^)(\d+)')
rxWordDash = re.compile(r'(\w)-(\w)')

def format_chord(chord: str) -> str:
    """ Formats a chord for display. """
    chord = rxExtensionNumber.sub(r'<sup>\1</sup>', chord)
    chord = rxWordDash.sub("", chord)
    chord = chord.replace("#", "&#9839;")
    chord = chord.replace("b", "&#9837;")
    chord = chord.replace(" ", "")
    chord += "&nbsp;"
    return chord

def format_lyrics(lyrics: str) -> str:
    """ Formats lyrics for display. """
    if lyrics.endswith(" "):
        lyrics = lyrics.strip() + "&nbsp;"
    lyrics = lyrics.strip()
    return lyrics

if __name__ == '__main__':
    render_song(
        output_filename='test',
        title='Test Song',
        artist='Test Artist',
        key='C#',
        sections=[
            ('Verse 1', '[1]This is a [Cbm 7]test.\n[2]A very excellent ex-[3m]ample'),
            ('Chorus', '[4]This is a [F#]test.'),
            ('Verse 2', '[6m]This is a[2m]nother test.'),
            ('Chorus', 'This [2m9]is a [F]test.'),
            ('Bridge', '[4]This is a [F#]test.'),
        ],
    )
