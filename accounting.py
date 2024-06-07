import csv

# Get report/input file here: https://www.paypal.com/reports/dlog

# Run with python accounting.py

# SUMMARY REPORT

def summarize_sale(date, buyer, brutto, avgift, source, countryCode, country, vat):
    with open('month.txt', 'a') as f:
        f.write('{}\n'.format(date))
        f.write('Försäljning via {}\n'.format(source))
        f.write('Köpare: {}\n'.format(buyer))
        f.write('Köparens land: {} ({})\n'.format(country, countryCode))
        f.write('{} kr\n'.format(brutto))
        f.write('Varav moms: {} kr\n'.format(vat))
        f.write('Paypal-avgift -{} kr\n'.format(avgift))
        f.write('\n\n')
        f.close()


def summarize_fee(date, title, fee):
    with open('month.txt', 'a') as f:
        f.write('{}\n'.format(date))
        f.write('{}\n'.format(title))
        f.write('-{} kr\n'.format(fee))
        f.write('\n\n')
        f.close()


def summarize_expense(date, title, fee, vat):
    with open('month.txt', 'a') as f:
        f.write('{}\n'.format(date))
        f.write('{}\n'.format(title))
        f.write('-{} kr\n'.format(fee))
        f.write('Varav moms: {} kr\n'.format(vat))
        f.write('\n\n')
        f.close()

# UTILS

def parse_date(date1):
    splitted = date1.split('.')
    day = splitted[0]
    month = splitted[1]
    year = splitted[2]
    return '{}{}{}'.format(year, month, day)


def parse_to_positive_number(input):
    return round(float(input.replace(',', '.').replace('−', '').replace('\xa0', '')), 2)


def clean_special_characters(name):
    return name.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace('Å', 'A').replace('Ä', 'A').replace('Ö', 'O').replace('ü', 'u').replace('Ü', 'U').replace('ë', 'e').replace('é', 'e')


eu_countries = ['BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT',
                'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI']
def is_eu(countryCode):
    return countryCode in eu_countries

PAYPAL_ACCOUNT_SEK = '1933'
PAYPAL_ACCOUNT_EURO = '1935'

EURO_TO_SEK_EXCHANGE_RATE = 11.63

# ACCOUNTING FUNCTIONS

def sale_sweden(date, buyer, brutto, avgift, source, currency):
    account = PAYPAL_ACCOUNT_SEK
    if (currency == 'EUR'):
        account = PAYPAL_ACCOUNT_EURO
        brutto = round(brutto * EURO_TO_SEK_EXCHANGE_RATE, 2)
    moms = round(brutto * 0.2, 2)
    netto = round(brutto * 0.8, 2)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{} - {}"\n'.format(date, source, buyer))
        f.write('{\n')
        f.write('#TRANS {} {{ }} {}\n'.format(account, brutto))
        f.write('#TRANS 3001 {{ }} -{}\n'.format(netto))
        f.write('#TRANS 2610 {{ }} -{}\n'.format(moms))
        f.write('#TRANS {} {{ }} -{}\n'.format(account, avgift))
        f.write('#TRANS 6570 {{ }} {}\n'.format(avgift))
        f.write('}\n')
        f.close()


def sale_eu(date, buyer, brutto, avgift, source, currency):
    account = PAYPAL_ACCOUNT_SEK
    if (currency == 'EUR'):
        account = PAYPAL_ACCOUNT_EURO
        brutto = round(brutto * EURO_TO_SEK_EXCHANGE_RATE, 2)
    moms = round(brutto * 0.2, 2)
    netto = round(brutto * 0.8, 2)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{} - {}"\n'.format(date, source, buyer))
        f.write('{\n')
        f.write('#TRANS {} {{ }} {}\n'.format(account, brutto))
        f.write('#TRANS 3106 {{ }} -{}\n'.format(netto))
        f.write('#TRANS 2610 {{ }} -{}\n'.format(moms))
        f.write('#TRANS {} {{ }} -{}\n'.format(account, avgift))
        f.write('#TRANS 6570 {{ }} {}\n'.format(avgift))
        f.write('}\n')
        f.close()


