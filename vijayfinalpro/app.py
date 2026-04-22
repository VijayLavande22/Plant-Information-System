from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'plants.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with plants table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create plants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL,
            scientific_name TEXT NOT NULL,
            family TEXT,
            plant_group TEXT,
            plant_type TEXT,
            description TEXT,
            distribution TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create plant_families table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_families (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            family_name TEXT NOT NULL UNIQUE,
            common_name TEXT,
            description TEXT,
            characteristics TEXT,
            distribution TEXT,
            economic_importance TEXT,
            medicinal_uses TEXT,
            example_plants TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert plant families data if empty
    cursor.execute('SELECT COUNT(*) FROM plant_families')
    if cursor.fetchone()[0] == 0:
        plant_families = [
            ("Fabaceae", "Legume Family", "Large family of flowering plants including peas, beans, and lentils. Known for nitrogen-fixing abilities.", "Compound leaves, papilionaceous flowers, legume pods, root nodules with nitrogen-fixing bacteria.", "Worldwide, especially tropical and subtropical regions.", "Food (beans, peas, lentils), fodder, green manure, timber, gums, and resins.", "Many species have medicinal properties including antimicrobial, anti-inflammatory, and antioxidant effects.", "Pongamia pinnata, Cassia fistula, Dalbergia, Acacia"),
            ("Poaceae", "Grass Family", "The most economically important plant family including cereals and bamboo.", "Hollow stems (culms), parallel-veined leaves, fibrous root systems, wind-pollinated flowers.", "Worldwide in all climates, dominant in grasslands and savannas.", "Food (rice, wheat, maize, barley), animal fodder, construction (bamboo), biofuel.", "Some grasses have medicinal uses; bamboo has traditional medicinal applications in Asia.", "Bambusa vulgaris, Oryza sativa, Triticum aestivum, Zea mays"),
            ("Rosaceae", "Rose Family", "Diverse family including roses, apples, cherries, and strawberries.", "Flowers with 5 petals, numerous stamens, alternate leaves with stipules, fleshy fruits.", "Temperate regions of Northern Hemisphere, some tropical.", "Fruits (apple, pear, cherry, strawberry), ornamental plants, timber.", "Rich in antioxidants, anti-inflammatory properties, digestive aids, vitamin C sources.", "Rosa rubiginosa, Prunus serrulata, Malus domestica, Fragaria"),
            ("Meliaceae", "Mahogany Family", "Family of tropical trees including neem and mahogany.", "Pinnate leaves, small flowers in panicles, woody capsules or drupes, aromatic wood.", "Tropical and subtropical regions worldwide.", "Timber (mahogany, teak), medicinal plants, insecticides, cosmetics.", "Neem has powerful antimicrobial, antifungal, and antiviral properties; used in traditional medicine.", "Azadirachta indica, Swietenia mahagoni, Melia azedarach"),
            ("Asteraceae", "Daisy Family", "Largest family of flowering plants with over 23,000 species.", "Composite flower heads, alternate leaves, achene fruits, often with pappus for wind dispersal.", "Worldwide, especially diverse in Mediterranean and tropical regions.", "Food (sunflower seeds, lettuce), ornamental, medicinal herbs, oils.", "Many species used medicinally including anti-inflammatory, digestive aids, and immune support.", "Helianthus annuus, Lactuca sativa, Artemisia, Calendula"),
            ("Lamiaceae", "Mint Family", "Aromatic herbs and shrubs including mint, basil, and lavender.", "Square stems, opposite leaves, bilabiate flowers, aromatic oils in glandular trichomes.", "Worldwide, especially in Mediterranean and temperate regions.", "Culinary herbs, essential oils, perfumes, medicinal teas, cosmetics.", "Antimicrobial, calming, digestive aids, respiratory relief, antioxidant properties.", "Ocimum basilicum, Lavandula angustifolia, Mentha, Rosmarinus"),
            ("Malvaceae", "Mallow Family", "Family including hibiscus, cotton, and okra.", "Alternate leaves with stipules, flowers with fused petals, stamens fused into column, mucilaginous sap.", "Tropical and subtropical regions, some temperate.", "Fiber (cotton), food (okra), ornamental (hibiscus), traditional medicine.", "Anti-inflammatory, diuretic, antioxidant, used for skin and hair care.", "Hibiscus rosa-sinensis, Gossypium, Abelmoschus esculentus"),
            ("Sapotaceae", "Sapodilla Family", "Family of tropical trees producing latex and edible fruits.", "Milky latex, alternate simple leaves, flowers in clusters, berry or drupe fruits with large seeds.", "Tropical regions of Americas, Africa, and Asia.", "Fruits (sapodilla, star apple), latex (chicle), timber, oil (shea butter).", "Latex used in traditional medicine, anti-inflammatory, wound healing properties.", "Madhuca longifolia, Mimusops elengi, Manilkara zapota, Vitellaria paradoxa"),
            ("Anacardiaceae", "Cashew Family", "Family including mango, cashew, and poison ivy.", "Resinous or milky sap, alternate leaves, flowers in panicles, drupe fruits.", "Tropical and subtropical regions worldwide.", "Fruits (mango, cashew, pistachio), timber, varnish, medicinal.", "Mango used in Ayurveda, anti-inflammatory, digestive aids, skin treatments.", "Mangifera indica, Anacardium occidentale, Pistacia vera"),
            ("Pinaceae", "Pine Family", "Conifer family including pines, firs, and spruces.", "Evergreen needle-like or linear leaves, woody cones, resinous wood.", "Northern Hemisphere temperate and boreal regions.", "Timber, paper pulp, resin (turpentine, rosin), Christmas trees, edible seeds.", "Pine needles and resin used in traditional medicine, antiseptic, respiratory relief.", "Pinus sylvestris, Abies, Picea, Cedrus"),
            ("Arecaceae", "Palm Family", "Family of palms including coconut, date, and oil palm.", "Unbranched trunk with crown of large compound leaves, flowers in spadices, drupe fruits.", "Tropical and subtropical regions worldwide.", "Food (coconut, dates, palm oil), fiber, construction material, ornamental.", "Coconut has antimicrobial, hydrating, nutritional properties; used extensively in traditional medicine.", "Cocos nucifera, Phoenix dactylifera, Elaeis guineensis"),
            ("Asphodelaceae", "Aloe Family", "Family of succulent plants including aloe and daylilies.", "Succulent leaves in rosettes, tubular flowers, fibrous or fleshy roots.", "Africa, Madagascar, and Arabian Peninsula; introduced worldwide.", "Medicinal (aloe gel), ornamental, fiber, food.", "Aloe vera is extensively used for skin conditions, digestive health, burns, and wounds.", "Aloe barbadensis miller, Aloe vera, Hemerocallis"),
            ("Combretaceae", "Combretum Family", "Family of tropical trees and shrubs including Arjun tree.", "Simple leaves, small flowers in spikes or racemes, winged or ridged fruits.", "Tropical and subtropical regions worldwide.", "Timber, traditional medicine, tannins.", "Arjun bark used in Ayurveda for heart conditions, Terminalia species used extensively.", "Terminalia arjuna, Terminalia chebula, Combretum"),
            ("Nyctaginaceae", "Four O'Clock Family", "Family including bougainvillea and four o'clocks.", "Opposite leaves, flowers surrounded by colorful bracts, no true petals, inferior ovary.", "Tropical and subtropical Americas, some worldwide.", "Ornamental (bougainvillea), some species have edible roots.", "Some species used in traditional medicine for anti-inflammatory and antimicrobial properties.", "Pisonia grandis, Bougainvillea, Mirabilis jalapa"),
            ("Moraceae", "Mulberry Family", "Family including figs, mulberries, and breadfruit.", "Milky latex, alternate leaves, unisexual flowers, compound fruits or syconia.", "Tropical and temperate regions worldwide.", "Fruits (fig, mulberry, jackfruit), fiber, fodder, medicinal.", "Fig and banyan used in traditional medicine, anti-inflammatory, digestive aids.", "Ficus benghalensis, Ficus carica, Morus, Artocarpus"),
            ("Fagaceae", "Beech Family", "Family including oaks, beeches, and chestnuts.", "Simple alternate leaves, male flowers in catkins, nuts enclosed in cupules.", "Temperate and subtropical regions of Northern Hemisphere.", "Timber, nuts (acorns, chestnuts), tannin, food for wildlife.", "Oak bark used for tannins, anti-inflammatory, wound healing.", "Quercus robur, Fagus sylvatica, Castanea sativa"),
        ]
        
        cursor.executemany('''
            INSERT INTO plant_families (family_name, common_name, description, characteristics, 
                distribution, economic_importance, medicinal_uses, example_plants)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', plant_families)
        conn.commit()
        print(f"Inserted {len(plant_families)} plant families")
    
    # Create plant_groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL UNIQUE,
            description TEXT,
            characteristics TEXT,
            distribution TEXT,
            economic_importance TEXT,
            medicinal_uses TEXT,
            example_plants TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert plant groups data if empty
    cursor.execute('SELECT COUNT(*) FROM plant_groups')
    if cursor.fetchone()[0] == 0:
        plant_groups = [
            ("Flowering Plants", "The most diverse group of land plants producing flowers and fruits. Includes trees, shrubs, and herbs.", "Flowers with reproductive structures, enclosed seeds in fruits, broad leaves with net-like veins (dicots) or parallel veins (monocots).", "Worldwide in all terrestrial habitats except extreme deserts and polar regions.", "Food, medicine, timber, ornamentals, fibers, dyes, and industrial products. Major source of human nutrition.", "Extensive medicinal uses across all families including cardiovascular, digestive, respiratory, and antimicrobial applications.", "Rosa rubiginosa, Mangifera indica, Hibiscus rosa-sinensis, Cassia fistula, Ocimum basilicum, Helianthus annuus"),
            ("Grasses", "Economically most important plant group including cereals, bamboo, and pasture grasses.", "Hollow stems called culms, parallel-veined leaves, fibrous roots, wind-pollinated flowers, and caryopsis fruits.", "Worldwide from tropics to arctic, dominant in grasslands, savannas, and cultivated lands.", "Food security (rice, wheat, maize), animal fodder, construction (bamboo), biofuel, paper, and erosion control.", "Some grasses have medicinal properties; bamboo has traditional uses in Asian medicine for cooling and detoxifying.", "Bambusa vulgaris, Oryza sativa, Triticum aestivum, Zea mays, Saccharum officinarum"),
            ("Conifers", "Ancient group of cone-bearing plants including pines, firs, and spruces.", "Needle-like or scale-like evergreen leaves, woody cones, resinous wood, and naked seeds.", "Northern Hemisphere temperate and boreal forests, some in Southern Hemisphere mountains.", "Timber construction, paper pulp, resin products (turpentine, rosin), Christmas trees, and edible pine nuts.", "Pine needles and resin used for respiratory conditions, antiseptic properties, and traditional medicine.", "Pinus sylvestris, Picea abies, Cedrus deodara, Abies balsamea, Taxus baccata"),
            ("Succulents", "Plants adapted to arid conditions with water-storing tissues in leaves, stems, or roots.", "Fleshy tissues for water storage, reduced leaves or spines, CAM photosynthesis, and shallow root systems.", "Arid and semi-arid regions worldwide, especially deserts and dry rocky areas.", "Ornamentals, medicinal uses (aloe), food, and xeriscaping for water-efficient landscaping.", "Aloe vera widely used for skin conditions, burns, digestive health; other succulents have various traditional uses.", "Aloe barbadensis miller, Aloe vera, Echeveria, Crassula, Sedum, Agave"),
            ("Palms", "Distinctive group of tropical plants with unbranched trunks and large compound leaves.", "Unbranched trunk, large pinnate or palmate leaves, spadix inflorescences, and drupe fruits.", "Tropical and subtropical regions worldwide, characteristic of coastal and island ecosystems.", "Food (coconut, dates, palm oil), fiber, construction materials, beverages, and ornamental landscaping.", "Coconut water and oil have antimicrobial, hydrating, and nutritional properties; used extensively in tropical medicine.", "Cocos nucifera, Phoenix dactylifera, Elaeis guineensis, Areca catechu, Borassus flabellifer"),
            ("Ferns", "Ancient group of vascular plants reproducing by spores rather than seeds or flowers.", "Fronds (large divided leaves), sori (spore clusters) on leaf undersides, and rhizomatous stems.", "Moist shady areas worldwide from tropics to temperate regions.", "Ornamentals, food (fiddlehead ferns), soil stabilization, and traditional medicine.", "Some ferns used for parasitic infections, digestive issues, and as diuretics in traditional medicine.", "Pteridium aquilinum, Adiantum, Asplenium, Nephrolepis, Matteuccia struthiopteris"),
            ("Mosses", "Non-vascular plants forming dense green clumps in moist habitats.", "Small size, no true roots/stems/leaves, rhizoids for anchoring, reproduce by spores, require moisture for reproduction.", "Moist environments worldwide, important in forest ecosystems and wetland formation.", "Soil formation, water retention, indicator species for environmental monitoring, and some traditional uses.", "Some mosses used for wound dressing, antimicrobial properties, and in traditional medicine.", "Sphagnum, Polytrichum, Bryum, Mnium, Marchantia"),
        ]
        
        cursor.executemany('''
            INSERT INTO plant_groups (group_name, description, characteristics, 
                distribution, economic_importance, medicinal_uses, example_plants)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', plant_groups)
        conn.commit()
        print(f"Inserted {len(plant_groups)} plant groups")
    
    # Create plant_categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            description TEXT,
            characteristics TEXT,
            distribution TEXT,
            economic_importance TEXT,
            medicinal_uses TEXT,
            example_plants TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert plant categories data if empty
    cursor.execute('SELECT COUNT(*) FROM plant_categories')
    if cursor.fetchone()[0] == 0:
        plant_categories = [
            ("Trees", "Large woody perennial plants with a single trunk or multiple trunks, typically growing over 5 meters tall. The backbone of forest ecosystems.", "Single or multiple woody trunks, perennial growth, secondary growth producing wood and bark, deep root systems, complex branching structure, long lifespan from decades to millennia.", "Every terrestrial ecosystem on Earth except polar regions and extreme deserts. From tropics to boreal forests.", "Timber and wood products, pulp and paper, fruit production, shade and shelter, carbon sequestration, soil conservation, watershed protection, biodiversity support, medicinal compounds.", "Immense medicinal value including bark (willow/aspirin), leaves, roots, and fruits used for treating diseases from cancer to heart conditions, respiratory ailments, and digestive disorders.", "Terminalia arjuna, Azadirachta indica, Mangifera indica, Cocos nucifera, Ficus benghalensis, Quercus robur, Pongamia pinnata, Cassia fistula, Pinus sylvestris, Madhuca longifolia, Mimusops elengi, Pisonia grandis"),
            ("Shrubs", "Multi-stemmed woody plants smaller than trees, typically 0.5 to 5 meters tall. Important for understory vegetation and landscape design.", "Multiple woody stems branching from or near ground level, perennial growth, moderate height, bushy growth habit, flexible branches, often thorny or spiny.", "Widespread in forests, woodlands, grasslands, deserts, and cultivated landscapes worldwide.", "Ornamental landscaping, hedges and boundaries, fruit production (berries), soil stabilization, wildlife habitat, medicinal uses, fuel wood, essential oils.", "Many shrubs have potent medicinal properties including antibacterial, anti-inflammatory, antioxidant, and anticancer compounds used in traditional and modern medicine.", "Hibiscus rosa-sinensis, Rosa rubiginosa, Lantana, Bougainvillea, Duranta, Ixora, Hamelia, Clerodendrum, Jatropha"),
            ("Herbs", "Non-woody plants with soft stems that die back to the ground each year. Include many aromatic and medicinal plants used throughout human history.", "Non-woody soft stems, annual or perennial lifecycle, rapid growth, aromatic oils often present, medicinal compounds concentrated in leaves and stems, fibrous root systems.", "Cultivated worldwide in gardens, farms, and wild in temperate and tropical regions. Essential for agriculture and horticulture.", "Culinary spices and flavorings, medicinal extracts and teas, essential oils and perfumes, natural dyes, pest control, traditional medicine systems (Ayurveda, TCM, Western herbalism).", "Primary source of modern pharmaceuticals and traditional medicines. Used for digestive, respiratory, cardiovascular, nervous system, skin conditions, immune support, pain relief, and countless other ailments.", "Ocimum basilicum, Ocimum tenuiflorum (Tulsi), Mentha, Rosmarinus officinalis, Thymus vulgaris, Petroselinum crispum, Coriandrum sativum, Allium sativum, Zingiber officinale, Curcuma longa, Echinacea, Withania somnifera, Andrographis paniculata, Centella asiatica"),
            ("Climbers", "Plants with weak stems that require support to grow vertically. Essential for vertical gardening and covering structures.", "Weak or flexible stems requiring external support, specialized climbing structures (tendrils, twining stems, adventitious roots, hooks, thorns), rapid vertical growth, often perennial, can reach great heights.", "Tropical rainforests, temperate woodlands, and cultivated gardens worldwide. Critical components of forest ecosystems.", "Ornamental coverage of walls and fences, shade provision, fruit production (grapes, passion fruit), medicinal uses, soil erosion control on slopes, living fences.", "Many climbers have significant medicinal value including cardiac glycosides, antioxidants, anti-inflammatory compounds used for heart conditions, liver health, immune support.", "Piper nigrum, Cissus quadrangularis, Tinospora cordifolia, Cissampelos pareira, Gloriosa superba, Abrus precatorius, Clitoria ternatea, Mucuna pruriens, Passiflora edulis, Vitis vinifera"),
            ("Aquatic Plants", "Plants adapted to living in water environments including freshwater and marine habitats. Critical for aquatic ecosystems.", "Adaptations for submerged or floating life (aerenchymatous tissues, floating leaves, reduced cuticle), specialized root systems for water uptake, often rapid growth, can be submerged, emergent, or floating.", "Ponds, lakes, rivers, marshes, wetlands, and coastal marine environments worldwide.", "Water purification and filtration, habitat for aquatic life, food source, oxygen production, biofuel production, rice cultivation (staple food for billions), ornamental water gardening.", "Many aquatic plants used in traditional medicine for kidney and urinary disorders, detoxification, cooling properties, wound healing, and nutritional supplements.", "Nelumbo nucifera (Lotus), Nymphaea (Water Lily), Eichhornia crassipes (Water Hyacinth), Hydrilla verticillata, Azolla, Trapa natans (Water Chestnut), Oryza sativa (Rice), Marsilea quadrifoliata, Pistia stratiotes, Salvinia"),
            ("Bulbs and Tubers", "Plants with underground storage organs that store nutrients and energy. Important food crops and ornamentals.", "Underground storage organs (bulbs, corms, tubers, rhizomes), perennial lifecycle, dormant periods, contractile roots, vegetative reproduction capability, food storage tissues.", "Temperate and tropical regions worldwide, extensively cultivated for agriculture.", "Major food crops (potatoes, onions, garlic, ginger, turmeric), ornamental flowers (tulips, lilies, daffodils), medicinal uses, industrial starch production.", "Many bulb and tuber crops are staple foods providing carbohydrates. Medicinal uses include antimicrobial (garlic, onion), anti-inflammatory (turmeric, ginger), digestive aids.", "Allium cepa (Onion), Allium sativum (Garlic), Zingiber officinale (Ginger), Curcuma longa (Turmeric), Solanum tuberosum (Potato), Ipomoea batatas (Sweet Potato), Manihot esculenta (Cassava), Colocasia esculenta (Taro), Amorphophallus paeoniifolius, Lilium, Tulipa, Narcissus"),
            ("Cacti and Succulents", "Plants adapted to arid environments with water-storing tissues. Unique forms and often showy flowers.", "Succulent water-storing stems, leaves, or roots, CAM photosynthesis, reduced or absent leaves often modified into spines, shallow but extensive root systems, thick cuticle, often ribbed or columnar growth.", "Native to Americas but cultivated worldwide. Deserts, arid regions, and rocky areas.", "Ornamental plants, xeriscaping (water-wise landscaping), food (fruits, pads), medicinal uses, natural barriers, dye production (cochineal), biofuel potential.", "Aloe vera is extensively used for skin conditions, burns, digestive health. Other succulents used for wound healing, anti-inflammatory, and traditional medicine.", "Aloe vera, Aloe barbadensis, Opuntia ficus-indica (Prickly Pear), Echinocactus, Cereus, Echeveria, Sedum, Kalanchoe pinnata (Bryophyllum), Crassula ovata, Agave americana"),
            ("Creepers and Ground Covers", "Low-growing plants that spread horizontally across the ground. Important for erosion control and lawn alternatives.", "Prostrate growth habit, stems that root at nodes, rapid spreading capability, often form dense mats, low maintenance, drought tolerance in many species.", "Gardens, landscapes, ground cover in forests, lawns, and cultivated areas worldwide.", "Soil erosion control, lawn alternatives, ornamental ground cover, medicinal uses, living mulch, weed suppression, sports turf.", "Many ground covers used in traditional medicine for skin conditions, digestive issues, cooling properties, and as vegetables (purslane, fenugreek).", "Tridax procumbens, Alternanthera sessilis, Portulaca oleracea, Eclipta alba, Centella asiatica, Cynodon dactylon, Desmodium gangeticum, Phyllanthus amarus, Boerhavia diffusa, Tribulus terrestris, Mucuna pruriens"),
            ("Epiphytes", "Plants that grow on other plants without being parasitic. Important components of tropical forest canopies.", "Grow on other plants for support only, specialized roots for attachment and absorption, often have CAM photosynthesis, adapted to catch moisture from air, reduced root systems in soil.", "Primarily tropical and subtropical rainforests, cloud forests. Also temperate forests for some species.", "Ornamental plants (orchids, bromeliads), important for forest ecosystem biodiversity, air quality indicators, traditional medicine sources.", "Many epiphytes used in traditional medicine including orchids for tonics, bromeliads for digestive issues, and various species for antimicrobial, anti-inflammatory properties.", "Vanda, Dendrobium, Cattleya, Phalaenopsis (Orchids), Tillandsia (Air Plants), Bromeliads, Dischidia, Hoya, Platycerium (Staghorn Ferns), Spanish Moss"),
            ("Parasitic Plants", "Plants that derive nutrients from other living plants. Specialized adaptations for obtaining resources from hosts.", "Modified structures for attaching to host plants (haustoria), reduced or absent chlorophyll in some, specialized metabolism for obtaining nutrients from hosts, often reduced leaves.", "Various ecosystems worldwide, particularly in forests and grasslands where host plants are abundant.", "Some have medicinal uses despite toxicity (mistletoe), others are agricultural pests (dodder, witchweed causing crop losses).", "Some parasitic plants have medicinal applications. Mistletoe used in cancer therapy research. Others used in traditional medicine for specific conditions.", "Cuscuta reflexa (Dodder), Viscum album (Mistletoe), Santalum album (Sandalwood - semi-parasitic), Rafflesia, Striga (Witchweed), Orobanche, Balanophora, Epifagus virginiana"),
        ]
        
        cursor.executemany('''
            INSERT INTO plant_categories (category_name, description, characteristics, 
                distribution, economic_importance, medicinal_uses, example_plants)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', plant_categories)
        conn.commit()
        print(f"Inserted {len(plant_categories)} plant categories")
    
    # Create plant_types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT NOT NULL UNIQUE,
            description TEXT,
            characteristics TEXT,
            growth_habits TEXT,
            care_requirements TEXT,
            common_uses TEXT,
            medicinal_uses TEXT,
            example_plants TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert plant types data if empty
    cursor.execute('SELECT COUNT(*) FROM plant_types')
    if cursor.fetchone()[0] == 0:
        plant_types = [
            ("Tree", "Large woody perennial plants with a single trunk or multiple trunks, typically growing over 5 meters tall. The backbone of forest ecosystems and provide numerous ecological services.", "Single or multiple woody trunks, perennial growth, secondary growth producing wood and bark, deep root systems, complex branching structure, long lifespan from decades to millennia.", "Slow to moderate growth rate, seasonal leaf shedding (deciduous) or year-round foliage (evergreen), reproduce via seeds, flowers, or vegetative propagation, can form extensive root networks.", "Require full sun to partial shade, well-drained soil, regular watering during establishment, minimal pruning except for shaping or removing dead branches, fertilization based on species requirements.", "Timber and wood products, shade and shelter, fruit production, ornamental landscaping, windbreaks, carbon sequestration, soil stabilization, wildlife habitat, medicinal compounds from bark, leaves, and fruits.", "Immense medicinal value including bark extracts (willow/aspirin), leaves for respiratory ailments, roots for digestive disorders, fruits for nutritional and therapeutic benefits, used in treating cardiovascular diseases, cancer, diabetes, and infections.", "Terminalia arjuna, Azadirachta indica, Mangifera indica, Cocos nucifera, Ficus benghalensis, Quercus robur, Pongamia pinnata, Cassia fistula, Pinus sylvestris"),
            ("Shrub", "Multi-stemmed woody plants smaller than trees, typically 0.5 to 5 meters tall. Essential for understory vegetation, landscape design, and providing habitat for smaller wildlife.", "Multiple woody stems branching from or near ground level, perennial growth, moderate height, bushy growth habit, flexible branches, often thorny or spiny for protection.", "Moderate growth rate, can be deciduous or evergreen, extensive branching creates dense foliage, reproduce via seeds, cuttings, or layering, respond well to pruning and shaping.", "Prefer well-drained soil, regular watering until established, moderate pruning to maintain shape and encourage flowering, mulching to retain moisture, protection from extreme weather during establishment.", "Ornamental landscaping, hedges and boundaries, fruit production (berries), soil stabilization on slopes, wildlife habitat and food source, medicinal extracts, essential oils, dye production.", "Many shrubs have potent medicinal properties including antibacterial, anti-inflammatory, antioxidant, and anticancer compounds. Used for treating skin conditions, digestive issues, respiratory ailments, and cardiovascular health.", "Hibiscus rosa-sinensis, Rosa rubiginosa, Lantana camara, Bougainvillea, Duranta erecta, Ixora, Hamelia patens, Clerodendrum, Jatropha curcas"),
            ("Herb", "Non-woody plants with soft stems that die back to the ground each year. Include many aromatic and medicinal plants used throughout human history for culinary and therapeutic purposes.", "Non-woody soft stems, annual or perennial lifecycle, rapid growth, aromatic oils often present in glands or ducts, medicinal compounds concentrated in leaves and stems, fibrous root systems.", "Fast growth rate, complete lifecycle within one season (annual) or regrow from roots (perennial), abundant flowering for reproduction, respond well to harvesting by producing more foliage, easily propagated from seeds or cuttings.", "Need well-drained fertile soil, regular watering but not waterlogged, full sun to partial shade depending on species, frequent harvesting encourages bushy growth, organic fertilization preferred, protection from frost for tender species.", "Culinary spices and flavorings, medicinal extracts and teas, essential oils for aromatherapy and perfumes, natural dyes and colorants, pest repellents, ornamental garden plants, companion planting for pest control.", "Primary source of modern pharmaceuticals and traditional medicines. Used for digestive disorders, respiratory conditions, cardiovascular health, nervous system support, skin treatments, immune boosting, pain relief, and countless other ailments.", "Ocimum basilicum, Ocimum tenuiflorum, Mentha species, Rosmarinus officinalis, Thymus vulgaris, Petroselinum crispum, Coriandrum sativum, Allium sativum, Zingiber officinale, Curcuma longa, Withania somnifera"),
            ("Grass", "Herbaceous plants with narrow leaves and hollow stems. Economically vital group including cereals, bamboo, and pasture grasses that form the foundation of many ecosystems.", "Hollow stems called culms, parallel-veined leaves, fibrous root systems, wind-pollinated flowers, caryopsis fruits, rapid growth from base meristems, can regrow after cutting or grazing.", "Very fast growth rate, can be annual or perennial, extensive fibrous root systems prevent soil erosion, reproduce via seeds or vegetative spread through rhizomes or stolons, tolerant of grazing and mowing.", "Minimal care required once established, drought tolerant after root development, prefer full sun, need occasional mowing or grazing to maintain health, benefit from occasional fertilization, some species require containment to prevent spreading.", "Food security (rice, wheat, maize, barley), animal fodder and pasture, construction materials (bamboo), biofuel production, paper and pulp, erosion control, thatching, basket weaving, ornamental lawns.", "Some grasses have medicinal properties including digestive aids, diuretics, and cooling agents. Bamboo has traditional uses in Asian medicine for detoxification and fever reduction. Wheat grass and barley grass used for nutritional supplements.", "Bambusa vulgaris, Oryza sativa, Triticum aestivum, Zea mays, Saccharum officinarum, Hordeum vulgare, Avena sativa, Secale cereale, Bambusa arundinacea"),
            ("Succulent", "Plants adapted to arid conditions with specialized tissues for water storage. Diverse group ranging from tiny living stones to large tree-like forms like cacti and aloes.", "Fleshy tissues for water storage in leaves, stems, or roots, reduced or absent leaves often modified into spines, CAM photosynthesis for water efficiency, thick cuticle to reduce water loss, shallow but extensive root systems.", "Slow to moderate growth rate, extremely drought tolerant, can survive long periods without water, reproduce via seeds, offsets, or leaf/stem cuttings, many produce showy flowers under stress conditions.", "Require minimal watering (only when soil is dry), well-drained sandy or gritty soil, full sun to bright indirect light, protection from frost and freezing temperatures, no fertilization needed or very minimal, avoid water on leaves to prevent rot.", "Ornamental plants for xeriscaping, medicinal uses (aloe vera), food (nopales, dragon fruit), natural barriers and fencing, living fences, dye production (cochineal), biofuel research, air purification.", "Aloe vera extensively used for burns, wounds, skin conditions, digestive health. Other succulents used for anti-inflammatory, antimicrobial, and traditional medicine. Some cacti used for diabetes management.", "Aloe barbadensis, Aloe vera, Opuntia ficus-indica, Echinocactus grusonii, Cereus repandus, Echeveria elegans, Sedum spectabile, Kalanchoe pinnata, Crassula ovata, Agave americana"),
            ("Climber", "Plants with weak stems that require external support to grow vertically. Essential for vertical gardening, covering structures, and maximizing space in gardens.", "Weak or flexible stems, specialized climbing structures (tendrils, twining stems, adventitious roots, hooks, thorns), rapid vertical growth capability, often perennial, can reach great heights by climbing on supports.", "Fast vertical growth rate, can cover large areas quickly, often produce abundant flowers, reproduce via seeds, cuttings, or layering, some form underground tubers or rhizomes, respond well to pruning to control spread.", "Need sturdy support structures (trellises, arbors, walls), well-drained soil, regular watering during establishment, moderate to full sun depending on species, regular pruning to control growth and encourage flowering, protection from strong winds.", "Ornamental coverage of walls and fences, shade provision, fruit production (grapes, passion fruit), privacy screens, soil erosion control on slopes, living fences, medicinal uses, nectar sources for pollinators.", "Many climbers have significant medicinal value including cardiac glycosides (digitalis), antioxidants, anti-inflammatory compounds. Used for heart conditions, liver health, immune support, and as adaptogens.", "Piper nigrum, Cissus quadrangularis, Tinospora cordifolia, Cissampelos pareira, Gloriosa superba, Abrus precatorius, Clitoria ternatea, Mucuna pruriens, Passiflora edulis, Vitis vinifera"),
            ("Fern", "Ancient group of vascular plants reproducing by spores rather than seeds or flowers. Important components of moist ecosystems and popular ornamental plants.", "Fronds (large divided leaves), sori (spore clusters) on leaf undersides, rhizomatous stems, fibrous roots, no flowers or seeds, reproduce via spores, fiddleheads as young growth.", "Moderate growth rate in suitable conditions, spread via underground rhizomes, can form dense colonies, some species are epiphytic, deciduous or evergreen depending on species and climate.", "Require consistently moist but well-drained soil, high humidity, indirect light or shade, protection from direct sunlight, regular watering, mulching to retain moisture, minimal fertilization with organic matter.", "Ornamental plants for shade gardens, food (fiddlehead ferns), soil stabilization in wet areas, traditional medicine, bioindicators for environmental health, companion plants for moisture-loving species.", "Some ferns used for parasitic infections, digestive issues, as diuretics, and for respiratory conditions in traditional medicine. Fiddlehead ferns are nutritious food source rich in vitamins and minerals.", "Pteridium aquilinum, Adiantum capillus-veneris, Asplenium nidus, Nephrolepis exaltata, Matteuccia struthiopteris, Cyathea cooperi, Dicksonia antarctica, Platycerium bifurcatum"),
            ("Palm", "Distinctive group of tropical plants with unbranched trunks and large compound leaves. Iconic symbols of tropical and subtropical regions worldwide.", "Unbranched trunk (usually), large pinnate or palmate leaves (fronds), spadix inflorescences, drupe or berry fruits, fibrous or woody trunk, adventitious root systems.", "Slow to moderate growth rate, evergreen, can live for decades to centuries, reproduce via seeds, some species produce offshoots or suckers, flowering and fruiting can be year-round or seasonal.", "Prefer full sun, well-drained soil, regular watering especially during establishment, benefit from high humidity, protection from frost and freezing temperatures, occasional deep watering, mulching beneficial, minimal pruning except removing dead fronds.", "Food (coconuts, dates, palm oil, heart of palm), fiber for ropes and mats, construction materials, beverages (palm wine, coconut water), ornamental landscaping, wax production, thatching.", "Coconut oil has antimicrobial, antifungal properties. Dates are nutritious with health benefits. Palm heart used for digestive health. Some palms have traditional uses for kidney and urinary issues.", "Cocos nucifera, Phoenix dactylifera, Elaeis guineensis, Areca catechu, Borassus flabellifer, Caryota urens, Licuala grandis, Ravenea rivularis, Washingtonia robusta"),
        ]
        
        cursor.executemany('''
            INSERT INTO plant_types (type_name, description, characteristics, 
                growth_habits, care_requirements, common_uses, medicinal_uses, example_plants)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', plant_types)
        conn.commit()
        print(f"Inserted {len(plant_types)} plant types")
    
    # Create crown_architecture table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crown_architecture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            architecture_name TEXT NOT NULL UNIQUE,
            description TEXT,
            characteristics TEXT,
            growth_pattern TEXT,
            ecological_significance TEXT,
            common_species TEXT,
            management_considerations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert crown architecture data if empty
    cursor.execute('SELECT COUNT(*) FROM crown_architecture')
    if cursor.fetchone()[0] == 0:
        crown_architectures = [
            ("Conical Crown", "A cone-shaped or pyramidal crown with a pointed top and narrow base, typical of conifers and some deciduous trees.", "Tapered, narrow crown that comes to a point at the apex, branches grow at acute angles upward, maximum light interception at the top, efficient snow and rain shedding.", "Central leader dominance with strong apical control, branches arranged in whorls or spirals, vertical growth prioritized over horizontal spread, maintains conical shape throughout life.", "Adapted to cold climates and high altitudes, efficient snow shedding prevents branch breakage, maximizes light capture in dense forests, wind resistance through streamlined shape, provides thermal cover for wildlife.", "Pinus sylvestris (Scots Pine), Picea abies (Norway Spruce), Abies alba (Silver Fir), Cupressus sempervirens (Italian Cypress), Thuja occidentalis (Arborvitae).", "Minimal pruning required, maintain central leader, remove competing leaders early, suitable for windbreaks and privacy screens, watch for snow load damage in heavy snowfall areas, space appropriately for mature height."),
            ("Rounded Crown", "A dome-shaped or spherical crown with a curved outline, broad at the middle and tapering at top and bottom.", "Broad, spreading crown with curved profile, branches extend horizontally then curve upward, maximum crown width at middle height, symmetrical or asymmetrical dome shape, dense foliage distribution throughout crown.", "Diffuse branching pattern without strong apical dominance, branches grow outward and upward, continuous lateral expansion throughout life, crown becomes wider with age, self-pruning of lower branches in dense stands.", "Maximum shade provision for understory plants, excellent for urban shade and cooling, high biodiversity support with multiple canopy layers, soil protection through extensive ground coverage, aesthetically pleasing landscape form.", "Quercus robur (English Oak), Ficus benghalensis (Banyan), Acer platanoides (Norway Maple), Tilia cordata (Small-leaved Lime), Magnolia grandiflora (Southern Magnolia).", "Regular pruning to maintain shape and remove dead wood, crown lifting for clearance beneath, structural pruning for branch strength, manage canopy density for light penetration, monitor for fungal issues in dense crowns."),
            ("Columnar Crown", "A narrow, upright crown with vertical or near-vertical branches forming a cylindrical shape.", "Very narrow crown width relative to height, branches grow upright or at narrow angles, minimal lateral spread, tall and slender silhouette, fastigiate or fastigate branching pattern.", "Strong apical dominance maintained throughout life, minimal lateral branch development, vertical growth significantly exceeds horizontal spread, suitable for confined spaces, maintains narrow profile even at maturity.", "Minimal ground space requirement allows high density planting, effective windbreaks without occupying much space, vertical accent in landscape design, screening without blocking views at lower levels, column effects in formal gardens.", "Populus nigra 'Italica' (Lombardy Poplar), Cupressus sempervirens (Italian Cypress), Carpinus betulus 'Fastigiata' (Upright Hornbeam), Liquidambar styraciflua 'Slender Silhouette', Quercus robur 'Fastigiata'.", "Staking may be needed in youth for straight trunk, minimal lateral pruning required, monitor for top-heaviness and wind damage, ensure adequate root space despite narrow crown, protect from strong winds."),
            ("Weeping Crown", "A crown with pendulous or drooping branches that hang down toward the ground, creating a cascading effect.", "Flexible, pendulous branches that droop downward, branches often touch or sweep the ground, weeping silhouette with branches growing downward rather than upward or outward, graceful cascading form, dense curtain of foliage.", "Weak apical dominance in branches, gravity-responsive branch growth, branches continue to elongate and droop with age, may require support in early years, outer branches root when touching ground in some species.", "Unique aesthetic value in landscape design, excellent specimen or focal point trees, dense shade and privacy at ground level, shelter for ground-dwelling wildlife, dramatic winter silhouette with branching structure visible.", "Salix babylonica (Weeping Willow), Ficus benjamina (Weeping Fig), Prunus subhirtella 'Pendula' (Weeping Cherry), Ulmus glabra 'Camperdownii' (Camperdown Elm), Morus alba 'Pendula' (Weeping Mulberry).", "Prune to maintain desired clearance from ground, remove dead or damaged pendulous branches, may require structural support for main trunk, protect from heavy snow loads that can break branches, regular inspection for branch health."),
            ("Vase-Shaped Crown", "An open, spreading crown with upright branches that arch outward and then curve back up, creating a vase or umbrella-like outline.", "Open center with upward and outward arching branches, vase or goblet silhouette with spreading top, branches curve gracefully upward at tips, central openness allows light penetration, broad crown spread at maturity.", "Multiple leaders or spreading main branches, upward and outward growth pattern, crown widens significantly with age, self-pruning creates open interior, architectural branching structure.", "Excellent street tree form with clearance beneath, allows light penetration to understory, strong branch structure resistant to wind, provides dappled shade rather than dense shade, facilitates pedestrian and vehicle passage beneath.", "Ulmus americana (American Elm), Zelkova serrata (Japanese Zelkova), Prunus serrulata 'Kwanzan' (Kwanzan Cherry), Viburnum prunifolium (Blackhaw), Acacia dealbata (Silver Wattle).", "Structural pruning to establish main scaffold branches, maintain central openness, remove crossing or competing branches, regular inspection for included bark in branch unions, crown reduction may be needed for size control."),
            ("Spreading Crown", "A very broad, flat-topped or umbrella-like crown with horizontal branches extending widely from the trunk.", "Extremely wide crown relative to height, horizontal or near-horizontal main branches, flat-topped or umbrella silhouette, layered branching structure, massive lateral spread, low crown base.", "Horizontal growth prioritized over vertical, dominant lateral branches suppress central leader, broad tiered branching pattern, wide crown expansion throughout life, may exceed height in width.", "Maximum ground coverage and shade provision, ideal for large area shading and cooling, extensive habitat for canopy wildlife, soil erosion prevention through wide coverage, distinctive landscape feature, picnic and gathering areas beneath.", "Ficus benghalensis (Banyan), Albizia sambiran (Silk Tree), Delonix regia (Royal Poinciana), Enterolobium cyclocarpum (Elephant Ear Tree), Samanea saman (Rain Tree), Ficus religiosa (Peepal).", "Extensive space requirements for mature spread, regular monitoring of branch unions for strength, crown lifting may be needed for clearance, protect branches from damage due to low height, structural support for heavy lateral limbs."),
            ("Oval Crown", "An elliptical or egg-shaped crown that is longer than wide, with the widest point above the middle.", "Elongated crown shape, broadest point in upper crown, tapered at both top and bottom, symmetrical or near-symmetrical outline, balanced vertical and horizontal proportions.", "Central leader maintained in youth often lost in maturity, branches grow upward and outward at moderate angles, crown elongates with age, transition from conical to oval shape over time, moderate expansion rate.", "Efficient crown shape for light interception, good wind resistance through streamlined form, versatile landscape use, balanced shade provision, suitable for various urban and suburban settings.", "Quercus palustris (Pin Oak), Carya illinoinensis (Pecan), Juglans nigra (Black Walnut), Populus deltoides (Eastern Cottonwood), Liriodendron tulipifera (Tulip Tree).", "Prune to maintain structural integrity, remove lower branches for clearance if needed, monitor branch angles for included bark issues, crown thinning for wind penetration, appropriate spacing for mature oval spread."),
            ("Irregular Crown", "An asymmetrical or uneven crown without a definite geometric shape, often unique to individual trees.", "Asymmetrical form with uneven branching, no consistent geometric pattern, may have multiple leaders or eccentric growth, one-sided crown development, artistic and unique silhouettes, variable density throughout crown.", "Variable apical dominance, uneven branch distribution, response to environmental factors (light, space, damage), may develop due to competition or disturbance, unique growth patterns, often picturesque or character-filled appearance.", "High visual interest and unique landscape features, wildlife habitat diversity through variable structure, adaptation to challenging growing conditions, often historically or culturally significant specimens, artistic and photographic appeal.", "Salix contorta (Corkscrew Willow), Robinia pseudoacacia 'Twisty Baby', Larix decidua at high altitudes, wind-swept specimens of various species, ancient olive trees, character trees in bonsai and natural settings.", "Minimal pruning to preserve natural character, selective removal of hazardous branches only, celebrate unique form rather than forcing symmetry, structural assessment for safety, appropriate for specimen or accent plantings."),
        ]
        
        cursor.executemany('''
            INSERT INTO crown_architecture (architecture_name, description, characteristics, 
                growth_pattern, ecological_significance, common_species, management_considerations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', crown_architectures)
        conn.commit()
        print(f"Inserted {len(crown_architectures)} crown architectures")
    
    # Insert sample plant data if table is empty
    cursor.execute('SELECT COUNT(*) FROM plants')
    if cursor.fetchone()[0] == 0:
        sample_plants = [
            # Trees
            ("Grand Devil's-Claws", "Pisonia grandis", "Nyctaginaceae", "Flowering Plants", "Tree", 
             "A large tree native to tropical regions with distinctive claw-like structures.", 
             "Tropical Asia, Pacific Islands", "/static/images/plants/Grand Devil's-Claws.jpg"),
            ("Indian Beach Tree", "Pongamia pinnata", "Fabaceae", "Flowering Plants", "Tree",
             "A medium-sized tree with fragrant purple flowers, commonly found along coastlines.",
             "India, Southeast Asia, Australia", "/static/images/plants/Indian Beach Tree.jpg"),
            ("Arjun Tree", "Terminalia arjuna", "Combretaceae", "Flowering Plants", "Tree",
             "Powerful cardiac tonic used in Ayurveda for heart health and blood pressure management.",
             "Indian subcontinent", "/static/images/plants/Arjun Tree.jpg"),
            ("Butter Tree", "Madhuca longifolia", "Sapotaceae", "Flowering Plants", "Tree",
             "A tropical tree known for its edible flowers and oil-rich seeds.",
             "India, Nepal, Sri Lanka", "/static/images/plants/Butter Tree.jpg"),
            ("Bullet Wood", "Mimusops elengi", "Sapotaceae", "Flowering Plants", "Tree",
             "An evergreen tree with fragrant white flowers, often used in traditional medicine.",
             "South Asia, Southeast Asia", "/static/images/plants/Bullet Wood.jpg"),
            ("Banyan Tree", "Ficus benghalensis", "Moraceae", "Flowering Plants", "Tree",
             "National tree of India known for its aerial prop roots and massive canopy.",
             "Indian subcontinent", "/static/images/plants/Banyan Tree.jpg"),
            ("Neem Tree", "Azadirachta indica", "Meliaceae", "Flowering Plants", "Tree",
             "Powerful medicinal tree with antibacterial, antiviral, and antifungal properties. Used for skin diseases, diabetes, and oral health.",
             "Indian subcontinent, Africa", "/static/images/plants/Neem Tree.jpg"),
            ("Golden Shower", "Cassia fistula", "Fabaceae", "Flowering Plants", "Tree",
             "National tree of Thailand with beautiful golden-yellow flower clusters.",
             "South Asia, Southeast Asia", "/static/images/plants/Golden Shower.jpg"),
            ("Cherry Blossom", "Prunus serrulata", "Rosaceae", "Flowering Plants", "Tree",
             "Ornamental cherry tree famous for its beautiful spring flowers.",
             "Japan, Korea, China", "/static/images/plants/Cherry Blossom.jpg"),
            ("Mango Tree", "Mangifera indica", "Anacardiaceae", "Flowering Plants", "Tree",
             "Tropical fruit tree producing the delicious mango fruit.",
             "Indian subcontinent, Southeast Asia", "/static/images/plants/Mango Tree.jpg"),
            ("Coconut Palm", "Cocos nucifera", "Arecaceae", "Palms", "Tree",
             "Tropical palm tree providing coconuts, oil, and fiber. Used for hydration, heart health, and traditional medicine.",
             "Tropical coastlines worldwide", "/static/images/plants/Coconut Palm.webp"),
            ("Amla Tree", "Phyllanthus emblica", "Phyllanthaceae", "Flowering Plants", "Tree",
             "Rich source of Vitamin C, used in Ayurveda for digestion, immunity, hair health, and anti-aging.",
             "India, Nepal, Southeast Asia", "/static/images/plants/amla.jpg"),
            ("Bahera Tree", "Terminalia bellerica", "Combretaceae", "Flowering Plants", "Tree",
             "One of the three fruits in Triphala. Used for digestive health, respiratory issues, and detoxification.",
             "India, Southeast Asia", "/static/images/plants/Bahera Tree.jpg"),
            ("Haritaki Tree", "Terminalia chebula", "Combretaceae", "Flowering Plants", "Tree",
             "King of Medicines in Ayurveda. Used for digestion, detoxification, and overall health.",
             "India, China, Southeast Asia", "/static/images/plants/Haritaki Tree.jpg"),
            ("Tulsi Tree", "Ocimum tenuiflorum", "Lamiaceae", "Flowering Plants", "Tree",
             "Holy Basil - sacred adaptogen for stress, immunity, respiratory health, and longevity.",
             "Indian subcontinent", "/static/images/plants/Tulsi Tree.jpg"),
            ("Ashoka Tree", "Saraca asoca", "Fabaceae", "Flowering Plants", "Tree",
             "Sacred tree used in Ayurveda for women's health, menstrual disorders, and uterine care.",
             "India, Southeast Asia", "/static/images/plants/Ashoka Tree.jpg"),
            ("Bael Tree", "Aegle marmelos", "Rutaceae", "Flowering Plants", "Tree",
             "Sacred tree with fruit used for digestive disorders, diabetes, and respiratory conditions.",
             "India, Southeast Asia", "/static/images/plants/Bael Tree.jpg"),
            ("Papaya Tree", "Carica papaya", "Caricaceae", "Flowering Plants", "Tree",
             "Fruit rich in enzymes for digestion. Leaves used for dengue fever and digestive health.",
             "Central America, Tropical regions", "/static/images/plants/Papaya Tree.jpg"),
            ("Guava Tree", "Psidium guajava", "Myrtaceae", "Flowering Plants", "Tree",
             "Rich in Vitamin C and antioxidants. Leaves used for diarrhea, diabetes, and wound healing.",
             "Central America, Tropical regions", "/static/images/plants/Guava Tree.jpg"),
            ("Jamun Tree", "Syzygium cumini", "Myrtaceae", "Flowering Plants", "Tree",
             "Fruit and seeds used for diabetes management, digestive health, and blood purification.",
             "Indian subcontinent, Southeast Asia", "/static/images/plants/Jamun Tree.jpg"),
            ("Gulmohar Tree", "Delonix regia", "Fabaceae", "Flowering Plants", "Tree",
             "Ornamental tree with beautiful red flowers. Used in traditional medicine for various ailments.",
             "Madagascar, Tropical regions", "/static/images/plants/Gulmohar Tree.jpg"),
            ("Drumstick Tree", "Moringa oleifera", "Moringaceae", "Flowering Plants", "Tree",
             "Moringa superfood with all essential nutrients. Used for malnutrition, diabetes, and inflammation.",
             "India, Africa, Asia", "/static/images/plants/Drumstick Tree.jpg"),
            ("Simarouba Tree", "Simarouba glauca", "Simaroubaceae", "Flowering Plants", "Tree",
             "Bitter tree used for fever, dysentery, and digestive disorders in traditional medicine.",
             "Central America, Caribbean", "/static/images/plants/Simarouba Tree.jpg"),
            ("Teak Tree", "Tectona grandis", "Lamiaceae", "Flowering Plants", "Tree",
             "Hardwood tree with medicinal bark used for skin conditions and as a diuretic.",
             "South Asia, Southeast Asia", "/static/images/plants/Teak Tree.jpg"),
            ("Sandalwood Tree", "Santalum album", "Santalaceae", "Flowering Plants", "Tree",
             "Sacred aromatic wood used for meditation, skin care, and urinary disorders.",
             "India, Southeast Asia", "/static/images/plants/Sandalwood Tree.jpg"),
            ("Eucalyptus Tree", "Eucalyptus globulus", "Myrtaceae", "Flowering Plants", "Tree",
             "Aromatic leaves used for respiratory conditions, congestion, and as an antiseptic.",
             "Australia, Worldwide", "/static/images/plants/Eucalyptus Tree.jpg"),
            
            # Shrubs
            ("Hibiscus", "Hibiscus rosa-sinensis", "Malvaceae", "Flowering Plants", "Shrub",
             "Popular ornamental plant with flowers used for hair health, blood pressure, and skin care.",
             "Tropical Asia", "/static/images/plants/Hibiscus.jpg"),
            ("Rose", "Rosa rubiginosa", "Rosaceae", "Flowering Plants", "Shrub",
             "Classic garden flower with petals used for skin health, stress relief, and digestion.",
             "Worldwide", "/static/images/plants/Rose.jpg"),
            ("Jasmine", "Jasminum officinale", "Oleaceae", "Flowering Plants", "Shrub",
             "Fragrant flowers used for aromatherapy, stress relief, and skin care in Ayurveda.",
             "Tropical Asia, Mediterranean", "/static/images/plants/Jasmine.jpg"),
            ("Marigold", "Tagetes erecta", "Asteraceae", "Flowering Plants", "Shrub",
             "Bright flowers with anti-inflammatory properties. Used for skin conditions and wound healing.",
             "Mexico, Worldwide", "/static/images/plants/Marigold.jpg"),
            ("Night Jasmine", "Nyctanthes arbor-tristis", "Oleaceae", "Flowering Plants", "Shrub",
             "Sacred night-blooming jasmine used for fever, arthritis, and digestive disorders.",
             "India, Southeast Asia", "/static/images/plants/Night Jasmine.jpg"),
            ("Curry Leaf Plant", "Murraya koenigii", "Rutaceae", "Flowering Plants", "Shrub",
             "Aromatic leaves used in cooking and medicine for diabetes, digestion, and hair health.",
             "India, Southeast Asia", "/static/images/plants/Curry Leaf Plant.jpg"),
            ("Lemon", "Citrus limon", "Rutaceae", "Flowering Plants", "Shrub",
             "Rich in Vitamin C. Used for immunity, digestion, detoxification, and skin brightening.",
             "Asia, Worldwide", "/static/images/plants/Lemon.jpg"),
            ("Orange", "Citrus sinensis", "Rutaceae", "Flowering Plants", "Shrub",
             "Fruit rich in Vitamin C and antioxidants. Used for immunity and heart health.",
             "Asia, Worldwide", "/static/images/plants/Orange.jpg"),
            ("Pomegranate", "Punica granatum", "Lythraceae", "Flowering Plants", "Shrub",
             "Superfruit with powerful antioxidants. Used for heart health, cancer prevention, and fertility.",
             "Middle East, India, Mediterranean", "/static/images/plants/Pomegranate.jpg"),
            ("Betel Leaf", "Piper betle", "Piperaceae", "Flowering Plants", "Shrub",
             "Leaves used for oral health, digestion, wound healing, and as a breath freshener.",
             "Southeast Asia, India", "/static/images/plants/Betel Leaf.jpg"),
            ("Black Pepper", "Piper nigrum", "Piperaceae", "Flowering Plants", "Shrub",
             "King of spices with piperine. Used for digestion, metabolism, and nutrient absorption.",
             "India, Southeast Asia", "/static/images/plants/Black Pepper.jpg"),
            ("Long Pepper", "Piper longum", "Piperaceae", "Flowering Plants", "Shrub",
             "Used in Ayurveda for respiratory conditions, digestion, and as a bioenhancer.",
             "India, Southeast Asia", "/static/images/plants/Long Pepper.jpg"),
            ("Cardamom", "Elettaria cardamomum", "Zingiberaceae", "Flowering Plants", "Shrub",
             "Queen of spices. Used for digestion, breath freshening, and detoxification.",
             "India, Southeast Asia", "/static/images/plants/Cardamom.jpg"),
            ("Clove", "Syzygium aromaticum", "Myrtaceae", "Flowering Plants", "Shrub",
             "Powerful antiseptic and analgesic. Used for toothache, digestion, and respiratory issues.",
             "Indonesia, Worldwide", "/static/images/plants/Clove.jpg"),
            ("Cinnamon", "Cinnamomum verum", "Lauraceae", "Flowering Plants", "Tree",
             "Bark used for blood sugar control, heart health, and as a warming digestive aid.",
             "Sri Lanka, Southeast Asia", "/static/images/plants/Cinnamon.jpg"),
            ("Turmeric", "Curcuma longa", "Zingiberaceae", "Flowering Plants", "Herb",
             "Golden spice with curcumin. Powerful anti-inflammatory used for arthritis, skin, and immunity.",
             "India, Southeast Asia", "/static/images/plants/Turmeric.jpg"),
            ("Ginger", "Zingiber officinale", "Zingiberaceae", "Flowering Plants", "Herb",
             "Rhizome used for digestion, nausea, inflammation, and respiratory conditions.",
             "Southeast Asia, India", "/static/images/plants/Ginger.jpg"),
            ("Galangal", "Alpinia galanga", "Zingiberaceae", "Flowering Plants", "Herb",
             "Rhizome used in Southeast Asian medicine for digestion, respiratory issues, and circulation.",
             "Southeast Asia", "/static/images/plants/Galangal.jpg"),
            ("Aloe Vera", "Aloe barbadensis miller", "Asphodelaceae", "Succulents", "Succulent",
             "Medicinal succulent known for its healing gel. Used for burns, skin care, and digestion.",
             "Arabian Peninsula, Worldwide", "/static/images/plants/alowera.jpg"),
            
            # Herbs
            ("Sunflower", "Helianthus annuus", "Asteraceae", "Flowering Plants", "Herb",
             "Seeds rich in Vitamin E and minerals. Used for heart health and as antioxidant.",
             "North America, Worldwide", "/static/images/plants/Sunflower.jpg"),
            ("Ashwagandha", "Withania somnifera", "Solanaceae", "Flowering Plants", "Herb",
             "Powerful adaptogen used for stress, anxiety, energy, and hormonal balance.",
             "India, Middle East", "/static/images/plants/Ashwagandha.jpg"),
            ("Brahmi", "Bacopa monnieri", "Plantaginaceae", "Flowering Plants", "Herb",
             "Brain tonic used for memory, concentration, anxiety, and cognitive enhancement.",
             "India, Southeast Asia", "/static/images/plants/Brahmi.jpg"),
            ("Gotu Kola", "Centella asiatica", "Apiaceae", "Flowering Plants", "Herb",
             "Brain and skin herb used for memory, wound healing, and venous insufficiency.",
             "India, Southeast Asia, Africa", "/static/images/plants/Gotu Kola.jpg"),
            ("Shankhpushpi", "Convolvulus pluricaulis", "Convolvulaceae", "Flowering Plants", "Herb",
             "Brain tonic used for memory, stress relief, and mental clarity.",
             "India", "/static/images/plants/Shankhpushpi.jpg"),
            ("Jatamansi", "Nardostachys jatamansi", "Caprifoliaceae", "Flowering Plants", "Herb",
             "Rare Himalayan herb used for stress, sleep disorders, and skin diseases.",
             "Himalayas, India", "/static/images/plants/Jatamansi.jpg"),
            ("Sarpagandha", "Rauwolfia serpentina", "Apocynaceae", "Flowering Plants", "Herb",
             "Used in Ayurveda for hypertension, insomnia, and mental disorders.",
             "India, Southeast Asia", "/static/images/plants/Sarpagandha.jpg"),
            ("Kalmegh", "Andrographis paniculata", "Acanthaceae", "Flowering Plants", "Herb",
             "Bitter herb used for liver health, immunity, fever, and digestive disorders.",
             "India, Southeast Asia", "/static/images/plants/Kalmegh.jpg"),
            ("Bhringraj", "Eclipta alba", "Asteraceae", "Flowering Plants", "Herb",
             "King of Hair herbs. Used for hair growth, liver health, and skin conditions.",
             "India, Southeast Asia", "/static/images/plants/Bhringraj.jpg"),
            ("Manjistha", "Rubia cordifolia", "Rubiaceae", "Flowering Plants", "Herb",
             "Blood purifier used for skin diseases, detoxification, and menstrual disorders.",
             "India, Southeast Asia", "/static/images/plants/Manjistha.jpg"),
            ("Sariva", "Hemidesmus indicus", "Apocynaceae", "Flowering Plants", "Herb",
             "Cooling herb used for blood purification, skin diseases, and urinary disorders.",
             "India", "/static/images/plants/Sariva.jpg"),
            ("Guduchi", "Tinospora cordifolia", "Menispermaceae", "Flowering Plants", "Herb",
             "Divine nectar herb used for immunity, diabetes, liver health, and fever.",
             "India, Southeast Asia", "/static/images/plants/Guduchi.jpg"),
            ("Punarnava", "Boerhavia diffusa", "Nyctaginaceae", "Flowering Plants", "Herb",
             "Rejuvenating herb used for kidney health, edema, and liver disorders.",
            "India, Worldwide", "/static/images/plants/Punarnava.jpg"),
            ("Mulethi", "Glycyrrhiza glabra", "Fabaceae", "Flowering Plants", "Herb",
             "Yashtimadhu - sweet root used for respiratory conditions, ulcers, and adrenal support.",
             "Europe, Asia", "/static/images/plants/Mulethi.jpg"),
            ("Chitrak", "Plumbago zeylanica", "Plumbaginaceae", "Flowering Plants", "Herb",
             "Digestive herb used for metabolism, digestive fire, and weight management.",
             "India, Southeast Asia", "/static/images/plants/Chitrak.jpg"),
            ("Vacha", "Acorus calamus", "Acoraceae", "Flowering Plants", "Herb",
             "Brain and speech herb used for memory, speech disorders, and digestion.",
             "India, Europe, Asia", "/static/images/plants/Vacha.jpg"),
            ("Kutki", "Picrorhiza kurroa", "Plantaginaceae", "Flowering Plants", "Herb",
             "Bitter Himalayan herb used for liver, digestion, and immune support.",
             "Himalayas", "/static/images/plants/Kutki.jpg"),
            ("Yashtimadhu", "Glycyrrhiza glabra", "Fabaceae", "Flowering Plants", "Herb",
             "Sweet root tonic for respiratory health, immunity, and digestive comfort.",
             "Mediterranean, Asia", "/static/images/plants/yashtimadhu.jpg"),
            ("Dandelion", "Taraxacum officinale", "Asteraceae", "Flowering Plants", "Herb",
             "Detox herb used for liver health, digestion, and as a diuretic.",
             "Europe, Asia, Americas", "/static/images/plants/Dandelion.jpg"),
            ("Milk Thistle", "Silybum marianum", "Asteraceae", "Flowering Plants", "Herb",
             "Liver protective herb with silymarin. Used for liver detox and regeneration.",
             "Mediterranean, Worldwide", "/static/images/plants/Milk Thistle.jpg"),
            ("Chamomile", "Matricaria chamomilla", "Asteraceae", "Flowering Plants", "Herb",
             "Calming herb used for sleep, anxiety, digestion, and skin inflammation.",
             "Europe, Asia", "/static/images/plants/Chamomile.jpg"),
            ("Peppermint", "Mentha piperita", "Lamiaceae", "Flowering Plants", "Herb",
             "Cooling herb used for digestion, headaches, respiratory conditions, and fresh breath.",
             "Europe, Asia, Worldwide", "/static/images/plants/Peppermint.jpg"),
            ("Spearmint", "Mentha spicata", "Lamiaceae", "Flowering Plants", "Herb",
             "Milder mint used for digestion, nausea, and hormonal balance in women.",
             "Europe, Asia, Worldwide", "/static/images/plants/Spearmint.jpg"),
            ("Lemon Balm", "Melissa officinalis", "Lamiaceae", "Flowering Plants", "Herb",
             "Calming herb used for anxiety, sleep, digestion, and cold sores.",
             "Mediterranean, Europe", "/static/images/plants/Lemon Balm.jpg"),
            ("Thyme", "Thymus vulgaris", "Lamiaceae", "Flowering Plants", "Herb",
             "Antiseptic herb used for respiratory infections, cough, and digestion.",
             "Mediterranean, Europe", "/static/images/plants/Thyme.jpg"),
            ("Oregano", "Origanum vulgare", "Lamiaceae", "Flowering Plants", "Herb",
             "Powerful antimicrobial herb used for infections, digestion, and antioxidants.",
             "Mediterranean, Europe", "/static/images/plants/Oregano.jpg"),
            ("Rosemary", "Rosmarinus officinalis", "Lamiaceae", "Flowering Plants", "Herb",
             "Brain and circulation herb used for memory, hair growth, and digestion.",
             "Mediterranean", "/static/images/plants/Rosemary.jpg"),
            ("Sage", "Salvia officinalis", "Lamiaceae", "Flowering Plants", "Herb",
             "Wise herb used for memory, menopause symptoms, sore throat, and digestion.",
             "Mediterranean, Europe", "/static/images/plants/Sage.jpg"),
            ("Lavender", "Lavandula angustifolia", "Lamiaceae", "Flowering Plants", "Herb",
             "Calming aromatic herb used for anxiety, sleep, skin healing, and stress.",
             "Mediterranean", "/static/images/plants/Lavender.jpg"),
            ("St. John's Wort", "Hypericum perforatum", "Hypericaceae", "Flowering Plants", "Herb",
             "Mood-supporting herb used for depression, anxiety, and nerve pain.",
             "Europe, Asia", "/static/images/plants/St. John's Wort.jpg"),
            ("Echinacea", "Echinacea purpurea", "Asteraceae", "Flowering Plants", "Herb",
             "Immune-boosting herb used for colds, flu, and respiratory infections.",
             "North America", "/static/images/plants/Echinacea.jpg"),
            ("Goldenseal", "Hydrastis canadensis", "Ranunculaceae", "Flowering Plants", "Herb",
             "Antibacterial herb used for infections, digestive issues, and immune support.",
             "North America", "/static/images/plants/Goldenseal.jpg"),
            ("Valerian", "Valeriana officinalis", "Caprifoliaceae", "Flowering Plants", "Herb",
             "Sleep herb used for insomnia, anxiety, and nervous system support.",
             "Europe, Asia", "/static/images/plants/Valerian.jpg"),
            ("Passionflower", "Passiflora incarnata", "Passifloraceae", "Flowering Plants", "Herb",
             "Calming herb used for anxiety, insomnia, and nervous tension.",
             "Americas", "/static/images/plants/Passionflower.jpg"),
            ("Skullcap", "Scutellaria lateriflora", "Lamiaceae", "Flowering Plants", "Herb",
             "Nervous system herb used for anxiety, stress, and nervous exhaustion.",
             "North America", "/static/images/plants/Skullcap.jpg"),
            ("Nettle", "Urtica dioica", "Urticaceae", "Flowering Plants", "Herb",
             "Nutritive herb rich in minerals. Used for allergies, inflammation, and prostate.",
             "Europe, Asia, Americas", "/static/images/plants/Nettle.jpg"),
            ("Red Clover", "Trifolium pratense", "Fabaceae", "Flowering Plants", "Herb",
             "Phytoestrogen herb used for menopause symptoms and blood purification.",
             "Europe, Asia, Americas", "/static/images/plants/Red Clover.jpg"),
            ("Alfalfa", "Medicago sativa", "Fabaceae", "Flowering Plants", "Herb",
             "Nutrient-dense herb used for digestion, cholesterol, and menopause.",
             "Europe, Asia", "/static/images/plants/alfalfa.jpg"),
            ("Fenugreek", "Trigonella foenum-graecum", "Fabaceae", "Flowering Plants", "Herb",
             "Seeds used for diabetes, cholesterol, digestion, and lactation support.",
             "Mediterranean, Asia", "/static/images/plants/Fenugreek.jpg"),
            ("Fennel", "Foeniculum vulgare", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds used for digestion, bloating, respiratory congestion, and lactation.",
             "Mediterranean, Worldwide", "/static/images/plants/Fennel.jpg"),
            ("Dill", "Anethum graveolens", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds and leaves used for digestion, colic, and as a carminative.",
             "Mediterranean, Europe", "/static/images/plants/Dill.jpg"),
            ("Coriander", "Coriandrum sativum", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds used for digestion, detoxification, and blood sugar regulation.",
             "Mediterranean, Asia", "/static/images/plants/Coriander.jpg"),
            ("Cumin", "Cuminum cyminum", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds used for digestion, immunity, and as a source of iron.",
             "Mediterranean, Middle East", "/static/images/plants/Cumin.jpg"),
            ("Caraway", "Carum carvi", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds used for digestion, bloating, and respiratory conditions.",
             "Europe, Asia", "/static/images/plants/Caraway.jpg"),
            ("Ajwain", "Trachyspermum ammi", "Apiaceae", "Flowering Plants", "Herb",
             "Seeds used for digestive disorders, respiratory issues, and pain relief.",
             "India, Middle East", "/static/images/plants/ajwain.jpg"),
            ("Asafoetida", "Ferula assa-foetida", "Apiaceae", "Flowering Plants", "Herb",
             "Pungent resin used for digestion, bloating, and respiratory conditions.",
             "Middle East, India", "/static/images/plants/Asafoetida.jpg"),
            ("Lemongrass", "Cymbopogon citratus", "Poaceae", "Grasses", "Grass",
             "Aromatic grass used for digestion, anxiety, and as a natural insect repellent.",
             "Southeast Asia, India", "/static/images/plants/Lemongrass.jpg"),
            ("Citronella", "Cymbopogon nardus", "Poaceae", "Grasses", "Grass",
             "Aromatic grass used as natural insect repellent and for fever reduction.",
             "Southeast Asia", "/static/images/plants/Citronella.jpg"),
            ("Vetiver", "Chrysopogon zizanioides", "Poaceae", "Grasses", "Grass",
             "Aromatic roots used for cooling, skin health, and calming the mind.",
             "India, Southeast Asia", "/static/images/plants/Vetiver.jpg"),
            ("Wheatgrass", "Triticum aestivum", "Poaceae", "Grasses", "Grass",
             "Young wheat shoots rich in chlorophyll and nutrients. Used for detox and energy.",
             "Worldwide", "/static/images/plants/Wheatgrass.jpg"),
            ("Barley Grass", "Hordeum vulgare", "Poaceae", "Grasses", "Grass",
             "Nutrient-rich grass used for digestion, cholesterol, and blood sugar control.",
             "Worldwide", "/static/images/plants/Barley Grass.jpg"),
            ("Psyllium", "Plantago ovata", "Plantaginaceae", "Flowering Plants", "Herb",
             "Seeds husk used for constipation, diarrhea, and cholesterol management.",
             "India, Middle East", "/static/images/plants/Psyllium.jpg"),
            ("Flax", "Linum usitatissimum", "Linaceae", "Flowering Plants", "Herb",
             "Seeds rich in omega-3 and fiber. Used for digestion, heart health, and hormones.",
             "Europe, Asia", "/static/images/plants/Flax.jpg"),
            ("Chia", "Salvia hispanica", "Lamiaceae", "Flowering Plants", "Herb",
             "Seeds rich in omega-3, protein, and fiber. Used for energy and heart health.",
             "Central America", "/static/images/plants/Chia.jpg"),
            ("Quinoa", "Chenopodium quinoa", "Amaranthaceae", "Flowering Plants", "Herb",
             "Protein-rich grain used for nutrition, energy, and as a complete protein source.",
             "South America", "/static/images/plants/Quinoa.jpg"),
            ("Amaranth", "Amaranthus hypochondriacus", "Amaranthaceae", "Flowering Plants", "Herb",
             "Ancient grain rich in protein and minerals. Used for nutrition and energy.",
             "Central America, Asia", "/static/images/plants/amarnath.jpg"),
            ("Spirulina", "Arthrospira platensis", "Phormidiaceae", "Cyanobacteria", "Algae",
             "Blue-green algae superfood rich in protein and nutrients. Used for immunity and energy.",
             "Worldwide", "/static/images/plants/Spirulina.jpg"),
            ("Chlorella", "Chlorella vulgaris", "Chlorellaceae", "Green Algae", "Algae",
             "Green algae superfood for detoxification, immunity, and heavy metal removal.",
             "Worldwide", "/static/images/plants/Chlorella.jpg"),
            ("Irish Moss", "Chondrus crispus", "Gigartinaceae", "Red Algae", "Seaweed",
             "Red seaweed used for respiratory health, digestion, and as a mineral source.",
             "Atlantic coasts", "/static/images/plants/Irish Moss.jpg"),
            ("Bladderwrack", "Fucus vesiculosus", "Fucaceae", "Brown Algae", "Seaweed",
             "Brown seaweed rich in iodine. Used for thyroid health and metabolism.",
             "Northern Hemisphere coasts", "/static/images/plants/Bladderwrack.jpg"),
            ("Kelp", "Laminaria digitata", "Laminariaceae", "Brown Algae", "Seaweed",
             "Brown seaweed rich in iodine and minerals. Used for thyroid and nutrition.",
             "Northern Atlantic, Pacific", "/static/images/plants/Kelp.jpg"),
            ("Wakame", "Undaria pinnatifida", "Alariaceae", "Brown Algae", "Seaweed",
             "Japanese seaweed rich in nutrients. Used for heart health and weight management.",
             "Japan, Korea, China", "/static/images/plants/Wakame.jpg"),
            ("Nori", "Porphyra umbilicalis", "Bangiaceae", "Red Algae", "Seaweed",
             "Japanese seaweed used for sushi, rich in nutrients and antioxidants.",
             "Japan, Worldwide", "/static/images/plants/Nori.jpg"),
            ("Arame", "Eisenia bicyclis", "Alariaceae", "Brown Algae", "Seaweed",
             "Japanese brown seaweed used for nutrition and hormonal balance.",
             "Japan", "/static/images/plants/Arame.jpg"),
            ("Dulse", "Palmaria palmata", "Palmariaceae", "Red Algae", "Seaweed",
             "Red seaweed rich in iron and minerals. Used for nutrition and thyroid health.",
             "North Atlantic, Pacific", "/static/images/plants/Dulse.jpg"),
            ("Hijiki", "Sargassum fusiforme", "Sargassaceae", "Brown Algae", "Seaweed",
             "Japanese seaweed rich in minerals. Used for bone health and nutrition.",
             "Japan, Korea, China", "/static/images/plants/Hijiki.jpg"),
            ("Agar Agar", "Gelidium amansii", "Gelidiaceae", "Red Algae", "Seaweed",
             "Seaweed used as vegetarian gelatin substitute and for digestion.",
             "Japan, Worldwide", "/static/images/plants/Agar.jpg"),
            ("Carrageenan", "Chondrus crispus", "Gigartinaceae", "Red Algae", "Seaweed",
             "Seaweed extract used for digestive health and as a thickener.",
             "Atlantic coasts", "/static/images/plants/Carrageenan.jpg"),
            ("Reishi Mushroom", "Ganoderma lucidum", "Ganodermataceae", "Fungi", "Mushroom",
             "Ganoderma - Mushroom of Immortality. Used for immunity, longevity, and stress relief.",
             "Asia, Worldwide", "/static/images/plants/Reishi Mushroom.jpg"),
            ("Shiitake", "Lentinula edodes", "Omphalotaceae", "Fungi", "Mushroom",
             "Medicinal mushroom used for immunity, heart health, and antiviral properties.",
             "East Asia, Worldwide", "/static/images/plants/Shiitake.jpg"),
            ("Maitake", "Grifola frondosa", "Meripilaceae", "Fungi", "Mushroom",
             "Dancing mushroom used for immunity, blood sugar control, and cancer support.",
             "Japan, North America", "/static/images/plants/Maitake.jpg"),
            ("Cordyceps", "Cordyceps sinensis", "Cordycipitaceae", "Fungi", "Mushroom",
             "Caterpillar fungus used for energy, athletic performance, and lung health.",
             "Himalayas, Tibet", "/static/images/plants/Cordyceps.jpg"),
            ("Lion's Mane", "Hericium erinaceus", "Hericiaceae", "Fungi", "Mushroom",
             "Brain mushroom used for cognitive function, nerve regeneration, and memory.",
             "North America, Europe, Asia", "/static/images/plants/Lion's Mane.jpg"),
            ("Turkey Tail", "Trametes versicolor", "Polyporaceae", "Fungi", "Mushroom",
             "Immune-supporting mushroom used for cancer support and immunity.",
             "Worldwide", "/static/images/plants/Turkey Tail.jpg"),
            ("Chaga", "Inonotus obliquus", "Hymenochaetaceae", "Fungi", "Mushroom",
             "Antioxidant-rich mushroom used for immunity, inflammation, and overall health.",
             "Boreal forests", "/static/images/plants/Chaga.jpg"),
            ("Enoki", "Flammulina velutipes", "Physalacriaceae", "Fungi", "Mushroom",
             "Long, thin mushroom used for immunity and as a nutritious food.",
             "East Asia, Worldwide", "/static/images/plants/Enoki.jpg"),
            ("Oyster Mushroom", "Pleurotus ostreatus", "Pleurotaceae", "Fungi", "Mushroom",
             "Protein-rich mushroom used for cholesterol reduction and immunity.",
             "Worldwide", "/static/images/plants/Oyster Mushroom.jpg"),
            ("White Button Mushroom", "Agaricus bisporus", "Agaricaceae", "Fungi", "Mushroom",
             "Common mushroom with immune and antioxidant properties.",
             "Worldwide", "/static/images/plants/White Button Mushroom.jpg"),
        ]
        
        cursor.executemany('''
            INSERT INTO plants (common_name, scientific_name, family, plant_group, plant_type, 
                              description, distribution, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_plants)
        conn.commit()
        print(f"Inserted {len(sample_plants)} plants")
    
    conn.close()

@app.route('/')
def index():
    """Main page with search bar and plant display"""
    return render_template('index.html')

@app.route('/api/search')
def search_all():
    """API endpoint to search all data: plants, families, groups, categories, types, and crown architectures"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"plants": [], "families": [], "groups": [], "categories": [], "types": [], "architectures": []})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    search_term = f"%{query}%"
    
    # Search plants
    cursor.execute("""
        SELECT * FROM plants 
        WHERE common_name LIKE ? OR scientific_name LIKE ? OR description LIKE ? 
        OR family LIKE ? OR plant_group LIKE ? OR plant_type LIKE ?
        ORDER BY common_name
    """, [search_term] * 6)
    plants = [dict(row) for row in cursor.fetchall()]
    
    # Search plant families
    cursor.execute("""
        SELECT * FROM plant_families 
        WHERE family_name LIKE ? OR common_name LIKE ? OR description LIKE ? 
        OR characteristics LIKE ? OR medicinal_uses LIKE ? OR example_plants LIKE ?
        ORDER BY family_name
    """, [search_term] * 6)
    families = [dict(row) for row in cursor.fetchall()]
    
    # Search plant groups
    cursor.execute("""
        SELECT * FROM plant_groups 
        WHERE group_name LIKE ? OR description LIKE ? OR characteristics LIKE ?
        OR medicinal_uses LIKE ? OR example_plants LIKE ?
        ORDER BY group_name
    """, [search_term] * 5)
    groups = [dict(row) for row in cursor.fetchall()]
    
    # Search plant categories
    cursor.execute("""
        SELECT * FROM plant_categories 
        WHERE category_name LIKE ? OR description LIKE ? OR characteristics LIKE ?
        OR medicinal_uses LIKE ? OR example_plants LIKE ?
        ORDER BY category_name
    """, [search_term] * 5)
    categories = [dict(row) for row in cursor.fetchall()]
    
    # Search plant types
    cursor.execute("""
        SELECT * FROM plant_types 
        WHERE type_name LIKE ? OR description LIKE ? OR characteristics LIKE ?
        OR growth_habits LIKE ? OR medicinal_uses LIKE ? OR example_plants LIKE ?
        ORDER BY type_name
    """, [search_term] * 6)
    types = [dict(row) for row in cursor.fetchall()]
    
    # Search crown architectures
    cursor.execute("""
        SELECT * FROM crown_architecture 
        WHERE architecture_name LIKE ? OR description LIKE ? OR characteristics LIKE ?
        OR growth_pattern LIKE ? OR ecological_significance LIKE ? OR common_species LIKE ?
        ORDER BY architecture_name
    """, [search_term] * 6)
    architectures = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "plants": plants,
        "families": families,
        "groups": groups,
        "categories": categories,
        "types": types,
        "architectures": architectures
    })

@app.route('/api/plants/<int:plant_id>')
def get_plant(plant_id):
    """Get single plant details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    plant = cursor.fetchone()
    conn.close()
    
    if plant:
        return jsonify(dict(plant))
    return jsonify({"error": "Plant not found"}), 404

@app.route('/api/filters')
def get_filters():
    """Get all available filter options"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT family FROM plants WHERE family IS NOT NULL ORDER BY family")
    families = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT plant_group FROM plants WHERE plant_group IS NOT NULL ORDER BY plant_group")
    groups = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT plant_type FROM plants WHERE plant_type IS NOT NULL ORDER BY plant_type")
    types = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "families": families,
        "groups": groups,
        "types": types
    })

@app.route('/plants')
def plants_page():
    """Display all plants page"""
    return render_template('plants.html')

@app.route('/api/all-plants')
def get_all_plants():
    """Get all plants"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants ORDER BY common_name")
    plants = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(plant) for plant in plants])

@app.route('/api/families')
def get_all_families():
    """Get all plant families with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_families ORDER BY family_name")
    families = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(family) for family in families])

@app.route('/api/families/<family_name>')
def get_family_details(family_name):
    """Get details of a specific plant family"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_families WHERE family_name = ?", (family_name,))
    family = cursor.fetchone()
    
    # Also get plants in this family
    cursor.execute("SELECT * FROM plants WHERE family = ? ORDER BY common_name", (family_name,))
    plants = cursor.fetchall()
    conn.close()
    
    if family:
        result = dict(family)
        result['plants'] = [dict(plant) for plant in plants]
        return jsonify(result)
    return jsonify({"error": "Family not found"}), 404

