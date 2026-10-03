from flask import Flask, render_template_string, request, abort, url_for
import sqlite3
import os
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "herbadex.db")


# ============================================================
# PLANT DATA
# ============================================================

PLANTS = [
    {
        "common_name": "Tulsi",
        "scientific_name": "Ocimum tenuiflorum L.",
        "family": "Lamiaceae",
        "biological_source": "Leaves and aerial parts of Ocimum tenuiflorum.",
        "plant_part": "Leaves / aerial parts",
        "active_constituents": "Eugenol, rosmarinic acid, ursolic acid",
        "phytochemicals": "Phenolics, terpenoids and essential-oil constituents",
        "traditional_uses": "Traditionally used in Indian systems of medicine and household herbal practices.",
        "description": "Tulsi is an aromatic medicinal plant widely cultivated in India. It is an important subject in pharmacognosy because of its characteristic leaves, aroma and phytochemical constituents.",
        "category": "Aromatic herbs",
        "safety_note": "Traditional use does not establish that a plant is suitable for every person. Use reliable references and consult a qualified professional for medical decisions.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ocimum_tenuiflorum.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Ocimum%20tenuiflorum"
    },
    {
        "common_name": "Neem",
        "scientific_name": "Azadirachta indica A.Juss.",
        "family": "Meliaceae",
        "biological_source": "Leaves, bark, seeds and other parts of Azadirachta indica.",
        "plant_part": "Leaves / bark / seeds",
        "active_constituents": "Azadirachtin, nimbin, nimbidin",
        "phytochemicals": "Limonoids, terpenoids and flavonoids",
        "traditional_uses": "Traditionally used in Indian herbal practices and for various household and medicinal preparations.",
        "description": "Neem is a well-known tree of the Indian subcontinent and is an important medicinal plant studied in pharmacognosy and phytochemistry.",
        "category": "Medicinal trees",
        "safety_note": "Neem preparations are not automatically safe for everyone. Avoid treating this educational entry as a dosage or treatment guide.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Azadirachta_indica.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Azadirachta%20indica"
    },
    {
        "common_name": "Turmeric",
        "scientific_name": "Curcuma longa L.",
        "family": "Zingiberaceae",
        "biological_source": "Rhizomes of Curcuma longa.",
        "plant_part": "Rhizome",
        "active_constituents": "Curcuminoids, including curcumin",
        "phytochemicals": "Curcuminoids and volatile oils",
        "traditional_uses": "Used traditionally as a spice and in Indian systems of traditional medicine.",
        "description": "Turmeric is a rhizomatous plant. Its underground rhizomes are the familiar yellow source used as a spice and in traditional preparations.",
        "category": "Spices",
        "safety_note": "This entry is educational. It does not recommend turmeric supplements, doses or treatment of any condition.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Curcuma_longa.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/796451-1"
    },
    {
        "common_name": "Ginger",
        "scientific_name": "Zingiber officinale Roscoe",
        "family": "Zingiberaceae",
        "biological_source": "Rhizomes of Zingiber officinale.",
        "plant_part": "Rhizome",
        "active_constituents": "Gingerols, shogaols and zingerone",
        "phytochemicals": "Phenolic compounds and volatile oils",
        "traditional_uses": "Traditionally used as a culinary spice and in herbal preparations.",
        "description": "Ginger is a rhizomatous plant in the Zingiberaceae family and is widely known as a culinary spice as well as a traditional herbal material.",
        "category": "Spices",
        "safety_note": "Traditional use is not the same as proven treatment. This repository does not provide dosage recommendations.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Zingiber_officinale.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Zingiber%20officinale"
    },
    {
        "common_name": "Amla",
        "scientific_name": "Phyllanthus emblica L.",
        "family": "Phyllanthaceae",
        "biological_source": "Fruit of Phyllanthus emblica.",
        "plant_part": "Fruit",
        "active_constituents": "Vitamin C, tannins and polyphenolic compounds",
        "phytochemicals": "Tannins, phenolics and flavonoids",
        "traditional_uses": "Traditionally used as a food and in Indian herbal systems.",
        "description": "Amla is a tree native to tropical and subtropical Asia. Its fruit is widely used as food and in traditional herbal preparations.",
        "category": "Medicinal fruits",
        "safety_note": "Information is provided for educational purposes and is not a personalized treatment recommendation.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Phyllanthus_emblica.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/353838-1"
    },
    {
        "common_name": "Ashwagandha",
        "scientific_name": "Withania somnifera (L.) Dunal",
        "family": "Solanaceae",
        "biological_source": "Roots and other parts of Withania somnifera.",
        "plant_part": "Root",
        "active_constituents": "Withanolides, alkaloids",
        "phytochemicals": "Steroidal lactones and alkaloids",
        "traditional_uses": "Traditionally used in Ayurveda and other traditional herbal practices.",
        "description": "Ashwagandha is a medicinal plant of the Solanaceae family and is widely studied for its characteristic steroidal lactones called withanolides.",
        "category": "Medicinal herbs",
        "safety_note": "Do not interpret this entry as a recommendation to use Ashwagandha or as a dosage guide.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Withania_somnifera.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Withania%20somnifera"
    },
    {
        "common_name": "Aloe Vera",
        "scientific_name": "Aloe vera (L.) Burm.f.",
        "family": "Asphodelaceae",
        "biological_source": "Leaf tissues of Aloe vera.",
        "plant_part": "Leaf gel / latex",
        "active_constituents": "Acemannan and anthraquinone-related compounds",
        "phytochemicals": "Polysaccharides, anthraquinones and phenolic compounds",
        "traditional_uses": "The leaf gel has a long history of use in traditional and cosmetic preparations.",
        "description": "Aloe vera is a succulent perennial plant with thick leaves containing a colourless gel-like tissue.",
        "category": "Succulents",
        "safety_note": "Different parts of Aloe have different chemical profiles. Do not use this entry as a treatment or ingestion guide.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Aloe_vera.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/530017-1"
    },
    {
        "common_name": "Brahmi",
        "scientific_name": "Bacopa monnieri (L.) Wettst.",
        "family": "Plantaginaceae",
        "biological_source": "Whole herb of Bacopa monnieri.",
        "plant_part": "Whole plant / aerial parts",
        "active_constituents": "Bacosides",
        "phytochemicals": "Triterpenoid saponins and alkaloids",
        "traditional_uses": "Traditionally used in Ayurveda and studied as an important medicinal herb.",
        "description": "Bacopa monnieri is a small herb associated with wet habitats and is widely studied for its characteristic saponin constituents.",
        "category": "Medicinal herbs",
        "safety_note": "This entry describes traditional and scientific information only and does not provide treatment advice.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bacopa_monnieri.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/1072674-2"
    },
    {
        "common_name": "Giloy",
        "scientific_name": "Tinospora cordifolia (Willd.) Hook.f. & Thomson",
        "family": "Menispermaceae",
        "biological_source": "Stem and other plant parts of Tinospora cordifolia.",
        "plant_part": "Stem",
        "active_constituents": "Diterpenoid lactones, alkaloids and polysaccharides",
        "phytochemicals": "Alkaloids, diterpenoids and glycosides",
        "traditional_uses": "Traditionally used in Indian systems of medicine.",
        "description": "Tinospora cordifolia is a climbing plant native to the Indian subcontinent and is an established subject of pharmacognosy research.",
        "category": "Medicinal climbers",
        "safety_note": "Traditional use should not be interpreted as a guarantee of safety or effectiveness.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tinospora_cordifolia.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/907828-1"
    },
    {
        "common_name": "Arjuna",
        "scientific_name": "Terminalia arjuna (Roxb. ex DC.) Wight & Arn.",
        "family": "Combretaceae",
        "biological_source": "Bark of Terminalia arjuna.",
        "plant_part": "Bark",
        "active_constituents": "Triterpenoids, tannins and flavonoids",
        "phytochemicals": "Tannins, triterpenoids and flavonoids",
        "traditional_uses": "Traditionally used in Ayurveda, particularly preparations involving the bark.",
        "description": "Arjuna is a large tree whose bark is an important crude drug studied in pharmacognosy.",
        "category": "Medicinal trees",
        "safety_note": "The entry is for academic study and is not a treatment or dosage recommendation.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Terminalia_arjuna.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Terminalia%20arjuna"
    },
    {
        "common_name": "Moringa",
        "scientific_name": "Moringa oleifera Lam.",
        "family": "Moringaceae",
        "biological_source": "Leaves, seeds and other parts of Moringa oleifera.",
        "plant_part": "Leaves / seeds",
        "active_constituents": "Glucosinolates, phenolics and flavonoids",
        "phytochemicals": "Phenolics, flavonoids and glucosinolates",
        "traditional_uses": "Used as a food plant and in traditional practices.",
        "description": "Moringa oleifera is a tree native to the Indian subcontinent and is important as both a food and useful plant.",
        "category": "Medicinal trees",
        "safety_note": "This repository does not recommend concentrated extracts or supplements.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Moringa_oleifera.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/584736-1"
    },
    {
        "common_name": "Shatavari",
        "scientific_name": "Asparagus racemosus Willd.",
        "family": "Asparagaceae",
        "biological_source": "Roots of Asparagus racemosus.",
        "plant_part": "Root",
        "active_constituents": "Steroidal saponins",
        "phytochemicals": "Steroidal saponins and polyphenolic compounds",
        "traditional_uses": "Traditionally used in Ayurveda.",
        "description": "Shatavari is a medicinal plant whose roots are used as a crude drug in traditional herbal systems.",
        "category": "Medicinal herbs",
        "safety_note": "Educational information only. Individual use should be discussed with a qualified professional.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Asparagus_racemosus.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Asparagus%20racemosus"
    },
    {
        "common_name": "Cinnamon",
        "scientific_name": "Cinnamomum verum J.Presl",
        "family": "Lauraceae",
        "biological_source": "Dried bark of Cinnamomum verum.",
        "plant_part": "Bark",
        "active_constituents": "Cinnamaldehyde and eugenol",
        "phytochemicals": "Phenylpropanoids and volatile oils",
        "traditional_uses": "Used as a spice and in traditional herbal preparations.",
        "description": "Cinnamon is an aromatic tree whose bark is commonly used as a spice and studied for its volatile oil constituents.",
        "category": "Spices",
        "safety_note": "Cinnamon preparations differ in composition. This page is not a dosage or treatment guide.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Cinnamomum_verum.jpg",
        "reference_url": "https://powo.science.kew.org/results?q=Cinnamomum%20verum"
    },
    {
        "common_name": "Clove",
        "scientific_name": "Syzygium aromaticum (L.) Merr. & L.M.Perry",
        "family": "Myrtaceae",
        "biological_source": "Dried flower buds of Syzygium aromaticum.",
        "plant_part": "Flower bud",
        "active_constituents": "Eugenol",
        "phytochemicals": "Phenylpropanoids and volatile oils",
        "traditional_uses": "Used as a spice and in traditional preparations.",
        "description": "Clove consists of the dried aromatic flower buds of Syzygium aromaticum. Eugenol is a major component of its volatile oil.",
        "category": "Spices",
        "safety_note": "Concentrated clove oil is different from culinary use. This website does not provide instructions for medicinal use.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Syzygium_aromaticum.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/601421-1"
    },
    {
        "common_name": "Peppermint",
        "scientific_name": "Mentha × piperita L.",
        "family": "Lamiaceae",
        "biological_source": "Leaves and aerial parts of Mentha × piperita.",
        "plant_part": "Leaves / aerial parts",
        "active_constituents": "Menthol, menthone",
        "phytochemicals": "Monoterpenes and volatile oils",
        "traditional_uses": "Used as an aromatic herb, food flavouring and in traditional preparations.",
        "description": "Peppermint is an accepted hybrid in the genus Mentha and is widely known for its aromatic essential oil.",
        "category": "Aromatic herbs",
        "safety_note": "Peppermint information here is educational and does not constitute medical advice.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Mentha_piperita.jpg",
        "reference_url": "https://powo.science.kew.org/taxon/450969-1"
    }
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL,
            scientific_name TEXT NOT NULL,
            family TEXT NOT NULL,
            biological_source TEXT,
            plant_part TEXT,
            active_constituents TEXT,
            phytochemicals TEXT,
            traditional_uses TEXT,
            description TEXT,
            image_url TEXT,
            reference_url TEXT,
            category TEXT,
            safety_note TEXT
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0]

    if count == 0:
        for plant in PLANTS:
            conn.execute("""
                INSERT INTO plants (
                    common_name,
                    scientific_name,
                    family,
                    biological_source,
                    plant_part,
                    active_constituents,
                    phytochemicals,
                    traditional_uses,
                    description,
                    image_url,
                    reference_url,
                    category,
                    safety_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plant["common_name"],
                plant["scientific_name"],
                plant["family"],
                plant["biological_source"],
                plant["plant_part"],
                plant["active_constituents"],
                plant["phytochemicals"],
                plant["traditional_uses"],
                plant["description"],
                plant["image_url"],
                plant["reference_url"],
                plant["category"],
                plant["safety_note"]
            ))

    conn.commit()
    conn.close()


# ============================================================
# HTML TEMPLATE
# ============================================================

BASE_STYLE = """
<style>
:root {
    --green: #236b45;
    --dark: #163d29;
    --light: #f3f8f4;
    --border: #dce9df;
    --text: #263b30;
    --muted: #65756c;
    --white: #ffffff;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #f7faf8;
    color: var(--text);
    line-height: 1.6;
}

a {
    color: inherit;
}

nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(255,255,255,.96);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
    padding: 17px 6%;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 27px;
    font-weight: 800;
    color: var(--green);
    text-decoration: none;
}

