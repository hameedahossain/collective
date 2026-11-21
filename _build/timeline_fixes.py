"""One-off clean-up of _data/timeline.json (Nov 2026): plain facts on the site, conflicts moved to a review list.
Writes _data/timeline.json and _data/timeline_review.json."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "_data"
t = json.loads((D / "timeline.json").read_text())
W = lambda slug, label: {"href": f"writings/{slug}.html", "label": label}
B = lambda key, label: {"href": f"books.html#{key}", "label": label}
BDI = "The Challenge of Citizenship in Building a Just Society"

# index -> changes. keys: date, title, text, connection, link (None = no link), flag (for the review list)
F = {
 1: dict(connection="Her father was a judge hearing Hur cases in Khairpur, and the unrest led her mother to move the children to Karachi.",
         link=None, flag="No published piece covers this; her memoir chapter on Sindh does, but it is not on the site."),
 2: dict(date="mid-1940s", text="She cycled to St Joseph's Convent in a mixed, cosmopolitan Karachi full of soldiers in the last years of the Second World War.",
         flag="Exact year not recorded; memoir says the family moved when she was about ten (c. 1944–45). Site shows 'mid-1940s'."),
 3: dict(connection="She saw Hindu classmates and neighbours leave Hyderabad and injured refugees arrive by train.", link=None,
         flag="Previously linked to the BDI lecture. No better published piece found; memoir covers it but is not on the site."),
 4: dict(link=W("herstory-womens-initiatives-for-peace-and-coping-with-war", "Herstory: Women's Initiatives for Peace"),
         flag="Linked to 'Herstory' (where she writes about her grandmother and her past) instead of the BDI lecture. Please confirm this is the right piece."),
 5: dict(date="c. 1950", text="She passed her Matriculation from St Mary's Convent in Hyderabad, Sindh, after most Hindu students had left the city.",
         flag="She gives the year as '1949/1950'. Site shows 'c. 1950'."),
 7: dict(link={"href": "photos.html", "label": "Photographs from the Forum, 1952"}),
 9: dict(title="Graduates from Wellesley; UN internship",
         text="After graduating she interned in the UN Secretariat's information unit in New York, then spent six months in London working for a women's organisation that helped women's groups register to vote.",
         flag="Graduation year: CV says BA 1958; BDI interview says Wellesley 1954–57; memoir has her home in Karachi by early 1958. Site shows 1957."),
 13: dict(text="A month's visit to her sister in Dhaka drew her into university debates on autonomy, women's groups and artisan communities; she met Rehman Sobhan and Kamal Hossain and helped edit an issue of Sarwar Murshid's journal New Values.",
          link=W("memories-of-my-encounters-with-anisuzzaman", "Memories of My Encounters with Anisuzzaman"),
          flag="Year: most accounts say 1963; tributes to Professor Razzaq and Kamal Hossain say 1962; a Forum draft says 1964. Site shows 1963. Link changed from the BDI lecture to her Anisuzzaman memoir of 1960s Dhaka University."),
 14: dict(date="1964", text="She married Dr Kamal Hossain and settled in Dhaka, where she set about learning Bangla.", link=None,
          flag="Year: Wikipedia and her Anisuzzaman tribute point to 1964; the BDI lecture and career notes say she came to live in Dhaka in 1965. Site shows 1964. 'How Kamal and I Married' is private, so no link."),
 15: dict(text="With her sister and friends she opened a small outlet in Dhanmondi so village artisans could sell directly to urban buyers rather than through middlemen.", link=None,
          flag="Name of the outlet: her career notes say 'Srijani'; her Karika history and BDI lecture say 'Arunima'. Site gives no name. Karika history is not published, so no link."),
 17: dict(text="Her two daughters were born in Dhaka in the late 1960s. The elder, Sara Hossain, is a barrister and human-rights lawyer; the younger, Dina Hossain, is a documentary filmmaker and teacher."),
 19: dict(text="She was editor, with Rehman Sobhan as executive editor and Kamal Hossain as publisher, of Forum, an English-language political weekly run from a garage room in Circuit House Road. Its first editorial was 'In Search of Freedom'.",
          link=None, flag="When permission for Forum came: 1967 or 1968 (her accounts differ); her CV dates her editorship 1967–71. Site shows only the first issue, November 1969. Memoir chapter on Forum not on the site."),
 21: dict(link=None), 22: dict(link=None), 23: dict(link=None),
 24: dict(link=B("of-the-nation-born", "Of the Nation Born (book)"),
          flag="Linked to her co-edited book Of the Nation Born; 'Independence, Yes – What Became of Liberation' is an unfinished draft and not on the site."),
 25: dict(link=None),
 26: dict(connection="", link=None, flag="Her Bangla interview on rehabilitating war-affected women covers this but is withheld (source unknown). No link for now."),
 27: dict(link=None, flag="Previously pointed to 'Gender in the Development Discourse', a Claiming Our Rights chapter (not on the site)."),
 29: dict(image=None, link=None, flag="The photo previously used here was an official visit in Tokyo, not a crafts exhibition, and has been removed. A photo of the 1973 exhibition would be welcome."),
 30: dict(link=None, flag="'The Story of KARIKA' is a draft with others' comments and is not on the site."),
 31: dict(link=None, flag="Previously linked to the BDI lecture. No better published piece found."),
 33: dict(link=None),
 34: dict(date="c. 1976", text="Encouraged by Tapan Raychaudhuri, she enrolled at St Antony's College, Oxford, and studied East India Company records in the India Office Library on Bengal's textile trade.",
          link=B("company-weavers-of-bengal", "The Company Weavers of Bengal (book)"),
          flag="Start date of doctorate not recorded; she says the idea came after settling in Oxford in 1975. Site shows 'c. 1976'."),
 35: dict(link=None, flag="'Alienation of Weavers' (1979, IESHR) is not on the site; a link to the journal could be added."),
 37: dict(text="She completed her doctorate in modern history at St Antony's College, Oxford, and the family returned to Dhaka.",
          link=B("company-weavers-of-bengal", "The Company Weavers of Bengal (book)")),
 39: dict(text="Inspired by the artist Qamrul Hasan, she helped found the National Crafts Council of Bangladesh and served as its secretary under his presidency.",
          flag="Year: NCCB notes and the Qamrul Hasan tribute say 1985; her CV says 1984. Site shows 1985."),
 40: dict(link=None, flag="Previously linked to the BDI lecture. No better published piece found."),
 41: dict(text="With Salma Sobhan, Khursheed Erfan Ahmed, Amirul Islam, F.H. Abed and others she founded Ain o Salish Kendra (ASK), starting with mediation and legal aid for women and workers from a borrowed garage in Dhanmondi. She was its Director of Research and Advocacy until 2003.",
          link=None, flag="Founding year: bios and the Daily Star say 1986; her timeline notes say 1985; the BDI lecture says 'early 1980s'. Site shows 1986. Her Salma Sobhan remembrance would fit but is a private transcript."),
 42: dict(text="She co-authored a study of women garment workers with Roushan Jahan and Salma Sobhan, published in 1990 as No Better Option? Industrial Women Workers in Bangladesh.",
          link=B("no-better-option", "No Better Option? (book)")),
 43: dict(link=B("company-weavers-of-bengal", "The Company Weavers of Bengal (book)")),
 45: dict(link=B("rising-from-the-ashes", "Rising from the Ashes (book)")),
 46: dict(link=B("claiming-our-rights", "Claiming Our Rights (book)")),
 47: dict(link=W("on-ayesha-khanam", "On Ayesha Khanam"), flag="Link changed from the BDI lecture to her Ayesha Khanam tribute, which discusses the Yasmin case."),
 48: dict(link=W("herstory-womens-initiatives-for-peace-and-coping-with-war", "Herstory: Women's Initiatives for Peace")),
 49: dict(text="She began editing ASK's annual report, Human Rights in Bangladesh.",
          link=W("bangladesh-2006-a-human-rights-audit", "Bangladesh 2006: A Human Rights Audit"),
          flag="End year: résumé and bios say she edited it until 2006; CV says 1996–2002. Site gives only the start year."),
 50: dict(date="1990s", text="With Ayesha Khanam of the Mahila Parishad and others she drafted a shadow report and presented it to the CEDAW Committee in New York.",
          flag="Year: her tribute says 1995, but the CEDAW Committee reviewed Bangladesh in 1997. Site shows '1990s'."),
 51: dict(link=None, flag="'Impressions of Afghanistan' is part of the unfinished memoir and not on the site."),
 53: dict(link=W("herstory-womens-initiatives-for-peace-and-coping-with-war", "Herstory: Women's Initiatives for Peace")),
 54: dict(link=B("claiming-our-rights", "Claiming Our Rights (book)")),
 55: dict(text="ASK published oral histories of 22 women who lived through 1971, gathered by a team she worked with. The English translation, Rising from the Ashes, followed.",
          link=B("rising-from-the-ashes", "Rising from the Ashes (book)"),
          flag="Year of Narir Ekattor: her foreword (as quoted in the Daily Star) says 2001; her timeline notes say 1997. English translation dated 2012 or 2013 by different records."),
 58: dict(link=W("welcome-address-sahr-meeting-kathmandu", "Welcome Address, SAHR Meeting, Kathmandu"),
          flag="Co-Chair years 2008–11 come only from her résumé."),
 59: dict(text="The High Court issued binding guidelines against sexual harassment in workplaces and educational institutions.",
          link=None, flag="Date: she gives 1 May 2009; press reports give 14 May 2009. Site shows 'May 2009'. Previously linked to the BDI lecture; no better piece found."),
 60: dict(link=B("freedom-from-fear", "Freedom from Fear, Freedom from Want? (book)")),
 61: dict(link=B("claiming-our-rights", "Claiming Our Rights (book)")),
 62: dict(link=B("claiming-our-rights", "Claiming Our Rights (book)"), flag="Her pieces on Tazreen are chapters of Claiming Our Rights, so the link goes to the book."),
 63: dict(link=W("garment-industry-workers-compensation-bn", "তৈরি পোশাকশিল্প: শ্রমিকদের ক্ষতিপূরণ কবে দেওয়া হবে?")),
 64: dict(link=W("its-time-to-pay-up", "It's Time to Pay Up")),
 65: dict(link=B("of-the-nation-born", "Of the Nation Born (book)")),
 66: dict(link=W("the-challenge-of-citizenship-in-building-a-just-society-bdi", "The Challenge of Citizenship in Building a Just Society")),
 67: dict(link=B("claiming-our-rights", "Claiming Our Rights (book)")),
}
assert t[17]["title"] == "Her daughters are born" and t[29]["title"] == "National crafts exhibition", "timeline order changed"
review = []
for i, e in enumerate(t):
    ch = F.get(i, {})
    flag = ch.pop("flag", "")
    for k, v in ch.items():
        if k == "image" and v is None:
            e.pop("image", None)
        elif k == "link":
            e["link"] = v
        else:
            e[k] = v
    if "link" not in e:   # keep only links to pieces on the site; never default to the BDI lecture
        e["link"] = W(e["related_slug"], e.get("related_writing") or "") if e.get("related_slug") and e.get("related_slug") != "the-challenge-of-citizenship-in-building-a-just-society-bdi" else None
    if flag:
        review.append({"year": e["year"], "event": e["title"], "note": flag, "shown": e.get("date") or str(e["year"]), "sources": e.get("source", "")})
bdi_links = sum(1 for e in t if e.get("link") and "citizenship" in e["link"]["href"])
(D / "timeline.json").write_text(json.dumps(t, ensure_ascii=False, indent=1))
(D / "timeline_review.json").write_text(json.dumps(review, ensure_ascii=False, indent=1))
print("review items", len(review), "| links", sum(1 for e in t if e.get("link")), "| BDI links", bdi_links)