@app.route('/api/families/<family_name>/plants')
def get_plants_by_family(family_name):
    """Get all plants belonging to a specific family"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE family = ? ORDER BY common_name", (family_name,))
    plants = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(plant) for plant in plants])

@app.route('/api/groups')
def get_all_groups():
    """Get all plant groups with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_groups ORDER BY group_name")
    groups = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(group) for group in groups])

@app.route('/api/groups/<group_name>')
def get_group_details(group_name):
    """Get details of a specific plant group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_groups WHERE group_name = ?", (group_name,))
    group = cursor.fetchone()
    
    # Also get plants in this group
    cursor.execute("SELECT * FROM plants WHERE plant_group = ? ORDER BY common_name", (group_name,))
    plants = cursor.fetchall()
    conn.close()
    
    if group:
        result = dict(group)
        result['plants'] = [dict(plant) for plant in plants]
        return jsonify(result)
    return jsonify({"error": "Group not found"}), 404

@app.route('/api/groups/<group_name>/plants')
def get_plants_by_group(group_name):
    """Get all plants belonging to a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE plant_group = ? ORDER BY common_name", (group_name,))
    plants = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(plant) for plant in plants])

@app.route('/api/categories')
def get_all_categories():
    """Get all plant categories with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_categories ORDER BY category_name")
    categories = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(category) for category in categories])

@app.route('/api/categories/<category_name>')
def get_category_details(category_name):
    """Get details of a specific plant category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_categories WHERE category_name = ?", (category_name,))
    category = cursor.fetchone()
    
    # Also get plants in this category
    cursor.execute("SELECT * FROM plants WHERE plant_type = ? ORDER BY common_name", (category_name,))
    plants = cursor.fetchall()
    conn.close()
    
    if category:
        result = dict(category)
        result['plants'] = [dict(plant) for plant in plants]
        return jsonify(result)
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/categories/<category_name>/plants')
def get_plants_by_category(category_name):
    """Get all plants belonging to a specific category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE plant_type = ? ORDER BY common_name", (category_name,))
    plants = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(plant) for plant in plants])

@app.route('/api/types')
def get_all_types():
    """Get all plant types with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_types ORDER BY type_name")
    types = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(type_item) for type_item in types])