.logo span {
    color: #86a96e;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 23px;
}

.nav-links a {
    text-decoration: none;
    font-weight: 600;
    color: #405248;
}

.nav-links a:hover {
    color: var(--green);
}

.container {
    width: min(1180px, 92%);
    margin: auto;
}

.hero {
    padding: 90px 6%;
    background:
        radial-gradient(circle at 90% 20%, #dcefe1, transparent 30%),
        linear-gradient(135deg, #edf7ef, #ffffff);
}

.hero-inner {
    max-width: 1000px;
    margin: auto;
}

.badge {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 30px;
    background: #dfeee3;
    color: var(--green);
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: clamp(40px, 7vw, 72px);
    line-height: 1.05;
    color: var(--dark);
    margin-bottom: 22px;
}

.hero h1 span {
    color: var(--green);
}

.hero p {
    max-width: 760px;
    color: var(--muted);
    font-size: 18px;
    margin-bottom: 28px;
}

.btn {
    display: inline-block;
    padding: 12px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 700;
    border: 1px solid var(--green);
    margin: 5px;
}

.btn-primary {
    background: var(--green);
    color: white;
}

.btn-outline {
    color: var(--green);
    background: white;
}

.section {
    padding: 70px 0;
}

.section-title {
    text-align: center;
    margin-bottom: 40px;
}

.section-title h2 {
    font-size: 34px;
    color: var(--dark);
    margin-bottom: 8px;
}

.section-title p {
    color: var(--muted);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2,1fr);
    gap: 25px;
}

.info-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(30,70,45,.05);
}

