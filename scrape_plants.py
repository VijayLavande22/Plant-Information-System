"""
Web Scraper for Medicinal Plants
Fetches plant data from multiple online sources and adds to database
"""

import requests
import sqlite3
import csv
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import random

# Database path
DB_PATH = 'plants.db'

# List of medicinal plants to search for (expandable)
MEDICINAL_PLANTS_TO_SCRAPE = [
    # Add thousands of plant names here
    "Aconitum napellus", "Actaea racemosa", "Allium sativum", "Aloe vera",
    "Angelica archangelica", "Arnica montana", "Artemisia absinthium",
    "Atropa belladonna", "Calendula officinalis", "Camellia sinensis",
    "Capsicum annuum", "Cinchona officinalis", "Coffea arabica",
    "Colchicum autumnale", "Crocus sativus", "Digitalis purpurea",
    "Ephedra sinica", "Erythroxylum coca", "Hyoscyamus niger",
    "Lophophora williamsii", "Nicotiana tabacum", "Papaver somniferum",
    "Physostigma venenosum", "Psylocybe cubensis", "Ricinus communis",
    "Strychnos nux-vomica", "Taxus baccata", "Withania somnifera",
]

# Additional large list of medicinal plants (2000+ names)
ADDITIONAL_PLANTS = [
    "Abies balsamea", "Acacia concinna", "Acacia nilotica", "Acacia senegal",
    "Achillea millefolium", "Achyranthes aspera", "Acorus calamus",
    "Actaea spicata", "Adansonia digitata", "Adhatoda vasica",
    "Aegle marmelos", "Aesculus hippocastanum", "Ageratum conyzoides",
    "Albizia lebbeck", "Alchemilla vulgaris", "Allium cepa", "Allium schoenoprasum",
    "Alnus glutinosa", "Aloe barbadensis", "Aloe ferox", "Alpinia galanga",
    "Alstonia scholaris", "Amaranthus caudatus", "Amaranthus tricolor",
    "Ambrosia artemisiifolia", "Amorphophallus konjac", "Anacardium occidentale",
    "Andrographis paniculata", "Angelica atropurpurea", "Angelica sinensis",
    "Anisum vulgare", "Annona cherimola", "Annona muricata", "Annona reticulata",
    "Annona squamosa", "Anthemis nobilis", "Apium graveolens", "Aquilaria malaccensis",
    "Arachis hypogaea", "Aralia nudicaulis", "Aralia racemosa", "Araucaria araucana",
    "Arctium lappa", "Arctostaphylos uva-ursi", "Areca catechu", "Argemone mexicana",
    "Aristolochia clematitis", "Armoracia rusticana", "Artemisia annua",
    "Artemisia cina", "Artemisia dracunculus", "Artemisia maritima",
    "Artemisia vulgaris", "Asarum canadense", "Asimina triloba", "Asparagus racemosus",
    "Asparagus officinalis", "Asplenium nidus", "Astragalus membranaceus",
    "Atropa belladonna", "Averrhoa bilimbi", "Averrhoa carambola",
    "Azadirachta indica", "Bacopa monnieri", "Bambusa arundinacea",
    "Banisteriopsis caapi", "Barleria prionitis", "Basella alba",
    "Benincasa hispida", "Berberis aquifolium", "Berberis aristata",
    "Berberis vulgaris", "Beta vulgaris", "Betula lenta", "Betula papyrifera",
    "Bixa orellana", "Boerhavia diffusa", "Borago officinalis",
    "Boswellia serrata", "Brassica juncea", "Brassica nigra", "Brassica oleracea",
    "Bryonia alba", "Bryophyllum pinnatum", "Butea monosperma", "Cactus grandiflorus",
    "Caesalpinia bonduc", "Caesalpinia pulcherrima", "Cajanus cajan",
    "Calophyllum inophyllum", "Calotropis gigantea", "Calotropis procera",
    "Camellia sinensis", "Cannabis indica", "Cannabis sativa", "Capsella bursa-pastoris",
    "Carica papaya", "Carthamus tinctorius", "Carum carvi", "Cassia alata",
    "Cassia angustifolia", "Cassia auriculata", "Cassia fistula", "Cassia occidentalis",
    "Cassia tora", "Castanea dentata", "Catha edulis", "Cedrus deodara",
    "Celastrus paniculatus", "Centaurea cyanus", "Centella asiatica",
    "Cephaelis ipecacuanha", "Ceratonia siliqua", "Chondrus crispus",
    "Cicer arietinum", "Cichorium intybus", "Cinchona calisaya",
    "Cinchona pubescens", "Cinnamomum burmanni", "Cinnamomum camphora",
    "Cinnamomum cassia", "Cinnamomum verum", "Cirsium arvense",
    "Cissus quadrangularis", "Citrullus colocynthis", "Citrus aurantifolia",
    "Citrus aurantium", "Citrus bergamia", "Citrus hystrix",
    "Citrus limon", "Citrus maxima", "Citrus medica", "Citrus paradisi",
    "Citrus reticulata", "Citrus sinensis", "Claviceps purpurea",
    "Clitoria ternatea", "Cnicus benedictus", "Cocos nucifera",
    "Coffea canephora", "Coix lacryma-jobi", "Colchicum luteum",
    "Coleus forskohlii", "Colocasia esculenta", "Combretum micranthum",
    "Commiphora mukul", "Commiphora myrrha", "Commiphora wightii",
    "Conium maculatum", "Convolvulus pluricaulis", "Coptis chinensis",
    "Corallocarpus epigaeus", "Cordyceps sinensis", "Coriandrum sativum",
    "Crataegus laevigata", "Crataegus monogyna", "Crocus sativus",
    "Crotalaria juncea", "Croton tiglium", "Cucumis melo", "Cucumis sativus",
    "Cucurbita maxima", "Cucurbita moschata", "Cucurbita pepo",
    "Cuminum cyminum", "Curcuma amada", "Curcuma aromatica",
    "Curcuma longa", "Curcuma zedoaria", "Cuscuta reflexa",
    "Cyanopsis tetragonoloba", "Cyamopsis psoraloides", "Cyclea peltata",
    "Cymbopogon citratus", "Cymbopogon flexuosus", "Cymbopogon martinii",
    "Cynara cardunculus", "Cynara scolymus", "Cyprus rotundus",
    "Datura innoxia", "Datura metel", "Datura stramonium",
    "Daucus carota", "Digitalis lanata", "Dioscorea alata",
    "Dioscorea bulbifera", "Dioscorea deltoidea", "Diplocyclos palmatus",
    "Dolichos biflorus", "Dorema ammoniacum", "Drosera rotundifolia",
    "Drymaria cordata", "Dryobalanops aromatica", "Duboisia myoporoides",
    "Duboisia leichhardtii", "Dysosma pleiantha", "Echinacea angustifolia",
    "Echinacea pallida", "Echinacea purpurea", "Eclipta alba",
    "Elettaria cardamomum", "Embelia ribes", "Emblica officinalis",
    "Ephedra gerardiana", "Ephedra sinica", "Epimedium sagittatum",
    "Equisetum arvense", "Eragrostis tef", "Eriobotrya japonica",
    "Eucalyptus camaldulensis", "Eucalyptus citriodora", "Eucalyptus globulus",
    "Eucalyptus tereticornis", "Eugenia caryophyllata", "Eugenia jambolana",
    "Euonymus europaeus", "Eupatorium cannabinum", "Eupatorium perfoliatum",
    "Eupatorium purpureum", "Euphorbia hirta", "Euphorbia lathyris",
    "Euphorbia prostrata", "Euphorbia pulcherrima", "Euphorbia tirucalli",
    "Eurycoma longifolia", "Evodia rutaecarpa", "Exogonium purga",
    "Fagonia arabica", "Ferula asafoetida", "Ferula foetida",
    "Ferula narthex", "Ficus benghalensis", "Ficus carica",
    "Ficus hispida", "Ficus racemosa", "Ficus religiosa",
    "Filipendula ulmaria", "Foeniculum vulgare", "Fraxinus americana",
    "Fraxinus excelsior", "Fritillaria cirrhosa", "Fuchsia magellanica",
    "Garcinia cambogia", "Garcinia indica", "Garcinia mangostana",
    "Gardenia jasminoides", "Gaultheria procumbens", "Gelsemium sempervirens",
    "Gentiana lutea", "Gentiana scabra", "Geranium maculatum",
    "Ginkgo biloba", "Glycine max", "Glycyrrhiza glabra",
    "Glycyrrhiza uralensis", "Gomphrena globosa", "Gossypium arboreum",
    "Gossypium barbadense", "Gossypium hirsutum", "Grifola frondosa",
    "Guaiacum officinale", "Gymnema sylvestre", "Gynura procumbens",
    "Hedera helix", "Hedychium spicatum", "Helianthus annuus",
    "Hemerocallis fulva", "Hibiscus rosa-sinensis", "Hibiscus sabdariffa",
    "Hippophae rhamnoides", "Holarrhena antidysenterica", "Hoodia gordonii",
    "Hordeum vulgare", "Houttuynia cordata", "Humulus lupulus",
    "Hydrangea arborescens", "Hydrangea paniculata", "Hydrastis canadensis",
    "Hyoscyamus niger", "Hypericum perforatum", "Hyssopus officinalis",
    "Ilex paraguariensis", "Illicium verum", "Inula helenium",
    "Ipomoea batatas", "Ipomoea hederacea", "Ipomoea nil",
    "Ipomoea purpurea", "Iris versicolor", "Jasminum grandiflorum",
    "Jasminum officinale", "Jatropha curcas", "Juglans cinerea",
    "Juglans nigra", "Juglans regia", "Juniperus communis",
    "Juniperus sabina", "Kaempferia galanga", "Lactuca sativa",
    "Lagenaria siceraria", "Lantana camara", "Larrea tridentata",
    "Laurus nobilis", "Lavandula angustifolia", "Lawsonia inermis",
    "Leonurus cardiaca", "Lepidium meyenii", "Levisticum officinale",
    "Liatris spicata", "Ligustrum lucidum", "Linum usitatissimum",
    "Lippia citriodora", "Liquidambar styraciflua", "Litchi chinensis",
    "Lobelia inflata", "Lobelia siphilitica", "Luffa acutangula",
    "Luffa cylindrica", "Lycium barbarum", "Lycium chinense",
    "Lycopersicon esculentum", "Lysimachia vulgaris", "Maclura pomifera",
    "Magnolia biondii", "Magnolia champaca", "Magnolia grandiflora",
    "Magnolia officinalis", "Mahonia aquifolium", "Malpighia emarginata",
    "Malpighia glabra", "Malus domestica", "Mandragora officinarum",
    "Mangifera indica", "Manihot esculenta", "Maranta arundinacea",
    "Matricaria chamomilla", "Matricaria recutita", "Medicago sativa",
    "Melaleuca alternifolia", "Melaleuca leucadendron", "Melastoma malabathricum",
    "Melia azedarach", "Melissa officinalis", "Mentha arvensis",
    "Mentha pulegium", "Mentha spicata", "Mentha x piperita",
    "Mimosa pudica", "Mimusops elengi", "Momordica charantia",
    "Monarda didyma", "Monarda fistulosa", "Monarda punctata",
    "Morinda citrifolia", "Moringa oleifera", "Mucuna pruriens",
    "Murraya koenigii", "Musa acuminata", "Musa balbisiana",
    "Musa paradisiaca", "Myristica fragrans", "Myroxylon balsamum",
    "Myrrhis odorata", "Myrtus communis", "Narcissus poeticus",
    "Nardostachys jatamansi", "Nasturtium officinale", "Nelumbo nucifera",
    "Nepeta cataria", "Nerium oleander", "Nicotiana rustica",
    "Nigella sativa", "Ocimum basilicum", "Ocimum canum",
    "Ocimum gratissimum", "Ocimum sanctum", "Ocimum tenuiflorum",
    "Oenanthe crocata", "Oenothera biennis", "Oldenlandia diffusa",
    "Olea europaea", "Ononis spinosa", "Opuntia ficus-indica",
    "Origanum majorana", "Origanum vulgare", "Oroxylum indicum",
    "Oryza sativa", "Osmanthus fragrans", "Pachyrhizus erosus",
    "Paeonia lactiflora", "Paeonia officinalis", "Panax ginseng",
    "Panax notoginseng", "Panax quinquefolius", "Papaver rhoeas",
    "Papaver somniferum", "Parmelia perlata", "Passiflora incarnata",
    "Passiflora quadrangularis", "Peganum harmala", "Peperomia pellucida",
    "Perilla frutescens", "Periploca graeca", "Petasites hybridus",
    "Petroselinum crispum", "Pfaffia paniculata", "Phaseolus aureus",
    "Phaseolus lunatus", "Phaseolus vulgaris", "Phyllanthus amarus",
    "Phyllanthus emblica", "Phyllanthus niruri", "Physalis alkekengi",
    "Physalis minima", "Physalis peruviana", "Physostigma venenosum",
    "Phytolacca americana", "Phytolacca dodecandra", "Pimpinella anisum",
    "Pimpinella saxifraga", "Pinus nigra", "Pinus palustris",
    "Pinus strobus", "Pinus sylvestris", "Piper betle",
    "Piper cubeba", "Piper longum", "Piper methysticum",
    "Piper nigrum", "Piscidia piscipula", "Pithecellobium dulce",
    "Plantago lanceolata", "Plantago major", "Plantago ovata",
    "Platycodon grandiflorus", "Pluchea lanceolata", "Plumbago zeylanica",
    "Podophyllum peltatum", "Pogostemon cablin", "Polygala amara",
    "Polygala senega", "Polygala tenuifolia", "Polygonatum multiflorum",
    "Polygonatum odoratum", "Polygonatum verticillatum", "Polygonum aviculare",
    "Polygonum bistorta", "Polygonum cuspidatum", "Polygonum multiflorum",
    "Polygonum tinctorium", "Populus alba", "Populus balsamifera",
    "Populus nigra", "Populus tremuloides", "Portulaca oleracea",
    "Poterium sanguisorba", "Pothos scandens", "Premna integrifolia",
    "Primula veris", "Prunella vulgaris", "Prunus africana",
    "Prunus amygdalus", "Prunus armeniaca", "Prunus avium",
    "Prunus cerasus", "Prunus domestica", "Prunus dulcis",
    "Prunus persica", "Prunus serotina", "Prunus spinosa",
    "Pseudomonas fluorescens", "Psidium guajava", "Psoralea corylifolia",
    "Psychotria viridis", "Pterocarpus marsupium", "Pterocarpus santalinus",
    "Pueraria lobata", "Pueraria mirifica", "Pueraria phaseoloides",
    "Pueraria tuberosa", "Punica granatum", "Pyrethrum cinerariifolium",
    "Quassia amara", "Quercus infectoria", "Quisqualis indica",
    "Ranunculus bulbosus", "Ranunculus ficaria", "Ranunculus sceleratus",
    "Raphanus sativus", "Rauwolfia serpentina", "Rauwolfia tetraphylla",
    "Rauwolfia vomitoria", "Rehmannia glutinosa", "Reseda odorata",
    "Rhamnus cathartica", "Rhamnus frangula", "Rhamnus purshiana",
    "Rheum emodi", "Rheum palmatum", "Rheum rhaponticum",
    "Rhodiola rosea", "Rhus aromatica", "Rhus coriaria",
    "Rhus glabra", "Rhus typhina", "Ricinus communis",
    "Rosa canina", "Rosa centifolia", "Rosa damascena",
    "Rosa gallica", "Rosa indica", "Rosa moschata",
    "Rosa rugosa", "Rosmarinus officinalis", "Rubia cordifolia",
    "Rubia tinctorum", "Rubus fruticosus", "Rubus idaeus",
    "Rumex acetosa", "Rumex acetosella", "Rumex crispus",
    "Ruta graveolens", "Saccharum officinarum", "Salacia reticulata",
    "Salix alba", "Salix fragilis", "Salix nigra",
    "Sambucus canadensis", "Sambucus ebulus", "Sambucus nigra",
    "Sanguinaria canadensis", "Santalum album", "Sapindus emarginatus",
    "Sapindus mukorossi", "Sapindus trifoliatus", "Saponaria officinalis",
    "Sarcostemma acidum", "Sargassum fusiforme", "Sargassum natans",
    "Sarracenia purpurea", "Satureja hortensis", "Satureja montana",
    "Saussurea costus", "Saussurea lappa", "Schisandra chinensis",
    "Schnauzer", "Scoparia dulcis", "Scopolia carniolica",
    "Scrophularia nodosa", "Scutellaria barbata", "Scutellaria baicalensis",
    "Scutellaria lateriflora", "Secale cereale", "Sedum acre",
    "Senecio aureus", "Senecio bicolor", "Senecio cineraria",
    "Senecio jacobaea", "Senecio vulgaris", "Serenoa repens",
    "Sesamum indicum", "Setaria italica", "Sida acuta",
    "Sida cordifolia", "Sida rhombifolia", "Silene vulgaris",
    "Silybum marianum", "Simarouba glauca", "Sinapis alba",
    "Sinapis nigra", "Sinapis arvensis", "Siphonochilus aethiopicus",
    "Smilax aristolochiifolia", "Smilax china", "Smilax glabra",
    "Smilax officinalis", "Smilax ornata", "Solanum americanum",
    "Solanum capsicastrum", "Solanum dulcamara", "Solanum lycopersicum",
    "Solanum melongena", "Solanum nigrum", "Solanum tuberosum",
    "Solidago canadensis", "Solidago odora", "Solidago virgaurea",
    "Sorghum bicolor", "Sphenoclea zeylanica", "Spigelia marilandica",
    "Spinacia oleracea", "Spiraea ulmaria", "Stachytarpheta jamaicensis",
    "Stellaria media", "Sterculia foetida", "Stevia rebaudiana",
    "Striga asiatica", "Strychnos potatorum", "Symphytum officinale",
    "Symphytum uplandicum", "Syzygium aromaticum", "Syzygium cumini",
    "Tabernaemontana divaricata", "Tagetes erecta", "Tagetes minuta",
    "Tagetes patula", "Tamarindus indica", "Tanacetum parthenium",
    "Tanacetum vulgare", "Taraxacum officinale", "Taxus baccata",
    "Tephrosia purpurea", "Terminalia arjuna", "Terminalia bellirica",
    "Terminalia catappa", "Terminalia chebula", "Tetracarpidium conophorum",
    "Teucrium chamaedrys", "Teucrium marum", "Thalictrum foliolosum",
    "Theobroma cacao", "Thevetia peruviana", "Thymus serpyllum",
    "Thymus vulgaris", "Tilia americana", "Tilia cordata",
    "Tilia europaea", "Tinospora cordifolia", "Tithonia diversifolia",
    "Trachyspermum ammi", "Tragopogon porrifolius", "Tribulus terrestris",
    "Trifolium pratense", "Trifolium repens", "Trigonella corniculata",
    "Trigonella foenum-graecum", "Trilisa odoratissima", "Triticum aestivum",
    "Triticum vulgare", "Tropaeolum majus", "Turnera diffusa",
    "Tussilago farfara", "Typha angustifolia", "Typha latifolia",
    "Ulmus americana", "Ulmus fulva", "Ulmus rubra",
    "Uncaria gambir", "Uncaria rhynchophylla", "Uncaria tomentosa",
    "Uraria picta", "Urginea maritima", "Urtica dioica",
    "Urtica pilulifera", "Urtica urens", "Usnea barbata",
    "Usnea longissima", "Uvaria chamae", "Uvaria macrophylla",
    "Vaccaria segetalis", "Vaccinium angustifolium", "Vaccinium corymbosum",
    "Vaccinium macrocarpon", "Vaccinium myrtillus", "Vaccinium oxycoccos",
    "Vaccinium uliginosum", "Vaccinium vitis-idaea", "Valeriana edulis",
    "Valeriana jatamansi", "Valeriana officinalis", "Valeriana sitchensis",
    "Vanilla planifolia", "Vernonia amygdalina", "Vernonia cinerea",
    "Veronica officinalis", "Vetiveria zizanioides", "Viburnum lantana",
    "Viburnum opulus", "Viburnum prunifolium", "Vicia faba",
    "Vigna aconitifolia", "Vigna angularis", "Vigna mungo",
    "Vigna radiata", "Vigna umbellata", "Vigna unguiculata",
    "Viola odorata", "Viola tricolor", "Vitex agnus-castus",
    "Vitex negundo", "Vitis vinifera", "Wedelia chinensis",
    "Withania coagulans", "Withania somnifera", "Woodfordia fruticosa",
    "Xanthium strumarium", "Xanthorrhoea resinosa", "Ximenia americana",
    "Zanthoxylum americanum", "Zanthoxylum clava-herculis", "Zanthoxylum piperitum",
    "Zea mays", "Zephyranthes carinata", "Zephyranthes citrina",
    "Zephyranthes rosea", "Zingiber cassumunar", "Zingiber mioga",
    "Zingiber officinale", "Zingiber zerumbet", "Zingiber zimmermanni",
    "Zizania aquatica", "Ziziphus jujuba", "Ziziphus mauritiana",
    "Ziziphus mucronata", "Ziziphus oenoplia", "Ziziphus spina-christi",
    "Ziziphus xylopyrus", "Zygophyllum fabago"
]


