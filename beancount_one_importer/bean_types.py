from datetime import date, datetime, timedelta


def is_str(x):
    return isinstance(x, str) and not is_float(x)


def to_str(x):
    return str(x).strip()


def is_float(x):
    return to_float(x) != None


def to_float(x):
    try:
        f = float(x)
        return f
    except:
        pass

    for c in x:
        if not c.isdigit() and c not in [",", "."]:
            return None

    commas = x.count(",")
    dots = x.count(".")

    if commas == 1 and dots == 0:
        try:
            x_comma = x.replace(",", ".")
            x_comma_num = float(x_comma)
            if x_comma_num != None:
                return x_comma_num
        except:
            return None

    if commas == 1 and dots == 1:
        if x.rfind(".") > x.rfind(","):
            x = x.replace(",", "")
            try:
                f = float(x)
                return f
            except:
                pass
        else:
            x = x.replace(".", "")
            x = x.replace(",", ".")
            try:
                f = float(x)
                return f
            except:
                pass

    if commas > 1 and dots == 0:
        x = x.replace(",", "")
        try:
            f = float(x)
            return f
        except:
            pass

    if commas == 0 and dots > 1:
        x = x.replace(".", "")
        try:
            f = float(x)
            return f
        except:
            pass

    try:
        f = float(x)
        return f
    except:
        return None


def to_num(x):
    if is_float(x):
        return to_float(x)

    parts = x.split(" ")
    if len(parts) == 1:
        return None

    for p in parts:
        pNum = to_float(p)
        if pNum != None:
            return pNum

    return None


def is_num(x):
    return to_num(x) != None


assert (to_num("2.43") == 2.43)
assert (to_num("2,43") == 2.43)
assert (to_num("2,43 EUR") == 2.43)
assert (to_num("2.43 EUR") == 2.43)
assert (to_num("EUR 2,43") == 2.43)
assert (to_num("EUR 2.43") == 2.43)
assert (to_num("5,898.20") == 5898.20)
assert (to_num("5.898,20") == 5898.20)
assert (to_num("5,898,20") == 589820)
assert (to_num("5.898.20") == 589820)


def is_iso_date(x):
    try:
        date.fromisoformat(x)
        return True
    except:
        return False


def is_date(x):
    standard_date = is_excel_date(x) or is_iso_date(x)
    if standard_date:
        return True

    try:
        # 01-Feb-2011
        datetime.strptime(x, "%d-%b-%Y").date()
        return True
    except:
        pass

    try:
        # 2022-04-06 07:39:19
        datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
        return True
    except:
        pass

    #
    # 18-06-2022
    # 18/06/2022
    #


def is_excel_date(x):
    x = to_float(x)
    if x == None:
        return False

    x = to_excel_date(x)
    if 1900 <= x.year and x.year <= 2100:
        return True

    return False


def to_excel_date(excel_date_number):
    if isinstance(excel_date_number, str):
        excel_date_number = to_float(excel_date_number)
    return date(1899, 12, 30) + timedelta(days=excel_date_number)


def to_date(x):
    if is_float(x):
        return to_excel_date(x)
    if not is_str(x):
        return None

    try:
        return date.fromisoformat(x)
    except:
        pass

    try:
        # 01-Feb-2011
        return datetime.strptime(x, "%d-%b-%Y").date()
    except:
        pass

    try:
        # 2022-04-06 07:39:19
        return datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    except:
        pass


assert (to_date("2011-02-01") == date(2011, 2, 1))
assert (to_date("44715.0") == date(2022, 6, 3))
assert (to_date("18-Feb-2020") == date(2020, 2, 18))
assert (to_date("2022-04-06 07:39:19") == date(2022, 4, 6))


def is_currency(x):
    if not is_str(x):
        return False

    s = to_str(x)
    if s == None or s == "":
        return False
    if not s.isalnum():
        return False
    if s.islower():
        return False
    if not s[0].isalpha():
        return False

    return True


def to_currency(x):
    return to_str(x)


assert (is_currency("EUR"))
assert (is_currency("VUSA2"))
assert (is_currency("VUSA 2") == False)

# An account name is a colon-separated list of capitalized words which begin with a letter


def is_account(x):
    if not is_str(x):
        return False

    s = to_str(x)
    if s == None or s == "":
        return False
    if ':' not in s:
        return False

    words = s.split(':')
    for w in words:
        if not w.isalnum():
            return False
        if not w[0].isalpha():
            return False

    return True


def to_currency(x):
    return to_str(x)
