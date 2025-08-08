from db import get_db, init_db, get_password_hash
from models import Item
from datetime import datetime, timedelta

"""
IMPORTANT_PRODUCTS structure now supports a list of brands for each pharmaceutical name.
Each product entry can have a 'brands' key with a list of dicts: {"brand_name": str, "stock": int}
If 'brands' is omitted, a default brandless entry is created.
"""
IMPORTANT_PRODUCTS = {
    "Radiology": [
        {"name": "Iohexol", "category": "contrast media", "unit": "vials", "unit_price": 500.0, "brands": [{"brand_name": "Omnipaque", "stock": 10}, {"brand_name": "Hexabrix", "stock": 8}]},
        {"name": "Gadobutrol", "category": "MRI contrast agent", "unit": "vials", "unit_price": 1200.0, "brands": [{"brand_name": "Gadovist", "stock": 6}, {"brand_name": "Gadavist", "stock": 5}]},
        {"name": "Propylene glycol + Carbomer base", "category": "ultrasound gel", "unit": "bottles", "unit_price": 20.0, "brands": [{"brand_name": "Parker Aquasonic", "stock": 15}, {"brand_name": "EcoVue", "stock": 10}]},
        {"name": "Lead Aprons", "category": "safety equipment", "unit": "pieces", "unit_price": 2000.0, "brands": [{"brand_name": "Infab", "stock": 5}, {"brand_name": "Bar-Ray", "stock": 4}]},
        {"name": "Barium Sulfate Suspension", "category": "contrast media", "unit": "bottles", "unit_price": 100.0, "brands": [{"brand_name": "E-Z-HD", "stock": 10}, {"brand_name": "Baritest", "stock": 8}]},
        {"name": "Sterile saline-filled syringes", "category": "supplies", "unit": "syringes", "unit_price": 15.0, "brands": [{"brand_name": "BD", "stock": 30}, {"brand_name": "Nipro", "stock": 25}]},
        {"name": "Diphenhydramine", "category": "antihistamine", "unit": "tablets", "unit_price": 10.0, "brands": [{"brand_name": "Benadryl", "stock": 20}, {"brand_name": "Histal", "stock": 15}, {"brand_name": "Histafen", "stock": 15}, {"brand_name": "CalmAid", "stock": 10}]},
        {"name": "Hydrocortisone", "category": "emergency steroid", "unit": "vials", "unit_price": 18.0, "brands": [{"brand_name": "Solu-Cortef", "stock": 10}, {"brand_name": "Wycort", "stock": 8}, {"brand_name": "Cortel", "stock": 10}, {"brand_name": "Locoid", "stock": 6}]},
        {"name": "Paracetamol", "category": "analgesic", "unit": "tablets", "unit_price": 2.0, "brands": [{"brand_name": "Dolo", "stock": 20}, {"brand_name": "Calpol", "stock": 15}, {"brand_name": "Crocin", "stock": 10}]},
        {"name": "Intravenous catheter", "category": "supplies", "unit": "pieces", "unit_price": 10.0, "brands": [{"brand_name": "BD Venflon", "stock": 20}, {"brand_name": "Romsons", "stock": 15}]},
        {"name": "Metoclopramide", "category": "medication", "unit": "tablets", "unit_price": 8.0, "brands": [{"brand_name": "Perinorm", "stock": 20}, {"brand_name": "Reglan", "stock": 15}, {"brand_name": "Maxolon", "stock": 10}]},
        {"name": "Ondansetron", "category": "medication", "unit": "tablets", "unit_price": 10.0, "brands": [{"brand_name": "Emeset", "stock": 20}, {"brand_name": "Zofran", "stock": 15}, {"brand_name": "Ondem", "stock": 10}]},
        {"name": "Lorazepam", "category": "medication", "unit": "tablets", "unit_price": 12.0, "brands": [{"brand_name": "Ativan", "stock": 20}, {"brand_name": "Larpose", "stock": 15}, {"brand_name": "Temesta", "stock": 10}]},
        {"name": "Prednisolone", "category": "medication", "unit": "tablets", "unit_price": 14.0, "brands": [{"brand_name": "Wysolone", "stock": 20}, {"brand_name": "Omnacortil", "stock": 15}, {"brand_name": "Predmet", "stock": 10}]},
        {"name": "Dexamethasone", "category": "medication", "unit": "tablets", "unit_price": 16.0, "brands": [{"brand_name": "Dexona", "stock": 20}, {"brand_name": "Decadron", "stock": 15}, {"brand_name": "Dexona-S", "stock": 10}]},
        {"name": "Diazepam", "category": "medication", "unit": "tablets", "unit_price": 10.0, "brands": [{"brand_name": "Valium", "stock": 20}, {"brand_name": "Calmpose", "stock": 15}, {"brand_name": "Zepose", "stock": 10}]},
        {"name": "Midazolam", "category": "medication", "unit": "ampoules", "unit_price": 18.0, "brands": [{"brand_name": "Mezolam", "stock": 10}, {"brand_name": "Dormicum", "stock": 8}, {"brand_name": "Midzolam", "stock": 6}]}
    ],
    # ...add all other departments here in the same deduplicated, valid format...
}
         "brands": [
             {"brand_name": "Inderal", "stock": 10},
             {"brand_name": "Ciplar", "stock": 8}
         ]},
        {"name": "Escitalopram", "category": "SSRI", "unit": "tablets", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Lexapro", "stock": 10},
             {"brand_name": "Nexito", "stock": 8}
         ]},
        {"name": "Trihexyphenidyl", "category": "anticholinergic", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Pacitane", "stock": 10},
             {"brand_name": "Trihex", "stock": 8}
         ]}
    ],
    "Pulmonology": [
        {"name": "Salbutamol", "category": "inhaled bronchodilator", "unit": "inhalers", "unit_price": 120.0,
         "brands": [
             {"brand_name": "Asthalin", "stock": 10},
             {"brand_name": "Ventolin", "stock": 8}
         ]},
        {"name": "Budesonide", "category": "steroid inhaler", "unit": "inhalers", "unit_price": 150.0,
         "brands": [
             {"brand_name": "Budecort", "stock": 10},
             {"brand_name": "Pulmicort", "stock": 8}
         ]},
        {"name": "Montelukast", "category": "leukotriene antagonist", "unit": "tablets", "unit_price": 25.0,
         "brands": [
             {"brand_name": "Montair", "stock": 10},
             {"brand_name": "Montek", "stock": 8}
         ]},
        {"name": "Levocetirizine", "category": "antihistamine", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Xyzal", "stock": 10},
             {"brand_name": "Levocet", "stock": 8}
         ]},
        {"name": "Ambroxol + Guaiphenesin", "category": "expectorant", "unit": "syrups", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Mucolite", "stock": 10},
             {"brand_name": "Ascoril", "stock": 8}
         ]},
        {"name": "Dextromethorphan", "category": "cough suppressant", "unit": "syrups", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Corex Dx", "stock": 10},
             {"brand_name": "Rexcof", "stock": 8}
         ]},
        {"name": "Azithromycin", "category": "antibiotic", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Azithral", "stock": 10},
             {"brand_name": "Zithrocin", "stock": 8}
         ]},
        {"name": "Xylometazoline", "category": "nasal decongestant", "unit": "drops", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Otrivin", "stock": 10},
             {"brand_name": "Nasivion", "stock": 8}
         ]},
        {"name": "Oxygen Canister (portable)", "category": "equipment", "unit": "pieces", "unit_price": 500.0,
         "brands": [
             {"brand_name": "Oxy99", "stock": 5},
             {"brand_name": "Oxygize", "stock": 4}
         ]},
        {"name": "Levosalbutamol + Ipratropium", "category": "nebulizer solution", "unit": "respules", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Duolin Respules", "stock": 10},
             {"brand_name": "Combivent", "stock": 8}
         ]}
    ],
    "Pulmonology": [
        {"name": "Salbutamol (Albuterol)", "category": "medication", "unit": "inhalers", "unit_price": 120.0,
         "brands": [
             {"brand_name": "Asthalin", "stock": 50},
             {"brand_name": "Ventorlin", "stock": 40},
             {"brand_name": "ProAir", "stock": 30}
         ]},
        {"name": "Budesonide", "category": "medication", "unit": "inhalers", "unit_price": 150.0,
         "brands": [
             {"brand_name": "Budecort", "stock": 30},
             {"brand_name": "Pulmicort", "stock": 25},
             {"brand_name": "Rhinocort", "stock": 20}
         ]},
        {"name": "Ipratropium Bromide", "category": "medication", "unit": "inhalers", "unit_price": 100.0,
         "brands": [
             {"brand_name": "Atrovent", "stock": 20},
             {"brand_name": "Cipla-Ipravent", "stock": 15},
             {"brand_name": "Iprav", "stock": 10}
         ]},
        {"name": "Theophylline", "category": "medication", "unit": "tablets", "unit_price": 30.0,
         "brands": [
             {"brand_name": "Deriphyllin", "stock": 20},
             {"brand_name": "Theolair", "stock": 15},
             {"brand_name": "Uniphyl", "stock": 10}
         ]},
        {"name": "Montelukast", "category": "medication", "unit": "tablets", "unit_price": 25.0,
         "brands": [
             {"brand_name": "Montair", "stock": 20},
             {"brand_name": "Singulair", "stock": 15},
             {"brand_name": "Montecip", "stock": 10}
         ]},
        {"name": "Levosalbutamol", "category": "medication", "unit": "inhalers", "unit_price": 110.0,
         "brands": [
             {"brand_name": "Levolin", "stock": 20},
             {"brand_name": "Xopenex", "stock": 15},
             {"brand_name": "Salbair", "stock": 10}
         ]},
        {"name": "Tiotropium", "category": "medication", "unit": "inhalers", "unit_price": 140.0,
         "brands": [
             {"brand_name": "Spiriva", "stock": 20},
             {"brand_name": "Tiova", "stock": 15},
             {"brand_name": "Tiomate", "stock": 10}
         ]},
        {"name": "Fluticasone + Salmeterol", "category": "medication", "unit": "inhalers", "unit_price": 180.0,
         "brands": [
             {"brand_name": "Seretide", "stock": 15},
             {"brand_name": "Foracort", "stock": 12},
             {"brand_name": "Airduo", "stock": 10}
         ]},
        {"name": "Dextromethorphan", "category": "medication", "unit": "syrups", "unit_price": 25.0,
         "brands": [
             {"brand_name": "Corex Dx", "stock": 20},
             {"brand_name": "Phensedyl DX", "stock": 15},
             {"brand_name": "Benadryl Cough", "stock": 10}
         ]},
        {"name": "Azithromycin", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Azithral", "stock": 20},
             {"brand_name": "Zithromax", "stock": 15},
             {"brand_name": "Azee", "stock": 10}
         ]}
    ],
    "Psychiatry": [
        {"name": "Sertraline", "category": "medication", "unit": "tablets", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Zoloft", "stock": 20},
             {"brand_name": "Serlift", "stock": 15},
             {"brand_name": "Daxid", "stock": 10}
         ]},
        {"name": "Fluoxetine", "category": "medication", "unit": "tablets", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Prozac", "stock": 20},
             {"brand_name": "Flunil", "stock": 15},
             {"brand_name": "Foxetin", "stock": 10}
         ]},
        {"name": "Olanzapine", "category": "medication", "unit": "tablets", "unit_price": 25.0,
         "brands": [
             {"brand_name": "Oliza", "stock": 20},
             {"brand_name": "Zyprexa", "stock": 15},
             {"brand_name": "Olanex", "stock": 10}
         ]},
        {"name": "Risperidone", "category": "medication", "unit": "tablets", "unit_price": 22.0,
         "brands": [
             {"brand_name": "Risperdal", "stock": 20},
             {"brand_name": "Sizodon", "stock": 15},
             {"brand_name": "Riscalin", "stock": 10}
         ]},
        {"name": "Alprazolam", "category": "medication", "unit": "tablets", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Alprax", "stock": 20},
             {"brand_name": "Restyl", "stock": 15},
             {"brand_name": "Xanor", "stock": 10}
         ]},
        {"name": "Clonazepam", "category": "medication", "unit": "tablets", "unit_price": 16.0,
         "brands": [
             {"brand_name": "Clonotril", "stock": 20},
             {"brand_name": "Rivotril", "stock": 15},
             {"brand_name": "Lonazep", "stock": 10}
         ]},
        {"name": "Escitalopram", "category": "medication", "unit": "tablets", "unit_price": 19.0,
         "brands": [
             {"brand_name": "Lexapro", "stock": 20},
             {"brand_name": "Nexito", "stock": 15},
             {"brand_name": "Cipralex", "stock": 10}
         ]},
        {"name": "Aripiprazole", "category": "medication", "unit": "tablets", "unit_price": 30.0,
         "brands": [
             {"brand_name": "Arip MT", "stock": 20},
             {"brand_name": "Abilify", "stock": 15},
             {"brand_name": "Arpizol", "stock": 10}
         ]},
        {"name": "Lithium Carbonate", "category": "medication", "unit": "tablets", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Lithosun", "stock": 20},
             {"brand_name": "Lithicarb", "stock": 15},
             {"brand_name": "Priadel", "stock": 10}
         ]},
        {"name": "Quetiapine", "category": "medication", "unit": "tablets", "unit_price": 28.0,
         "brands": [
             {"brand_name": "Qutan", "stock": 20},
             {"brand_name": "Seroquel", "stock": 15},
             {"brand_name": "Quitipin", "stock": 10}
         ]}
    ],
    "Radiology": [
        {"name": "Metoclopramide", "category": "medication", "unit": "tablets", "unit_price": 8.0,
         "brands": [
             {"brand_name": "Perinorm", "stock": 20},
             {"brand_name": "Reglan", "stock": 15},
             {"brand_name": "Maxolon", "stock": 10}
         ]},
        {"name": "Ondansetron", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Emeset", "stock": 20},
             {"brand_name": "Zofran", "stock": 15},
             {"brand_name": "Ondem", "stock": 10}
         ]},
        {"name": "Lorazepam", "category": "medication", "unit": "tablets", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Ativan", "stock": 20},
             {"brand_name": "Larpose", "stock": 15},
             {"brand_name": "Temesta", "stock": 10}
         ]},
        {"name": "Prednisolone", "category": "medication", "unit": "tablets", "unit_price": 14.0,
         "brands": [
             {"brand_name": "Wysolone", "stock": 20},
             {"brand_name": "Omnacortil", "stock": 15},
             {"brand_name": "Predmet", "stock": 10}
         ]},
        {"name": "Diphenhydramine", "category": "medication", "unit": "syrups", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Benadryl", "stock": 20},
             {"brand_name": "Histafen", "stock": 15},
             {"brand_name": "CalmAid", "stock": 10}
         ]},
        {"name": "Dexamethasone", "category": "medication", "unit": "tablets", "unit_price": 16.0,
         "brands": [
             {"brand_name": "Dexona", "stock": 20},
             {"brand_name": "Decadron", "stock": 15},
             {"brand_name": "Dexona-S", "stock": 10}
         ]},
        {"name": "Diazepam", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Valium", "stock": 20},
             {"brand_name": "Calmpose", "stock": 15},
             {"brand_name": "Zepose", "stock": 10}
         ]},
        {"name": "Midazolam", "category": "medication", "unit": "ampoules", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Mezolam", "stock": 10},
             {"brand_name": "Dormicum", "stock": 8},
             {"brand_name": "Midzolam", "stock": 6}
         ]},
        {"name": "Hydrocortisone", "category": "medication", "unit": "vials", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Cortel", "stock": 10},
             {"brand_name": "Solu-Cortef", "stock": 8},
             {"brand_name": "Locoid", "stock": 6}
         ]},
        {"name": "Paracetamol", "category": "medication", "unit": "tablets", "unit_price": 2.0,
         "brands": [
             {"brand_name": "Crocin", "stock": 20},
             {"brand_name": "Calpol", "stock": 15},
             {"brand_name": "Dolo", "stock": 10}
         ]}
    ,
    ],
    "Emergency Department": [
        {"name": "Adrenaline (Epinephrine)", "category": "medication", "unit": "ampoules", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Adrenaline Chloride Injection", "stock": 100},
             {"brand_name": "EpiPen", "stock": 50}
         ]},
        {"name": "Atropine", "category": "medication", "unit": "ampoules", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Atropen", "stock": 70},
             {"brand_name": "Atrostat", "stock": 40}
         ]},
        {"name": "Nitroglycerin", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Nitrostat", "stock": 80},
             {"brand_name": "Angispan", "stock": 60},
             {"brand_name": "Nitrolingual", "stock": 40}
         ]},
        {"name": "Diazepam (Injection)", "category": "medication", "unit": "ampoules", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Calmpose", "stock": 60},
             {"brand_name": "Valium", "stock": 40}
         ]},
        {"name": "Naloxone", "category": "medication", "unit": "ampoules", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Narcan", "stock": 20},
             {"brand_name": "Nexloxa", "stock": 15}
         ]},
        {"name": "Dopamine", "category": "medication", "unit": "ampoules", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Dopamine Hydrochloride Injection", "stock": 30}
         ]},
        {"name": "Hydrocortisone (IV)", "category": "medication", "unit": "vials", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Solu-Cortef", "stock": 20},
             {"brand_name": "Hydrocort", "stock": 15}
         ]},
        {"name": "Midazolam", "category": "medication", "unit": "ampoules", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Midacip", "stock": 15},
             {"brand_name": "Dormicum", "stock": 10},
             {"brand_name": "Mezolam", "stock": 8}
         ]},
        {"name": "Furosemide (IV)", "category": "medication", "unit": "ampoules", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Lasix", "stock": 20},
             {"brand_name": "Frusemide", "stock": 15}
         ]},
        {"name": "Mannitol (IV)", "category": "medication", "unit": "bottles", "unit_price": 25.0,
         "brands": [
             {"brand_name": "Osmitrol", "stock": 10},
             {"brand_name": "Mannite", "stock": 8}
         ]}
    ],
    "Pediatrics": [
        {"name": "Paracetamol Syrup", "category": "medication", "unit": "bottles", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Crocin DS", "stock": 60},
             {"brand_name": "Calpol", "stock": 50},
             {"brand_name": "T-98", "stock": 40}
         ]},
        {"name": "Amoxicillin (Syrup)", "category": "medication", "unit": "bottles", "unit_price": 35.0,
         "brands": [
             {"brand_name": "Mox", "stock": 30},
             {"brand_name": "Novamox", "stock": 25},
             {"brand_name": "Almox", "stock": 20}
         ]},
        {"name": "ORS Sachets", "category": "supplies", "unit": "sachets", "unit_price": 3.0,
         "brands": [
             {"brand_name": "Electral", "stock": 30},
             {"brand_name": "Enerzal", "stock": 25},
             {"brand_name": "DripDrop", "stock": 20}
         ]},
        {"name": "Zinc Sulphate", "category": "medication", "unit": "tablets", "unit_price": 5.0,
         "brands": [
             {"brand_name": "Zinconia", "stock": 30},
             {"brand_name": "Zincovit", "stock": 25},
             {"brand_name": "Z&D", "stock": 20}
         ]},
        {"name": "Albendazole (Syrup)", "category": "medication", "unit": "bottles", "unit_price": 4.0,
         "brands": [
             {"brand_name": "Zentel", "stock": 20},
             {"brand_name": "Alworm", "stock": 15},
             {"brand_name": "Bendex", "stock": 10}
         ]},
        {"name": "Salbutamol Syrup", "category": "medication", "unit": "bottles", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Asthalin", "stock": 30},
             {"brand_name": "Salbair", "stock": 25},
             {"brand_name": "Ventorlin", "stock": 20}
         ]},
        {"name": "Ibuprofen (Suspension)", "category": "medication", "unit": "bottles", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Ibugesic Plus", "stock": 20},
             {"brand_name": "Nurofen for Children", "stock": 15}
         ]},
        {"name": "Cefixime (Suspension)", "category": "medication", "unit": "bottles", "unit_price": 30.0,
         "brands": [
             {"brand_name": "Taxim-O", "stock": 30},
             {"brand_name": "Cefolac", "stock": 25},
             {"brand_name": "Zifi", "stock": 20}
         ]},
        {"name": "Multivitamin Drops", "category": "medication", "unit": "bottles", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Polybion", "stock": 20},
             {"brand_name": "Supradyn", "stock": 15},
             {"brand_name": "Becozinc", "stock": 10}
         ]},
        {"name": "Iron Supplement Drops", "category": "medication", "unit": "bottles", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Feronia", "stock": 20},
             {"brand_name": "Orofer", "stock": 15},
             {"brand_name": "Dexorange", "stock": 10}
         ]}
    ],
        {"name": "Nitroglycerin", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Sorbitrate", "stock": 80},
             {"brand_name": "Nitrostat", "stock": 60},
             {"brand_name": "Angispan", "stock": 40}
         ]},
        {"name": "Dopamine", "category": "medication", "unit": "ampoules", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Intropin", "stock": 30},
             {"brand_name": "Dopacon", "stock": 20},
             {"brand_name": "Doparest", "stock": 10}
         ]},
        {"name": "Lidocaine (Lignocaine)", "category": "medication", "unit": "ampoules", "unit_price": 8.0,
         "brands": [
             {"brand_name": "Lox", "stock": 30},
             {"brand_name": "Xylocaine", "stock": 20},
             {"brand_name": "Lignox", "stock": 10}
         ]},
        {"name": "Midazolam", "category": "medication", "unit": "ampoules", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Mezolam", "stock": 20},
             {"brand_name": "Midacip", "stock": 15},
             {"brand_name": "Hypnovel", "stock": 10}
         ]},
        {"name": "Aspirin", "category": "medication", "unit": "tablets", "unit_price": 2.0,
         "brands": [
             {"brand_name": "Ecosprin", "stock": 60},
             {"brand_name": "Aspicot", "stock": 40},
             {"brand_name": "Ascard", "stock": 20}
         ]},
        {"name": "Naloxone", "category": "medication", "unit": "ampoules", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Narcan", "stock": 20},
             {"brand_name": "Nalox", "stock": 15},
             {"brand_name": "Naxon", "stock": 10}
         ]},
    ],
    "Dermatology": [
        {"name": "Hydrocortisone Cream", "category": "medication", "unit": "tubes", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Cortizone", "stock": 20},
             {"brand_name": "HC Derm", "stock": 15},
             {"brand_name": "Cutisoft HC", "stock": 10}
         ]},
        {"name": "Clotrimazole", "category": "medication", "unit": "tubes", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Candid", "stock": 20},
             {"brand_name": "Canesten", "stock": 15},
             {"brand_name": "Clocip", "stock": 10}
         ]},
        {"name": "Mupirocin", "category": "medication", "unit": "tubes", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Bactroban", "stock": 10},
             {"brand_name": "T-Bact", "stock": 8},
             {"brand_name": "Mupi", "stock": 6}
         ]},
        {"name": "Fusidic Acid", "category": "medication", "unit": "tubes", "unit_price": 20.0,
         "brands": [
             {"brand_name": "Fucidin", "stock": 10},
             {"brand_name": "Fusigen", "stock": 8},
             {"brand_name": "Fusiwal", "stock": 6}
         ]},
        {"name": "Calamine Lotion", "category": "medication", "unit": "bottles", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Calosoft", "stock": 10},
             {"brand_name": "Caladryl", "stock": 8},
             {"brand_name": "Calaz", "stock": 6}
         ]},
        {"name": "Permethrin", "category": "medication", "unit": "tubes", "unit_price": 16.0,
         "brands": [
             {"brand_name": "Permite", "stock": 10},
             {"brand_name": "Scabper", "stock": 8},
             {"brand_name": "Elimite", "stock": 6}
         ]},
        {"name": "Betamethasone", "category": "medication", "unit": "tubes", "unit_price": 14.0,
         "brands": [
             {"brand_name": "Betnovate", "stock": 10},
             {"brand_name": "Diprosone", "stock": 8},
             {"brand_name": "Topgraf-B", "stock": 6}
         ]},
        {"name": "Isotretinoin (topical)", "category": "medication", "unit": "gels", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Retino-A", "stock": 10},
             {"brand_name": "Isotroin Gel", "stock": 8},
             {"brand_name": "Acnetoin", "stock": 6}
         ]},
        {"name": "Ketoconazole Cream", "category": "medication", "unit": "tubes", "unit_price": 22.0,
         "brands": [
             {"brand_name": "Nizral", "stock": 10},
             {"brand_name": "Ketomac", "stock": 8},
             {"brand_name": "Scalpe", "stock": 6}
         ]},
        {"name": "Salicylic Acid", "category": "medication", "unit": "tubes", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Salicylix", "stock": 10},
             {"brand_name": "Acnestar", "stock": 8},
             {"brand_name": "Ducray", "stock": 6}
         ]}
    ],
    "Obstetrics & Gynecology (OB/GYN)": [
        {"name": "Oxytocin Injection", "category": "medication", "unit": "ampoules", "unit_price": 25.0},
        {"name": "Folic Acid", "category": "medication", "unit": "tablets", "unit_price": 2.0},
        {"name": "Iron Tablets", "category": "medication", "unit": "tablets", "unit_price": 3.0},
        {"name": "Magnesium Sulfate", "category": "medication", "unit": "vials", "unit_price": 20.0},
        {"name": "Maternity Pads", "category": "supplies", "unit": "packs", "unit_price": 15.0},
        {"name": "Pregnancy Test Kit", "category": "supplies", "unit": "kits", "unit_price": 10.0},
        {"name": "Calcium Tablets", "category": "medication", "unit": "tablets", "unit_price": 4.0},
        {"name": "Vitamin D3", "category": "medication", "unit": "tablets", "unit_price": 5.0},
        {"name": "Breast Pump", "category": "equipment", "unit": "pieces", "unit_price": 200.0},
        {"name": "Condoms", "category": "supplies", "unit": "pieces", "unit_price": 1.0},
    ],
    "Orthopedics": [
        {"name": "Plaster of Paris Bandage", "category": "supplies", "unit": "rolls", "unit_price": 20.0},
        {"name": "Crutches", "category": "equipment", "unit": "pairs", "unit_price": 300.0},
        {"name": "Knee Brace", "category": "equipment", "unit": "pieces", "unit_price": 250.0},
        {"name": "Calcium Tablets", "category": "medication", "unit": "tablets", "unit_price": 4.0},
        {"name": "Ibuprofen", "category": "medication", "unit": "tablets", "unit_price": 3.0},
        {"name": "Arm Sling", "category": "supplies", "unit": "pieces", "unit_price": 40.0},
        {"name": "Elastic Bandage", "category": "supplies", "unit": "rolls", "unit_price": 10.0},
        {"name": "Hot/Cold Pack", "category": "supplies", "unit": "packs", "unit_price": 30.0},
        {"name": "Wheelchair", "category": "equipment", "unit": "pieces", "unit_price": 1500.0},
        {"name": "Laryngeal Mask Airway", "category": "equipment", "unit": "pieces", "unit_price": 300.0},
        {"name": "Endotracheal Tube", "category": "supplies", "unit": "pieces", "unit_price": 25.0},
        {"name": "Spinal Needle", "category": "supplies", "unit": "pieces", "unit_price": 15.0},
        {"name": "Bupivacaine", "category": "medication", "unit": "vials", "unit_price": 30.0},
        {"name": "Ambu Bag", "category": "equipment", "unit": "pieces", "unit_price": 400.0},
        {"name": "Oxygen Cylinder", "category": "equipment", "unit": "pieces", "unit_price": 2000.0},
        {"name": "Suction Machine", "category": "equipment", "unit": "pieces", "unit_price": 2500.0},
    ],
    "Pathology": [
        {"name": "Microscope Slides", "category": "supplies", "unit": "boxes", "unit_price": 30.0},
        {"name": "Test Tubes", "category": "supplies", "unit": "boxes", "unit_price": 20.0},
        {"name": "Blood Collection Tubes", "category": "supplies", "unit": "boxes", "unit_price": 25.0},
        {"name": "Centrifuge", "category": "equipment", "unit": "pieces", "unit_price": 3000.0},
        {"name": "Staining Rack", "category": "equipment", "unit": "pieces", "unit_price": 500.0},
        {"name": "Pipette Tips", "category": "supplies", "unit": "boxes", "unit_price": 15.0},
        {"name": "Reagent Bottles", "category": "supplies", "unit": "bottles", "unit_price": 12.0},
        {"name": "Blood Grouping Kit", "category": "supplies", "unit": "kits", "unit_price": 100.0},
        {"name": "Urine Test Strips", "category": "supplies", "unit": "boxes", "unit_price": 18.0},
        {"name": "Microtome", "category": "equipment", "unit": "pieces", "unit_price": 4000.0},
    ],
    "Dermatology": [
        {"name": "Hydrocortisone Cream", "category": "medication", "unit": "tubes", "unit_price": 15.0},
        {"name": "Clotrimazole Cream", "category": "medication", "unit": "tubes", "unit_price": 12.0},
        {"name": "Antifungal Powder", "category": "medication", "unit": "bottles", "unit_price": 20.0},
        {"name": "Aloe Vera Gel", "category": "medication", "unit": "tubes", "unit_price": 10.0},
        {"name": "Benzoyl Peroxide", "category": "medication", "unit": "gels", "unit_price": 18.0},
        {"name": "Salicylic Acid Ointment", "category": "medication", "unit": "tubes", "unit_price": 14.0},
        {"name": "Emollient Lotion", "category": "medication", "unit": "bottles", "unit_price": 22.0},
        {"name": "Permethrin Cream", "category": "medication", "unit": "tubes", "unit_price": 16.0},
        {"name": "Coal Tar Shampoo", "category": "medication", "unit": "bottles", "unit_price": 25.0},
        {"name": "Antihistamine Tablets", "category": "medication", "unit": "tablets", "unit_price": 5.0},
    ],
    "Psychiatry": [
        {"name": "Sertraline", "category": "medication", "unit": "tablets", "unit_price": 20.0},
        {"name": "Olanzapine", "category": "medication", "unit": "tablets", "unit_price": 25.0},
        {"name": "Diazepam", "category": "medication", "unit": "tablets", "unit_price": 10.0},
        {"name": "Risperidone", "category": "medication", "unit": "tablets", "unit_price": 18.0},
        {"name": "Amitriptyline", "category": "medication", "unit": "tablets", "unit_price": 8.0},
        {"name": "Quetiapine", "category": "medication", "unit": "tablets", "unit_price": 22.0},
        {"name": "Lithium Carbonate", "category": "medication", "unit": "tablets", "unit_price": 15.0},
        {"name": "Haloperidol", "category": "medication", "unit": "tablets", "unit_price": 12.0},
        {"name": "Mirtazapine", "category": "medication", "unit": "tablets", "unit_price": 19.0},
        {"name": "Zolpidem", "category": "medication", "unit": "tablets", "unit_price": 16.0},
    ],
    "Ophthalmology": [
        {"name": "Artificial Tears", "category": "medication", "unit": "bottles", "unit_price": 15.0},
        {"name": "Timolol Eye Drops", "category": "medication", "unit": "bottles", "unit_price": 18.0},
        {"name": "Atropine Eye Drops", "category": "medication", "unit": "bottles", "unit_price": 20.0},
        {"name": "Sterile Eye Pads", "category": "supplies", "unit": "pieces", "unit_price": 3.0},
        {"name": "Eye Ointment", "category": "medication", "unit": "tubes", "unit_price": 12.0},
        {"name": "Fluorescein Strips", "category": "supplies", "unit": "strips", "unit_price": 5.0},
        {"name": "Antibiotic Eye Drops", "category": "medication", "unit": "bottles", "unit_price": 22.0},
        {"name": "Cyclopentolate Drops", "category": "medication", "unit": "bottles", "unit_price": 17.0},
        {"name": "Eye Shield", "category": "supplies", "unit": "pieces", "unit_price": 8.0},
        {"name": "Sterile Eye Wash", "category": "supplies", "unit": "bottles", "unit_price": 10.0},
    ],
    "ENT": [
        {"name": "Levocetirizine", "category": "medication", "unit": "tablets", "unit_price": 5.0,
         "brands": [
             {"brand_name": "Xyzal", "stock": 30},
             {"brand_name": "Levocet", "stock": 25},
             {"brand_name": "Vozet", "stock": 20}
         ]},
        {"name": "Mometasone Nasal Spray", "category": "medication", "unit": "bottles", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Nasonex", "stock": 15},
             {"brand_name": "Momate Nasal", "stock": 12},
             {"brand_name": "Metaspray", "stock": 10}
         ]},
        {"name": "Ofloxacin (Ear Drops)", "category": "medication", "unit": "bottles", "unit_price": 18.0,
         "brands": [
             {"brand_name": "Oflox", "stock": 15},
             {"brand_name": "Optilox", "stock": 12},
             {"brand_name": "Oflin", "stock": 10}
         ]},
        {"name": "Betahistine", "category": "medication", "unit": "tablets", "unit_price": 7.0,
         "brands": [
             {"brand_name": "Vertin", "stock": 20},
             {"brand_name": "Betavert", "stock": 15},
             {"brand_name": "Histinorm", "stock": 10}
         ]},
        {"name": "Chlorpheniramine Maleate", "category": "medication", "unit": "tablets", "unit_price": 4.0,
         "brands": [
             {"brand_name": "CPM", "stock": 20},
             {"brand_name": "Cetzine-D", "stock": 15},
             {"brand_name": "Allerfin", "stock": 10}
         ]},
        {"name": "Azithromycin", "category": "medication", "unit": "tablets", "unit_price": 10.0,
         "brands": [
             {"brand_name": "Azithral", "stock": 20},
             {"brand_name": "Zithromax", "stock": 15},
             {"brand_name": "Azee", "stock": 10}
         ]},
        {"name": "Oxymetazoline Nasal Drops", "category": "medication", "unit": "bottles", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Nasivion", "stock": 15},
             {"brand_name": "Otrivin", "stock": 12},
             {"brand_name": "Sinarest", "stock": 10}
         ]},
        {"name": "Fexofenadine", "category": "medication", "unit": "tablets", "unit_price": 8.0,
         "brands": [
             {"brand_name": "Allegra", "stock": 20},
             {"brand_name": "Telfast", "stock": 15},
             {"brand_name": "Fexigo", "stock": 10}
         ]},
        {"name": "Fluticasone Nasal Spray", "category": "medication", "unit": "bottles", "unit_price": 15.0,
         "brands": [
             {"brand_name": "Flixonase", "stock": 10},
             {"brand_name": "Nasoflo", "stock": 8},
             {"brand_name": "Flohale", "stock": 6}
         ]},
        {"name": "Clotrimazole Ear Drops", "category": "medication", "unit": "bottles", "unit_price": 12.0,
         "brands": [
             {"brand_name": "Candid Ear Drops", "stock": 10},
             {"brand_name": "Canesten", "stock": 8},
             {"brand_name": "Cloderm", "stock": 6}
         ]},
    ],
}