.info-card h3 {
    color: var(--green);
    margin-bottom: 10px;
}

.search-box {
    background: white;
    border: 1px solid var(--border);
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
}

.search-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 12px;
}

input, select {
    width: 100%;
    padding: 13px 14px;
    border: 1px solid #ccdacf;
    border-radius: 8px;
    font-size: 15px;
    background: white;
}

button {
    border: none;
    cursor: pointer;
}

.search-btn {
    padding: 13px 20px;
    background: var(--green);
    color: white;
    border-radius: 8px;
    font-weight: 700;
}

.plant-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 24px;
}

.plant-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(30,70,45,.05);
    transition: .2s;
}

.plant-card:hover {
    transform: translateY(-4px);
}

.plant-card img {
    width: 100%;
    height: 220px;
    object-fit: cover;
    background: #e8f1e9;
}

.plant-body {
    padding: 20px;
}

.plant-body h3 {
    color: var(--dark);
    margin-bottom: 4px;
}

.scientific {
    color: var(--green);
    font-style: italic;
    margin-bottom: 10px;
}

.family {
    display: inline-block;
    background: #eaf4ed;
    color: var(--green);
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 700;
}

.detail {
    padding: 60px 0;
}

.detail-grid {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 40px;
}

.detail-image {
    width: 100%;
    height: 430px;
    object-fit: cover;
    border-radius: 18px;
    background: #e8f1e9;
}

