---
title:  Bank App
---

Bohumil Hruška

# Úvod

-   ## Popis

Vytvoření mobilní a webové aplikaci pro bankovnictví s širokým spektrem
funkcí včetně vkladů, výběrů a vytváření účtů. Tato aplikace bude také
schopna pracovat s aktuálními kurzy měn, aby uživatelé mohli snadno
provádět transakce v různých měnách.

-   ## Odkaz

https://github.com/Bohumil-Hruska/bankApp

# Přehled aplikace

## Technologie

Programovací jazyk Python. Framework pro webové aplikace Flask.

## Funkce

-   Přihlášení -- pomocí email a hesla, dvoufázové ověření pomocí kódu
    poslaného na email

-   Vytvoření účtu -- možnost přidat účet v nové měně s počátečním
    zůstatkem 0

-   Uživatelský účet -- správa účtů v různých měnách, vklad a výběr
    peněz, provádění plateb, primární účet v CZK

-   Historie transakcí -- možnost zobrazit historii transakcí (platby,
    výběry)

-   Zobrazení zůstatků na účtech

-   Vklad na účet -- možnost vložit prostředky na zvolený účet

-   Výběr z účtu

-   Platba na jiný účet -- možnost převodu peněz na zvolený účet (tak
    jak jsme zvyklý z klasické bankovní aplikace), pokud nebude dostatek
    financí na účtu tak platba nebude provedena. Pokud však uživatel
    bude posílat peníze na jiný účet v jiné měně, než je aktuální
    zvolený účet ale zároveň uživatel je vlastníkem účtu s měnou, ve
    které chce platbu provést tak dojde k převodu peněz z vedlejšího
    účtu.

-   Přepnutí účtu -- volba přepnutí ze seznamu již vytvořených účtů

## Server

Serverová část se stará o přihlášení a ověřování uživatele. Zároveň se
stará o převody měn podle kurzu ČNB, ukládání dat to databáze, a to
včetně denní aktualizace kurzů.

## Objekty aplikace

Uživatel -- definován jménem, příjmením, emailem, heslem a ID

Účet -- definován číslem účtu (6 číslic), ID účtu, vlastníkem, měnou (na
2 desetinná místa) a datem vytvoření

# Vizuální strana aplikace

Webová aplikace (responsivní design) v českém jazyce. Ovládání pomocí
tlačítek (přihlášení, vytvoření platby, vytvoření účtu, zobrazení
historie transakcí, ...).

# Chybové stavy

V případě chyby dojde k upozornění uživatele a následnému odhlášení
uživatele. Chybové stavy, které mohou nastat (Ztráta spojení mezi
serverem a klientem, Ztráta internetového připojení).

V případě výpadku ČNB dojde k použití posledního uloženého kurzu
v databázi

# Podrobný popis funkcí

## Způsob přihlášení

Uživatel zadá svůj email, heslo a pomocí tlačítka „Vygenerovat kód"
dojde k odeslání kódu a jeho email. Po vložení do kódu do pole
„Autorizační kód" se zpřístupní možnost přihlášení pomocí tlačítka
„Přihlásit". V případě správných přístupových údajů a shodného kódu
dojde k přihlášení uživatele.

## Způsob platby 

Platba se provádí v hlavním menu aplikace pomocí tlačítka „Zadat
platba". Uživatel vyplní pole „Číslo účtu, Částka" a pokud jeho aktuální
finanční stav umožní odeslání platby dojde k zpracování platby a
následnému odeslání.

## Způsob vybrání částky

Pomocí tlačítka „Vybrat hotovost" dojde k odečtení zadané částky za
podmínek, že uživatel má dost prostředků.

## Způsob vložení částky

Vložení částky na účet je zaručen pomocí tlačítka „Vložit prostředky".
Po zadání částky dojde k n přičtení částky na účet, který je vybrán jako
aktivní.

## Způsob přepnutí účtu

Pomocí tlačítka „Přepnout účet" dojde k zobrazení seznamu již
vytvořených účtů a po kliknutí na tlačítko „Přepnout" dojde k přepnutí
na zvolený účet.

#  