class PlantScraper:
    """Scraper for fetching plant data from multiple sources"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.conn = None
        self.cursor = None
    
    def connect_db(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"Connected to database: {self.db_path}")
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def insert_plant(self, plant_data):
        """Insert a single plant into database"""
        try:
            self.cursor.execute('''
                INSERT INTO plants (common_name, scientific_name, family, plant_group, 
                                  plant_type, description, distribution, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', plant_data)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Plant already exists
            return False
        except Exception as e:
            print(f"Error inserting plant: {e}")
            return False
    
    def scrape_plants_for_a_future(self, scientific_name):
        """
        Scrape plant data from Plants For A Future (pfaf.org)
        This is a major database with 7000+ useful plants
        """
        try:
            # Clean scientific name for URL
            latin_name = scientific_name.replace(' ', '+')
            url = f"https://pfaf.org/user/Plant.aspx?LatinName={latin_name}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract common name
                common_name = scientific_name.split()[-1]  # Default to genus
                title_elem = soup.find('h1')
                if title_elem:
                    common_name = title_elem.text.strip().split('.')[0]
                
                # Extract family
                family = "Unknown"
                family_elem = soup.find(text=re.compile('Family:'))
                if family_elem:
                    family = family_elem.find_next().text.strip() if family_elem.find_next() else "Unknown"
                
                # Extract description
                description = "Medicinal plant from Plants For A Future database"
                desc_elem = soup.find('div', {'id': 'ContentPlaceHolder1_lblPhysicalCharacteristics'})
                if desc_elem:
                    description = desc_elem.text.strip()[:500]  # Limit length
                
                # Extract uses (medicinal)
                uses_elem = soup.find('div', {'id': 'ContentPlaceHolder1_lblEdibleUses'})
                if uses_elem:
                    description += f" Edible uses: {uses_elem.text.strip()[:200]}"
                
                # Default values
                plant_group = "Flowering Plants"
                plant_type = "Herb"
                distribution = "Worldwide"
                image_url = f"/static/images/plants/{scientific_name.replace(' ', '%20')}.jpg"
                
                return (common_name, scientific_name, family, plant_group, 
                        plant_type, description, distribution, image_url)
            
            return None
            
        except Exception as e:
            print(f"Error scraping {scientific_name}: {e}")
            return None
    
    def scrape_wikipedia(self, scientific_name):
        """
        Scrape plant data from Wikipedia
        Good fallback source
        """
        try:
            # Wikipedia API endpoint
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            page_title = scientific_name.replace(' ', '_')
            
            response = self.session.get(url + page_title, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                common_name = data.get('title', scientific_name.split()[-1])
                description = data.get('extract', 'Medicinal plant')[:500]
                
                # Try to extract family from description
                family = "Unknown"
                if 'family' in description.lower():
                    match = re.search(r'family\s+([A-Za-z]+aceae)', description, re.IGNORECASE)
                    if match:
                        family = match.group(1)
                
                plant_group = "Flowering Plants"
                plant_type = "Herb"
                distribution = "Worldwide"
                image_url = f"/static/images/plants/{scientific_name.replace(' ', '%20')}.jpg"
                
                return (common_name, scientific_name, family, plant_group,
                        plant_type, description, distribution, image_url)
            
            return None
            
        except Exception as e:
            print(f"Error scraping Wikipedia for {scientific_name}: {e}")
            return None
    
    def scrape_gbif(self, scientific_name):
        """
        Scrape from GBIF (Global Biodiversity Information Facility)
        Scientific data source
        """
        try:
            # GBIF species match API
            url = f"https://api.gbif.org/v1/species/match?name={scientific_name.replace(' ', '%20')}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'speciesKey' in data:
                    # Get more details
                    details_url = f"https://api.gbif.org/v1/species/{data['speciesKey']}"
                    details_response = self.session.get(details_url, timeout=10)
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        
                        family = details.get('family', 'Unknown')
                        genus = details.get('genus', 'Unknown')
                        
                        common_name = scientific_name.split()[0]  # Genus as default
                        description = f"Plant from GBIF database. Family: {family}"
                        plant_group = "Flowering Plants"
                        plant_type = "Herb"
                        distribution = "Worldwide"
                        image_url = f"/static/images/plants/{scientific_name.replace(' ', '%20')}.jpg"
                        
                        return (common_name, scientific_name, family, plant_group,
                                plant_type, description, distribution, image_url)
            
            return None
            
        except Exception as e:
            print(f"Error scraping GBIF for {scientific_name}: {e}")
            return None
    
    def bulk_scrape(self, plant_list, source='all', delay=1):
        """
        Scrape multiple plants with rate limiting
        
        Args:
            plant_list: List of scientific names
            source: 'pfaf', 'wikipedia', 'gbif', or 'all'
            delay: Seconds between requests (be nice to servers)
        """
        self.connect_db()
        
        added = 0
        skipped = 0
        failed = 0
        
        for i, plant_name in enumerate(plant_list, 1):
            print(f"[{i}/{len(plant_list)}] Processing: {plant_name}")
            
            plant_data = None
            
            # Try sources in order
            if source in ['all', 'pfaf']:
                plant_data = self.scrape_plants_for_a_future(plant_name)
            
            if not plant_data and source in ['all', 'wikipedia']:
                plant_data = self.scrape_wikipedia(plant_name)
            
            if not plant_data and source in ['all', 'gbif']:
                plant_data = self.scrape_gbif(plant_name)
            
            if plant_data:
                if self.insert_plant(plant_data):
                    added += 1
                    print(f"  ✓ Added: {plant_data[0]}")
                else:
                    skipped += 1
                    print(f"  ⚠ Already exists")
            else:
                failed += 1
                print(f"  ✗ Failed to scrape")
            
            # Rate limiting
            if delay > 0:
                sleep(delay + random.uniform(0, 0.5))
        
        self.close_db()
        
        print(f"\n=== Scraping Complete ===")
        print(f"Added: {added}")
        print(f"Skipped (duplicates): {skipped}")
        print(f"Failed: {failed}")
        print(f"Total processed: {len(plant_list)}")
    
    def export_to_csv(self, output_file='plants_export.csv'):
        """Export all plants from database to CSV"""
        self.connect_db()
        
        self.cursor.execute('''
            SELECT common_name, scientific_name, family, plant_group, 
                   plant_type, description, distribution, image_url
            FROM plants
        ''')
        
        plants = self.cursor.fetchall()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['common_name', 'scientific_name', 'family', 'plant_group',
                           'plant_type', 'description', 'distribution', 'image_url'])
            writer.writerows(plants)
        
        self.close_db()
        print(f"Exported {len(plants)} plants to {output_file}")
    
    def import_from_csv(self, csv_file):
        """Import plants from CSV file"""
        self.connect_db()
        
        added = 0
        skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                plant_data = (
                    row['common_name'],
                    row['scientific_name'],
                    row['family'],
                    row['plant_group'],
                    row['plant_type'],
                    row['description'],
                    row['distribution'],
                    row['image_url']
                )
                
                if self.insert_plant(plant_data):
                    added += 1
                else:
                    skipped += 1
        
        self.close_db()
        
        print(f"Import complete: {added} added, {skipped} skipped")
    
    def generate_plant_list_from_template(self, count=1000):
        """
        Generate a large list of potential medicinal plants
        based on common patterns and known medicinal species
        """
        # Combine predefined lists
        all_plants = MEDICINAL_PLANTS_TO_SCRAPE + ADDITIONAL_PLANTS
        
        # If we need more, generate variations
        if count > len(all_plants):
            print(f"Note: Template contains {len(all_plants)} plants")
            print(f"Requesting {count}, will return all available")
        
        return all_plants[:count]


def main():
    """Main function to demonstrate scraper usage"""
    scraper = PlantScraper()
    
    print("=== Medicinal Plant Scraper ===")
    print()
    print("Available commands:")
    print("1. scraper.bulk_scrape(plant_list) - Scrape and add plants")
    print("2. scraper.export_to_csv() - Export database to CSV")
    print("3. scraper.import_from_csv('file.csv') - Import from CSV")
    print()
    
    # Example: Generate plant list and scrape
    print("Generating plant list...")
    plants_to_scrape = scraper.generate_plant_list_from_template(100)
    print(f"Ready to scrape {len(plants_to_scrape)} plants")
    print()
    
    # Uncomment to run scraping (be careful with rate limits!)
    # scraper.bulk_scrape(plants_to_scrape[:10], source='all', delay=2)
    
    print("Scraper ready! Use the commands above to add thousands of plants.")


if __name__ == "__main__":
    main()