.detail-content h1 {
    font-size: 42px;
    color: var(--dark);
    margin-bottom: 5px;
}

.detail-content h2 {
    font-size: 20px;
    color: var(--green);
    font-style: italic;
    font-weight: 500;
    margin-bottom: 25px;
}

.data-list {
    display: grid;
    gap: 14px;
}

.data-item {
    padding: 16px;
    background: #f5f9f6;
    border: 1px solid var(--border);
    border-radius: 10px;
}

.data-item strong {
    display: block;
    color: var(--dark);
    margin-bottom: 4px;
}

.table-wrap {
    overflow-x: auto;
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 700px;
}

th, td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

th {
    background: #edf6ef;
    color: var(--dark);
}

.disclaimer {
    background: #fffbea;
    border: 1px solid #eadfae;
    border-radius: 13px;
    padding: 22px;
    margin-top: 30px;
}

.disclaimer h3 {
    color: #735f25;
    margin-bottom: 7px;
}

.disclaimer p {
    color: #685f42;
}

.page-head {
    padding: 65px 0 35px;
    background: #edf7ef;
}

.page-head h1 {
    font-size: 45px;
    color: var(--dark);
}

.page-head p {
    color: var(--muted);
    max-width: 700px;
}

.reference-list {
    display: grid;
    gap: 15px;
}

