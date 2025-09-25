import re
import json
import arxiv

def get_paper_infos(pdf_urls):
    """Gets the paper information from the arxiv API and returns the paper info."""
    print("Getting the paper information from arXiv...")
    paper_urls = {}

    for key, value in pdf_urls.items():
        # extract the arxiv id from the pdf url using regular expressions
        match = re.search(r"\d{4}\.\d{5}", value[1])
        if match:
            arxiv_id = match.group(0)
            # Construct the paper URL using the arXiv ID
            paper_url = f"https://arxiv.org/abs/{arxiv_id}"
            paper_urls[key] = [value[0], paper_url]

    paper_infos = {}

    for key, value in paper_urls.items():
        # Extract the arXiv ID from the paper URL
        arxiv_id = value[1].split("/")[-1]
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        title = paper.title
        authors = [author.name for author in paper.authors]
        abstract = paper.summary
        paper_infos[key] = {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "page_id": value[0],
        }

    with open("paper_infos.json", "w") as f:
        json.dump(paper_infos, f, indent=2)

    print("Paper information saved to 'paper_infos.json'.")
    return paper_infos


def auto_fetch_paper(arxiv_info, save_path):
    print("Getting the paper information from arXiv...")
    query, max_results = arxiv_info["query"], arxiv_info["max_results"]
    search = arxiv.Search(
        query=query, sort_by=arxiv.SortCriterion.SubmittedDate, max_results=max_results
    )

    # Extract the paper titles and PDF URLs
    papers = []
    for id, result in enumerate(search.results()):
        paper = {
            "id": id + 1,
            "title": result.title,
            "pdf_url": result.pdf_url,
            "published_date": result.published.strftime("%Y-%m-%d"),
        }
        papers.append(paper)

    # Save the papers to a JSON file
    with open(save_path, "w") as f:
        json.dump(papers, f, indent=2)

    print("Paper information saved to 'papers.json'.")


def get_paper_authors(paper_infos):
    """Gets the paper authors and returns the paper authors."""
    paper_authors = {}
    for key, value in paper_infos.items():
        paper_authors[key] = [value["page_id"], value["authors"]]
    return paper_authors
