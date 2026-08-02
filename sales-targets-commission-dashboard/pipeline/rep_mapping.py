"""
Anonymized sales rep names for presentation purposes.
Maps the original workbook's sheet-based identities to fictional,
presentation-safe names. Update REP_MAPPING if real names are needed
for internal (non-demo) use later.
"""

REP_MAPPING = {
    "Ana Roque": "Naledi Mokoena",
    "Joburg Account Manager 2": "Kabelo Sithole",
    "Leanette Mtsweni": "Refilwe Dube",
    "Andrea Klopper": "Chantelle Nel",
    "Ntokozo Masango": "Thandeka Ngcobo",
    "Sheti Ramokone": "Palesa Mahlangu",
    "Kisha Edwards": "Amanda Pillay",
    "Thato Moratho": "Bongani Khumalo",
    "AM 8": "Werner Botha",
    "AM 9": "Lindiwe Zulu",
    "AM 10": "Johan Pretorius",
    "CSA / Telesales 1": "Zanele Mokwena",
    "CSA / Telesales 2": "Michael van der Berg",
    "CSA / Telesales 3": "Precious Nkosi",
    "CSA / Telesales 4": "Grant Naidoo",
    "House Account": "House Account",
}

# Role groupings, useful for the dashboard filters
REP_ROLES = {
    "Naledi Mokoena": "Sales Consultant",
    "Kabelo Sithole": "Account Manager",
    "Refilwe Dube": "Account Manager",
    "Chantelle Nel": "Sales Consultant",
    "Thandeka Ngcobo": "Account Manager",
    "Palesa Mahlangu": "Sales Consultant",
    "Amanda Pillay": "Sales Consultant",
    "Bongani Khumalo": "Account Manager",
    "Werner Botha": "Account Manager",
    "Lindiwe Zulu": "Account Manager",
    "Johan Pretorius": "Account Manager",
    "Zanele Mokwena": "CSA / Telesales",
    "Michael van der Berg": "CSA / Telesales",
    "Precious Nkosi": "CSA / Telesales",
    "Grant Naidoo": "CSA / Telesales",
    "House Account": "House Account",
}