.reference {
    background: white;
    padding: 20px;
    border: 1px solid var(--border);
    border-radius: 12px;
}

.reference a {
    color: var(--green);
    font-weight: 700;
    text-decoration: none;
}

footer {
    background: var(--dark);
    color: white;
    text-align: center;
    padding: 35px 6%;
    margin-top: 50px;
}

footer p {
    color: #d0ded5;
    margin-top: 5px;
}

.empty {
    text-align: center;
    padding: 50px;
    background: white;
    border: 1px dashed #bfd0c4;
    border-radius: 12px;
    color: var(--muted);
}

@media(max-width:900px) {
    .plant-grid {
        grid-template-columns: repeat(2,1fr);
    }

    .detail-grid {
        grid-template-columns: 1fr;
    }

    .search-row {
        grid-template-columns: 1fr 1fr;
    }
}

@media(max-width:650px) {
    .nav-links {
        display: none;
    }

    .info-grid,
    .plant-grid {
        grid-template-columns: 1fr;
    }

    .hero {
        padding: 60px 5%;
    }

    .search-row {
        grid-template-columns: 1fr;
    }

    .detail-content h1 {
        font-size: 34px;
    }
}
</style>
"""


def page(title, content, description="HerbaDex Indian Medicinal Plants & Herbal Knowledge Repository"):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | HerbaDex</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
{BASE_STYLE}
</head>
<body>

<nav>
    <a href="/" class="logo">Herba<span>Dex</span></a>

    <ul class="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/plants">Plants</a></li>
        <li><a href="/phytochemistry">Phytochemistry</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/references">References</a></li>
    </ul>
</nav>

{content}

<footer>
    <h3>HerbaDex</h3>
    <p>Indian Medicinal Plants & Herbal Knowledge Repository</p>
    <p>Academic Prototype | Pharmacognosy & Phytochemistry</p>
</footer>

</body>
</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    content = """
<section class="hero">
<div class="hero-inner">

<div class="badge">PHARMACOGNOSY & PHYTOCHEMISTRY DIRECTORY</div>

<h1>
Indian Medicinal Plants
<span>Herbal Repository</span>
</h1>

<p>
HerbaDex is an educational digital repository designed to organize
information about Indian medicinal plants, botanical identity,
plant parts, active constituents and phytochemical profiles.
</p>

<a href="/plants" class="btn btn-primary">Explore Plants</a>
<a href="/phytochemistry" class="btn btn-outline">Explore Phytochemistry</a>

</div>
</section>

<section class="section">
<div class="container">

<div class="section-title">
<h2>Explore Herbal Knowledge</h2>
<p>Learn medicinal-plant information through a structured academic repository.</p>
</div>

<div class="info-grid">

<div class="info-card">
<h3>🌿 Pharmacognosy</h3>
<p>
Pharmacognosy is the study of medicinal substances obtained from
natural sources, especially plants. It includes identification,
description, collection and evaluation of crude drugs.
</p>
</div>