def sale_outside_eu(date, buyer, brutto, avgift, source, currency):
    account = PAYPAL_ACCOUNT_SEK
    if (currency == 'EUR'):
        account = PAYPAL_ACCOUNT_EURO
        brutto = round(brutto * EURO_TO_SEK_EXCHANGE_RATE, 2)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{} - {}"\n'.format(date, source, buyer))
        f.write('{\n')
        f.write('#TRANS {} {{ }} {}\n'.format(account, brutto))
        f.write('#TRANS 3105 {{ }} -{}\n'.format(brutto))
        f.write('#TRANS {} {{ }} -{}\n'.format(account, avgift))
        f.write('#TRANS 6570 {{ }} {}\n'.format(avgift))
        f.write('}\n')
        f.close()


def handle_sale(row, source):
    currency = row['Valuta']
    if currency != 'SEK' and currency != 'EUR':
        print("!!! Sale for unknown currency: " + row['Namn'] + currency)
        print("")
        return
    date = parse_date(row['\ufeff"Datum"'])
    buyer = row['Namn']
    brutto = row['Brutto']
    avgift = row['Avgift']
    try:
        countryCode = row['Köparens landskod']
    except KeyError:
        countryCode = row['Landskod']
    country = row['Land']

    bruttoNumber = parse_to_positive_number(brutto)
    avgiftNumberPositive = parse_to_positive_number(avgift)

    buyer = clean_special_characters(buyer)
    vat = round(bruttoNumber * 0.2, 2)

    # print('')
    if (countryCode == 'SE'):
        sale_sweden(date, buyer, bruttoNumber, avgiftNumberPositive, source, currency)
        summarize_sale(date, buyer, bruttoNumber,
                       avgiftNumberPositive, source, countryCode, country, vat)
    elif (is_eu(countryCode)):
        sale_eu(date, buyer, bruttoNumber, avgiftNumberPositive, source, currency)
        summarize_sale(date, buyer, bruttoNumber,
                       avgiftNumberPositive, source, countryCode, country, vat)
    else:
        sale_outside_eu(date, buyer, bruttoNumber,
                        avgiftNumberPositive, source, currency)
        summarize_sale(date, buyer, bruttoNumber,
                       avgiftNumberPositive, source, countryCode, country, 0)

def handle_webshop(row):
    handle_sale(row, 'Jawbreaker.se')

def handle_bandcamp(row):
    handle_sale(row, 'Bandcamp')

def handle_discogs(row):
    handle_sale(row, 'Discogs')


def handle_discogs_fee(row):
    if row['Valuta'] != 'SEK':
        print('Discogs fee - currency {} Not implemented', row['Valuta'])
        return

    date = parse_date(row['\ufeff"Datum"'])
    title = '{} - {}'.format(row['Typ'], 'Discogs')

    brutto = row['Brutto']
    avgift = parse_to_positive_number(brutto)

    summarize_fee(date, 'Avgift till Discogs', avgift)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{}"\n'.format(date, title))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(avgift))
        f.write('#TRANS 6570 {{ }} {}\n'.format(avgift))
        f.write('}\n')
        f.close()


def handle_bandcamp_subscription(row):
    if row['Valuta'] != 'SEK':
        # ignore, this is handled by the SEK post only
        return

    date = parse_date(row['\ufeff"Datum"'])
    title = 'Bandcamp - Label Account Subscription'
    brutto = row['Brutto']
    avgift = float(brutto.replace(',', '.').replace('−', ''))
    moms = avgift * 0.25

    summarize_expense(date, title, avgift, moms)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{}"\n'.format(date, title))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(avgift))
        f.write('#TRANS 6230 {{ }} {}\n'.format(avgift))
        f.write('#TRANS 4598 {{ }} -{}\n'.format(avgift))
        f.write('#TRANS 4531 {{ }} {}\n'.format(avgift))
        f.write('#TRANS 2614 {{ }} -{}\n'.format(moms))
        f.write('#TRANS 2645 {{ }} {}\n'.format(moms))
        f.write('}\n')
        f.close()


