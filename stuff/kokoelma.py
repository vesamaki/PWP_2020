import csv
import json
import nuuskija
import sys
import time

PITKA_MUOTO = "%H:%M:%S"
LYHYT_MUOTO = "%M:%S"

def valitse_artisti(levy):
    return levy["artisti"]

def valitse_levy(levy):
    return levy["albumi"]
    
def valitse_n(levy):
    return levy["n"]
    
def valitse_kesto(levy):
    return levy["kesto"]

def valitse_vuosi(levy):
    return levy["vuosi"]    

def kysy_luku(kysymys):
    while True:
        try:
            luku = int(input(kysymys))
        except ValueError:
            print("Arvon tulee olla kokonaisluku")
        else:
            return luku    
            
def kysy_aika(kysymys):
     while True:
        aika = input(kysymys)
        try:
            aika = tarkista_kesto(aika)
        except ValueError:
            print("Anna aika muodossa tunnit:minuutit:sekunnit tai minuutit:sekunnit")
            continue
        return aika        
        
def tarkista_kesto(kesto):
    try:
        kesto = time.strptime(kesto, PITKA_MUOTO)
    except ValueError:
        kesto = time.strptime(kesto, LYHYT_MUOTO)
    return kesto
        
def parsi_kestot(kokoelma):
    for levy in kokoelma:
        levy["kesto"] = time.struct_time(levy["kesto"])
        
def muuta_kenttia(levy):
    print("Nykyiset tiedot:")
    print("{artisti}, {levy}, {n}, {kesto}, {vuosi}".format(
        artisti=levy["artisti"], 
        levy=levy["albumi"], 
        n=levy["n"], 
        kesto=time.strftime(PITKA_MUOTO, levy["kesto"]).lstrip("0:"), 
        vuosi=levy["vuosi"]))
    print("Valitse muutettava kenttä syöttämällä sen numero. Jätä tyhjäksi lopettaaksesi.")
    print("1 - artisti")
    print("2 - levyn nimi")
    print("3 - kappaleiden määrä")
    print("4 - levyn kesto")
    print("5 - julkaisuvuosi")
    while True:
        kentta = input("Valitse kenttä (1-5): ")
        if not kentta:
            break
        elif kentta == "1":
            levy["artisti"] = input("Anna artistin nimi: ")
        elif kentta == "2":
            levy["albumi"] = input("Anna levyn: ")
        elif kentta == "3":
            levy["n"] = kysy_luku("Anna kappaleiden määrä: ")
        elif kentta == "4":
            levy["kesto"] = kysy_aika("Anna levyn kesto: ")
        elif kentta == "5":
            levy["vuosi"] = kysy_luku("Anna julkaisuvuosi: ")
        else:
            print("Kenttää ei ole olemassa")

def lataa_kokoelma(tiedosto):    
    try:
        with open(tiedosto, newline="") as lahde:
            kokoelma = json.load(lahde)
            parsi_kestot(kokoelma)
    except IOError:
        print("Tiedoston avaaminen ei onnistunut. Aloitetaan tyhjällä kokoelmalla")
        kokoelma = []
    
    return kokoelma

def rakenna_kokoelma():
    kansio = input("Syötä kansio josta haluat rakentaa kokoelman: ")
    try:
        kokoelma = nuuskija.lue_kokoelma(kansio)
    except FileNotFoundError:
        print("Kansiota ei löytynyt")
    return kokoelma
    
def tallenna_kokoelma(kokoelma, tiedosto):
    try:
        with open(tiedosto, "w", newline="") as kohde:
            json.dump(kokoelma, kohde)
    except IOError:
        print("Kohdetiedostoa ei voitu avata. Tallennus epäonnistui")
   
def lisaa(kokoelma):
    print("Täytä lisättävän levyn tiedot. Jätä levyn nimi tyhjäksi lopettaaksesi")
    while True:
        levy = input("Levyn nimi: ")
        if not levy:
            break
            
        kokoelma.append({
            "artisti": input("Artistin nimi: "), 
            "albumi": levy, 
            "n": kysy_luku("Kappaleiden lukumäärä: "),
            "kesto": kysy_aika("Kesto: "),
            "vuosi": kysy_luku("Julkaisuvuosi: ")
        })
 
def muokkaa(kokoelma):
    print("Täytä muutettavan levyn nimi ja artistin nimi. Jätä levyn nimi tyhjäksi lopettaaksesi")
    while True:
        nimi = input("Anna muutettavan levyn nimi: ").lower()
        if not nimi:
            break
        artisti = input("Anna muutettavan levyn artisti: ").lower()
        for levy in kokoelma: 
            if levy["artisti"].lower() == artisti and levy["albumi"].lower() == nimi:
                muuta_kenttia(levy)
                print("Levyn tiedot muutettu")
 