<div class="info-card">
<h3>🧪 Phytochemistry</h3>
<p>
Phytochemistry deals with chemical constituents found in plants,
including groups such as alkaloids, flavonoids, terpenoids,
phenolics and saponins.
</p>
</div>

</div>

</div>
</section>

<section class="section">
<div class="container">

<div class="section-title">
<h2>What can you find here?</h2>
<p>Use the repository to explore structured plant information.</p>
</div>

<div class="info-grid">

<div class="info-card">
<h3>Plant Directory</h3>
<p>Search and filter medicinal plants by name, botanical family, plant part and constituents.</p>
</div>

<div class="info-card">
<h3>Plant Details</h3>
<p>View botanical identity, biological source, phytochemistry, traditional uses and references.</p>
</div>

<div class="info-card">
<h3>Phytochemistry</h3>
<p>Explore selected plants and their major phytochemical classes.</p>
</div>

<div class="info-card">
<h3>Scientific References</h3>
<p>Open external botanical references for further academic reading.</p>
</div>

</div>

</div>
</section>

<section class="section">
<div class="container">

<div class="disclaimer">
<h3>Educational Disclaimer</h3>
<p>
HerbaDex is for educational and informational purposes only.
It does not provide diagnosis, treatment, dosage recommendations
or personalized medical advice. Always consult a qualified
healthcare professional for medical decisions.
</p>
</div>

</div>
</section>
"""

    return page(
        "Home",
        content,
        "HerbaDex Indian medicinal plants and herbal knowledge repository."
    )


# ============================================================
# PLANTS
# ============================================================

@app.route("/plants")
def plants():

    search = request.args.get("search", "").strip()
    family = request.args.get("family", "").strip()
    part = request.args.get("part", "").strip()

    conn = get_db()

    query = "SELECT * FROM plants WHERE 1=1"
    params = []

    if search:
        query += """
        AND (
            common_name LIKE ?
            OR scientific_name LIKE ?
            OR family LIKE ?
            OR active_constituents LIKE ?
            OR phytochemicals LIKE ?
        )
        """

        term = f"%{search}%"
        params.extend([term, term, term, term, term])

    if family:
        query += " AND family = ?"
        params.append(family)

    if part:
        query += " AND plant_part LIKE ?"
        params.append(f"%{part}%")

    query += " ORDER BY common_name"

    rows = conn.execute(query, params).fetchall()

    families = conn.execute(
        "SELECT DISTINCT family FROM plants ORDER BY family"
    ).fetchall()

    parts = conn.execute(
        "SELECT DISTINCT plant_part FROM plants ORDER BY plant_part"
    ).fetchall()

    conn.close()

    cards = ""

    for plant in rows:
        cards += f"""
        <article class="plant-card">

            <img
                src="{plant['image_url']}"
                alt="{plant['common_name']} medicinal plant"
                onerror="this.style.display='none';"
            >

            <div class="plant-body">

                <h3>{plant['common_name']}</h3>

                <p class="scientific">
                    {plant['scientific_name']}
                </p>

                <span class="family">
                    {plant['family']}
                </span>

                <p style="margin-top:12px;color:#65756c;">
                    {plant['description'][:150]}...
                </p>

                <a
                    href="/plant/{plant['id']}"
                    class="btn btn-primary"
                    style="margin-left:0;margin-top:15px;"
                >
                    View Details
                </a>

            </div>

        </article>
        """

    if not cards:
        cards = """
        <div class="empty">
            <h3>No plants found</h3>
            <p>Try another plant name, family or constituent.</p>
        </div>
        """

    family_options = '<option value="">All Families</option>'

    for f in families:
        selected = "selected" if f["family"] == family else ""
        family_options += f"""
        <option value="{f['family']}" {selected}>
            {f['family']}
        </option>
        """

    part_options = '<option value="">All Plant Parts</option>'

    for p in parts:
        selected = "selected" if p["plant_part"] == part else ""
        part_options += f"""
        <option value="{p['plant_part']}" {selected}>
            {p['plant_part']}
        </option>
        """

    content = f"""
<section class="page-head">
<div class="container">
<h1>Plant Directory</h1>
<p>
Explore medicinal plants using search and filters.
</p>
</div>
</section>

<section class="section">
<div class="container">

<div class="search-box">

<form method="GET" action="/plants">

<div class="search-row">

