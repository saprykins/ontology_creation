# Official doc arxiv: Request from api
import urllib
import urllib.request

# Getting key information from xml
import xml.etree.ElementTree as ET

import requests

# Ontology
from owlready2 import *

# Text extraction
from pdfminer.high_level import extract_text


def get_article_data(url):
    """
    GET INFORMATION ON ARTICLE FROM ARXIV SITE
    """

    data = urllib.request.urlopen(url)
    # print(data.read().decode('utf-8'))

    tree = ET.parse(data)

    # putting article data in dictionary
    array_of_articles = []
    root = tree.getroot()
    # article_buffer = {}
    for child in root:

        article_buffer = {}
        art_authors = []
        for grand_child in child:

            # finds and updates article's link
            if grand_child.tag == "{http://www.w3.org/2005/Atom}id":
                article_link = grand_child.text
                pdf_link = article_link.replace(
                    "http://arxiv.org/abs", "http://arxiv.org/pdf"
                )
                article_buffer["pdf_link"] = pdf_link

            if grand_child.tag == "{http://www.w3.org/2005/Atom}title":
                title = grand_child.text.replace('"', "_")
                article_buffer["title"] = title

            if grand_child.tag == "{http://www.w3.org/2005/Atom}published":
                # in order to keep only the year
                article_buffer["published_on_date"] = grand_child.text[:4]

            if grand_child.tag == "{http://www.w3.org/2005/Atom}summary":
                article_buffer["summary"] = grand_child.text

            if grand_child.tag == "{http://arxiv.org/schemas/atom}comment":
                article_buffer["comment"] = grand_child.text

            if grand_child.tag == "{http://arxiv.org/schemas/atom}journal_ref":
                # we keep only the part related to the name of journal
                # and don't keep page numbers
                journal_name_limiter = grand_child.text.find(")")
                journal_name = grand_child.text[: journal_name_limiter + 1]
                article_buffer["journal_ref"] = journal_name.replace('"', "_")

            # ::2 to avoid printing departments
            # for grand_grand_child in grand_child[::2]:
            author_dict = {}
            for grand_grand_child in grand_child:

                if grand_grand_child.tag == "{http://www.w3.org/2005/Atom}name":
                    writer = grand_grand_child.text
                    author_dict["name"] = writer
                    # print(writer)

                # some API responses provide information on author's lab
                if (
                    grand_grand_child.tag
                    == "{http://arxiv.org/schemas/atom}affiliation"
                ):
                    lab_of_writer = grand_grand_child.text
                    # print(lab_of_writer)
                    author_dict["lab"] = lab_of_writer
                    # print(lab_of_writer)

            # fill in the list of authors (each author is a dictionary with name and lab of the author)
            if author_dict:
                art_authors.append(author_dict)

            if article_buffer:
                article_buffer["authors"] = author_dict

            if len(art_authors) > 0:
                article_buffer["authors"] = art_authors

        # if dictionary is empty
        if article_buffer:
            array_of_articles.append(article_buffer)
    return array_of_articles


def line_of_authors_to_array(line):
    """
    TRANSFORMS REFERENCES (IN TEXT) FORMAT TO ARRAY OF AUTHORS
    """
    array_of_authors = []

    # "&" splits authors in references
    special_character = "&"
    if special_character in line:
        last_author = line[line.find("&") + 2 :]
        line = line[: line.find("&")]
        array_of_authors.append(last_author.strip())

    while len(line) > 3:
        # if find = -1 means that it did not find
        if line.find(".,") != -1:
            author_i = line[: line.find(".,") + 1].strip()
            array_of_authors.append(author_i)
            line = line[line.find(".,") + 3 :]

        else:
            array_of_authors.append(line.strip())
            line = ""

    return array_of_authors


def get_references_in_text_format_from_link(pdf_url):
    """
    GIVE A LINK WITH ARTICLE, GET REFERENCES IN TEXT
    """
    try:
        text = send_a_pdf_to_api_and_get_text_from_api(pdf_url)
        reference_word = "Reference"
        references = text[text.find(reference_word) :]

    except Exception:
        references = "references_"

    return references[12:]


def get_array_of_references_from_string_of_references(references_2):
    """
    Transpose string of references to array
    """
    array_of_references = []
    # sometimes extraction quality is bad, if many references are of a bad quality, it skips the document
    max_numer_of_trials_to_read_reference = 30
    # j number of trials to read the file
    j = 0

    # if less than 10 characters left, it's not a complete reference
    while len(references_2) > 10:
        ref_buffer = {}
        array_ref_authors = []

        ref_authors_end_index = references_2.find("(")

        ref_authors = references_2[:ref_authors_end_index]

        # keep text from right to the last new line symbol (\n)
        # in case line offset
        if ref_authors.rfind("\n") > 0:
            ref_authors = ref_authors[ref_authors.rfind("\n") + 1 :]

        array_ref_authors = line_of_authors_to_array(ref_authors)

        ref_buffer["authors"] = array_ref_authors

        date_end_index = references_2.find(")")
        ref_year = references_2[ref_authors_end_index + 1 : date_end_index]

        # check line quality
        # and exit cycle if bad
        # used to verify if data is in 19** format
        date_format = "(^[1][9][0-9][0-9]$)"
        match = re.search(date_format, ref_year)
        if (not bool(match)) and (j < max_numer_of_trials_to_read_reference):
            references_2 = references_2[date_end_index + 1 :]
            j += 1
            continue

        ref_buffer["year"] = ref_year
        references_2 = references_2[date_end_index:]

        ref_title_start = references_2.find(".")
        ref_title_end = references_2.find(".", references_2.find(".") + 1)
        ref_title = references_2[ref_title_start + 2 : ref_title_end].replace("\n", "")

        ref_buffer["title"] = ref_title
        references_2 = references_2[ref_title_end + 2 :]
        ref_source = references_2[: references_2.find(",")].replace("\n", "")

        references_2 = references_2[references_2.find(".") + 3 :]
        ref_buffer["ref_source"] = ref_source

        if (
            (ref_buffer)
            and ref_buffer["authors"]
            and (not ref_buffer["authors"][0].find(".") == -1)
            and bool(re.search(date_format, ref_year))
        ):
            array_of_references.append(ref_buffer)
    return array_of_references