def handle_utbetalning(row):
    date = parse_date(row['\ufeff"Datum"'])
    title = 'PayPal till SEB'
    brutto = row['Brutto']
    bruttoNumberPositive = parse_to_positive_number(brutto)

    summarize_fee(date, 'Egen överföring till bankkonto', bruttoNumberPositive)

    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{}"\n'.format(date, title))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(bruttoNumberPositive))
        f.write('#TRANS 1930 {{ }} {}\n'.format(bruttoNumberPositive))
        f.write('}\n')
        f.close()


def refund_sweden(date, buyer, brutto):
    moms = round(brutto * 0.2)
    netto = round(brutto * 0.8)
    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "Refund - {}"\n'.format(date, buyer))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(brutto))
        f.write('#TRANS 3001 {{ }} {}\n'.format(netto))
        f.write('#TRANS 2610 {{ }} {}\n'.format(moms))
        f.write('}\n')
        f.close()


def refund_eu(date, buyer, brutto):
    moms = round(brutto * 0.2)
    netto = round(brutto * 0.8)
    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "Refund - {}"\n'.format(date, buyer))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(brutto))
        f.write('#TRANS 3106 {{ }} {}\n'.format(netto))
        f.write('#TRANS 2610 {{ }} {}\n'.format(moms))
        f.write('}\n')
        f.close()


def refund_outside_eu(date, buyer, brutto):
    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "Refund - {}"\n'.format(date, buyer))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} -{}\n'.format(brutto))
        f.write('#TRANS 3105 {{ }} {}\n'.format(brutto))
        f.write('}\n')
        f.close()


def handle_refund(row):
    date = parse_date(row['\ufeff"Datum"'])
    buyer = row['Namn']
    brutto = row['Brutto']
    bruttoNumberPositive = parse_to_positive_number(brutto)
    try:
        countryCode = row['Köparens landskod']
    except KeyError:
        countryCode = row['Landskod']

    summarize_fee(date, 'Återbetalning till {}'.format(
        buyer), bruttoNumberPositive)
    if (countryCode == 'SE'):
        refund_sweden(date, buyer, bruttoNumberPositive)
    elif (is_eu(countryCode)):
        refund_eu(date, buyer, bruttoNumberPositive)
    else:
        refund_outside_eu(date, buyer, bruttoNumberPositive)


def digital_sale(date, buyer, brutto, source):
    with open('paypal.si', 'a') as f:
        f.write('#VER "" "" {} "{} - {}"\n'.format(date, source, buyer))
        f.write('{\n')
        f.write('#TRANS 1933 {{ }} {}\n'.format(brutto))
        f.write('#TRANS 3305 {{ }} -{}\n'.format(brutto))
        f.write('}\n')
        f.close()


def summarize_digital_sale(date, brutto, source):
    with open('month.txt', 'a') as f:
        f.write('{}\n'.format(date))
        f.write('Digital försäljning via {}\n'.format(source))
        f.write('(Utanför EU)\n')
        f.write('{} kr\n'.format(brutto))
        f.write('\n\n')
        f.close()


def handle_digital_sales(row, source, buyer):
    date = parse_date(row['\ufeff"Datum"'])
    brutto = row['Brutto']
    bruttoNumber = parse_to_positive_number(brutto)

    digital_sale(date, buyer, bruttoNumber, source)
    summarize_digital_sale(date, bruttoNumber, buyer)

