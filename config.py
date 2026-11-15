
BASE_URL = "https://schoolkeuze020.nl/"

OPEN_DAYS_URL = (
    "https://schoolkeuze020.nl/open-dagen/"
)

# School types and their full names

SCHOOL_TYPES = {
    "praktijkonderwijs": "praktijkonderwijs",
    "vmbo-b": "vmbo-basis",
    "vmbo-basis": "vmbo-basis",
    "vmbo-k": "vmbo-kader",
    "vmbo-kader": "vmbo-kader",
    "vmbo-gl": "vmbo-gemengde-leerweg",
    "vmbo-gemengde-leerweg": "vmbo-gemengde-leerweg",
    "vmbo-tl": "vmbo-theoretische-leerweg",
    "vmbo-theoretische-leerweg": "vmbo-theoretische-leerweg",
    "havo": "havo",
    "vwo": "vwo",
    "kopklas": "kopklas",
}

# Amsterdam districts

STADSDEEL_FILTERS = {
    "centrum": "Centrum",
    "zuid": "Zuid",
    "noord": "Noord",
    "west": "West",
    "oost": "Oost",
    "nieuw-west": "Nieuw-West",
    "zuidoost": "Zuidoost",
    "weesp": "Weesp",
}

IGNORE_SCHOOLS = {
    "Kopklas Amsterdam",
    "Kolom VSO Alphons Laudy",
}

ALLECIJFERS_SUFFIX = {
    "VONK": "vonk-amsterdam/",
    "TASC (Tech Amsterdam Scholen Collectief)": "tasc-amsterdam/",
    "Fons Vitae Lyceum": "fons-vitae-lyceum-amsterdam-reijnier-vinkeleskade/",
    "CSB": "csb-amsterdam/",
    "College De Meer": "college-de-meer-amsterdam-radioweg/",
    "Het Amsterdams Lyceum": "het-amsterdams-lyceum-amsterdam-valeriusplein/",
    "IVKO": "ivko-leren-van-kunst/",
    "Montessori Lyceum Amsterdam (MLA)": "montessori-lyceum-amsterdam-locatie-hoofdlocatie/",
    "Hubertus & Berkhoff": "hubertus-berkhoff-de-culinaire-vakschool/",
    "St. Ignatiusgymnasium": "sint-ignatiusgymnasium/",
    "Yuverta vmbo en pro Amsterdam-Oost": "yuverta-locatie-amsterdam-oost/",

}

# Output configuration

OUTPUT_FILE = "data/schools.json"

# HTTP configuration

REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}