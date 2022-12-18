from datetime import date, datetime, timedelta
from beancount.core.number import Decimal


def is_str(x) -> bool:
    return isinstance(x, str) and not is_float(x)


def to_str(x) -> str:
    return str(x).strip()


def to_decimal(x) -> Decimal:
    return Decimal(to_str(to_num(x)))


def is_float(x) -> bool:
    return to_float(x) != None


def to_float(inp: str | float) -> float | None:
    try:
        if isinstance(inp, float):
            f = inp
        else:
            f = float(inp)
        return f
    except:
        pass

    x = str(inp).strip()
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


def is_excel_date(input: str | float):
    x = to_float(input)
    if x == None:
        return False

    dt = to_excel_date(x)
    if dt == None:
        return False
    if 2000 <= dt.year and dt.year <= 2100:
        return True

    return False


def to_excel_date(input: float | str):
    if input == None:
        return None
    elif isinstance(input, str):
        excel_date_number = to_float(input)
        if excel_date_number == None:
            return None
    else:
        excel_date_number = input
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


def is_currency(x):
    if not is_str(x):
        return False

    s = to_str(x)
    if s == None or s == "":
        return False
    if not s.isalnum():
        return False
    if not s.isupper():
        return False
    if not s[0].isalpha():
        return False

    return True


def to_currency(x):
    return to_str(x)


# An account name is a colon-separated list of capitalized words which begin with a letter
def is_account(x):
    if not is_str(x):
        return False

    s = to_str(x)
    if s == None or s == "":
        return False
    if ":" not in s:
        return False

    words = s.split(":")
    for w in words:
        if not w.isalnum():
            return False
        if not w[0].isalpha():
            return False

    return True