def create_onto_from_one_article(article, array_of_references):
    """
    CREATES ONTOLOGY
    """
    ontology_local_link = "onto_output.owl"
    onto = get_ontology("http://test.org/onto.owl")
    with onto:

        class Authors(Thing):
            pass

        class Articles(Thing):
            pass

        class Journals(Thing):
            pass

        class Institutions(Thing):
            pass

        class wrote_article(ObjectProperty):
            domain = [Authors]
            range = [Articles]

        class works_in(ObjectProperty):
            domain = [Authors]
            range = [Institutions]

        class published_in(ObjectProperty):
            domain = [Authors]
            range = [Journals]

        class references_article(ObjectProperty):
            domain = [Articles]
            range = [Articles]

        class read_article(ObjectProperty):
            domain = [Authors]
            range = [Articles]

        class published_on_date(DataProperty):
            range = [str]

    # get data from article-dictionary
    authors = article["authors"]

    published_on_date = article["published_on_date"].replace(" ", "_")

    article_title = article["title"].replace(" ", "_")
    article_i = Articles(article_title)

    journal_title = article["journal_ref"].replace(" ", "_")
    journal_i = Journals(journal_title)
    journal_i.published_on_date.append(published_on_date)

    for reference in array_of_references:
        # we search for article titles and replace spaces with underscore for better ontology representation
        reference_title = reference["title"]
        reference_title = reference_title.replace("  ", "_")
        reference_title = reference_title.replace(" ", "_")

        reference_i = Articles(reference_title)
        article_i.references_article.append(reference_i)

        for author_of_reference in reference["authors"]:
            author_of_reference = author_of_reference.replace(" ", "_")
            author_i = Authors(author_of_reference)
            author_i.wrote_article.append(article_i)

    for author in authors:

        author_i = Authors(author["name"].replace(" ", "_"))
        author_i.published_in.append(journal_i)
        author_i.wrote_article.append(article_i)

        try:
            lab_i = Institutions(author["lab"].replace(" ", "_"))
            author_i.works_in.append(lab_i)

        except Exception:
            pass

    onto.save(file=ontology_local_link)


def send_a_pdf_to_api_and_get_text_from_api(file_url):
    """
    Establishing connection with api
    """
    local_file = "local_copy.pdf"
    # it's the internal api
    # is used to send pdf-file and get document_id
    post_url = "http://localhost:5000/documents"

    urllib.request.urlretrieve(file_url, local_file)

    files = {"file": open(local_file, "rb")}

    # send file
    response = requests.post(post_url, files=files)

    # api is configured to return documenet_id
    document_id = response.json()["id"]

    # getting data from api
    get_url = "http://localhost:5000/text/" + str(document_id) + ".txt"

    # the api is configured to return text when document_id is sent
    response = requests.get(get_url)
    text_from_file = response.json()

    return text_from_file["text"]


def make_text_xml_friendly(text):
    """
    REMPLACING UNACCEPTABLE FOR XML FORMAT CHARACTERS
    """

    text = text.replace("|", "_")
    text = text.replace("`", "_")
    text = text.replace("\\", "_")
    text = text.replace('"', "_")
    text = text.replace("{", "_")
    text = text.replace("}", "_")
    text = text.replace("(cid:14)", "ffi")
    text = text.replace("(cid:12)", "fi")
    text = text.replace("(cid:11)", "ff")
    text = text.replace("(cid:13)", "fl")
    text = text.replace("(unpublished)", "_")
    text = text.replace("#", "_")
    text = text.replace("“", "_")

    return text


def main(number_of_articles):
    """
    Request to arxiv and cycle through the articles
    """

    url = (
        "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results="
        + str(number_of_articles)
    )
    array_of_articles = get_article_data(url)  # request to arxiv

    # CYCLE THROUGH articles
    i = 0
    print("______")
    print("Id", "link")
    for article in array_of_articles:
        pdf_url = article["pdf_link"]
        text = get_references_in_text_format_from_link(pdf_url)
        text = make_text_xml_friendly(text)
        array_of_references = get_array_of_references_from_string_of_references(text)

        try:
            create_onto_from_one_article(article, array_of_references)
        except Exception:
            pass
        i += 1
        print(i, pdf_url)
    print("------")


if __name__ == "__main__":
    # the number can be modified
    number_of_articles = 3
    main(number_of_articles)