<input
    type="text"
    name="search"
    value="{search}"
    placeholder="Search plant, scientific name, family or constituent..."
>

<select name="family">
{family_options}
</select>

<select name="part">
{part_options}
</select>

<button class="search-btn" type="submit">
Search
</button>

</div>

</form>

</div>

<p style="margin-bottom:20px;color:#65756c;">
Showing {len(rows)} plant(s)
</p>

<div class="plant-grid">
{cards}
</div>

</div>
</section>
"""

    return page(
        "Plant Directory",
        content,
        "Search Indian medicinal plants by botanical name, family and phytochemical constituents."
    )


# ============================================================
# PLANT DETAIL
# ============================================================

@app.route("/plant/<int:plant_id>")
def plant_detail(plant_id):

    conn = get_db()

    plant = conn.execute(
        "SELECT * FROM plants WHERE id = ?",
        (plant_id,)
    ).fetchone()

    conn.close()

    if plant is None:
        abort(404)

    content = f"""
<section class="detail">

<div class="container">

<div class="detail-grid">

<div>
<img
    class="detail-image"
    src="{plant['image_url']}"
    alt="{plant['common_name']} medicinal plant"
    onerror="this.style.display='none';"
>
</div>

<div class="detail-content">

<h1>{plant['common_name']}</h1>

<h2>{plant['scientific_name']}</h2>

<div class="data-list">

<div class="data-item">
<strong>Botanical Family</strong>
{plant['family']}
</div>

<div class="data-item">
<strong>Biological Source</strong>
{plant['biological_source']}
</div>

<div class="data-item">
<strong>Plant Part Used</strong>
{plant['plant_part']}
</div>

<div class="data-item">
<strong>Active Constituents</strong>
{plant['active_constituents']}
</div>

<div class="data-item">
<strong>Phytochemical Profile</strong>
{plant['phytochemicals']}
</div>

<div class="data-item">
<strong>Traditional / Reported Uses</strong>
{plant['traditional_uses']}
</div>

<div class="data-item">
<strong>Description</strong>
{plant['description']}
</div>

</div>

<br>

<a
    href="{plant['reference_url']}"
    target="_blank"
    rel="noopener noreferrer"
    class="btn btn-primary"
>
View Scientific Reference
</a>

<a
    href="/plants"
    class="btn btn-outline"
>
Back to Directory
</a>

<div class="disclaimer">
<h3>Safety / Educational Note</h3>
<p>{plant['safety_note']}</p>
</div>

</div>

</div>

</div>
</section>
"""

    return page(
        plant["common_name"],
        content,
        f"{plant['common_name']} - {plant['scientific_name']} medicinal plant information."
    )


# ============================================================
# PHYTOCHEMISTRY
# ============================================================

@app.route("/phytochemistry")
def phytochemistry():

    conn = get_db()

    plants = conn.execute(
        """
        SELECT common_name,
               scientific_name,
               active_constituents,
               phytochemicals
        FROM plants
        ORDER BY common_name
        """
    ).fetchall()

    conn.close()

    rows = ""

    for p in plants:
        rows += f"""
        <tr>
            <td><strong>{p['common_name']}</strong></td>
            <td><i>{p['scientific_name']}</i></td>
            <td>{p['active_constituents']}</td>
            <td>{p['phytochemicals']}</td>
        </tr>
        """

    content = f"""
<section class="page-head">
<div class="container">
<h1>Phytochemistry</h1>
<p>
Explore major constituents and broad phytochemical classes associated
with the plants in the HerbaDex repository.
</p>
</div>
</section>

<section class="section">
<div class="container">

<div class="search-box">
<input
    id="phytoSearch"
    type="text"
    placeholder="Search phytochemical, plant or constituent..."
>
</div>

<div class="table-wrap">

<table id="phytoTable">

<thead>
<tr>
<th>Plant</th>
<th>Scientific Name</th>
<th>Active Constituents</th>
<th>Phytochemical Profile</th>
</tr>
</thead>

<tbody>
{rows}
</tbody>

</table>

</div>

</div>
</section>