def seed_products():
    db = next(get_db())
    for dept, products in IMPORTANT_PRODUCTS.items():
        for prod in products:
            brands = prod.get("brands")
            if brands:
                for brand in brands:
                    exists = db.query(Item).filter(
                        Item.name == prod["name"],
                        Item.department == dept,
                        Item.brand_name == brand["brand_name"]
                    ).first()
                    if not exists:
                        item = Item(
                            name=prod["name"],
                            category=prod["category"],
                            current_stock=brand.get("stock", 100),
                            min_threshold=10,
                            max_capacity=1000,
                            unit=prod["unit"],
                            unit_price=prod["unit_price"],
                            supplier_name="Default Supplier",
                            expiry_date=datetime.now().date() + timedelta(days=365),
                            location="Main Store",
                            department=dept,
                            barcode=None,
                            brand_name=brand["brand_name"]
                        )
                        db.add(item)
            else:
                exists = db.query(Item).filter(
                    Item.name == prod["name"],
                    Item.department == dept,
                    Item.brand_name == None
                ).first()
                if not exists:
                    item = Item(
                        name=prod["name"],
                        category=prod["category"],
                        current_stock=prod.get("current_stock", 100),
                        min_threshold=10,
                        max_capacity=1000,
                        unit=prod["unit"],
                        unit_price=prod["unit_price"],
                        supplier_name="Default Supplier",
                        expiry_date=datetime.now().date() + timedelta(days=365),
                        location="Main Store",
                        department=dept,
                        barcode=None,
                        brand_name=None
                    )
                    db.add(item)
    db.commit()
    print("Important products seeded!")

if __name__ == "__main__":
    init_db()
    seed_products()