@app.route('/api/types/<type_name>')
def get_type_details(type_name):
    """Get details of a specific plant type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plant_types WHERE type_name = ?", (type_name,))
    type_item = cursor.fetchone()
    
    # Also get plants of this type
    cursor.execute("SELECT * FROM plants WHERE plant_type = ? ORDER BY common_name", (type_name,))
    plants = cursor.fetchall()
    conn.close()
    
    if type_item:
        result = dict(type_item)
        result['plants'] = [dict(plant) for plant in plants]
        return jsonify(result)
    return jsonify({"error": "Type not found"}), 404

@app.route('/api/types/<type_name>/plants')
def get_plants_by_type(type_name):
    """Get all plants of a specific type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE plant_type = ? ORDER BY common_name", (type_name,))
    plants = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(plant) for plant in plants])

@app.route('/api/crown-architecture')
def get_all_crown_architectures():
    """Get all crown architecture types with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crown_architecture ORDER BY architecture_name")
    architectures = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(arch) for arch in architectures])

@app.route('/api/crown-architecture/<arch_name>')
def get_crown_architecture_details(arch_name):
    """Get details of a specific crown architecture"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crown_architecture WHERE architecture_name = ?", (arch_name,))
    arch = cursor.fetchone()
    conn.close()
    
    if arch:
        return jsonify(dict(arch))
    return jsonify({"error": "Crown architecture not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