<script>
document.getElementById("phytoSearch").addEventListener("keyup", function() {{

    const value = this.value.toLowerCase();

    document.querySelectorAll("#phytoTable tbody tr").forEach(function(row) {{

        row.style.display =
            row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";

    }});
}});
</script>
"""

    return page(
        "Phytochemistry",
        content,
        "Phytochemical constituents of selected medicinal plants."
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    content = """
<section class="page-head">
<div class="container">
<h1>About HerbaDex</h1>
<p>
An academic prototype for studying medicinal plants through
pharmacognosy and phytochemistry.
</p>
</div>
</section>

<section class="section">
<div class="container">

<div class="info-grid">

<div class="info-card">
<h3>What is HerbaDex?</h3>
<p>
HerbaDex is a digital medicinal-plant repository created as an
academic prototype. It organizes botanical identity, biological
source, plant parts, constituents, phytochemical information and
references in one searchable interface.
</p>
</div>

<div class="info-card">
<h3>Why was it created?</h3>
<p>
Students often have information distributed across textbooks,
notes and online resources. HerbaDex demonstrates how structured
digital information can make academic exploration easier.
</p>
</div>

<div class="info-card">
<h3>Who can use it?</h3>
<p>
Students, teachers, researchers and general learners can use the
repository as an educational starting point for learning about
medicinal plants.
</p>
</div>

<div class="info-card">
<h3>Academic Scope</h3>
<p>
The project connects pharmacognosy, botanical identification,
phytochemistry, structured databases, web development and
information retrieval.
</p>
</div>

</div>

<div class="disclaimer">
<h3>Important Educational Disclaimer</h3>
<p>
This website is for educational and informational purposes only.
It does not provide diagnosis, treatment, dosage recommendations,
or personalized medical advice. Information about traditional
uses should not be interpreted as proof that a plant can treat
a disease. Consult qualified healthcare professionals for
medical decisions.
</p>
</div>

</div>
</section>
"""

    return page("About", content)


# ============================================================
# REFERENCES
# ============================================================

@app.route("/references")
def references():

    conn = get_db()

    plants = conn.execute(
        """
        SELECT common_name,
               scientific_name,
               reference_url
        FROM plants
        ORDER BY common_name
        """
    ).fetchall()

    conn.close()

    references_html = ""

    for p in plants:
        references_html += f"""
        <div class="reference">
            <h3>{p['common_name']}</h3>
            <p><i>{p['scientific_name']}</i></p>
            <a
                href="{p['reference_url']}"
                target="_blank"
                rel="noopener noreferrer"
            >
                View botanical reference →
            </a>
        </div>
        """

    content = f"""
<section class="page-head">
<div class="container">
<h1>References</h1>
<p>
External botanical references used as starting points for
plant identification and academic verification.
</p>
</div>
</section>

<section class="section">
<div class="container">

<div class="reference-list">
{references_html}
</div>

<div class="disclaimer">
<h3>Reference note</h3>
<p>
External websites may update their content or URLs. Always verify
scientific information using current authoritative sources before
using it in academic or professional work.
</p>
</div>

</div>
</section>
"""

    return page("References", content)


# ============================================================
# ROBOTS.TXT
# ============================================================

@app.route("/robots.txt")
def robots():
    return f"""User-agent: *
Allow: /

Sitemap: {url_for('sitemap', _external=True)}
"""


# ============================================================
# SITEMAP
# ============================================================

@app.route("/sitemap.xml")
def sitemap():

    conn = get_db()
    plants = conn.execute("SELECT id FROM plants").fetchall()
    conn.close()

    urls = [
        url_for("home", _external=True),
        url_for("plants", _external=True),
        url_for("phytochemistry", _external=True),
        url_for("about", _external=True),
        url_for("references", _external=True)
    ]

    for plant in plants:
        urls.append(
            url_for(
                "plant_detail",
                plant_id=plant["id"],
                _external=True
            )
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

    for item in urls:
        xml += f"<url><loc>{item}</loc></url>"

    xml += "</urlset>"

    return xml, 200, {"Content-Type": "application/xml"}


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def not_found(error):

    content = """
<section class="section">
<div class="container">

<div class="empty">

<h1>404</h1>

<h2>Page not found</h2>

<p>
The page you are looking for does not exist.
</p>

<br>

<a href="/" class="btn btn-primary">
Go Home
</a>

</div>

</div>
</section>
"""

    return page("Page Not Found", content), 404


# ============================================================
# START APPLICATION
# ============================================================

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)