def handle_kreditering_jawbreaker(row):
    if row['Ärende'].__contains__('Discogs'):
        handle_discogs(row)
    elif row['Typ'].__contains__('Allmän betalning') or row['Typ'].__contains__('Mobilbetalning'):
        handle_sale(row, 'Betalning')
    elif row['Typ'].__contains__('Express Checkout-betalning'):
        handle_bandcamp(row)
    elif row['Fakturanummer'].__contains__('JAW-'):
        handle_webshop(row)
    elif row['Ärende'].__contains__("You've got money from Bandcamp"):
        handle_digital_sales(row, 'Digital sales', 'Bandcamp')
    elif row['Ärende'].__contains__("DistroKid LLC has sent you a payment"):
        handle_digital_sales(row, 'Digital sales', 'Distrokid')
    elif row['Ärende'].__contains__('Label Account Subscription'):
        #ignore, this is handled by the SEK post only
        return
    else:
        print("!!!!! UNKNOWN TRANSACTION TYPE (KREDITERING) !!!!!!")
        print(row['Typ'], row['Namn'], row['Fakturanummer'], row['Ärende'])
        print("")

def handle_kreditering_turborock(row):
    if row['Typ'].__contains__('Express Checkout-betalning'):
        handle_sale(row, 'Turborock.se')
    elif row['Typ'].__contains__('Allmän betalning') or row['Typ'].__contains__('Mobilbetalning'):
        handle_sale(row, 'Betalning')
    elif row['Ärende'].__contains__("You've got money from Bandcamp"):
        handle_digital_sales(row, 'Digital sales', 'Bandcamp')
    else:
        print("!!!!! UNKNOWN TRANSACTION TYPE (KREDITERING) !!!!!!")
        print(row['Typ'], row['Namn'], row['Fakturanummer'], row['Ärende'])
        print("")

def handle_debitering_jawbreaker(row):
    if (row['Ärende'].__contains__('Discogs') or row['Objektstitel'].__contains__('Discogs')) and row['Typ'].__contains__('Partneravgift'):
        handle_discogs_fee(row)
    elif row['Typ'].__contains__('Återbetalning'):
        handle_refund(row)
    elif row['Ärende'].__contains__('Label Account Subscription'):
        handle_bandcamp_subscription(row)
    elif row['Typ'].__contains__('Överföring påbörjad av användare') or row['Typ'].__contains__('Allmän överföring'):
        handle_utbetalning(row)
    else:
        print("!!!!! UNKNOWN TRANSACTION TYPE (DEBITERING) !!!!!!")
        print(row['Typ'], row['Namn'], row['Fakturanummer'], row['Ärende'])
        print("")

# PROGRAM START

with open('paypal.si', 'w') as f:
    f.write('#KONTO 1933 "Paypalkonto"\n')
    f.close()

with open('month.txt', 'w') as f:
    f.write('PAYPAL-HISTORIK månad 2023\n\n\n')
    f.close()

with open('Download.CSV', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Saldoeffekt'].__contains__('Kreditering'):
            if row['Till mejladress'] == 'info@jawbreaker.se' or row['Till mejladress'] == 'paypal@jawbreaker.se':
                handle_kreditering_jawbreaker(row)
            elif row['Till mejladress'] == 'heavymetal@turborock.se' or row['Till mejladress'] == 'linniface@hotmail.com':
                handle_kreditering_turborock(row)
            else:
                print("!!!!! NOT IMPLEMENTED: {} !!!!!!".format(row))
        elif row['Saldoeffekt'].__contains__('Debitering'):
            if row['Från mejladress'] == 'info@jawbreaker.se' or row['Från mejladress'] == 'paypal@jawbreaker.se':
                handle_debitering_jawbreaker(row)
            elif row['Från mejladress'] == 'heavymetal@turborock.se':
                print("NOT IMPLEMENTED")
            else:
                print("!!!!! NOT IMPLEMENTED: {} !!!!!!".format(row))
        else:
            print("!!!!! UNKNOWN TRANSACTION !!!!!!")
            print(row['Typ'], row['Namn'], row['Fakturanummer'], row['Ärende'])

    with open('month.txt', 'a') as f:
        f.write('SALDO VID MÅNADENS UTGÅNG: \n{} kr'.format(row['Saldo']))
        f.close()