def poista(kokoelma):
    print("Täytä poistettavan levyn nimi ja artistin nimi. Jätä levyn nimi tyhjäksi lopettaaksesi")
    while True:
        nimi = input("Anna poistettavan levyn nimi: ").lower()
        if not nimi:
            break
        artisti = input("Anna poistettavan levyn artisti: ").lower()
        for levy in kokoelma[:]: 
            if levy["artisti"].lower() == artisti and levy["albumi"].lower() == nimi:
                kokoelma.remove(levy)
                print("Levy poistettu")

def jarjesta(kokoelma):
    print("Valitse kenttä jonka mukaan kokoelma järjestetään syöttämällä kenttää vastaava numero")
    print("1 - artisti")
    print("2 - levyn nimi")
    print("3 - kappaleiden määrä")
    print("4 - levyn kesto")
    print("5 - julkaisuvuosi")
    kentta = input("Valitse kenttä (1-5): ")
    jarjestys = input("Järjestys; (l)askeva vai (n)ouseva: ").lower()
    if jarjestys == "l":    
        kaanna = True
    else:
        kaanna = False
    if kentta == "1":
        kokoelma.sort(key=valitse_artisti, reverse=kaanna)
    elif kentta == "2":
        kokoelma.sort(key=valitse_levy, reverse=kaanna)
    elif kentta == "3":
        kokoelma.sort(key=valitse_n, reverse=kaanna)
    elif kentta == "4":
        kokoelma.sort(key=valitse_kesto, reverse=kaanna)
    elif kentta == "5":
        kokoelma.sort(key=valitse_vuosi, reverse=kaanna)        
    else: 
        print("Kenttää ei ole olemassa")
  
def muotoile_sivu(rivit):
    for levy in rivit:
        print("{artisti} - {levy} ({vuosi}) [{n}] [{kesto}]".format(
            artisti=levy["artisti"], 
            levy=levy["albumi"], 
            n=levy["n"], 
            kesto=time.strftime(PITKA_MUOTO, levy["kesto"]).lstrip("0:"), 
            vuosi=levy["vuosi"]))
  
def tulosta(kokoelma):
    tulostuksia = int(len(kokoelma) / 20 + 0.95)
    for i in range(tulostuksia):
        alku = i * 20
        loppu = (i + 1) * 20
        muotoile_sivu(kokoelma[alku:loppu])        
        if i < tulostuksia - 1:
            input("   -- paina enter jatkaaksesi tulostusta --")

def lue_argumentit(argumentit):
    if len(argumentit) >= 3:
        lahde = argumentit[1]
        kohde = argumentit[2]
        return lahde, kohde
    elif len(argumentit) == 2:
        lahde = argumentit[1]
        return lahde, lahde
    else:
        return None, None            

def main(lahdetiedosto, kohdetiedosto):
    kokoelma = lataa_kokoelma(lahdetiedosto)
    print("Tämä ohjelma ylläpitää levykokoelmaa. Voit valita seuraavista toiminnoista:")
    print("(R)akenna kokoelma")
    print("(L)isää uusia levyjä")
    print("(M)uokkaa levyjä")
    print("(P)oista levyjä")
    print("(J)ärjestä kokoelma")
    print("(T)ulosta kokoelma")
    print("(Q)uittaa")
    while True:
        valinta = input("Tee valintasi: ").strip().lower()
        if valinta == "r":
            kokoelma = rakenna_kokoelma()
        elif valinta == "l":
            lisaa(kokoelma)
        elif valinta == "m":
            muokkaa(kokoelma)
        elif valinta == "p":
            poista(kokoelma)
        elif valinta == "j":
            jarjesta(kokoelma)
        elif valinta == "t":
            tulosta(kokoelma)
        elif valinta == "q":
            break    
        else:
            print("Valitsemaasi toimintoa ei ole olemassa")
    tallenna_kokoelma(kokoelma, kohdetiedosto)
            
lahde, kohde = lue_argumentit(sys.argv)
if lahde:    
    try:
        main(lahde, kohde)
    except KeyboardInterrupt:
        print("Ohjelma keskeytettiin, kokoelmaa ei tallennettu")
else:
    print("Ohjelman käyttö:")
    print("python kokoelma.py lähdetiedosto (kohdetiedosto)")
