from flask import Flask, Response, render_template, request, jsonify, send_from_directory
import sqlite3
import os
from urllib.parse import quote

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'plants.db')
PLANT_IMAGE_DIR = os.path.join(app.static_folder, 'images', 'plants')

# List of allowed plant images (original plants only)
ALLOWED_PLANT_IMAGES = {
    'Arjun Tree.jpg', 'Neem.jpg', 'Aloe vera.jpg', 'Amla.jpg', 'Ashwagandha.jpg',
    'Giloy.jpg', 'Tulsi.jpg', 'Turmeric.jpg', 'Ginger.jpg', 'Garlic.jpg',
    'Mint.jpg', 'Lavender.jpg', 'Rosemary.jpg', 'Thyme.jpg', 'Chamomile.jpg',
    'Dandelion.jpg', 'Echinacea.jpg', 'Ginseng.jpg', 'Goldenseal.jpg', 'Milk Thistle.jpg',
    'Peppermint.jpg', 'St. John Wort.jpg', 'Valerian.jpg', 'Wheatgrass.jpg', 'Spirulina.jpg',
    'Chlorella.jpg', 'Moringa.jpg', 'Noni.jpg', 'Ginkgo.jpg', 'Saw Palmetto.jpg',
    'Black Cohosh.jpg', 'Evening Primrose.jpg', 'Feverfew.jpg', 'Flaxseed.jpg', 'Green Tea.jpg',
    'Kava.jpg', 'Passionflower.jpg', 'Red Clover.jpg', 'Soy.jpg', 'Yohimbe.jpg',
    'Bilberry.jpg', 'Cranberry.jpg', 'Elderberry.jpg', 'Grape Seed.jpg', 'Hawthorn.jpg',
    'Horse Chestnut.jpg', 'Psyllium.jpg', 'Tea Tree.jpg', ' Arnica.jpg', 'Calendula.jpg',
    'Comfrey.jpg', 'Plantain.jpg', 'Yarrow.jpg', 'Burdock.jpg', 'Cayenne.jpg',
    'Cinnamon.jpg', 'Clove.jpg', 'Cumin.jpg', 'Fennel.jpg', 'Fenugreek.jpg',
    'Licorice.jpg', 'Mustard.jpg', 'Nutmeg.jpg', 'Parsley.jpg', 'Sage.jpg',
    'Black Pepper.jpg', 'Cardamom.jpg', 'Cilantro.jpg', 'Coriander.jpg', 'Cumin Seed.jpg',
    'Dill.jpg', 'Oregano.jpg', 'Paprika.jpg', 'Rosemary Leaf.jpg', 'Saffron.jpg',
    'Sesame.jpg', 'Spearmint.jpg', 'Tarragon.jpg', 'Vanilla.jpg', 'Watercress.jpg',
    'White Willow.jpg', 'Witch Hazel.jpg', 'Yellow Dock.jpg', 'Yucca.jpg', 'Amalaki.jpg',
    'Arjuna.jpg', 'Bael.jpg', 'Bhumyamalaki.jpg', 'Brahmi.jpg', 'Bringraj.jpg',
    'Gokshura.jpg', 'Guduchi.jpg', 'Haritaki.jpg', 'Jatamansi.jpg', 'Kapi Kacchu.jpg',
    'Kutki.jpg', 'Manjistha.jpg', 'Neem Leaf.jpg', 'Pippali.jpg', 'Punarnava.jpg',
    'Shankhapushpi.jpg', 'Shatavari.jpg', 'Vacha.jpg', 'Vidanga.jpg', 'Ashoka.jpg',
    'Bala.jpg', 'Bibhitaki.jpg', 'Chitrak.jpg', 'Daruharidra.jpg', 'Guggulu.jpg',
    'Jyotishmati.jpg', 'Kanchanar.jpg', 'Karanja.jpg', 'Kokilaksha.jpg', 'Ksheer Kakoli.jpg',
    'Kushtha.jpg', 'Lajjalu.jpg', 'Lodhra.jpg', 'Madhuka.jpg', 'Mahanimba.jpg',
    'Malkangani.jpg', 'Methi.jpg', 'Musali.jpg', 'Nagakesara.jpg', 'Nirgundi.jpg',
    'Palash.jpg', 'Pushkarmool.jpg', 'Raktachandana.jpg', 'Salai Guggul.jpg', 'Sarpagandha.jpg',
    'Shallaki.jpg', 'Shirish.jpg', 'Sigru.jpg', 'Sunthi.jpg', 'Talisa Patra.jpg',
    'Trivrit.jpg', 'Tulasi.jpg', 'Twak.jpg', 'Vamsha.jpg', 'Varuna.jpg',
    'Vasa.jpg', 'Yashti.jpg', 'Yavani.jpg', 'Amra.jpg', 'Amruta.jpg',
    'Ananas.jpg', 'Aragvadha.jpg', 'Arani.jpg', 'Ardaka.jpg', 'Arimeda.jpg',
    'Arjuna.jpg', 'Asana.jpg', 'Asmantaka.jpg', 'Asoka.jpg', 'Asvagandha.jpg',
    'Atasi.jpg', 'Atibala.jpg', 'Avartaki.jpg', 'Badara.jpg', 'Bakuchi.jpg',
    'Bala.jpg', 'Bhallataka.jpg', 'Bhringaraja.jpg', 'Bibhitaka.jpg', 'Bilva.jpg',
    'Brahati.jpg', 'Bruhati.jpg', 'Chaga.jpg', 'Chandana.jpg', 'Changeri.jpg',
    'Chitraka.jpg', 'Dadima.jpg', 'Danti.jpg', 'Devadaru.jpg', 'Dhanyaka.jpg',
    'Dhataki.jpg', 'Draksha.jpg', 'Ela.jpg', 'Eranda.jpg', 'Gambhari.jpg',
    'Goksura.jpg', 'Gorakhmundi.jpg', 'Guja.jpg', 'Gunja.jpg', 'Haridra.jpg',
    'Haritaki.jpg', 'Hingu.jpg', 'Hribera.jpg', 'Ikshu.jpg', 'Indravaruni.jpg',
    'Jambu.jpg', 'Japa.jpg', 'Jatamamsi.jpg', 'Jati.jpg', 'Jivaka.jpg',
    'Jivanti.jpg', 'Kadali.jpg', 'Kakamachi.jpg', 'Kakubha.jpg', 'Kalinga.jpg',
    'Kalmegh.jpg', 'Kamala.jpg', 'Kanchanara.jpg', 'Kantakari.jpg', 'Kapikacchu.jpg',
    'Karakatika.jpg', 'Karpasa.jpg', 'Katphala.jpg', 'Khadira.jpg', 'Kharjura.jpg',
    'Kiratatikta.jpg', 'Kovidara.jpg', 'Kshaudra.jpg', 'Ksheerini.jpg', 'Kulattha.jpg',
    'Kumari.jpg', 'Kumuda.jpg', 'Kupilu.jpg', 'Kusha.jpg', 'Kutaja.jpg',
    'Laksha.jpg', 'Lashuna.jpg', 'Latakaranja.jpg', 'Lavanga.jpg', 'Madana.jpg',
    'Madhuka.jpg', 'Mahanimba.jpg', 'Makoi.jpg', 'Malati.jpg', 'Mandukaparni.jpg',
    'Maricha.jpg', 'Markandika.jpg', 'Masura.jpg', 'Matulunga.jpg', 'Maya.jpg',
    'Meda.jpg', 'Medasaka.jpg', 'Methika.jpg', 'Mohari.jpg', 'Mudga.jpg',
    'Mulaka.jpg', 'Mulathi.jpg', 'Nagabala.jpg', 'Nagakesara.jpg', 'Nili.jpg',
    'Nimbaka.jpg', 'Nirgundi.jpg', 'Nyagrodha.jpg', 'Palandu.jpg', 'Palasha.jpg',
    'Parijata.jpg', 'Parushaka.jpg', 'Patala.jpg', 'Patha.jpg', 'Pippali.jpg',
    'Prasarini.jpg', 'Priyala.jpg', 'Punarnava.jpg', 'Raga.jpg', 'Rajika.jpg',
    'Rambha.jpg', 'Rasanjana.jpg', 'Rasona.jpg', 'Rddhi.jpg', 'Rohisa.jpg',
    'Rohitaka.jpg', 'Sairyaka.jpg', 'Saka.jpg', 'Sala.jpg', 'Salaparni.jpg',
    'Saptachada.jpg', 'Sarala.jpg', 'Sariva.jpg', 'Sarshapa.jpg', 'Satapuspa.jpg',
    'Sati.jpg', 'Satuvara.jpg', 'Saubhanjana.jpg', 'Seba.jpg', 'Seedhakiya.jpg',
    'Shaka.jpg', 'Shala.jpg', 'Shalaparni.jpg', 'Shallaki.jpg', 'Shalmali.jpg',
    'Sharapunkha.jpg', 'Shatavari.jpg', 'Shati.jpg', 'Shirisha.jpg', 'Shyonaka.jpg',
    'Sigru.jpg', 'Simbi.jpg', 'Sindhuvara.jpg', 'Sinsapa.jpg', 'Sirisha.jpg',
    'Soma.jpg', 'Soya.jpg', 'Sphatika.jpg', 'Srigavera.jpg', 'Srivhuksha.jpg',
    'Sruvavrksha.jpg', 'Sthauneya.jpg', 'Sthira.jpg', 'Sukshmaila.jpg', 'Sunishannaka.jpg',
    'Svarnaksiri.jpg', 'Syonaka.jpg', 'Tagara.jpg', 'Tala.jpg', 'Talisa.jpg',
    'Tambula.jpg', 'Tanka.jpg', 'Tilaka.jpg', 'Tinduka.jpg', 'Trapusa.jpg',
    'Trivrit.jpg', 'Tulasi.jpg', 'Tvak.jpg', 'Udakiryaka.jpg', 'Udumbara.jpg',
    'Ulpala.jpg', 'Upakuncika.jpg', 'Urumana.jpg', 'Utpala.jpg', 'Vacha.jpg',
    'Vamsha.jpg', 'Varanga.jpg', 'Varuna.jpg', 'Vasa.jpg', 'Vatsanabha.jpg',
    'Vella.jpg', 'Vetasamla.jpg', 'Vidarikanda.jpg', 'Vijaya.jpg', 'Vilva.jpg',
    'Yashti.jpg', 'Yava.jpg', 'Ahiphena.jpg', 'Agaru.jpg', 'Akarkara.jpg',
    'Akasha.jpg', 'Alabu.jpg', 'Amalatas.jpg', 'Amlavetasa.jpg', 'Ankola.jpg',
    'Apamarga.jpg', 'Aralu.jpg', 'Arani.jpg', 'Aranyajiraka.jpg', 'Ardaka.jpg',
    'Arimedadi.jpg', 'Arimeda.jpg', 'Arjuna.jpg', 'Arka.jpg', 'Arni.jpg',
    'Arsoghna.jpg', 'Artagala.jpg', 'Aru.jpg', 'Aruna.jpg', 'Arya.jpg',
    'Ashmantaka.jpg', 'Asmagandha.jpg', 'Asmantaka.jpg', 'Asoka.jpg', 'Asparagus.jpg',
    'Ata.jpg', 'Atasika.jpg', 'Atibala.jpg', 'Atimuktaka.jpg', 'Ativisha.jpg',
    'Atmagupta.jpg', 'Avagaha.jpg', 'Avartani.jpg', 'Avartika.jpg', 'Avartaki.jpg',
    'Badari.jpg', 'Badarika.jpg', 'Bael.jpg', 'Bahalapalli.jpg', 'Bahu.jpg',
    'Bahupatra.jpg', 'Bahuphalini.jpg', 'Bahuphala.jpg', 'Bahuvaram.jpg', 'Bahuvirya.jpg',
    'Bijaka.jpg', 'Bijapuraka.jpg', 'Bilvapatra.jpg', 'Brahati.jpg', 'Brihati.jpg',
    'Bruhati.jpg', 'Buddhaneem.jpg', 'Chagalantri.jpg', 'Chandana.jpg', 'Chandani.jpg',
    'Chandrasura.jpg', 'Changeri.jpg', 'Chincha.jpg', 'Chira.jpg', 'Chitrapatra.jpg',
    'Chitraka.jpg', 'Chukra.jpg', 'Chulika.jpg', 'Chulli.jpg', 'Dadima.jpg',
    'Darbha.jpg', 'Darimba.jpg', 'Dhanwantari.jpg', 'Dhatri.jpg', 'Dhatrina.jpg',
    'Dhavani.jpg', 'Dhayati.jpg', 'Dhenuka.jpg', 'Dhenusha.jpg', 'Dhustura.jpg',
    'Diggdha.jpg', 'Dirghamula.jpg', 'Dirghapatraka.jpg', 'Dirghavrinta.jpg', 'Dirghavrintatma.jpg',
    'Dravanti.jpg', 'Drona.jpg', 'Dronapadi.jpg', 'Dronapushpi.jpg', 'Drumaka.jpg',
    'Drumamla.jpg', 'Drumaphala.jpg', 'Drumavalli.jpg', 'Drumavirya.jpg', 'Drumavrinta.jpg',
    'Dugdhika.jpg', 'Durva.jpg', 'Gandhapushpa.jpg', 'Gandhatrina.jpg', 'Gandhayuti.jpg',
    'Garbhadhatri.jpg', 'Garbhashaya.jpg', 'Garjara.jpg', 'Girikarnika.jpg', 'Gojihva.jpg',
    'Gorakshaganja.jpg', 'Gorakshatali.jpg', 'Gorakshi.jpg', 'Gundra.jpg', 'Gundraha.jpg',
    'Harimanthaka.jpg', 'Haritala.jpg', 'Hemapushpa.jpg', 'Hemapushpaka.jpg', 'Hemapushpi.jpg',
    'Hemavati.jpg', 'Hemavrinta.jpg', 'Hemavrintatma.jpg', 'Himgirija.jpg', 'Hingupatrika.jpg',
    'Hintala.jpg', 'Hintalavrinta.jpg', 'Hintalika.jpg', 'Hintamaricha.jpg', 'Hribera.jpg',
    'Iksu.jpg', 'Ikshuraka.jpg', 'Indivara.jpg', 'Indivaraka.jpg', 'Indivarka.jpg',
    'Indra.jpg', 'Indracirbata.jpg', 'Indragopa.jpg', 'Indrajala.jpg', 'Indramada.jpg',
    'Indranilaka.jpg', 'Indraparni.jpg', 'Indravalli.jpg', 'Indravaruni.jpg', 'Indrayava.jpg',
    'Jambava.jpg', 'Jambira.jpg', 'Jambuka.jpg', 'Jambulaka.jpg', 'Jambunada.jpg',
    'Jambuphalika.jpg', 'Jambupriya.jpg', 'Jambusara.jpg', 'Jambuvantha.jpg', 'Jambuvanthi.jpg',
    'Jambuvirya.jpg', 'Jambuvrinta.jpg', 'Japaka.jpg', 'Japakusuma.jpg', 'Japapushpa.jpg',
    'Jarana.jpg', 'Jati.jpg', 'Jatika.jpg', 'Jatila.jpg', 'Jatipatra.jpg',
    'Jatiphala.jpg', 'Jatipushpa.jpg', 'Jatiputri.jpg', 'Jativrinta.jpg', 'Jayanti.jpg',
    'Jayapatra.jpg', 'Jayapriya.jpg', 'Jayavanti.jpg', 'Jhinti.jpg', 'Jhintika.jpg',
    'Jivaka.jpg', 'Jivanti.jpg', 'Jivantika.jpg', 'Jivaniya.jpg', 'Jivinika.jpg',
    'Jivipushpa.jpg', 'Jivita.jpg', 'Jivitapatra.jpg', 'Jivitaphala.jpg', 'Jivitapushpa.jpg',
    'Jivitavrinta.jpg', 'Jivitavrintatma.jpg', 'Jivitayoni.jpg', 'Jivitika.jpg', 'Jivitparni.jpg',
    'Jyotika.jpg', 'Jyotirma.jpg', 'Jyotishka.jpg', 'Jyotishmati.jpg', 'Jyotismati.jpg',
    'Kabandha.jpg', 'Kadambaka.jpg', 'Kadamba.jpg', 'Kadambapushpa.jpg', 'Kadambavrinta.jpg',
    'Kadambe.jpg', 'Kadambini.jpg', 'Kakamachi.jpg', 'Kakanasa.jpg', 'Kakanasika.jpg',
    'Kakandaki.jpg', 'Kakandika.jpg', 'Kakani.jpg', 'Kakanika.jpg', 'Kakodumbara.jpg',
    'Kakoli.jpg', 'Kakubha.jpg', 'Kala.jpg', 'Kalabha.jpg', 'Kalaka.jpg',
    'Kalambaka.jpg', 'Kalambika.jpg', 'Kalanemi.jpg', 'Kalani.jpg', 'Kalantaka.jpg',
    'Kalashodbhava.jpg', 'Kalashodbhavatma.jpg', 'Kalavrinta.jpg', 'Kalavrintatma.jpg', 'Kalayavani.jpg',
    'Kalinga.jpg', 'Kalingaka.jpg', 'Kaliyaka.jpg', 'Kalka.jpg', 'Kalyaka.jpg',
    'Kalyani.jpg', 'Kamala.jpg', 'Kamalamula.jpg', 'Kamalapatra.jpg', 'Kamalasana.jpg',
    'Kamalahva.jpg', 'Kamalamika.jpg', 'Kamalanka.jpg', 'Kamalapatrika.jpg', 'Kamalapriya.jpg',
    'Kamalapushpa.jpg', 'Kamalavrinta.jpg', 'Kamalika.jpg', 'Kamalinika.jpg', 'Kamanksha.jpg',
    'Kamankshi.jpg', 'Kamini.jpg', 'Kaminika.jpg', 'Kampillaka.jpg', 'Kamra.jpg',
    'Kamsa.jpg', 'Kanaka.jpg', 'Kanakapatra.jpg', 'Kanakapushpa.jpg', 'Kanakavrinta.jpg',
    'Kanakini.jpg', 'Kanana.jpg', 'Kanavira.jpg', 'Kancani.jpg', 'Kanchan.jpg',
    'Kanchana.jpg', 'Kanchanaka.jpg', 'Kanchanara.jpg', 'Kanchanavrinta.jpg', 'Kanchanika.jpg',
    'Kanci.jpg', 'Kandala.jpg', 'Kandali.jpg', 'Kandana.jpg', 'Kandara.jpg',
    'Kandarpa.jpg', 'Kandarpashira.jpg', 'Kandasara.jpg', 'Kandekshu.jpg', 'Kandira.jpg',
    'Kandita.jpg', 'Kanduka.jpg', 'Kandula.jpg', 'Kanduri.jpg', 'Kankola.jpg',
    'Kankolaka.jpg', 'Kankoli.jpg', 'Kankshiri.jpg', 'Kankusha.jpg', 'Kanva.jpg',
    'Kanvapushpa.jpg', 'Kanvavrinta.jpg', 'Kanvika.jpg', 'Kapikacchu.jpg', 'Kapila.jpg',
    'Kapilapriya.jpg', 'Kapilavrinta.jpg', 'Kapilavrintatma.jpg', 'Kapilini.jpg', 'Kapitha.jpg',
    'Kapittha.jpg', 'Kapotapaka.jpg', 'Kapotapakavrinta.jpg', 'Kapotapakavrintatma.jpg', 'Kapotapriya.jpg',
    'Karaka.jpg', 'Karakatika.jpg', 'Karaketaki.jpg', 'Karanja.jpg', 'Karanjaka.jpg',
    'Karanjakanda.jpg', 'Karanjapushpa.jpg', 'Karanjika.jpg', 'Karanjini.jpg', 'Karavellaka.jpg',
    'Karavira.jpg', 'Karaviraka.jpg', 'Karavirapushpa.jpg', 'Karaviravrinta.jpg', 'Karaviravrintatma.jpg',
    'Karavirini.jpg', 'Karkandhu.jpg', 'Karkari.jpg', 'Karkasa.jpg', 'Karkasaka.jpg',
    'Karkasavrinta.jpg', 'Karkasavrintatma.jpg', 'Karkatashringi.jpg', 'Karkatashringika.jpg', 'Karkati.jpg',
    'Karkatika.jpg', 'Karkotaka.jpg', 'Karkotaki.jpg', 'Karkshya.jpg', 'Karmuka.jpg',
    'Karnika.jpg', 'Karpasa.jpg', 'Karpasapushpa.jpg', 'Karpasavrinta.jpg', 'Karpasi.jpg',
    'Karpoora.jpg', 'Karpooraka.jpg', 'Karpuraka.jpg', 'Karshya.jpg', 'Kartta.jpg',
    'Karttaka.jpg', 'Karuka.jpg', 'Karumbuka.jpg', 'Karuna.jpg', 'Karunaka.jpg',
    'Karvatika.jpg', 'Karvatilaka.jpg', 'Karvatini.jpg', 'Karvira.jpg', 'Karviraka.jpg',
    'Karvirapushpa.jpg', 'Karviravrinta.jpg', 'Karviravrintatma.jpg', 'Karviri.jpg', 'Karvirini.jpg',
    'Karvudara.jpg', 'Karvudaraka.jpg', 'Karvudaravrinta.jpg', 'Karvudaravrintatma.jpg', 'Karvudari.jpg',
    'Kashaka.jpg', 'Kashamardaka.jpg', 'Kashamardika.jpg', 'Kashaya.jpg', 'Kashayaka.jpg',
    'Kashayavrinta.jpg', 'Kashayavrintatma.jpg', 'Kashayini.jpg', 'Kashi.jpg', 'Kashika.jpg',
    'Kashishtha.jpg', 'Kashmari.jpg', 'Kashmarika.jpg', 'Kashmiraka.jpg', 'Kasmari.jpg',
    'Kasmarika.jpg', 'Kataka.jpg', 'Kataka.jpg', 'Kataka.jpg', 'Katambhara.jpg',
    'Katambhara.jpg', 'Katambhara.jpg', 'Katantraka.jpg', 'Katphala.jpg', 'Katphalaka.jpg',
    'Katsarika.jpg', 'Kauchika.jpg', 'Kauchikavrinta.jpg', 'Kauchikavrintatma.jpg', 'Kaundinya.jpg',
    'Kaundinyaka.jpg', 'Kaundinyavrinta.jpg', 'Kaundinyavrintatma.jpg', 'Kaurava.jpg', 'Kausheya.jpg',
    'Kausheyaka.jpg', 'Kausheyavrinta.jpg', 'Kausheyavrintatma.jpg', 'Kautilya.jpg', 'Kautilyaka.jpg',
    'Kautilyavrinta.jpg', 'Kautilyavrintatma.jpg', 'Kavaca.jpg', 'Kavachini.jpg', 'Kavachinika.jpg',
    'Kavachitaka.jpg', 'Kavachitavrinta.jpg', 'Kavachitavrintatma.jpg', 'Kavaka.jpg', 'Kavaki.jpg',
    'Kavala.jpg', 'Kavika.jpg', 'Kavikavaca.jpg', 'Kavikavacavrinta.jpg', 'Kavikavacavrintatma.jpg',
    'Kavikavachini.jpg', 'Kavikavachinika.jpg', 'Kavikavachitaka.jpg', 'Kavikavachitavrinta.jpg', 'Kavikavachitavrintatma.jpg',
    'Kaviraja.jpg', 'Kavirajaka.jpg', 'Kavirajavrinta.jpg', 'Kavirajavrintatma.jpg', 'Kaviraji.jpg',
    'Kavirajika.jpg', 'Kavirajini.jpg', 'Kavirajitaka.jpg', 'Kavirajitavrinta.jpg', 'Kavirajitavrintatma.jpg',
    'Kavishvara.jpg', 'Kavishvaraka.jpg', 'Kavishvaravrinta.jpg', 'Kavishvaravrintatma.jpg', 'Kavishvari.jpg',
    'Kavishvarika.jpg', 'Kavishvarini.jpg', 'Kavishvaritaka.jpg', 'Kavishvaritavrinta.jpg', 'Kavishvaritavrintatma.jpg',
    'Kavya.jpg', 'Kavyaka.jpg', 'Kavyavrinta.jpg', 'Kavyavrintatma.jpg', 'Kavyika.jpg',
    'Kavyini.jpg', 'Kavyitaka.jpg', 'Kavyitavrinta.jpg', 'Kavyitavrintatma.jpg', 'Kesara.jpg',
    'Kesaraka.jpg', 'Kesaravrinta.jpg', 'Kesaravrintatma.jpg', 'Kesari.jpg', 'Kesarika.jpg',
    'Kesarini.jpg', 'Kesaritaka.jpg', 'Kesaritavrinta.jpg', 'Kesaritavrintatma.jpg', 'Kesha.jpg',
    'Keshaka.jpg', 'Keshala.jpg', 'Keshalaka.jpg', 'Kesham.jpg', 'Keshamaya.jpg',
    'Keshar.jpg', 'Keshara.jpg', 'Kesharaja.jpg', 'Kesharavrinta.jpg', 'Kesharavrintatma.jpg',
    'Keshari.jpg', 'Kesharika.jpg', 'Kesharini.jpg', 'Kesharitaka.jpg', 'Kesharitavrinta.jpg',
    'Kesharitavrintatma.jpg', 'Keshava.jpg', 'Keshavaka.jpg', 'Keshavavrinta.jpg', 'Keshavavrintatma.jpg',
    'Keshavi.jpg', 'Keshavika.jpg', 'Keshavini.jpg', 'Keshavitaka.jpg', 'Keshavitavrinta.jpg',
    'Keshavitavrintatma.jpg', 'Keshi.jpg', 'Keshika.jpg', 'Keshini.jpg', 'Keshitaka.jpg',
    'Keshitavrinta.jpg', 'Keshitavrintatma.jpg', 'Keshu.jpg', 'Keshuka.jpg', 'Keshula.jpg',
    'Keshumaya.jpg', 'Ketaka.jpg', 'Ketakapushpa.jpg', 'Ketakavrinta.jpg', 'Ketakavrintatma.jpg',
    'Ketaki.jpg', 'Ketakika.jpg', 'Ketakinika.jpg', 'Ketakipushpa.jpg', 'Ketakipushpaka.jpg',
    'Ketakivrinta.jpg', 'Ketakivrintatma.jpg', 'Ketana.jpg', 'Ketanaka.jpg', 'Ketanavrinta.jpg',
    'Ketanavrintatma.jpg', 'Ketani.jpg', 'Ketanika.jpg', 'Ketanini.jpg', 'Ketanitaka.jpg',
    'Ketanitavrinta.jpg', 'Ketanitavrintatma.jpg', 'Kethumaya.jpg', 'Ketumaya.jpg', 'Ketumayaka.jpg',
    'Ketumayavrinta.jpg', 'Ketumayavrintatma.jpg', 'Ketu.jpg', 'Ketuka.jpg', 'Ketumari.jpg',
    'Ketumarika.jpg', 'Ketumarivrinta.jpg', 'Ketumarivrintatma.jpg', 'Ketusha.jpg', 'Ketushaka.jpg',
    'Ketushavrinta.jpg', 'Ketushavrintatma.jpg', 'Ketushi.jpg', 'Ketushika.jpg', 'Ketushini.jpg',
    'Ketushitaka.jpg', 'Ketushitavrinta.jpg', 'Ketushitavrintatma.jpg', 'Khadi.jpg', 'Khadira.jpg',
    'Khadiraka.jpg', 'Khadiravrinta.jpg', 'Khadiravrintatma.jpg', 'Khadirini.jpg', 'Khala.jpg',
    'Khalaka.jpg', 'Khalapushpa.jpg', 'Khalapushpaka.jpg', 'Khalavrinta.jpg', 'Khalavrintatma.jpg',
    'Khalini.jpg', 'Khanaka.jpg', 'Khanavrinta.jpg', 'Khanavrintatma.jpg', 'Khandaka.jpg',
    'Khandalaka.jpg', 'Khandavrinta.jpg', 'Khandavrintatma.jpg', 'Khandini.jpg', 'Khanduka.jpg',
    'Khanilaka.jpg', 'Khanilavrinta.jpg', 'Khanilavrintatma.jpg', 'Khanjana.jpg', 'Khanjanaka.jpg',
    'Khanjanavrinta.jpg', 'Khanjanavrintatma.jpg', 'Khanji.jpg', 'Khanjika.jpg', 'Khanjini.jpg',
    'Khanjitaka.jpg', 'Khanjitavrinta.jpg', 'Khanjitavrintatma.jpg', 'Kharaka.jpg', 'Kharala.jpg',
    'Kharalaka.jpg', 'Kharalavrinta.jpg', 'Kharalavrintatma.jpg', 'Kharali.jpg', 'Kharalika.jpg',
    'Kharalini.jpg', 'Kharalitaka.jpg', 'Kharalitavrinta.jpg', 'Kharalitavrintatma.jpg', 'Khara.jpg',
    'Kharaka.jpg', 'Kharalaka.jpg', 'Kharalavrinta.jpg', 'Kharalavrintatma.jpg', 'Kharali.jpg',
    'Kharalika.jpg', 'Kharalini.jpg', 'Kharalitaka.jpg', 'Kharalitavrinta.jpg', 'Kharalitavrintatma.jpg',
    'Kharjura.jpg', 'Kharjuraka.jpg', 'Kharjuravrinta.jpg', 'Kharjuravrintatma.jpg', 'Kharjuri.jpg',
    'Kharjurika.jpg', 'Kharjurini.jpg', 'Kharjuritaka.jpg', 'Kharjuritavrinta.jpg', 'Kharjuritavrintatma.jpg',
    'Kharpushpa.jpg', 'Kharpushpaka.jpg', 'Kharpushpavrinta.jpg', 'Kharpushpavrintatma.jpg', 'Kharpushpi.jpg',
    'Kharpushpika.jpg', 'Kharpushpinika.jpg', 'Kharpushpitaka.jpg', 'Kharpushpitavrinta.jpg', 'Kharpushpitavrintatma.jpg',
    'Kharvrinta.jpg', 'Kharvrintatma.jpg', 'Kharvrinti.jpg', 'Kharvrintika.jpg', 'Kharvrintinika.jpg',
    'Kharvrintitaka.jpg', 'Kharvrintitavrinta.jpg', 'Kharvrintitavrintatma.jpg', 'Kharvuka.jpg', 'Kharvukaka.jpg',
    'Kharvukavrinta.jpg', 'Kharvukavrintatma.jpg', 'Kharvuki.jpg', 'Kharvukika.jpg', 'Kharvukini.jpg',
    'Kharvukitaka.jpg', 'Kharvukitavrinta.jpg', 'Kharvukitavrintatma.jpg', 'Khasa.jpg', 'Khasaka.jpg',
    'Khasavrinta.jpg', 'Khasavrintatma.jpg', 'Khasi.jpg', 'Khasika.jpg', 'Khasini.jpg',
    'Khasitaka.jpg', 'Khasitavrinta.jpg', 'Khasitavrintatma.jpg', 'Khaya.jpg', 'Khayaka.jpg',
    'Khayavrinta.jpg', 'Khayavrintatma.jpg', 'Khayi.jpg', 'Khayika.jpg', 'Khayini.jpg',
    'Khayitaka.jpg', 'Khayitavrinta.jpg', 'Khayitavrintatma.jpg', 'Khela.jpg', 'Khelaka.jpg',
    'Khelavrinta.jpg', 'Khelavrintatma.jpg', 'Kheli.jpg', 'Khelika.jpg', 'Khelini.jpg',
    'Khelitaka.jpg', 'Khelitavrinta.jpg', 'Khelitavrintatma.jpg', 'Kheta.jpg', 'Khetaka.jpg',
    'Khetavrinta.jpg', 'Khetavrintatma.jpg', 'Kheti.jpg', 'Khetika.jpg', 'Khetini.jpg',
    'Khetitaka.jpg', 'Khetitavrinta.jpg', 'Khetitavrintatma.jpg', 'Kheya.jpg', 'Kheyaka.jpg',
    'Kheyavrinta.jpg', 'Kheyavrintatma.jpg', 'Kheyi.jpg', 'Kheyika.jpg', 'Kheyini.jpg',
    'Kheyitaka.jpg', 'Kheyitavrinta.jpg', 'Kheyitavrintatma.jpg', 'Khira.jpg', 'Khiraka.jpg',
    'Khiravrinta.jpg', 'Khiravrintatma.jpg', 'Khiri.jpg', 'Khirika.jpg', 'Khirini.jpg',
    'Khiritaka.jpg', 'Khiritavrinta.jpg', 'Khiritavrintatma.jpg', 'Khoma.jpg', 'Khosha.jpg',
    'Khoshaka.jpg', 'Khoshavrinta.jpg', 'Khoshavrintatma.jpg', 'Khoshi.jpg', 'Khoshika.jpg',
    'Khoshini.jpg', 'Khoshitaka.jpg', 'Khoshitavrinta.jpg', 'Khoshitavrintatma.jpg', 'Khou.jpg',
    'Khouka.jpg', 'Khoukavrinta.jpg', 'Khoukavrintatma.jpg', 'Khouki.jpg', 'Khoukika.jpg',
    'Khoukini.jpg', 'Khoukitaka.jpg', 'Khoukitavrinta.jpg', 'Khoukitavrintatma.jpg', 'Khova.jpg',
    'Khovaka.jpg', 'Khovavrinta.jpg', 'Khovavrintatma.jpg', 'Khovi.jpg', 'Khovika.jpg',
    'Khovini.jpg', 'Khovitaka.jpg', 'Khovitavrinta.jpg', 'Khovitavrintatma.jpg', 'Khoya.jpg',
    'Khoyaka.jpg', 'Khoyavrinta.jpg', 'Khoyavrintatma.jpg', 'Khoyi.jpg', 'Khoyika.jpg',
    'Khoyini.jpg', 'Khoyitaka.jpg', 'Khoyitavrinta.jpg', 'Khoyitavrintatma.jpg', 'Khu.jpg',
    'Khuka.jpg', 'Khukavrinta.jpg', 'Khukavrintatma.jpg', 'Khuki.jpg', 'Khukika.jpg',
    'Khukini.jpg', 'Khukitaka.jpg', 'Khukitavrinta.jpg', 'Khukitavrintatma.jpg', 'Khula.jpg',
    'Khulaka.jpg', 'Khulavrinta.jpg', 'Khulavrintatma.jpg', 'Khuli.jpg', 'Khulika.jpg',
    'Khulini.jpg', 'Khulitaka.jpg', 'Khulitavrinta.jpg', 'Khulitavrintatma.jpg', 'Khuma.jpg',
    'Khumaka.jpg', 'Khumavrinta.jpg', 'Khumavrintatma.jpg', 'Khumi.jpg', 'Khumika.jpg',
    'Khumini.jpg', 'Khumitaka.jpg', 'Khumitavrinta.jpg', 'Khumitavrintatma.jpg', 'Khura.jpg',
    'Khuraka.jpg', 'Khuravrinta.jpg', 'Khuravrintatma.jpg', 'Khuri.jpg', 'Khurika.jpg',
    'Khurini.jpg', 'Khuritaka.jpg', 'Khuritavrinta.jpg', 'Khuritavrintatma.jpg', 'Khusha.jpg',
    'Khushaka.jpg', 'Khushavrinta.jpg', 'Khushavrintatma.jpg', 'Khushi.jpg', 'Khushika.jpg',
    'Khushini.jpg', 'Khushitaka.jpg', 'Khushitavrinta.jpg', 'Khushitavrintatma.jpg', 'Khuta.jpg',
    'Khutaka.jpg', 'Khutavrinta.jpg', 'Khutavrintatma.jpg', 'Khuti.jpg', 'Khutika.jpg',
    'Khutini.jpg', 'Khutitaka.jpg', 'Khutitavrinta.jpg', 'Khutitavrintatma.jpg', 'Khuva.jpg',
    'Khuvaka.jpg', 'Khuvavrinta.jpg', 'Khuvavrintatma.jpg', 'Khuvi.jpg', 'Khuvika.jpg',
    'Khuvini.jpg', 'Khuvitaka.jpg', 'Khuvitavrinta.jpg', 'Khuvitavrintatma.jpg', 'Khuya.jpg',
    'Khuyaka.jpg', 'Khuyavrinta.jpg', 'Khuyavrintatma.jpg', 'Khuyi.jpg', 'Khuyika.jpg',
    'Khuyini.jpg', 'Khuyitaka.jpg', 'Khuyitavrinta.jpg', 'Khuyitavrintatma.jpg', 'Ki.jpg',
    'Kirata.jpg', 'Kiratatiktaka.jpg', 'Kiratatikti.jpg', 'Kiratatiktika.jpg', 'Kiratatikti.jpg',
    'Kiratatiktaka.jpg', 'Kiratatiktavrinta.jpg', 'Kiratatiktavrintatma.jpg', 'Kiratatikti.jpg', 'Kiratatiktika.jpg',
    'Kiratatiktinika.jpg', 'Kiratatiktitaka.jpg', 'Kiratatiktitavrinta.jpg', 'Kiratatiktitavrintatma.jpg', 'Kiratatiktuka.jpg',
    'Kiratatiktukaka.jpg', 'Kiratatiktukavrinta.jpg', 'Kiratatiktukavrintatma.jpg', 'Kiratatiktuki.jpg', 'Kiratatiktukika.jpg',
    'Kiratatiktukini.jpg', 'Kiratatiktukitaka.jpg', 'Kiratatiktukitavrinta.jpg', 'Kiratatiktukitavrintatma.jpg', 'Kiratatiktuma.jpg',
    'Kiratatiktumaka.jpg', 'Kiratatiktumavrinta.jpg', 'Kiratatiktumavrintatma.jpg', 'Kiratatiktumi.jpg', 'Kiratatiktumika.jpg',
    'Kiratatiktumini.jpg', 'Kiratatiktumitaka.jpg', 'Kiratatiktumitavrinta.jpg', 'Kiratatiktumitavrintatma.jpg', 'Kiratatiktuna.jpg',
    'Kiratatiktunaka.jpg', 'Kiratatiktunavrinta.jpg', 'Kiratatiktunavrintatma.jpg', 'Kiratatiktuni.jpg', 'Kiratatiktunika.jpg',
    'Kiratatiktunini.jpg', 'Kiratatiktunitaka.jpg', 'Kiratatiktunitavrinta.jpg', 'Kiratatiktunitavrintatma.jpg', 'Kiratatiktura.jpg',
    'Kiratatikturaka.jpg', 'Kiratatikturavrinta.jpg', 'Kiratatikturavrintatma.jpg', 'Kiratatikturi.jpg', 'Kiratatikturika.jpg',
    'Kiratatikturini.jpg', 'Kiratatikturitaka.jpg', 'Kiratatikturitavrinta.jpg', 'Kiratatikturitavrintatma.jpg', 'Kiratatiktusa.jpg',
    'Kiratatiktusaka.jpg', 'Kiratatiktusavrinta.jpg', 'Kiratatiktusavrintatma.jpg', 'Kiratatiktusi.jpg', 'Kiratatiktusika.jpg',
    'Kiratatiktusini.jpg', 'Kiratatiktusitaka.jpg', 'Kiratatiktusitavrinta.jpg', 'Kiratatiktusitavrintatma.jpg', 'Kiratatiktu.jpg',
    'Kiratatiktuka.jpg', 'Kiratatiktukavrinta.jpg', 'Kiratatiktukavrintatma.jpg', 'Kiratiktuka.jpg', 'Kiratiktukaka.jpg',
    'Kiratiktukavrinta.jpg', 'Kiratiktukavrintatma.jpg', 'Kiratiktuki.jpg', 'Kiratiktukika.jpg', 'Kiratiktukini.jpg',
    'Kiratiktukitaka.jpg', 'Kiratiktukitavrinta.jpg', 'Kiratiktukitavrintatma.jpg', 'Kiratiktuma.jpg', 'Kiratiktumaka.jpg',
    'Kiratiktumavrinta.jpg', 'Kiratiktumavrintatma.jpg', 'Kiratiktumi.jpg', 'Kiratiktumika.jpg', 'Kiratiktumini.jpg',
    'Kiratiktumitaka.jpg', 'Kiratiktumitavrinta.jpg', 'Kiratiktumitavrintatma.jpg', 'Kiratiktu.jpg', 'Kiratiktuka.jpg',
    'Kiratiktukavrinta.jpg', 'Kiratiktukavrintatma.jpg', 'Kiratiktuki.jpg', 'Kiratiktukika.jpg', 'Kiratiktukini.jpg',
    'Kiratiktukitaka.jpg', 'Kiratiktukitavrinta.jpg', 'Kiratiktukitavrintatma.jpg', 'Kiratiktuma.jpg', 'Kiratiktumaka.jpg',
    'Kiratiktumavrinta.jpg', 'Kiratiktumavrintatma.jpg', 'Kiratiktumi.jpg', 'Kiratiktumika.jpg', 'Kiratiktumini.jpg',
    'Kiratiktumitaka.jpg', 'Kiratiktumitavrinta.jpg', 'Kiratiktumitavrintatma.jpg', 'Kiratiktuna.jpg', 'Kiratiktunaka.jpg',
    'Kiratiktunavrinta.jpg', 'Kiratiktunavrintatma.jpg', 'Kiratiktuni.jpg', 'Kiratiktunika.jpg', 'Kiratiktunini.jpg',
    'Kiratiktunitaka.jpg', 'Kiratiktunitavrinta.jpg', 'Kiratiktunitavrintatma.jpg', 'Kiratiktura.jpg', 'Kiratikturaka.jpg',
    'Kiratikturavrinta.jpg', 'Kiratikturavrintatma.jpg', 'Kiratikturi.jpg', 'Kiratikturika.jpg', 'Kiratikturini.jpg',
    'Kiratikturitaka.jpg', 'Kiratikturitavrinta.jpg', 'Kiratikturitavrintatma.jpg', 'Kiratiktusa.jpg', 'Kiratiktusaka.jpg',
    'Kiratiktusavrinta.jpg', 'Kiratiktusavrintatma.jpg', 'Kiratiktusi.jpg', 'Kiratiktusika.jpg', 'Kiratiktusini.jpg',
    'Kiratiktusitaka.jpg', 'Kiratiktusitavrinta.jpg', 'Kiratiktusitavrintatma.jpg'
}

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def build_image_placeholder_svg(plant_name):
    """Build a small SVG placeholder for plants without a local image file."""
    safe_name = (plant_name or "Medicinal Plant")[:36]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1f6f43" />
      <stop offset="100%" stop-color="#8fcf6a" />
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#bg)" />
  <circle cx="300" cy="145" r="58" fill="rgba(255,255,255,0.16)" />
  <text x="300" y="160" text-anchor="middle" font-size="52">🌿</text>
  <text x="300" y="240" text-anchor="middle" font-size="28" fill="#ffffff" font-family="Arial, sans-serif">{safe_name}</text>
  <text x="300" y="278" text-anchor="middle" font-size="16" fill="#e7f8df" font-family="Arial, sans-serif">Image coming soon</text>
</svg>
""".strip()


def build_image_placeholder_data_uri(plant_name):
    """Return a data URI placeholder for frontend image tags."""
    return f"data:image/svg+xml;charset=UTF-8,{quote(build_image_placeholder_svg(plant_name))}"


def resolve_plant_image_url(plant):
    """Return a stable image URL for a plant record."""
    image_url = plant.get('image_url')
    if image_url:
        filename = os.path.basename(image_url)
        if os.path.exists(os.path.join(PLANT_IMAGE_DIR, filename)):
            return image_url
    return build_image_placeholder_data_uri(plant.get('common_name'))


def serialize_plant(row):
    """Convert a SQLite plant row into a frontend-safe dictionary."""
    plant = dict(row)
    plant['image_url'] = resolve_plant_image_url(plant)
    return plant


def serialize_plants(rows):
    """Serialize a list of SQLite plant rows consistently."""
    return [serialize_plant(row) for row in rows]

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
             "Indian subcontinent", "/static/images/plants/arjun.jpg"),
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
             "Japan", "/static/images/plants/amare.jpg"),
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
            
            # ========== TRADITIONAL CHINESE MEDICINE (TCM) PLANTS ==========
            ("Ginseng", "Panax ginseng", "Araliaceae", "Flowering Plants", "Herb",
             "Root used for energy, stress reduction, immune support, and vitality. Premier TCM adaptogen.",
             "China, Korea, Russia", "/static/images/plants/Ginseng.jpg"),
            ("Dong Quai", "Angelica sinensis", "Apiaceae", "Flowering Plants", "Herb",
             "Female ginseng used for menstrual disorders, blood health, and menopause symptoms.",
             "China", "/static/images/plants/Dong Quai.jpg"),
            ("Astragalus", "Astragalus membranaceus", "Fabaceae", "Flowering Plants", "Herb",
             "Qi tonic used for immune support, fatigue, and digestive health in TCM.",
             "China, Mongolia", "/static/images/plants/Astragalus.jpg"),
            ("Licorice Root", "Glycyrrhiza uralensis", "Fabaceae", "Flowering Plants", "Herb",
             "Sweet root used for respiratory, digestive, and adrenal support in TCM.",
             "China, Central Asia", "/static/images/plants/Licorice Root.jpg"),
            ("Bupleurum", "Bupleurum chinense", "Apiaceae", "Flowering Plants", "Herb",
             "Liver tonic used for fever, liver disorders, and emotional balance in TCM.",
             "China", "/static/images/plants/Bupleurum.jpg"),
            ("Rehmannia", "Rehmannia glutinosa", "Orobanchaceae", "Flowering Plants", "Herb",
             "Blood tonic used for kidney health, anemia, and immune support.",
             "China", "/static/images/plants/Rehmannia.jpg"),
            ("Coptis", "Coptis chinensis", "Ranunculaceae", "Flowering Plants", "Herb",
             "Bitter herb used for digestive disorders, infections, and inflammation.",
             "China", "/static/images/plants/Coptis.jpg"),
            ("Poria", "Wolfiporia extensa", "Polyporaceae", "Fungi", "Mushroom",
             "Fungus used for diuretic effects, immune support, and digestive health.",
             "China", "/static/images/plants/Poria.jpg"),
            ("White Peony", "Paeonia lactiflora", "Paeoniaceae", "Flowering Plants", "Herb",
             "Root used for blood circulation, menstrual disorders, and liver health.",
             "China", "/static/images/plants/White Peony.jpg"),
            ("Chinese Skullcap", "Scutellaria baicalensis", "Lamiaceae", "Flowering Plants", "Herb",
             "Root used for inflammation, infections, allergies, and respiratory health.",
             "China, Russia", "/static/images/plants/Chinese Skullcap.jpg"),
            ("Codonopsis", "Codonopsis pilosula", "Campanulaceae", "Flowering Plants", "Climber",
             "Gentle ginseng substitute used for energy, digestion, and immune support.",
             "China", "/static/images/plants/Codonopsis.jpg"),
            ("Goji Berry", "Lycium barbarum", "Solanaceae", "Flowering Plants", "Shrub",
             "Wolfberry used for eye health, immune support, and longevity in TCM.",
             "China", "/static/images/plants/Goji Berry.jpg"),
            ("Schisandra", "Schisandra chinensis", "Schisandraceae", "Flowering Plants", "Climber",
             "Five-flavor berry used for liver, cognitive function, and stress adaptation.",
             "China, Russia", "/static/images/plants/Schisandra.jpg"),
            ("Epimedium", "Epimedium sagittatum", "Berberidaceae", "Flowering Plants", "Herb",
             "Horny goat weed used for sexual health, bone strength, and cardiovascular support.",
             "China", "/static/images/plants/Epimedium.jpg"),
            ("Chinese Yam", "Dioscorea polystachya", "Dioscoreaceae", "Flowering Plants", "Climber",
             "Shan yao used for digestion, respiratory health, and kidney support.",
             "China", "/static/images/plants/Chinese Yam.jpg"),
            ("Job's Tears", "Coix lacryma-jobi", "Poaceae", "Grasses", "Grass",
             "Yi yi ren used for digestive health, joint pain, and immune support.",
             "China, Southeast Asia", "/static/images/plants/Jobs Tears.jpg"),
            ("Chinese Motherwort", "Leonurus japonicus", "Lamiaceae", "Flowering Plants", "Herb",
             "Yi mu cao used for menstrual disorders, cardiovascular health, and anxiety.",
             "China, Asia", "/static/images/plants/Chinese Motherwort.jpg"),
            ("Sichuan Lovage", "Ligusticum striatum", "Apiaceae", "Flowering Plants", "Herb",
             "Chuan xiong used for blood circulation, headaches, and menstrual disorders.",
             "China", "/static/images/plants/Sichuan Lovage.jpg"),
            ("Chinese Rhubarb", "Rheum palmatum", "Polygonaceae", "Flowering Plants", "Herb",
             "Da huang used for constipation, digestion, and blood purification.",
             "China", "/static/images/plants/Chinese Rhubarb.jpg"),
            ("Cinnamon Twig", "Cinnamomum cassia", "Lauraceae", "Flowering Plants", "Tree",
             "Gui zhi used for colds, circulation, and menstrual disorders in TCM.",
             "China, Southeast Asia", "/static/images/plants/Cinnamon Twig.jpg"),
            ("Eucommia", "Eucommia ulmoides", "Eucommiaceae", "Flowering Plants", "Tree",
             "Du zhong used for kidney health, bone strength, and hypertension.",
             "China", "/static/images/plants/Eucommia.jpg"),
            ("Morus Root", "Morus alba", "Moraceae", "Flowering Plants", "Tree",
             "Sang bai pi used for cough, asthma, and fluid retention.",
             "China", "/static/images/plants/Morus Root.jpg"),
            ("Trichosanthes", "Trichosanthes kirilowii", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Gua lou used for chest congestion, constipation, and breast health.",
             "China", "/static/images/plants/Trichosanthes.jpg"),
            ("Fritillaria", "Fritillaria cirrhosa", "Liliaceae", "Flowering Plants", "Herb",
             "Bei mu used for cough, phlegm, and respiratory conditions.",
             "China, Himalayas", "/static/images/plants/Fritillaria.jpg"),
            ("Platycodon", "Platycodon grandiflorus", "Campanulaceae", "Flowering Plants", "Herb",
             "Jie geng used for cough, sore throat, and lung abscesses.",
             "China, Korea, Japan", "/static/images/plants/Platycodon.jpg"),
            ("Pinellia", "Pinellia ternata", "Araceae", "Flowering Plants", "Herb",
             "Ban xia used for nausea, cough, and phlegm reduction in TCM.",
             "China, Japan", "/static/images/plants/Pinellia.jpg"),
            ("Atractylodes", "Atractylodes macrocephala", "Asteraceae", "Flowering Plants", "Herb",
             "Bai zhu used for digestion, fluid retention, and immune support.",
             "China", "/static/images/plants/Atractylodes.jpg"),
            ("Phellodendron", "Phellodendron amurense", "Rutaceae", "Flowering Plants", "Tree",
             "Huang bai used for infections, inflammation, and damp-heat conditions.",
             "China", "/static/images/plants/Phellodendron.jpg"),
            ("Gardenia", "Gardenia jasminoides", "Rubiaceae", "Flowering Plants", "Shrub",
             "Zhi zi used for anxiety, insomnia, bleeding, and inflammation.",
             "China, Asia", "/static/images/plants/Gardenia.jpg"),
            ("Scrophularia", "Scrophularia ningpoensis", "Scrophulariaceae", "Flowering Plants", "Herb",
             "Xuan shen used for fever, constipation, and throat inflammation.",
             "China", "/static/images/plants/Scrophularia.jpg"),
            ("Isatis Root", "Isatis tinctoria", "Brassicaceae", "Flowering Plants", "Herb",
             "Ban lan gen used for viral infections, fever, and throat inflammation.",
             "China, Europe", "/static/images/plants/Isatis Root.jpg"),
            ("Honeysuckle", "Lonicera japonica", "Caprifoliaceae", "Flowering Plants", "Climber",
             "Jin yin hua used for fever, infections, and detoxification.",
             "China, Asia", "/static/images/plants/Honeysuckle.jpg"),
            ("Forsythia", "Forsythia suspensa", "Oleaceae", "Flowering Plants", "Shrub",
             "Lian qiao used for fever, infections, and heart health.",
             "China", "/static/images/plants/Forsythia.jpg"),
            ("Burdock Fruit", "Arctium lappa", "Asteraceae", "Flowering Plants", "Herb",
             "Niu bang zi used for colds, throat infections, and skin conditions.",
             "Europe, Asia", "/static/images/plants/Burdock Fruit.jpg"),
            ("Vitex", "Vitex agnus-castus", "Lamiaceae", "Flowering Plants", "Shrub",
             "Chaste tree used for menstrual disorders, PMS, and hormonal balance.",
             "Mediterranean, Asia", "/static/images/plants/Vitex.jpg"),
            ("Cyperus", "Cyperus rotundus", "Cyperaceae", "Grasses", "Grass",
             "Xiang fu used for menstrual disorders, digestive issues, and liver stagnation.",
             "China, Worldwide", "/static/images/plants/Cyperus.jpg"),
            ("Lindera", "Lindera aggregata", "Lauraceae", "Flowering Plants", "Shrub",
             "Wu yao used for abdominal pain, urinary issues, and menstrual disorders.",
             "China, Japan", "/static/images/plants/Lindera.jpg"),
            ("Magnolia Bark", "Magnolia officinalis", "Magnoliaceae", "Flowering Plants", "Tree",
             "Hou po used for digestive disorders, anxiety, and respiratory congestion.",
             "China", "/static/images/plants/Magnolia Bark.jpg"),
            ("Amomum", "Amomum villosum", "Zingiberaceae", "Flowering Plants", "Herb",
             "Sha ren used for digestive disorders, nausea, and morning sickness.",
             "China, Southeast Asia", "/static/images/plants/Amomum.jpg"),
            ("Cardamom", "Elettaria cardamomum", "Zingiberaceae", "Flowering Plants", "Herb",
             "Bai dou kou used for digestive disorders, nausea, and dampness.",
             "India, Sri Lanka", "/static/images/plants/Cardamom.jpg"),
            ("Aucklandia", "Aucklandia lappa", "Asteraceae", "Flowering Plants", "Herb",
             "Mu xiang used for abdominal pain, diarrhea, and digestive stagnation.",
             "China, India", "/static/images/plants/Aucklandia.jpg"),
            ("Melia", "Melia azedarach", "Meliaceae", "Flowering Plants", "Tree",
             "Ku lian zi used for parasitic infections, pain, and skin conditions.",
             "China, India", "/static/images/plants/Melia.jpg"),
            ("Quisqualis", "Quisqualis indica", "Combretaceae", "Flowering Plants", "Climber",
             "Shi jun zi used for parasitic infections, especially roundworms.",
             "China, Southeast Asia", "/static/images/plants/Quisqualis.jpg"),
            ("Pumpkin Seed", "Cucurbita pepo", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Nan gua zi used for parasitic infections and prostate health.",
             "Americas, Worldwide", "/static/images/plants/Pumpkin Seed.jpg"),
            ("Areca Nut", "Areca catechu", "Arecaceae", "Palms", "Palm",
             "Bin lang used for parasitic infections, digestion, and as a stimulant.",
             "Southeast Asia", "/static/images/plants/Areca Nut.jpg"),
            ("Torreya", "Torreya grandis", "Taxaceae", "Conifers", "Tree",
             "Fei zi used for parasitic infections, cough, and constipation.",
             "China", "/static/images/plants/Torreya.jpg"),
            ("Rangoon Creeper", "Combretum indicum", "Combretaceae", "Flowering Plants", "Climber",
             "Shi jun zi used for parasitic infections and skin conditions.",
             "Southeast Asia", "/static/images/plants/Rangoon Creeper.jpg"),
            ("Agrimony", "Agrimonia pilosa", "Rosaceae", "Flowering Plants", "Herb",
             "Xian he cao used for bleeding disorders, parasites, and skin conditions.",
             "China, Asia", "/static/images/plants/Agrimony.jpg"),
            ("Sophora Flower", "Sophora japonica", "Fabaceae", "Flowering Plants", "Tree",
             "Huai hua used for bleeding disorders, especially hemorrhoids.",
             "China, Korea, Japan", "/static/images/plants/Sophora Flower.jpg"),
            ("Sanguisorba", "Sanguisorba officinalis", "Rosaceae", "Flowering Plants", "Herb",
             "Di yu used for bleeding disorders, burns, and skin conditions.",
             "Europe, Asia", "/static/images/plants/Sanguisorba.jpg"),
            ("Platycladus", "Platycladus orientalis", "Cupressaceae", "Conifers", "Tree",
             "Ce bai ye used for bleeding disorders, cough, and hair health.",
             "China, Korea", "/static/images/plants/Platycladus.jpg"),
            ("Imperata", "Imperata cylindrica", "Poaceae", "Grasses", "Grass",
             "Bai mao gen used for bleeding, urinary disorders, and fever.",
             "Tropical regions", "/static/images/plants/Imperata.jpg"),
            ("Bletilla", "Bletilla striata", "Orchidaceae", "Flowering Plants", "Herb",
             "Bai ji used for bleeding, wounds, and tissue regeneration.",
             "China, Japan", "/static/images/plants/Bletilla.jpg"),
            ("Typha", "Typha angustifolia", "Typhaceae", "Flowering Plants", "Herb",
             "Pu huang used for bleeding, menstrual disorders, and pain.",
             "Worldwide", "/static/images/plants/Typha.jpg"),
            ("Rubia", "Rubia cordifolia", "Rubiaceae", "Flowering Plants", "Climber",
             "Qian cao gen used for bleeding, menstrual disorders, and circulation.",
             "Europe, Asia", "/static/images/plants/Rubia.jpg"),
            ("Galla Chinensis", "Rhus chinensis", "Anacardiaceae", "Flowering Plants", "Tree",
             "Wu bei zi used for diarrhea, bleeding, and excessive sweating.",
             "China", "/static/images/plants/Galla Chinensis.jpg"),
            ("Pomegranate Husk", "Punica granatum", "Lythraceae", "Flowering Plants", "Tree",
             "Shi liu pi used for diarrhea, parasites, and bleeding.",
             "Middle East, Mediterranean", "/static/images/plants/Pomegranate Husk.jpg"),
            ("Toon Bark", "Toona sinensis", "Meliaceae", "Flowering Plants", "Tree",
             "Chun pi used for diarrhea, bleeding, and parasites.",
             "China", "/static/images/plants/Toon Bark.jpg"),
            ("Poppy Capsule", "Papaver somniferum", "Papaveraceae", "Flowering Plants", "Herb",
             "Ying su ke used for diarrhea, cough, and pain relief.",
             "Mediterranean, Asia", "/static/images/plants/Poppy Capsule.jpg"),
            ("Myristica", "Myristica fragrans", "Myristicaceae", "Flowering Plants", "Tree",
             "Rou dou kou used for diarrhea, digestion, and warming.",
             "Southeast Asia", "/static/images/plants/Myristica.jpg"),
            
            # ========== WESTERN & EUROPEAN HERBAL MEDICINE ==========
            ("St. John's Wort", "Hypericum perforatum", "Hypericaceae", "Flowering Plants", "Herb",
             "Used for depression, anxiety, wound healing, and nerve pain. Top herbal antidepressant.",
             "Europe, Asia, Worldwide", "/static/images/plants/St Johns Wort.jpg"),
            ("Echinacea", "Echinacea purpurea", "Asteraceae", "Flowering Plants", "Herb",
             "Purple coneflower used for immune support, colds, flu, and wound healing.",
             "North America", "/static/images/plants/Echinacea.jpg"),
            ("Milk Thistle", "Silybum marianum", "Asteraceae", "Flowering Plants", "Herb",
             "Used for liver detoxification, gallbladder health, and mushroom poisoning.",
             "Mediterranean, Worldwide", "/static/images/plants/Milk Thistle.jpg"),
            ("Ginkgo Biloba", "Ginkgo biloba", "Ginkgoaceae", "Gymnosperms", "Tree",
             "Living fossil used for memory, circulation, cognitive function, and tinnitus.",
             "China, Worldwide", "/static/images/plants/Ginkgo Biloba.jpg"),
            ("Saw Palmetto", "Serenoa repens", "Arecaceae", "Palms", "Palm",
             "Used for prostate health, BPH, hair loss, and urinary function in men.",
             "North America", "/static/images/plants/Saw Palmetto.jpg"),
            ("Valerian Root", "Valeriana officinalis", "Caprifoliaceae", "Flowering Plants", "Herb",
             "Used for insomnia, anxiety, stress, and as a natural sedative.",
             "Europe, Asia", "/static/images/plants/Valerian Root.jpg"),
            ("Passionflower", "Passiflora incarnata", "Passifloraceae", "Flowering Plants", "Climber",
             "Used for anxiety, insomnia, ADHD, and nervous system disorders.",
             "Americas", "/static/images/plants/Passionflower.jpg"),
            ("Chamomile", "Matricaria chamomilla", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, anxiety, sleep, skin conditions, and inflammation.",
             "Europe, Worldwide", "/static/images/plants/Chamomile.jpg"),
            ("Peppermint", "Mentha piperita", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for digestion, IBS, headaches, nausea, and respiratory congestion.",
             "Europe, Worldwide", "/static/images/plants/Peppermint.jpg"),
            ("Lavender", "Lavandula angustifolia", "Lamiaceae", "Flowering Plants", "Shrub",
             "Used for anxiety, sleep, skin healing, headaches, and aromatherapy.",
             "Mediterranean", "/static/images/plants/Lavender.jpg"),
            ("Elderberry", "Sambucus nigra", "Adoxaceae", "Flowering Plants", "Shrub",
             "Used for colds, flu, immune support, and viral infections.",
             "Europe, North America", "/static/images/plants/Elderberry.jpg"),
            ("Cranberry", "Vaccinium macrocarpon", "Ericaceae", "Flowering Plants", "Shrub",
             "Used for UTIs, kidney health, and urinary tract infections prevention.",
             "North America", "/static/images/plants/Cranberry.jpg"),
            ("Hawthorn", "Crataegus laevigata", "Rosaceae", "Flowering Plants", "Tree",
             "Used for heart health, blood pressure, cholesterol, and angina.",
             "Europe, North America", "/static/images/plants/Hawthorn.jpg"),
            ("Hops", "Humulus lupulus", "Cannabaceae", "Flowering Plants", "Climber",
             "Used for anxiety, insomnia, digestion, and menopause symptoms.",
             "Europe, North America", "/static/images/plants/Hops.jpg"),
            ("Goldenseal", "Hydrastis canadensis", "Ranunculaceae", "Flowering Plants", "Herb",
             "Used for infections, digestive disorders, and immune support.",
             "North America", "/static/images/plants/Goldenseal.jpg"),
            ("Black Cohosh", "Actaea racemosa", "Ranunculaceae", "Flowering Plants", "Herb",
             "Used for menopause symptoms, hot flashes, PMS, and menstrual cramps.",
             "North America", "/static/images/plants/Black Cohosh.jpg"),
            ("Blue Cohosh", "Caulophyllum thalictroides", "Berberidaceae", "Flowering Plants", "Herb",
             "Used for menstrual disorders, labor induction, and gynecological issues.",
             "North America", "/static/images/plants/Blue Cohosh.jpg"),
            ("Wild Yam", "Dioscorea villosa", "Dioscoreaceae", "Flowering Plants", "Climber",
             "Used for menstrual cramps, menopause, digestive disorders, and inflammation.",
             "North America", "/static/images/plants/Wild Yam.jpg"),
            ("Dandelion", "Taraxacum officinale", "Asteraceae", "Flowering Plants", "Herb",
             "Used for liver detox, digestion, diuretic effects, and skin conditions.",
             "Europe, Worldwide", "/static/images/plants/Dandelion.jpg"),
            ("Burdock", "Arctium lappa", "Asteraceae", "Flowering Plants", "Herb",
             "Used for blood purification, skin conditions, digestion, and arthritis.",
             "Europe, Asia", "/static/images/plants/Burdock.jpg"),
            ("Nettle", "Urtica dioica", "Urticaceae", "Flowering Plants", "Herb",
             "Used for allergies, arthritis, prostate, and as a nutritive tonic.",
             "Europe, Worldwide", "/static/images/plants/Nettle.jpg"),
            ("Red Clover", "Trifolium pratense", "Fabaceae", "Flowering Plants", "Herb",
             "Used for menopause, bone health, blood purification, and cancer support.",
             "Europe, Asia", "/static/images/plants/Red Clover.jpg"),
            ("Yarrow", "Achillea millefolium", "Asteraceae", "Flowering Plants", "Herb",
             "Used for wounds, bleeding, fever, digestion, and menstrual disorders.",
             "Europe, Asia", "/static/images/plants/Yarrow.jpg"),
            ("Calendula", "Calendula officinalis", "Asteraceae", "Flowering Plants", "Herb",
             "Used for wound healing, skin inflammation, and digestive health.",
             "Mediterranean", "/static/images/plants/Calendula.jpg"),
            ("Plantain Leaf", "Plantago major", "Plantaginaceae", "Flowering Plants", "Herb",
             "Used for wounds, insect bites, digestive disorders, and respiratory issues.",
             "Worldwide", "/static/images/plants/Plantain Leaf.jpg"),
            ("Comfrey", "Symphytum officinale", "Boraginaceae", "Flowering Plants", "Herb",
             "Used for wound healing, bone fractures, bruises, and skin conditions.",
             "Europe, Asia", "/static/images/plants/Comfrey.jpg"),
            ("Chickweed", "Stellaria media", "Caryophyllaceae", "Flowering Plants", "Herb",
             "Used for skin conditions, weight loss, digestion, and inflammation.",
             "Europe, Worldwide", "/static/images/plants/Chickweed.jpg"),
            ("Mullein", "Verbascum thapsus", "Scrophulariaceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, cough, ear infections, and inflammation.",
            "Europe, Asia", "/static/images/plants/Mullein.jpg"),
            ("Thyme", "Thymus vulgaris", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for respiratory infections, cough, digestion, and antimicrobial action.",
             "Mediterranean", "/static/images/plants/Thyme.jpg"),
            ("Sage", "Salvia officinalis", "Lamiaceae", "Flowering Plants", "Shrub",
             "Used for memory, sore throat, digestion, menopause, and inflammation.",
             "Mediterranean", "/static/images/plants/Sage.jpg"),
            ("Rosemary", "Rosmarinus officinalis", "Lamiaceae", "Flowering Plants", "Shrub",
             "Used for memory, circulation, digestion, and as an antioxidant.",
             "Mediterranean", "/static/images/plants/Rosemary.jpg"),
            ("Oregano", "Origanum vulgare", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for infections, digestion, respiratory conditions, and as an antioxidant.",
             "Mediterranean", "/static/images/plants/Oregano.jpg"),
            ("Basil", "Ocimum basilicum", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for digestion, stress, inflammation, and as an antimicrobial.",
             "Tropical Asia, Worldwide", "/static/images/plants/Basil.jpg"),
            ("Parsley", "Petroselinum crispum", "Apiaceae", "Flowering Plants", "Herb",
             "Used for kidney health, digestion, diuretic effects, and as a vitamin source.",
             "Mediterranean", "/static/images/plants/Parsley.jpg"),
            ("Cilantro", "Coriandrum sativum", "Apiaceae", "Flowering Plants", "Herb",
             "Used for digestion, detoxification, cholesterol, and as an antimicrobial.",
             "Mediterranean, Worldwide", "/static/images/plants/Cilantro.jpg"),
            ("Fennel", "Foeniculum vulgare", "Apiaceae", "Flowering Plants", "Herb",
             "Used for digestion, colic, respiratory conditions, and milk production.",
             "Mediterranean", "/static/images/plants/Fennel.jpg"),
            ("Anise", "Pimpinella anisum", "Apiaceae", "Flowering Plants", "Herb",
             "Used for cough, digestion, colic, and as an expectorant.",
             "Mediterranean, Middle East", "/static/images/plants/Anise.jpg"),
            ("Caraway", "Carum carvi", "Apiaceae", "Flowering Plants", "Herb",
             "Used for digestion, colic, bloating, and respiratory conditions.",
             "Europe, Asia", "/static/images/plants/Caraway.jpg"),
            ("Dill", "Anethum graveolens", "Apiaceae", "Flowering Plants", "Herb",
             "Used for digestion, colic, insomnia, and respiratory conditions.",
             "Mediterranean, Europe", "/static/images/plants/Dill.jpg"),
            ("Tarragon", "Artemisia dracunculus", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestion, appetite stimulation, and as an antimicrobial.",
             "Central Asia, Europe", "/static/images/plants/Tarragon.jpg"),
            ("Marjoram", "Origanum majorana", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for digestion, menstrual disorders, and respiratory conditions.",
             "Mediterranean", "/static/images/plants/Marjoram.jpg"),
            ("Lemon Balm", "Melissa officinalis", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for anxiety, sleep, digestion, cold sores, and cognitive function.",
             "Mediterranean", "/static/images/plants/Lemon Balm.jpg"),
            ("Catnip", "Nepeta cataria", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for anxiety, sleep, digestion, colic, and fever reduction.",
             "Europe, Asia", "/static/images/plants/Catnip.jpg"),
            ("Skullcap", "Scutellaria lateriflora", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for anxiety, nervous tension, insomnia, and withdrawal symptoms.",
             "North America", "/static/images/plants/Skullcap.jpg"),
            ("California Poppy", "Eschscholzia californica", "Papaveraceae", "Flowering Plants", "Herb",
             "Used for anxiety, insomnia, pain, and nervous disorders.",
             "North America", "/static/images/plants/California Poppy.jpg"),
            ("Kava Kava", "Piper methysticum", "Piperaceae", "Flowering Plants", "Shrub",
             "Used for anxiety, stress, insomnia, and muscle relaxation.",
             "Pacific Islands", "/static/images/plants/Kava Kava.jpg"),
            ("Kratom", "Mitragyna speciosa", "Rubiaceae", "Flowering Plants", "Tree",
             "Used for pain, energy, opioid withdrawal, and mood enhancement.",
             "Southeast Asia", "/static/images/plants/Kratom.jpg"),
            ("Willow Bark", "Salix alba", "Salicaceae", "Flowering Plants", "Tree",
             "Natural aspirin source used for pain, inflammation, fever, and headaches.",
             "Europe, Asia", "/static/images/plants/Willow Bark.jpg"),
            ("Devil's Claw", "Harpagophytum procumbens", "Pedaliaceae", "Flowering Plants", "Herb",
             "Used for arthritis, back pain, inflammation, and digestive disorders.",
             "Africa", "/static/images/plants/Devils Claw.jpg"),
            ("Boswellia", "Boswellia serrata", "Burseraceae", "Flowering Plants", "Tree",
             "Indian frankincense used for arthritis, inflammation, and asthma.",
             "India, Africa", "/static/images/plants/Boswellia.jpg"),
            ("Arnica", "Arnica montana", "Asteraceae", "Flowering Plants", "Herb",
             "Used for bruises, sprains, muscle pain, and inflammation. External use only.",
             "Europe, North America", "/static/images/plants/Arnica.jpg"),
            ("Rue", "Ruta graveolens", "Rutaceae", "Flowering Plants", "Herb",
             "Used for menstrual disorders, arthritis, and as a digestive stimulant.",
             "Mediterranean", "/static/images/plants/Rue.jpg"),
            ("Wormwood", "Artemisia absinthium", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestion, parasites, appetite loss, and liver conditions.",
             "Europe, Asia", "/static/images/plants/Wormwood.jpg"),
            ("Mugwort", "Artemisia vulgaris", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestion, menstrual disorders, and as a dream enhancer.",
             "Europe, Asia", "/static/images/plants/Mugwort.jpg"),
            ("Sweet Annie", "Artemisia annua", "Asteraceae", "Flowering Plants", "Herb",
             "Source of artemisinin used for malaria and fever reduction.",
             "China, Worldwide", "/static/images/plants/Sweet Annie.jpg"),
            ("Elecampane", "Inula helenium", "Asteraceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, cough, digestion, and as an expectorant.",
             "Europe, Asia", "/static/images/plants/Elecampane.jpg"),
            (" Coltsfoot", "Tussilago farfara", "Asteraceae", "Flowering Plants", "Herb",
             "Used for cough, asthma, bronchitis, and respiratory conditions.",
             "Europe, Asia", "/static/images/plants/Coltsfoot.jpg"),
            ("Hyssop", "Hyssopus officinalis", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, digestion, and as an antimicrobial.",
             "Mediterranean", "/static/images/plants/Hyssop.jpg"),
            ("Lungwort", "Pulmonaria officinalis", "Boraginaceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, cough, and bronchitis.",
             "Europe", "/static/images/plants/Lungwort.jpg"),
            ("Ground Ivy", "Glechoma hederacea", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, digestion, and as a diuretic.",
             "Europe, Asia", "/static/images/plants/Ground Ivy.jpg"),
            ("Self Heal", "Prunella vulgaris", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for wounds, inflammation, sore throat, and viral infections.",
             "Worldwide", "/static/images/plants/Self Heal.jpg"),
            ("Horehound", "Marrubium vulgare", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for cough, respiratory conditions, digestion, and diabetes.",
             "Europe, Asia", "/static/images/plants/Horehound.jpg"),
            ("Licorice", "Glycyrrhiza glabra", "Fabaceae", "Flowering Plants", "Herb",
             "European licorice used for digestion, cough, adrenal support.",
             "Europe, Asia", "/static/images/plants/Licorice.jpg"),
            ("Slippery Elm", "Ulmus rubra", "Ulmaceae", "Flowering Plants", "Tree",
             "Used for digestive disorders, sore throat, and skin conditions.",
             "North America", "/static/images/plants/Slippery Elm.jpg"),
            ("Marshmallow Root", "Althaea officinalis", "Malvaceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, sore throat, and skin inflammation.",
             "Europe, Asia", "/static/images/plants/Marshmallow Root.jpg"),
            ("Irish Moss", "Chondrus crispus", "Gigartinaceae", "Algae", "Seaweed",
             "Used for respiratory conditions, digestion, and as a thickening agent.",
             "Atlantic Coast", "/static/images/plants/Irish Moss.jpg"),
            ("Bladderwrack", "Fucus vesiculosus", "Fucaceae", "Algae", "Seaweed",
             "Used for thyroid health, weight loss, and iodine supplementation.",
             "North Atlantic", "/static/images/plants/Bladderwrack.jpg"),
            ("Dulse", "Palmaria palmata", "Palmariaceae", "Algae", "Seaweed",
             "Nutritive seaweed used for thyroid, minerals, and as a food.",
             "North Atlantic", "/static/images/plants/Dulse.jpg"),
            ("Wakame", "Undaria pinnatifida", "Alariaceae", "Algae", "Seaweed",
             "Japanese seaweed used for thyroid, minerals, and cardiovascular health.",
             "Japan, Korea", "/static/images/plants/Wakame.jpg"),
            ("Nori", "Porphyra umbilicalis", "Bangiaceae", "Algae", "Seaweed",
             "Edible seaweed used for nutrition, thyroid, and as a wrap for sushi.",
             "Japan, Worldwide", "/static/images/plants/Nori.jpg"),
            ("Hijiki", "Sargassum fusiforme", "Sargassaceae", "Algae", "Seaweed",
             "Japanese seaweed used for minerals, fiber, and detoxification.",
             "Japan, Korea", "/static/images/plants/Hijiki.jpg"),
            ("Arame", "Eisenia bicyclis", "Lessoniaceae", "Algae", "Seaweed",
             "Japanese kelp used for thyroid, minerals, and immune support.",
             "Japan", "/static/images/plants/Arame.jpg"),
            ("Kombu", "Saccharina japonica", "Laminariaceae", "Algae", "Seaweed",
             "Japanese kelp used for digestion, minerals, and umami flavor.",
             "Japan, Korea", "/static/images/plants/Kombu.jpg"),
            ("Sea Lettuce", "Ulva lactuca", "Ulvaceae", "Algae", "Seaweed",
             "Green seaweed used for nutrition, detoxification, and as a food.",
             "Worldwide", "/static/images/plants/Sea Lettuce.jpg"),
            ("Spirulina", "Arthrospira platensis", "Phormidiaceae", "Cyanobacteria", "Cyanobacteria",
             "Blue-green algae used for protein, immune support, and detoxification.",
             "Worldwide", "/static/images/plants/Spirulina.jpg"),
            ("Chlorella", "Chlorella vulgaris", "Chlorellaceae", "Green Algae", "Algae",
             "Green algae used for detoxification, immune support, and nutrition.",
             "Worldwide", "/static/images/plants/Chlorella.jpg"),
            ("Wheatgrass", "Triticum aestivum", "Poaceae", "Grasses", "Grass",
             "Young wheat shoots used for detoxification, nutrition, and energy.",
             "Worldwide", "/static/images/plants/Wheatgrass.jpg"),
            ("Barley Grass", "Hordeum vulgare", "Poaceae", "Grasses", "Grass",
             "Young barley shoots used for detoxification, nutrition, and alkalization.",
             "Worldwide", "/static/images/plants/Barley Grass.jpg"),
            ("Alfalfa", "Medicago sativa", "Fabaceae", "Flowering Plants", "Herb",
             "Used for nutrition, digestion, cholesterol, and menopause symptoms.",
             "Worldwide", "/static/images/plants/Alfalfa.jpg"),
            ("Bee Pollen", "Apis mellifera", "Apidae", "Flowering Plants", "Herb",
             "Used for energy, immune support, allergies, and athletic performance.",
             "Worldwide", "/static/images/plants/Bee Pollen.jpg"),
            ("Propolis", "Apis mellifera", "Apidae", "Flowering Plants", "Herb",
             "Bee resin used for immune support, infections, and wound healing.",
             "Worldwide", "/static/images/plants/Propolis.jpg"),
            ("Royal Jelly", "Apis mellifera", "Apidae", "Flowering Plants", "Herb",
             "Bee secretion used for longevity, energy, and immune support.",
             "Worldwide", "/static/images/plants/Royal Jelly.jpg"),
            ("Manuka Honey", "Leptospermum scoparium", "Myrtaceae", "Flowering Plants", "Tree",
             "Honey with antimicrobial properties used for wounds and infections.",
             "New Zealand, Australia", "/static/images/plants/Manuka Honey.jpg"),
            
            # ========== AFRICAN TRADITIONAL MEDICINE ==========
            ("African Potato", "Hypoxis hemerocallidea", "Hypoxidaceae", "Flowering Plants", "Herb",
             "Used for immune support, HIV/AIDS support, urinary tract infections, and cancer.",
             "Southern Africa", "/static/images/plants/African Potato.jpg"),
            ("Devil's Claw Root", "Harpagophytum zeyheri", "Pedaliaceae", "Flowering Plants", "Herb",
             "Used for arthritis, back pain, digestive disorders, and fever.",
             "Southern Africa", "/static/images/plants/Devils Claw Root.jpg"),
            ("Pelargonium", "Pelargonium sidoides", "Geraniaceae", "Flowering Plants", "Herb",
             "Umckaloabo used for respiratory infections, bronchitis, and sinusitis.",
             "South Africa", "/static/images/plants/Pelargonium.jpg"),
            ("Sutherlandia", "Sutherlandia frutescens", "Fabaceae", "Flowering Plants", "Shrub",
             "Cancer bush used for cancer, HIV/AIDS, immune support, and stress.",
             "Southern Africa", "/static/images/plants/Sutherlandia.jpg"),
            ("Cape Aloe", "Aloe ferox", "Asphodelaceae", "Succulents", "Succulent",
             "Used for constipation, skin conditions, and wound healing.",
             "South Africa", "/static/images/plants/Cape Aloe.jpg"),
            ("Bulbine", "Bulbine frutescens", "Asphodelaceae", "Succulents", "Succulent",
             "Used for wounds, burns, skin conditions, and eczema.",
             "South Africa", "/static/images/plants/Bulbine.jpg"),
            ("Pau d'Arco", "Tabebuia impetiginosa", "Bignoniaceae", "Flowering Plants", "Tree",
             "Lapacho used for cancer, infections, inflammation, and candida.",
             "South America", "/static/images/plants/Pau dArco.jpg"),
            ("Yohimbe", "Pausinystalia johimbe", "Rubiaceae", "Flowering Plants", "Tree",
             "Used for erectile dysfunction, athletic performance, and weight loss.",
             "West Africa", "/static/images/plants/Yohimbe.jpg"),
            ("Griffonia", "Griffonia simplicifolia", "Fabaceae", "Flowering Plants", "Shrub",
             "5-HTP source used for depression, anxiety, insomnia, and fibromyalgia.",
             "West Africa", "/static/images/plants/Griffonia.jpg"),
            ("Kigelia", "Kigelia africana", "Bignoniaceae", "Flowering Plants", "Tree",
             "Sausage tree used for skin conditions, breast firming, and infections.",
             "Africa", "/static/images/plants/Kigelia.jpg"),
            ("Moringa", "Moringa oleifera", "Moringaceae", "Flowering Plants", "Tree",
             "Drumstick tree used for nutrition, diabetes, inflammation, and malnutrition.",
             "Africa, Asia", "/static/images/plants/Moringa.jpg"),
            ("Baobab", "Adansonia digitata", "Malvaceae", "Flowering Plants", "Tree",
             "Superfruit used for vitamin C, digestion, immune support, and hydration.",
             "Africa", "/static/images/plants/Baobab.jpg"),
            ("Rooibos", "Aspalathus linearis", "Fabaceae", "Flowering Plants", "Shrub",
             "Red bush tea used for antioxidants, digestion, allergies, and heart health.",
             "South Africa", "/static/images/plants/Rooibos.jpg"),
            ("Honeybush", "Cyclopia genistoides", "Fabaceae", "Flowering Plants", "Shrub",
             "Used for antioxidants, menopause symptoms, and digestive disorders.",
             "South Africa", "/static/images/plants/Honeybush.jpg"),
            ("Buchu", "Agathosma betulina", "Rutaceae", "Flowering Plants", "Shrub",
             "Used for urinary tract infections, prostate, and digestive disorders.",
             "South Africa", "/static/images/plants/Buchu.jpg"),
            ("Wild Ginger", "Siphonochilus aethiopicus", "Zingiberaceae", "Flowering Plants", "Herb",
             "African ginger used for colds, flu, asthma, and pain relief.",
             "Southern Africa", "/static/images/plants/Wild Ginger.jpg"),
            ("Cancer Bush", "Lessertia frutescens", "Fabaceae", "Flowering Plants", "Shrub",
             "Same as Sutherlandia. Used for immune support and cancer.",
             "Southern Africa", "/static/images/plants/Cancer Bush.jpg"),
            ("African Wormwood", "Artemisia afra", "Asteraceae", "Flowering Plants", "Herb",
             "Wilde-als used for colds, flu, malaria, and digestive disorders.",
             "Africa", "/static/images/plants/African Wormwood.jpg"),
            ("Umckaloabo", "Pelargonium sidoides", "Geraniaceae", "Flowering Plants", "Herb",
             "Same as Pelargonium. Used for respiratory infections.",
             "South Africa", "/static/images/plants/Umckaloabo.jpg"),
            ("African Myrrh", "Commiphora africana", "Burseraceae", "Flowering Plants", "Tree",
             "Used for wounds, infections, and aromatic purposes.",
             "Africa", "/static/images/plants/African Myrrh.jpg"),
            ("Shea Tree", "Vitellaria paradoxa", "Sapotaceae", "Flowering Plants", "Tree",
             "Shea butter source used for skin care, cooking, and medicinal purposes.",
             "Africa", "/static/images/plants/Shea Tree.jpg"),
            ("Neem African", "Azadirachta indica", "Meliaceae", "Flowering Plants", "Tree",
             "Used for skin diseases, malaria, diabetes, and as insect repellent.",
             "Africa, India", "/static/images/plants/Neem African.jpg"),
            ("Acacia Senegal", "Acacia senegal", "Fabaceae", "Flowering Plants", "Tree",
             "Gum arabic source used for diabetes, digestive disorders, and as a prebiotic.",
             "Africa", "/static/images/plants/Acacia Senegal.jpg"),
            ("Ethiopian Banana", "Ensete ventricosum", "Musaceae", "Flowering Plants", "Herb",
             "False banana used for food, fiber, and traditional medicine.",
             "Ethiopia", "/static/images/plants/Ethiopian Banana.jpg"),
            ("Prunus Africana", "Prunus africana", "Rosaceae", "Flowering Plants", "Tree",
             "African cherry used for prostate health and BPH.",
             "Africa", "/static/images/plants/Prunus Africana.jpg"),
            ("Calabash", "Crescentia cujete", "Bignoniaceae", "Flowering Plants", "Tree",
             "Used for respiratory conditions, skin diseases, and as containers.",
             "Africa, Americas", "/static/images/plants/Calabash.jpg"),
            ("Physic Nut", "Jatropha curcas", "Euphorbiaceae", "Flowering Plants", "Shrub",
             "Used for wounds, constipation, and as biodiesel source.",
             "Central America, Africa", "/static/images/plants/Physic Nut.jpg"),
            ("Castor Oil Plant", "Ricinus communis", "Euphorbiaceae", "Flowering Plants", "Shrub",
             "Used for constipation, arthritis, and industrial applications.",
             "Africa, Asia", "/static/images/plants/Castor Oil Plant.jpg"),
            ("Bitter Leaf", "Vernonia amygdalina", "Asteraceae", "Flowering Plants", "Shrub",
             "Ewuro used for diabetes, malaria, fever, and digestive disorders.",
             "Africa", "/static/images/plants/Bitter Leaf.jpg"),
            ("Guinea Pepper", "Aframomum melegueta", "Zingiberaceae", "Flowering Plants", "Herb",
             "Grains of paradise used for digestive disorders, pain, and as spice.",
             "West Africa", "/static/images/plants/Guinea Pepper.jpg"),
            
            # ========== NATIVE AMERICAN MEDICINE ==========
            ("Black Walnut", "Juglans nigra", "Juglandaceae", "Flowering Plants", "Tree",
             "Used for parasites, fungal infections, skin conditions, and thyroid.",
             "North America", "/static/images/plants/Black Walnut.jpg"),
            ("White Willow", "Salix alba", "Salicaceae", "Flowering Plants", "Tree",
             "Used for pain, fever, inflammation, and as natural aspirin source.",
             "Europe, North America", "/static/images/plants/White Willow.jpg"),
            ("American Ginseng", "Panax quinquefolius", "Araliaceae", "Flowering Plants", "Herb",
             "Cooling ginseng used for stress, immune support, and fatigue.",
             "North America", "/static/images/plants/American Ginseng.jpg"),
            ("Poke Root", "Phytolacca americana", "Phytolaccaceae", "Flowering Plants", "Herb",
             "Used for lymphatic congestion, arthritis, and skin conditions. Toxic in high doses.",
             "North America", "/static/images/plants/Poke Root.jpg"),
            ("Osha Root", "Ligusticum porteri", "Apiaceae", "Flowering Plants", "Herb",
             "Bear medicine used for respiratory infections, altitude sickness, and immunity.",
             "North America", "/static/images/plants/Osha Root.jpg"),
            ("Bearberry", "Arctostaphylos uva-ursi", "Ericaceae", "Flowering Plants", "Shrub",
             "Uva ursi used for urinary tract infections, kidney stones, and diuretic.",
             "North America, Europe", "/static/images/plants/Bearberry.jpg"),
            ("Cascara Sagrada", "Frangula purshiana", "Rhamnaceae", "Flowering Plants", "Tree",
             "Sacred bark used for constipation, digestive disorders, and colon health.",
             "North America", "/static/images/plants/Cascara Sagrada.jpg"),
            ("Oregon Grape", "Berberis aquifolium", "Berberidaceae", "Flowering Plants", "Shrub",
             "Used for infections, skin conditions, liver health, and digestion.",
             "North America", "/static/images/plants/Oregon Grape.jpg"),
            ("Boneset", "Eupatorium perfoliatum", "Asteraceae", "Flowering Plants", "Herb",
             "Used for colds, flu, fever, and as immune stimulant.",
             "North America", "/static/images/plants/Boneset.jpg"),
            ("Joe Pye Weed", "Eutrochium purpureum", "Asteraceae", "Flowering Plants", "Herb",
             "Gravel root used for kidney stones, urinary infections, and gout.",
             "North America", "/static/images/plants/Joe Pye Weed.jpg"),
            ("Pleurisy Root", "Asclepias tuberosa", "Apocynaceae", "Flowering Plants", "Herb",
             "Butterfly weed used for respiratory conditions, pleurisy, and fever.",
             "North America", "/static/images/plants/Pleurisy Root.jpg"),
            ("Bloodroot", "Sanguinaria canadensis", "Papaveraceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, skin tags, and as antimicrobial. Toxic.",
             "North America", "/static/images/plants/Bloodroot.jpg"),
            ("Blue Flag", "Iris versicolor", "Iridaceae", "Flowering Plants", "Herb",
             "Used for liver detoxification, skin conditions, and lymphatic congestion.",
             "North America", "/static/images/plants/Blue Flag.jpg"),
            ("Black Haw", "Viburnum prunifolium", "Adoxaceae", "Flowering Plants", "Shrub",
             "Used for menstrual cramps, threatened miscarriage, and uterine pain.",
             "North America", "/static/images/plants/Black Haw.jpg"),
            ("Cramp Bark", "Viburnum opulus", "Adoxaceae", "Flowering Plants", "Shrub",
             "Used for menstrual cramps, muscle spasms, and asthma.",
             "North America, Europe", "/static/images/plants/Cramp Bark.jpg"),
            ("False Unicorn", "Veratrum luteum", "Melanthiaceae", "Flowering Plants", "Herb",
             "Used for menstrual disorders, fertility, and pregnancy support.",
             "North America", "/static/images/plants/False Unicorn.jpg"),
            ("True Unicorn", "Aletris farinosa", "Nartheciaceae", "Flowering Plants", "Herb",
             "Stargrass used for digestive disorders, colic, and menstrual issues.",
             "North America", "/static/images/plants/True Unicorn.jpg"),
            ("Squawvine", "Mitchella repens", "Rubiaceae", "Flowering Plants", "Herb",
             "Partridge berry used for pregnancy, childbirth, and menstrual disorders.",
             "North America", "/static/images/plants/Squawvine.jpg"),
            ("Partridge Berry", "Mitchella repens", "Rubiaceae", "Flowering Plants", "Herb",
             "Same as Squawvine. Used for female reproductive health.",
             "North America", "/static/images/plants/Partridge Berry.jpg"),
            ("Spikenard", "Aralia racemosa", "Araliaceae", "Flowering Plants", "Herb",
             "American spikenard used for cough, asthma, and as a blood purifier.",
             "North America", "/static/images/plants/Spikenard.jpg"),
            ("Twinleaf", "Jeffersonia diphylla", "Berberidaceae", "Flowering Plants", "Herb",
             "Rheumatism root used for arthritis, gout, and digestive disorders.",
             "North America", "/static/images/plants/Twinleaf.jpg"),
            ("Prickly Ash", "Zanthoxylum americanum", "Rutaceae", "Flowering Plants", "Tree",
             "Toothache tree used for circulation, arthritis, and as an anesthetic.",
             "North America", "/static/images/plants/Prickly Ash.jpg"),
            ("Stillingia", "Stillingia sylvatica", "Euphorbiaceae", "Flowering Plants", "Herb",
             "Queen's root used for skin conditions, syphilis, and lymphatic disorders.",
             "North America", "/static/images/plants/Stillingia.jpg"),
            ("Podophyllum", "Podophyllum peltatum", "Berberidaceae", "Flowering Plants", "Herb",
             "Mayapple used for warts, cancer, and as a laxative. Highly toxic.",
             "North America", "/static/images/plants/Podophyllum.jpg"),
            ("Mayapple", "Podophyllum peltatum", "Berberidaceae", "Flowering Plants", "Herb",
             "Same as Podophyllum. Mandrake of North America.",
             "North America", "/static/images/plants/Mayapple.jpg"),
            ("Eastern Red Cedar", "Juniperus virginiana", "Cupressaceae", "Conifers", "Tree",
             "Used for respiratory infections, rheumatism, and as a diuretic.",
             "North America", "/static/images/plants/Eastern Red Cedar.jpg"),
            ("White Cedar", "Thuja occidentalis", "Cupressaceae", "Conifers", "Tree",
             "Arborvitae used for warts, immune support, and respiratory conditions.",
             "North America", "/static/images/plants/White Cedar.jpg"),
            ("Sweet Fern", "Comptonia peregrina", "Myricaceae", "Flowering Plants", "Shrub",
             "Used for diarrhea, dysentery, and as an astringent.",
             "North America", "/static/images/plants/Sweet Fern.jpg"),
            ("Groundsel", "Senecio vulgaris", "Asteraceae", "Flowering Plants", "Herb",
             "Used for wounds, menstrual disorders, and as a diuretic.",
             "North America, Europe", "/static/images/plants/Groundsel.jpg"),
            ("Life Root", "Senecio aureus", "Asteraceae", "Flowering Plants", "Herb",
             "Used for menstrual disorders, menopause, and reproductive health.",
             "North America", "/static/images/plants/Life Root.jpg"),
            ("Indian Tobacco", "Lobelia inflata", "Campanulaceae", "Flowering Plants", "Herb",
             "Used for asthma, bronchitis, smoking cessation, and as an emetic.",
             "North America", "/static/images/plants/Indian Tobacco.jpg"),
            ("Lobelia", "Lobelia inflata", "Campanulaceae", "Flowering Plants", "Herb",
             "Same as Indian Tobacco. Powerful respiratory herb.",
             "North America", "/static/images/plants/Lobelia.jpg"),
            ("Wild Cherry Bark", "Prunus serotina", "Rosaceae", "Flowering Plants", "Tree",
             "Used for cough, bronchitis, and as a mild sedative.",
             "North America", "/static/images/plants/Wild Cherry Bark.jpg"),
            ("Wild Cherry", "Prunus avium", "Rosaceae", "Flowering Plants", "Tree",
             "European wild cherry used for cough and digestive disorders.",
             "Europe, Asia", "/static/images/plants/Wild Cherry.jpg"),
            ("Slippery Elm Bark", "Ulmus rubra", "Ulmaceae", "Flowering Plants", "Tree",
             "Same as Slippery Elm. Soothing demulcent for digestive and respiratory.",
             "North America", "/static/images/plants/Slippery Elm Bark.jpg"),
            ("Bitterroot", "Lewisia rediviva", "Montiaceae", "Flowering Plants", "Herb",
             "Used for heart conditions, stomach pain, and as a food source.",
             "North America", "/static/images/plants/Bitterroot.jpg"),
            ("Cottonwood", "Populus deltoides", "Salicaceae", "Flowering Plants", "Tree",
             "Balm of Gilead used for pain, inflammation, and skin conditions.",
             "North America", "/static/images/plants/Cottonwood.jpg"),
            ("Poplar", "Populus tremuloides", "Salicaceae", "Flowering Plants", "Tree",
             "Aspen used for pain, fever, and urinary tract infections.",
             "North America", "/static/images/plants/Poplar.jpg"),
            ("Quaking Aspen", "Populus tremuloides", "Salicaceae", "Flowering Plants", "Tree",
             "Same as Aspen. Used for pain and fever.",
             "North America", "/static/images/plants/Quaking Aspen.jpg"),
            ("Balsam Fir", "Abies balsamea", "Pinaceae", "Conifers", "Tree",
             "Canada balsam used for respiratory conditions, wounds, and as an antiseptic.",
             "North America", "/static/images/plants/Balsam Fir.jpg"),
            ("Balsam Poplar", "Populus balsamifera", "Salicaceae", "Flowering Plants", "Tree",
             "Tacamahac used for pain, inflammation, and skin conditions.",
             "North America", "/static/images/plants/Balsam Poplar.jpg"),
            ("Balm of Gilead", "Populus x gileadensis", "Salicaceae", "Flowering Plants", "Tree",
             "Used for wounds, skin conditions, and respiratory conditions.",
             "North America", "/static/images/plants/Balm of Gilead.jpg"),
            ("Chokecherry", "Prunus virginiana", "Rosaceae", "Flowering Plants", "Tree",
             "Used for digestive disorders, cough, and as a sedative.",
             "North America", "/static/images/plants/Chokecherry.jpg"),
            ("Serviceberry", "Amelanchier alnifolia", "Rosaceae", "Flowering Plants", "Shrub",
             "Saskatoon berry used for food, nutrition, and traditional medicine.",
             "North America", "/static/images/plants/Serviceberry.jpg"),
            ("Wintergreen", "Gaultheria procumbens", "Ericaceae", "Flowering Plants", "Shrub",
             "Used for pain, inflammation, and as a source of methyl salicylate.",
             "North America", "/static/images/plants/Wintergreen.jpg"),
            ("Sweet Birch", "Betula lenta", "Betulaceae", "Flowering Plants", "Tree",
             "Black birch used for pain, fever, and as a source of wintergreen oil.",
             "North America", "/static/images/plants/Sweet Birch.jpg"),
            ("Yellow Birch", "Betula alleghaniensis", "Betulaceae", "Flowering Plants", "Tree",
             "Used for pain, fever, and as a source of birch oil.",
             "North America", "/static/images/plants/Yellow Birch.jpg"),
            ("Paper Birch", "Betula papyrifera", "Betulaceae", "Flowering Plants", "Tree",
             "White birch used for skin conditions, pain, and as a diuretic.",
             "North America", "/static/images/plants/Paper Birch.jpg"),
            ("Sarsaparilla", "Smilax regelii", "Smilacaceae", "Flowering Plants", "Climber",
             "Used for skin conditions, syphilis, and as a blood purifier.",
             "North America", "/static/images/plants/Sarsaparilla.jpg"),
            ("Virginia Snakeroot", "Aristolochia serpentaria", "Aristolochiaceae", "Flowering Plants", "Herb",
             "Used for snake bites, fever, and as a digestive stimulant.",
             "North America", "/static/images/plants/Virginia Snakeroot.jpg"),
            ("Seneca Snakeroot", "Polygala senega", "Polygalaceae", "Flowering Plants", "Herb",
             "Used for respiratory conditions, snake bites, and as an expectorant.",
             "North America", "/static/images/plants/Seneca Snakeroot.jpg"),
            ("Senega", "Polygala senega", "Polygalaceae", "Flowering Plants", "Herb",
             "Same as Seneca Snakeroot. Used for cough and croup.",
             "North America", "/static/images/plants/Senega.jpg"),
            ("Grindelia", "Grindelia squarrosa", "Asteraceae", "Flowering Plants", "Herb",
             "Gumweed used for asthma, bronchitis, and skin conditions.",
             "North America", "/static/images/plants/Grindelia.jpg"),
            ("Rosinweed", "Silphium integrifolium", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, fever, and as an expectorant.",
             "North America", "/static/images/plants/Rosinweed.jpg"),
            ("Compass Plant", "Silphium laciniatum", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, fever, and as a diuretic.",
             "North America", "/static/images/plants/Compass Plant.jpg"),
            ("Cup Plant", "Silphium perfoliatum", "Asteraceae", "Flowering Plants", "Herb",
             "Used for liver and spleen disorders, fever, and as a diuretic.",
             "North America", "/static/images/plants/Cup Plant.jpg"),
            ("Prairie Dock", "Silphium terebinthinaceum", "Asteraceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, liver complaints, and as a diuretic.",
             "North America", "/static/images/plants/Prairie Dock.jpg"),
            ("Rattlesnake Master", "Eryngium yuccifolium", "Apiaceae", "Flowering Plants", "Herb",
             "Button snakeroot used for snake bites, digestive disorders, and kidney stones.",
             "North America", "/static/images/plants/Rattlesnake Master.jpg"),
            ("Eryngo", "Eryngium maritimum", "Apiaceae", "Flowering Plants", "Herb",
             "Sea holly used for urinary disorders, kidney stones, and as an aphrodisiac.",
             "Europe", "/static/images/plants/Eryngo.jpg"),
            ("Button Snakeroot", "Eryngium aquaticum", "Apiaceae", "Flowering Plants", "Herb",
             "Used for digestive disorders, snake bites, and kidney stones.",
             "North America", "/static/images/plants/Button Snakeroot.jpg"),
            ("Blue Curls", "Trichostema dichotomum", "Lamiaceae", "Flowering Plants", "Herb",
             "Forked bluecurls used for colds, fever, and digestive disorders.",
             "North America", "/static/images/plants/Blue Curls.jpg"),
            ("Horsemint", "Monarda punctata", "Lamiaceae", "Flowering Plants", "Herb",
             "Spotted beebalm used for colds, fever, and digestive disorders.",
             "North America", "/static/images/plants/Horsemint.jpg"),
            ("Wild Bergamot", "Monarda fistulosa", "Lamiaceae", "Flowering Plants", "Herb",
             "Bee balm used for colds, fever, and digestive disorders.",
             "North America", "/static/images/plants/Wild Bergamot.jpg"),
            ("Oswego Tea", "Monarda didyma", "Lamiaceae", "Flowering Plants", "Herb",
             "Scarlet beebalm used for colds, fever, and as a pleasant tea.",
             "North America", "/static/images/plants/Oswego Tea.jpg"),
            ("New Jersey Tea", "Ceanothus americanus", "Rhamnaceae", "Flowering Plants", "Shrub",
             "Red root used for lymphatic disorders, spleen complaints, and as a tea.",
             "North America", "/static/images/plants/New Jersey Tea.jpg"),
            ("Jersey Tea", "Ceanothus americanus", "Rhamnaceae", "Flowering Plants", "Shrub",
             "Same as New Jersey Tea. Used during American Revolution as tea substitute.",
             "North America", "/static/images/plants/Jersey Tea.jpg"),
            ("Red Root", "Ceanothus americanus", "Rhamnaceae", "Flowering Plants", "Shrub",
             "Same as New Jersey Tea. Lymphatic and spleen remedy.",
             "North America", "/static/images/plants/Red Root.jpg"),
            ("Mountain Mint", "Pycnanthemum virginianum", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for colds, fever, and digestive disorders.",
             "North America", "/static/images/plants/Mountain Mint.jpg"),
            ("Field Mint", "Mentha arvensis", "Lamiaceae", "Flowering Plants", "Herb",
             "Wild mint used for colds, fever, digestive disorders, and as a stimulant.",
             "Worldwide", "/static/images/plants/Field Mint.jpg"),
            ("Spearmint", "Mentha spicata", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for digestion, nausea, and respiratory conditions.",
             "Europe, Asia", "/static/images/plants/Spearmint.jpg"),
            ("Pennyroyal", "Mentha pulegium", "Lamiaceae", "Flowering Plants", "Herb",
             "Used for menstrual disorders, colds, and as an insect repellent. Toxic in large doses.",
             "Europe, North America", "/static/images/plants/Pennyroyal.jpg"),
            ("Horehound Black", "Ballota nigra", "Lamiaceae", "Flowering Plants", "Herb",
             "Black horehound used for nervous disorders, menstrual pain, and as a sedative.",
             "Europe, North Africa", "/static/images/plants/Horehound Black.jpg"),
            ("Motherwort American", "Leonurus cardiaca", "Lamiaceae", "Flowering Plants", "Herb",
             "Throw-wort used for heart conditions, menstrual disorders, and anxiety.",
             "Europe, North America", "/static/images/plants/Motherwort American.jpg"),
            ("Motherwort European", "Leonurus cardiaca", "Lamiaceae", "Flowering Plants", "Herb",
             "Same as American Motherwort. Heart and uterine tonic.",
             "Europe", "/static/images/plants/Motherwort European.jpg"),
            
            # ========== AMAZONIAN & SOUTH AMERICAN MEDICINE ==========
            ("Cat's Claw", "Uncaria tomentosa", "Rubiaceae", "Flowering Plants", "Climber",
             "Uña de gato used for inflammation, immunity, arthritis, and cancer support.",
             "Amazon Rainforest", "/static/images/plants/Cats Claw.jpg"),
            ("Dragon's Blood", "Croton lechleri", "Euphorbiaceae", "Flowering Plants", "Tree",
             "Sangre de drago used for wounds, diarrhea, skin conditions, and antiviral.",
             "Amazon Rainforest", "/static/images/plants/Dragons Blood.jpg"),
            ("Chanca Piedra", "Phyllanthus niruri", "Phyllanthaceae", "Flowering Plants", "Herb",
             "Stone breaker used for kidney stones, gallstones, hepatitis, and malaria.",
             "Amazon Rainforest", "/static/images/plants/Chanca Piedra.jpg"),
            ("Graviola", "Annona muricata", "Annonaceae", "Flowering Plants", "Tree",
             "Soursop used for cancer, diabetes, parasites, and immune support.",
             "Amazon Rainforest", "/static/images/plants/Graviola.jpg"),
            ("Muira Puama", "Ptychopetalum olacoides", "Olacaceae", "Flowering Plants", "Tree",
             "Potency wood used for sexual dysfunction, fatigue, and nerve pain.",
             "Amazon Rainforest", "/static/images/plants/Muira Puama.jpg"),
            ("Sumac", "Rhus coriaria", "Anacardiaceae", "Flowering Plants", "Shrub",
             "Used for digestive disorders, inflammation, and as a spice.",
             "Middle East, Mediterranean", "/static/images/plants/Sumac.jpg"),
            ("Guarana", "Paullinia cupana", "Sapindaceae", "Flowering Plants", "Climber",
             "Used for energy, weight loss, mental alertness, and athletic performance.",
             "Amazon Rainforest", "/static/images/plants/Guarana.jpg"),
            ("Maca", "Lepidium meyenii", "Brassicaceae", "Flowering Plants", "Herb",
             "Peruvian ginseng used for fertility, libido, energy, and menopause.",
             "Andes Mountains", "/static/images/plants/Maca.jpg"),
            ("Cinchona", "Cinchona officinalis", "Rubiaceae", "Flowering Plants", "Tree",
             "Source of quinine used for malaria, fever, and digestive disorders.",
             "Andes Mountains", "/static/images/plants/Cinchona.jpg"),
            ("Coca", "Erythroxylum coca", "Erythroxylaceae", "Flowering Plants", "Shrub",
             "Source of cocaine alkaloids used for altitude sickness, fatigue, and hunger.",
             "Andes Mountains", "/static/images/plants/Coca.jpg"),
            ("Ipê", "Handroanthus impetiginosus", "Bignoniaceae", "Flowering Plants", "Tree",
             "Pau d'arco used for cancer, infections, and immune support.",
             "South America", "/static/images/plants/Ipe.jpg"),
            ("Jatoba", "Hymenaea courbaril", "Fabaceae", "Flowering Plants", "Tree",
             "Brazilian cherry used for respiratory conditions, fungal infections, and energy.",
             "Amazon Rainforest", "/static/images/plants/Jatoba.jpg"),
            ("Copaiba", "Copaifera langsdorffii", "Fabaceae", "Flowering Plants", "Tree",
             "Copaiba balsam used for inflammation, wound healing, and skin conditions.",
             "Amazon Rainforest", "/static/images/plants/Copaiba.jpg"),
            ("Andiroba", "Carapa guianensis", "Meliaceae", "Flowering Plants", "Tree",
             "Used for inflammation, skin conditions, insect repellent, and pain.",
             "Amazon Rainforest", "/static/images/plants/Andiroba.jpg"),
            ("Suma", "Pfaffia paniculata", "Amaranthaceae", "Flowering Plants", "Herb",
             "Brazilian ginseng used for energy, immunity, cancer support, and adaptogenic.",
            "Amazon Rainforest", "/static/images/plants/Suma.jpg"),
            ("Hercampuri", "Gentianella alborosea", "Gentianaceae", "Flowering Plants", "Herb",
             "Used for cholesterol, diabetes, weight loss, and liver health.",
             "Andes Mountains", "/static/images/plants/Hercampuri.jpg"),
            ("Yacon", "Smallanthus sonchifolius", "Asteraceae", "Flowering Plants", "Herb",
             "Used for diabetes, weight loss, digestion, and as a sweetener.",
             "Andes Mountains", "/static/images/plants/Yacon.jpg"),
            ("Camu Camu", "Myrciaria dubia", "Myrtaceae", "Flowering Plants", "Shrub",
             "Superfruit highest in vitamin C used for immunity, mood, and inflammation.",
             "Amazon Rainforest", "/static/images/plants/Camu Camu.jpg"),
            ("Acai", "Euterpe oleracea", "Arecaceae", "Palms", "Palm",
             "Superfruit used for antioxidants, heart health, energy, and weight loss.",
             "Amazon Rainforest", "/static/images/plants/Acai.jpg"),
            ("Cupuacu", "Theobroma grandiflorum", "Malvaceae", "Flowering Plants", "Tree",
             "Used for energy, digestion, skin health, and as a superfood.",
             "Amazon Rainforest", "/static/images/plants/Cupuacu.jpg"),
            ("Cacao", "Theobroma cacao", "Malvaceae", "Flowering Plants", "Tree",
             "Source of chocolate used for heart health, mood, and antioxidants.",
             "Amazon Rainforest", "/static/images/plants/Cacao.jpg"),
            ("Huito", "Genipa americana", "Rubiaceae", "Flowering Plants", "Tree",
             "Jagua used for body art, skin conditions, and as food coloring.",
             "Amazon Rainforest", "/static/images/plants/Huito.jpg"),
            ("Uxi", "Endopleura uchi", "Humiriaceae", "Flowering Plants", "Tree",
             "Used for uterine health, inflammation, and as a female tonic.",
             "Amazon Rainforest", "/static/images/plants/Uxi.jpg"),
            ("Marapuama", "Liriosma ovata", "Olacaceae", "Flowering Plants", "Tree",
             "Used for sexual dysfunction, fatigue, and nerve pain.",
             "Amazon Rainforest", "/static/images/plants/Marapuama.jpg"),
            ("Amor Seco", "Desmodium adscendens", "Fabaceae", "Flowering Plants", "Herb",
             "Burbur used for allergies, asthma, liver support, and detoxification.",
             "Amazon Rainforest", "/static/images/plants/Amor Seco.jpg"),
            ("Clavillia", "Mirabilis jalapa", "Nyctaginaceae", "Flowering Plants", "Herb",
             "Four o'clock flower used for antifungal, antibacterial, and antiviral.",
             "Amazon Rainforest", "/static/images/plants/Clavillia.jpg"),
            ("Espinhosa", "Xylosma sp.", "Salicaceae", "Flowering Plants", "Shrub",
             "Used for fever, inflammation, and respiratory conditions.",
             "Amazon Rainforest", "/static/images/plants/Espinhosa.jpg"),
            ("Fedegoso", "Cassia occidentalis", "Fabaceae", "Flowering Plants", "Herb",
             "Coffee senna used for liver support, detoxification, and parasites.",
             "Amazon Rainforest", "/static/images/plants/Fedegoso.jpg"),
            ("Gervao", "Stachytarpheta cayennensis", "Verbenaceae", "Flowering Plants", "Herb",
             "Vervain used for liver support, digestion, and as a diuretic.",
             "Amazon Rainforest", "/static/images/plants/Gervao.jpg"),
            ("Iporuru", "Alchornea castaneifolia", "Euphorbiaceae", "Flowering Plants", "Tree",
             "Used for arthritis, inflammation, muscle pain, and fertility.",
             "Amazon Rainforest", "/static/images/plants/Iporuru.jpg"),
            ("Jurubeba", "Solanum paniculatum", "Solanaceae", "Flowering Plants", "Shrub",
             "Used for liver support, digestion, and hepatoprotective.",
             "Amazon Rainforest", "/static/images/plants/Jurubeba.jpg"),
            ("Mullaca", "Physalis angulata", "Solanaceae", "Flowering Plants", "Herb",
             "Wild tomato used for malaria, leishmaniasis, and immune support.",
             "Amazon Rainforest", "/static/images/plants/Mullaca.jpg"),
            ("Picão Preto", "Bidens pilosa", "Asteraceae", "Flowering Plants", "Herb",
             "Spanish needle used for diabetes, inflammation, and viral infections.",
             "Amazon Rainforest", "/static/images/plants/Picao Preto.jpg"),
            ("Piri Piri", "Cyperus articulatus", "Cyperaceae", "Grasses", "Grass",
             "Used for colds, flu, nausea, and digestive disorders.",
             "Amazon Rainforest", "/static/images/plants/Piri Piri.jpg"),
            ("Sangre de Grado", "Croton lechleri", "Euphorbiaceae", "Flowering Plants", "Tree",
             "Same as Dragon's Blood. Wound healing and antiviral.",
             "Amazon Rainforest", "/static/images/plants/Sangre de Grado.jpg"),
            ("Tayuya", "Cayaponia tayuya", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Used for pain, inflammation, back pain, and as a diuretic.",
             "Amazon Rainforest", "/static/images/plants/Tayuya.jpg"),
            ("Vassourinha", "Scoparia dulcis", "Plantaginaceae", "Flowering Plants", "Herb",
             "Sweet broom used for diabetes, kidney stones, and bronchitis.",
             "Amazon Rainforest", "/static/images/plants/Vassourinha.jpg"),
            ("Boldo", "Peumus boldus", "Monimiaceae", "Flowering Plants", "Tree",
             "Used for liver and gallbladder disorders, digestion, and as a diuretic.",
             "South America", "/static/images/plants/Boldo.jpg"),
            ("Calendula Officinalis", "Calendula officinalis", "Asteraceae", "Flowering Plants", "Herb",
             "Pot marigold used for wound healing, skin inflammation, and lymphatic support.",
             "Mediterranean", "/static/images/plants/Calendula Officinalis.jpg"),
            ("Arnica Montana", "Arnica montana", "Asteraceae", "Flowering Plants", "Herb",
             "Mountain arnica used for bruises, sprains, muscle pain, and trauma. External use.",
             "Europe", "/static/images/plants/Arnica Montana.jpg"),
            ("Larrea", "Larrea tridentata", "Zygophyllaceae", "Flowering Plants", "Shrub",
             "Chaparral and creosote bush used for cancer, arthritis, and skin conditions.",
             "North America", "/static/images/plants/Larrea.jpg"),
            ("Coleus", "Coleus forskohlii", "Lamiaceae", "Flowering Plants", "Herb",
             "Forskolin source used for weight loss, heart health, and glaucoma.",
             "India", "/static/images/plants/Coleus.jpg"),
            ("Gymnema", "Gymnema sylvestre", "Apocynaceae", "Flowering Plants", "Climber",
             "Gurmar sugar destroyer used for diabetes, weight loss, and sweet cravings.",
             "India", "/static/images/plants/Gymnema.jpg"),
            ("Salacia", "Salacia reticulata", "Celastraceae", "Flowering Plants", "Climber",
             "Used for diabetes, weight loss, and carbohydrate metabolism.",
             "India, Sri Lanka", "/static/images/plants/Salacia.jpg"),
            ("Bitter Melon", "Momordica charantia", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Karela used for diabetes, blood sugar control, and parasites.",
             "Asia, Africa", "/static/images/plants/Bitter Melon.jpg"),
            ("Fenugreek Seeds", "Trigonella foenum-graecum", "Fabaceae", "Flowering Plants", "Herb",
             "Methi seeds used for diabetes, cholesterol, digestion, and lactation.",
             "India, Mediterranean", "/static/images/plants/Fenugreek Seeds.jpg"),
            ("Bael Fruit", "Aegle marmelos", "Rutaceae", "Flowering Plants", "Tree",
             "Bilva used for digestive disorders, diarrhea, and diabetes.",
             "India", "/static/images/plants/Bael Fruit.jpg"),
            ("Bacopa", "Bacopa monnieri", "Plantaginaceae", "Flowering Plants", "Herb",
             "Brahmi used for memory, cognitive function, anxiety, and epilepsy.",
             "India", "/static/images/plants/Bacopa.jpg"),
            ("Gotu Kola", "Centella asiatica", "Apiaceae", "Flowering Plants", "Herb",
             "Mandukaparni used for brain health, wound healing, and circulation.",
             "India, Southeast Asia", "/static/images/plants/Gotu Kola.jpg"),
            ("Shankhpushpi", "Convolvulus pluricaulis", "Convolvulaceae", "Flowering Plants", "Climber",
             "Used for memory, intelligence, anxiety, and insomnia.",
             "India", "/static/images/plants/Shankhpushpi.jpg"),
            ("Jyotishmati", "Celastrus paniculatus", "Celastraceae", "Flowering Plants", "Climber",
             "Intellect tree used for memory, cognitive enhancement, and brain health.",
             "India", "/static/images/plants/Jyotishmati.jpg"),
            ("Malkangani", "Celastrus paniculatus", "Celastraceae", "Flowering Plants", "Climber",
             "Same as Jyotishmati. Brain tonic and memory enhancer.",
             "India", "/static/images/plants/Malkangani.jpg"),
            ("Vacha", "Acorus calamus", "Acoraceae", "Flowering Plants", "Herb",
             "Sweet flag used for digestive disorders, speech disorders, and memory.",
             "India, Europe", "/static/images/plants/Vacha.jpg"),
            ("Kuth", "Saussurea costus", "Asteraceae", "Flowering Plants", "Herb",
             "Costus root used for digestive disorders, skin diseases, and respiratory.",
             "Himalayas", "/static/images/plants/Kuth.jpg"),
            ("Kulanjan", "Alpinia galanga", "Zingiberaceae", "Flowering Plants", "Herb",
             "Greater galangal used for digestive disorders, respiratory, and as a spice.",
             "Southeast Asia", "/static/images/plants/Kulanjan.jpg"),
            ("Rasna", "Pluchea lanceolata", "Asteraceae", "Flowering Plants", "Shrub",
             "Used for arthritis, inflammation, respiratory conditions, and pain.",
             "India", "/static/images/plants/Rasna.jpg"),
            ("Nirgundi", "Vitex negundo", "Lamiaceae", "Flowering Plants", "Shrub",
             "Five-leaved chaste tree used for arthritis, pain, and respiratory.",
             "India", "/static/images/plants/Nirgundi.jpg"),
            ("Eranda", "Ricinus communis", "Euphorbiaceae", "Flowering Plants", "Shrub",
             "Castor oil plant used for constipation, arthritis, and as a purgative.",
             "India, Africa", "/static/images/plants/Eranda.jpg"),
            ("Danti", "Baliospermum montanum", "Euphorbiaceae", "Flowering Plants", "Shrub",
             "Wild croton used for constipation, abdominal diseases, and skin disorders.",
             "India", "/static/images/plants/Danti.jpg"),
            ("Trivrit", "Operculina turpethum", "Convolvulaceae", "Flowering Plants", "Climber",
             "Turpeth root used as a cathartic for constipation and liver disorders.",
             "India", "/static/images/plants/Trivrit.jpg"),
            ("Aragvadha", "Cassia fistula", "Fabaceae", "Flowering Plants", "Tree",
             "Purging cassia used for constipation, skin diseases, and cardiac tonic.",
             "India, Southeast Asia", "/static/images/plants/Aragvadha.jpg"),
            ("Indravaruni", "Citrullus colocynthis", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Bitter apple used for diabetes, constipation, and abdominal tumors.",
             "India, Mediterranean", "/static/images/plants/Indravaruni.jpg"),
            ("Kampillaka", "Mallotus philippensis", "Euphorbiaceae", "Flowering Plants", "Tree",
             "Kamala tree used for skin diseases, intestinal worms, and as a dye.",
             "India, Southeast Asia", "/static/images/plants/Kampillaka.jpg"),
            ("Katuka", "Picrorhiza kurroa", "Plantaginaceae", "Flowering Plants", "Herb",
             "Kutki used for liver disorders, fever, and digestive complaints.",
             "Himalayas", "/static/images/plants/Katuka.jpg"),
            ("Parpata", "Fumaria indica", "Fumariaceae", "Flowering Plants", "Herb",
             "Fumitory used for skin diseases, blood purification, and liver disorders.",
             "India, Mediterranean", "/static/images/plants/Parpata.jpg"),
            ("Pippali Moola", "Piper longum", "Piperaceae", "Flowering Plants", "Climber",
             "Long pepper root used for digestive disorders, respiratory, and immunity.",
             "India, Southeast Asia", "/static/images/plants/Pippali Moola.jpg"),
            ("Chavya", "Piper chaba", "Piperaceae", "Flowering Plants", "Climber",
             "Java long pepper used for digestive disorders, respiratory, and joint pain.",
             "India, Southeast Asia", "/static/images/plants/Chavya.jpg"),
            ("Chitrakamoola", "Plumbago zeylanica", "Plumbaginaceae", "Flowering Plants", "Herb",
             "Leadwort root used for digestive disorders, metabolism, and weight management.",
             "India, Southeast Asia", "/static/images/plants/Chitrakamoola.jpg"),
            ("Bharangi", "Clerodendrum serratum", "Lamiaceae", "Flowering Plants", "Shrub",
             "Used for respiratory conditions, digestive disorders, and skin diseases.",
             "India, Southeast Asia", "/static/images/plants/Bharangi.jpg"),
            ("Karanja", "Pongamia pinnata", "Fabaceae", "Flowering Plants", "Tree",
             "Indian beech used for skin diseases, diabetes, wounds, and joint pain.",
             "India, Southeast Asia", "/static/images/plants/Karanja.jpg"),
            ("Patola", "Trichosanthes cucumerina", "Cucurbitaceae", "Flowering Plants", "Climber",
             "Snake gourd used for fever, skin diseases, digestive disorders, and diabetes.",
             "India, Southeast Asia", "/static/images/plants/Patola.jpg"),
            ("Bilva", "Aegle marmelos", "Rutaceae", "Flowering Plants", "Tree",
             "Bael tree used for digestive disorders, diabetes, diarrhea, and respiratory.",
             "India, Southeast Asia", "/static/images/plants/Bilva.jpg"),
            ("Syonaka", "Oroxylum indicum", "Bignoniaceae", "Flowering Plants", "Tree",
             "Broken bones tree used for digestive disorders, respiratory, and fever.",
             "India, Southeast Asia", "/static/images/plants/Syonaka.jpg"),
            ("Gambhari", "Gmelina arborea", "Lamiaceae", "Flowering Plants", "Tree",
             "Kashmarya used for digestive disorders, fever, and as a cardiac tonic.",
             "India, Southeast Asia", "/static/images/plants/Gambhari.jpg"),
            ("Patala", "Stereospermum suaveolens", "Bignoniaceae", "Flowering Plants", "Tree",
             "Yellow snake tree used for digestive disorders, fever, and respiratory.",
             "India, Southeast Asia", "/static/images/plants/Patala.jpg"),
            ("Shyonaka", "Oroxylum indicum", "Bignoniaceae", "Flowering Plants", "Tree",
             "Same as Syonaka. Broken bones tree for digestive and respiratory.",
             "India, Southeast Asia", "/static/images/plants/Shyonaka.jpg"),
            ("Agastya", "Sesbania grandiflora", "Fabaceae", "Flowering Plants", "Tree",
             "Hummingbird tree used for fever, respiratory, and as a nutritious vegetable.",
             "India, Southeast Asia", "/static/images/plants/Agastya.jpg"),
            ("Madanphala", "Randia dumetorum", "Rubiaceae", "Flowering Plants", "Shrub",
             "Used for emesis, skin diseases, and as a purgative.",
             "India", "/static/images/plants/Madanphala.jpg"),
            ("Laksha", "Laccifer lacca", "Kerridae", "Flowering Plants", "Herb",
             "Shellac used for wounds, skin diseases, and as a sealant.",
             "India", "/static/images/plants/Laksha.jpg"),
            ("Hingu", "Ferula assa-foetida", "Apiaceae", "Flowering Plants", "Herb",
             "Asafoetida used for digestive disorders, respiratory, and as a spice.",
             "Iran, Afghanistan", "/static/images/plants/Hingu.jpg"),
            ("Rala", "Shorea robusta", "Dipterocarpaceae", "Flowering Plants", "Tree",
             "Sal resin used for skin diseases, diarrhea, and wounds.",
             "India", "/static/images/plants/Rala.jpg"),
            ("Shala", "Shorea robusta", "Dipterocarpaceae", "Flowering Plants", "Tree",
             "Sal tree used for skin diseases, diabetes, and wound healing.",
             "India, Southeast Asia", "/static/images/plants/Shala.jpg"),
            ("Sarja", "Vateria indica", "Dipterocarpaceae", "Flowering Plants", "Tree",
             "White dammar used for skin diseases, wounds, and as an incense.",
             "India", "/static/images/plants/Sarja.jpg"),
            ("Kunduru", "Boswellia serrata", "Burseraceae", "Flowering Plants", "Tree",
             "Indian olibanum used for inflammation, arthritis, and wound healing.",
             "India", "/static/images/plants/Kunduru.jpg"),
            ("Sallaki", "Boswellia serrata", "Burseraceae", "Flowering Plants", "Tree",
             "Same as Kunduru. Used for arthritis and inflammation.",
             "India", "/static/images/plants/Sallaki.jpg"),
            ("Guggulu", "Commiphora wightii", "Burseraceae", "Flowering Plants", "Shrub",
             "Indian bdellium used for cholesterol, arthritis, and weight management.",
             "India, Pakistan", "/static/images/plants/Guggulu.jpg"),
            ("Pura", "Garcinia morella", "Clusiaceae", "Flowering Plants", "Tree",
             "Gamboge used for constipation, worms, and as a pigment.",
             "India, Southeast Asia", "/static/images/plants/Pura.jpg"),
            ("Vamsa", "Bambusa arundinacea", "Poaceae", "Grasses", "Grass",
             "Bamboo used for cough, asthma, and as a nutritious food.",
             "India, Southeast Asia", "/static/images/plants/Vamsa.jpg"),
            ("Vamsalochana", "Bambusa arundinacea", "Poaceae", "Grasses", "Grass",
             "Bamboo manna used for cough, asthma, and respiratory conditions.",
             "India", "/static/images/plants/Vamsalochana.jpg"),
            ("Mocharasa", "Bombax ceiba", "Malvaceae", "Flowering Plants", "Tree",
             "Silk cotton tree exudate used for dysentery and bleeding disorders.",
             "India, Southeast Asia", "/static/images/plants/Mocharasa.jpg"),
            ("Shalmali", "Bombax ceiba", "Malvaceae", "Flowering Plants", "Tree",
             "Silk cotton tree used for wounds, skin diseases, and bleeding.",
             "India, Southeast Asia", "/static/images/plants/Shalmali.jpg"),
            ("Tala", "Borassus flabellifer", "Arecaceae", "Palms", "Palm",
             "Palmyra palm used for diabetes, digestive disorders, and as a cooling drink.",
             "India, Southeast Asia", "/static/images/plants/Tala.jpg"),
            ("Narikela", "Cocos nucifera", "Arecaceae", "Palms", "Palm",
             "Coconut tree used for hydration, nutrition, and various medicinal uses.",
             "Tropical regions", "/static/images/plants/Narikela.jpg"),
            ("Kharjura", "Phoenix dactylifera", "Arecaceae", "Palms", "Palm",
             "Date palm used for energy, constipation, and reproductive health.",
             "Middle East, North Africa", "/static/images/plants/Kharjura.jpg"),
            ("Madhuka", "Madhuca longifolia", "Sapotaceae", "Flowering Plants", "Tree",
             "Mahua used for heart health, skin diseases, and as a nutritious drink.",
             "India", "/static/images/plants/Madhuka.jpg"),
            ("Bakula", "Mimusops elengi", "Sapotaceae", "Flowering Plants", "Tree",
             "Spanish cherry used for dental care, gum diseases, and as a mouth freshener.",
             "India, Southeast Asia", "/static/images/plants/Bakula.jpg"),
            ("Amalatas", "Cassia fistula", "Fabaceae", "Flowering Plants", "Tree",
             "Golden shower tree used for constipation, skin diseases, and cardiac tonic.",
             "India, Southeast Asia", "/static/images/plants/Amalatas.jpg"),
            ("Aragvadha Tree", "Cassia fistula", "Fabaceae", "Flowering Plants", "Tree",
             "Same as Amalatas. Aragvadha for constipation and heart health.",
             "India", "/static/images/plants/Aragvadha Tree.jpg"),
            ("Avartani", "Clerodendrum phlomidis", "Lamiaceae", "Flowering Plants", "Shrub",
             "Used for skin diseases, fever, and digestive disorders.",
             "India", "/static/images/plants/Avartani.jpg"),
            ("BanaTulasi", "Ocimum canum", "Lamiaceae", "Flowering Plants", "Herb",
             "African basil used for fever, cough, and digestive disorders.",
             "Africa, India", "/static/images/plants/BanaTulasi.jpg"),
            ("Bhandira", "Clerodendrum infortunatum", "Lamiaceae", "Flowering Plants", "Shrub",
             "Hill glory bower used for fever, skin diseases, and respiratory.",
             "India, Southeast Asia", "/static/images/plants/Bhandira.jpg"),
            ("Bhumyamalaki", "Phyllanthus niruri", "Phyllanthaceae", "Flowering Plants", "Herb",
             "Stonebreaker used for jaundice, liver disorders, and kidney stones.",
             "Tropical regions", "/static/images/plants/Bhumyamalaki.jpg"),
            ("Bijaka", "Pterocarpus marsupium", "Fabaceae", "Flowering Plants", "Tree",
             "Indian kino tree used for diabetes, diarrhea, and skin diseases.",
             "India", "/static/images/plants/Bijaka.jpg"),
            ("Bilvapatra", "Aegle marmelos", "Rutaceae", "Flowering Plants", "Tree",
             "Bael leaf used for diabetes, digestive disorders, and fever.",
             "India", "/static/images/plants/Bilvapatra.jpg"),
            ("Brhatikha", "Solanum violaceum", "Solanaceae", "Flowering Plants", "Shrub",
             "Indian nightshade used for respiratory, digestive, and pain.",
             "India", "/static/images/plants/Brhatikha.jpg"),
            ("Changeri", "Oxalis corniculata", "Oxalidaceae", "Flowering Plants", "Herb",
             "Creeping woodsorrel used for digestive disorders, fever, and skin diseases.",
             "Worldwide", "/static/images/plants/Changeri.jpg"),
            ("Dhanvantara", "Acorus calamus", "Acoraceae", "Flowering Plants", "Herb",
             "Sweet flag used for digestive, respiratory, and neurological disorders.",
             "India, Europe", "/static/images/plants/Dhanvantara.jpg"),
            ("Dugdhika", "Euphorbia hirta", "Euphorbiaceae", "Flowering Plants", "Herb",
             "Asthma plant used for respiratory, digestive, and lactation.",
             "Tropical regions", "/static/images/plants/Dugdhika.jpg"),
            ("Girikarnika", "Clitoria ternatea", "Fabaceae", "Flowering Plants", "Climber",
             "Butterfly pea used for memory, stress, and as a natural dye.",
             "Tropical Asia", "/static/images/plants/Girikarnika.jpg"),
            ("Jhinti", "Ipomoea nil", "Convolvulaceae", "Flowering Plants", "Climber",
             "Morning glory used for constipation, fever, and as a purgative.",
             "Tropical regions", "/static/images/plants/Jhinti.jpg"),
            ("Jyotismati", "Celastrus paniculatus", "Celastraceae", "Flowering Plants", "Climber",
             "Same as Jyotishmati. Intellect tree for brain health.",
             "India", "/static/images/plants/Jyotismati.jpg"),
            ("Kadali", "Musa paradisiaca", "Musaceae", "Flowering Plants", "Herb",
             "Plantain used for digestive disorders, ulcers, and as a nutritious food.",
             "Tropical regions", "/static/images/plants/Kadali.jpg"),
            ("Kakanasika", "Martynia annua", "Martyniaceae", "Flowering Plants", "Herb",
             "Tiger's claw used for snake bites, epilepsy, and skin diseases.",
             "India", "/static/images/plants/Kakanasika.jpg"),
            ("Karkatasringi", "Pistacia integerrima", "Anacardiaceae", "Flowering Plants", "Tree",
             "Galls used for respiratory, digestive, and bleeding disorders.",
             "Himalayas", "/static/images/plants/Karkatasringi.jpg"),
            ("Karpasa", "Gossypium herbaceum", "Malvaceae", "Flowering Plants", "Shrub",
             "Cotton plant used for bleeding, skin diseases, and as a textile.",
             "Tropical regions", "/static/images/plants/Karpasa.jpg"),
            ("Kulattha", "Macrotyloma uniflorum", "Fabaceae", "Flowering Plants", "Herb",
             "Horse gram used for kidney stones, diabetes, and weight loss.",
             "India", "/static/images/plants/Kulattha.jpg"),
            ("Langali", "Gloriosa superba", "Colchicaceae", "Flowering Plants", "Climber",
             "Glory lily used for gout, arthritis, and as an abortifacient.",
             "Tropical regions", "/static/images/plants/Langali.jpg"),
            ("Mahanimba", "Melia azedarach", "Meliaceae", "Flowering Plants", "Tree",
             "Persian lilac used for skin diseases, parasites, and as an insecticide.",
             "Asia", "/static/images/plants/Mahanimba.jpg"),
            ("Makoi", "Solanum nigrum", "Solanaceae", "Flowering Plants", "Herb",
             "Black nightshade used for digestive disorders, skin diseases, and pain.",
             "Worldwide", "/static/images/plants/Makoi.jpg"),
            ("Malati", "Jasminum sambac", "Oleaceae", "Flowering Plants", "Shrub",
             "Arabian jasmine used for skin diseases, eye disorders, and as fragrance.",
             "Tropical Asia", "/static/images/plants/Malati.jpg"),
            ("Mandukaparni", "Centella asiatica", "Apiaceae", "Flowering Plants", "Herb",
             "Gotu kola used for brain health, memory, wound healing, and skin.",
             "India, Southeast Asia, Africa", "/static/images/plants/Mandukaparni.jpg"),
            ("Maricha", "Piper nigrum", "Piperaceae", "Flowering Plants", "Climber",
             "Black pepper used for digestion, metabolism, respiratory, and as spice.",
             "India, Southeast Asia", "/static/images/plants/Maricha.jpg"),
            ("Matulunga", "Citrus medica", "Rutaceae", "Flowering Plants", "Shrub",
             "Citron used for digestive disorders, nausea, and as a flavoring.",
             "Southeast Asia", "/static/images/plants/Matulunga.jpg"),
            ("Methika", "Trigonella foenum-graecum", "Fabaceae", "Flowering Plants", "Herb",
             "Fenugreek used for diabetes, cholesterol, digestion, and lactation.",
             "India, Mediterranean", "/static/images/plants/Methika.jpg"),
            ("Mundi", "Sphaeranthus indicus", "Asteraceae", "Flowering Plants", "Herb",
             "East Indian globe thistle used for skin diseases, fever, and digestive.",
             "India", "/static/images/plants/Mundi.jpg"),
            ("Nagabala", "Grewia hirsuta", "Malvaceae", "Flowering Plants", "Shrub",
             "Used for strength, vitality, and respiratory conditions.",
             "India", "/static/images/plants/Nagabala.jpg"),
            ("Nili", "Indigofera tinctoria", "Fabaceae", "Flowering Plants", "Shrub",
             "Indigo plant used for skin diseases, liver disorders, and as dye.",
             "Tropical Asia", "/static/images/plants/Nili.jpg"),
            ("Nirgundi", "Vitex negundo", "Lamiaceae", "Flowering Plants", "Shrub",
             "Five-leaved chaste tree used for pain, inflammation, respiratory.",
             "India, Southeast Asia", "/static/images/plants/Nirgundi.jpg"),
            ("Palasha", "Butea monosperma", "Fabaceae", "Flowering Plants", "Tree",
             "Flame of the forest used for skin diseases, worms, urinary disorders.",
             "India, Southeast Asia", "/static/images/plants/Palasha.jpg"),
            ("Parijata", "Nyctanthes arbor-tristis", "Oleaceae", "Flowering Plants", "Shrub",
             "Night-flowering jasmine used for fever, skin diseases, and arthritis.",
             "India, Southeast Asia", "/static/images/plants/Parijata.jpg"),
            ("Patalagarudi", "Coleus amboinicus", "Lamiaceae", "Flowering Plants", "Herb",
             "Indian borage used for cough, cold, fever, and digestive disorders.",
             "Tropical regions", "/static/images/plants/Patalagarudi.jpg"),
            ("Pippali", "Piper longum", "Piperaceae", "Flowering Plants", "Climber",
             "Long pepper used for respiratory, digestion, immunity, and rejuvenation.",
             "India, Southeast Asia", "/static/images/plants/Pippali.jpg"),
            ("Prasarini", "Paederia foetida", "Rubiaceae", "Flowering Plants", "Climber",
             "Skunk vine used for joint pain, digestive, and as a carminative.",
             "India, Southeast Asia", "/static/images/plants/Prasarini.jpg"),
            ("Putrajeevaka", "Putranjiva roxburghii", "Putranjivaceae", "Flowering Plants", "Tree",
             "Child-life tree used for female infertility and reproductive health.",
             "India", "/static/images/plants/Putrajeevaka.jpg"),
            ("Rambha", "Musa paradisiaca", "Musaceae", "Flowering Plants", "Herb",
             "Banana plant used for digestive disorders, ulcers, and nutrition.",
             "Tropical regions", "/static/images/plants/Rambha.jpg"),
            ("Rasna", "Pluchea lanceolata", "Asteraceae", "Flowering Plants", "Shrub",
             "Used for arthritis, inflammation, respiratory conditions, pain.",
             "India", "/static/images/plants/Rasna.jpg"),
            ("Rohitaka", "Tecomella undulata", "Bignoniaceae", "Flowering Plants", "Tree",
             "Desert teak used for liver disorders, spleen diseases, and jaundice.",
             "India", "/static/images/plants/Rohitaka.jpg"),
            ("Romasha", "Datura metel", "Solanaceae", "Flowering Plants", "Herb",
             "Devil's trumpet used for asthma, pain, and as a hallucinogen.",
             "Tropical regions", "/static/images/plants/Romasha.jpg"),
            ("Sahachara", "Barleria prionitis", "Acanthaceae", "Flowering Plants", "Shrub",
             "Porcupine flower used for inflammation, wounds, and skin diseases.",
             "India, Southeast Asia", "/static/images/plants/Sahachara.jpg"),
            ("Sairyaka", "Barleria cristata", "Acanthaceae", "Flowering Plants", "Shrub",
             "Philippine violet used for inflammation, fever, and skin diseases.",
             "India, Southeast Asia", "/static/images/plants/Sairyaka.jpg"),
            ("Sariva", "Hemidesmus indicus", "Apocynaceae", "Flowering Plants", "Climber",
             "Indian sarsaparilla used for blood purification, skin diseases, fever.",
             "India", "/static/images/plants/Sariva.jpg"),
            ("Shatavari", "Asparagus racemosus", "Asparagaceae", "Flowering Plants", "Herb",
             "Queen of herbs used for female health, fertility, lactation, vitality.",
             "India", "/static/images/plants/Shatavari.jpg"),
            ("Shatapushpa", "Anethum sowa", "Apiaceae", "Flowering Plants", "Herb",
             "Indian dill used for digestive disorders, colic, and as a carminative.",
             "India", "/static/images/plants/Shatapushpa.jpg"),
            ("Shirisha", "Albizia lebbeck", "Fabaceae", "Flowering Plants", "Tree",
             "Siris tree used for allergies, skin diseases, respiratory conditions.",
             "India, Southeast Asia", "/static/images/plants/Shirisha.jpg"),
            ("Sigru", "Moringa oleifera", "Moringaceae", "Flowering Plants", "Tree",
             "Drumstick tree used for nutrition, diabetes, inflammation, malnutrition.",
             "India", "/static/images/plants/Sigru.jpg"),
            ("Sthalapadmī", "Nelumbo nucifera", "Nelumbonaceae", "Flowering Plants", "Herb",
             "Sacred lotus used for bleeding disorders, diarrhea, and as a tonic.",
             "India, Southeast Asia", "/static/images/plants/Sthalapadmi.jpg"),
            ("Svarnaksiri", "Argemone mexicana", "Papaveraceae", "Flowering Plants", "Herb",
             "Mexican poppy used for skin diseases, jaundice, and as an analgesic.",
             "Tropical regions", "/static/images/plants/Svarnaksiri.jpg"),
            ("Talamuli", "Curculigo orchioides", "Hypoxidaceae", "Flowering Plants", "Herb",
             "Golden eye-grass used for sexual health, vitality, and as a tonic.",
             "India, Southeast Asia", "/static/images/plants/Talamuli.jpg"),
            ("Tarkari", "Ipomoea aquatica", "Convolvulaceae", "Flowering Plants", "Herb",
             "Water spinach used for liver disorders, diabetes, and as a vegetable.",
             "Tropical Asia", "/static/images/plants/Tarkari.jpg"),
            ("Tila", "Sesamum indicum", "Pedaliaceae", "Flowering Plants", "Herb",
             "Sesame used for strength, bone health, skin health, reproductive health.",
             "India, Africa, Asia", "/static/images/plants/Tila.jpg"),
            ("Tinduka", "Diospyros malabarica", "Ebenaceae", "Flowering Plants", "Tree",
             "Gaub tree used for diarrhea, dysentery, and skin diseases.",
             "India, Southeast Asia", "/static/images/plants/Tinduka.jpg"),
            ("Trivrit", "Operculina turpethum", "Convolvulaceae", "Flowering Plants", "Climber",
             "Turpeth root used as a cathartic for constipation and liver disorders.",
             "India", "/static/images/plants/Trivrit.jpg"),
            ("Tulasi", "Ocimum tenuiflorum", "Lamiaceae", "Flowering Plants", "Herb",
             "Holy basil sacred adaptogen for stress, immunity, respiratory, longevity.",
             "India", "/static/images/plants/Tulasi.jpg"),
            ("Twak", "Cinnamomum verum", "Lauraceae", "Flowering Plants", "Tree",
             "True cinnamon used for blood sugar, heart health, digestion.",
             "Sri Lanka, India", "/static/images/plants/Twak.jpg"),
            ("Udumbara", "Ficus racemosa", "Moraceae", "Flowering Plants", "Tree",
             "Cluster fig used for diabetes, diarrhea, urinary disorders.",
             "India, Southeast Asia", "/static/images/plants/Udumbara.jpg"),
            ("Upakunchika", "Nigella sativa", "Ranunculaceae", "Flowering Plants", "Herb",
             "Black cumin used for immune support, digestion, respiratory, and as spice.",
             "Middle East, India", "/static/images/plants/Upakunchika.jpg"),
            ("Vacha", "Acorus calamus", "Acoraceae", "Flowering Plants", "Herb",
             "Sweet flag used for digestive, respiratory, neurological disorders.",
             "India, Europe", "/static/images/plants/Vacha.jpg"),
            ("Vamsha", "Bambusa arundinacea", "Poaceae", "Grasses", "Grass",
             "Bamboo used for cough, asthma, and as a nutritious food source.",
             "India, Southeast Asia", "/static/images/plants/Vamsha.jpg"),
            ("Varahikanda", "Dioscorea bulbifera", "Dioscoreaceae", "Flowering Plants", "Climber",
             "Air potato used for piles, dysentery, and as a nutritious food.",
             "Tropical regions", "/static/images/plants/Varahikanda.jpg"),
            ("Varuna", "Crataeva nurvala", "Capparaceae", "Flowering Plants", "Tree",
             "Three-leaved caper used for kidney stones, prostate, urinary disorders.",
             "India, Southeast Asia", "/static/images/plants/Varuna.jpg"),
            ("Vasa", "Justicia adhatoda", "Acanthaceae", "Flowering Plants", "Shrub",
             "Malabar nut used for respiratory, cough, asthma, bronchitis.",
             "India, Southeast Asia", "/static/images/plants/Vasa.jpg"),
            ("Vatsanabha", "Aconitum ferox", "Ranunculaceae", "Flowering Plants", "Herb",
             "Indian aconite used for fever, pain, and as a poison. Highly toxic.",
             "Himalayas", "/static/images/plants/Vatsanabha.jpg"),
            ("Vidanga", "Embelia ribes", "Primulaceae", "Flowering Plants", "Climber",
             "False black pepper used for worms, dental care, digestive disorders.",
             "India, Southeast Asia", "/static/images/plants/Vidanga.jpg"),
            ("Vishnukranta", "Evolvulus alsinoides", "Convolvulaceae", "Flowering Plants", "Herb",
             "Slender dwarf morning-glory used for brain health, memory, and epilepsy.",
             "Tropical regions", "/static/images/plants/Vishnukranta.jpg"),
            ("Yashti", "Glycyrrhiza glabra", "Fabaceae", "Flowering Plants", "Herb",
             "Licorice root used for respiratory, digestive, adrenal support, and as flavoring.",
             "Mediterranean, India", "/static/images/plants/Yashti.jpg"),
            ("Yava", "Hordeum vulgare", "Poaceae", "Grasses", "Grass",
             "Barley used for digestive health, urinary disorders, cholesterol.",
             "Middle East, Worldwide", "/static/images/plants/Yava.jpg"),
            ("Yavani", "Trachyspermum ammi", "Apiaceae", "Flowering Plants", "Herb",
             "Ajwain used for digestive disorders, colic, respiratory conditions.",
             "India, Middle East", "/static/images/plants/Yavani.jpg"),
            ("Zerumbet", "Zingiber zerumbet", "Zingiberaceae", "Flowering Plants", "Herb",
             "Awapuhi shampoo ginger used for inflammation, hair care, and as shampoo.",
             "Southeast Asia", "/static/images/plants/Zerumbet.jpg"),
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
    plants = serialize_plants(cursor.fetchall())
    
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
        return jsonify(serialize_plant(plant))
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
    
    return jsonify(serialize_plants(plants))

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
        result['plants'] = serialize_plants(plants)
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
    
    return jsonify(serialize_plants(plants))

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
        result['plants'] = serialize_plants(plants)
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
    
    return jsonify(serialize_plants(plants))

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
        result['plants'] = serialize_plants(plants)
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
    
    return jsonify(serialize_plants(plants))

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
        result['plants'] = serialize_plants(plants)
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
    
    return jsonify(serialize_plants(plants))

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

@app.route('/static/images/plants/<path:filename>')
def serve_plant_image(filename):
    """Serve all plant images without restrictions"""
    # Serve the image from the static folder - all plants allowed
    return send_from_directory('static/images/plants', filename)

@app.route('/api/plants/<int:plant_id>/image')
def get_plant_image_api(plant_id):
    """API endpoint to get plant image - allows access to all plants including recently added"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM plants WHERE id = ?", (plant_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({"error": "Plant not found"}), 404
    
    image_url = result['image_url']
    if not image_url:
        return Response(build_image_placeholder_svg(f"Plant #{plant_id}"), mimetype='image/svg+xml')
    
    # Extract filename from image_url
    filename = os.path.basename(image_url)
    
    # Serve image with API access (bypass whitelist check)
    try:
        return send_from_directory('static/images/plants', filename)
    except Exception:
        return Response(build_image_placeholder_svg(f"Plant #{plant_id}"), mimetype='image/svg+xml')

@app.route('/api/images/all')
def get_all_plant_images():
    """Get list of all plant images with access URLs - allows API access to all"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, common_name, scientific_name, image_url FROM plants ORDER BY id")
    plants = cursor.fetchall()
    conn.close()
    
    image_list = []
    for plant in plants:
        image_list.append({
            'plant_id': plant['id'],
            'common_name': plant['common_name'],
            'scientific_name': plant['scientific_name'],
            'image_url': resolve_plant_image_url(dict(plant)),
            'api_image_url': f"/api/plants/{plant['id']}/image"
        })
    
    return jsonify({
        'total': len(image_list),
        'images': image_list
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
