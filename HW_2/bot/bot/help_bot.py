from switcher import main as switcher
from help_bot_classes import (
    AddressBook,
    Name,
    Phone,
    Email,
    Address,
    Record,
    Birthday,
    PhoneError,
    BirthdayError,
    EmailError,
    RequestShowTable,
    RequestShowString,
    Handler,
    RequestShowHelp,
)
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from prompt_toolkit.styles import Style
from pathlib import Path

helper = {
    "add": "example: add name",
    "add_address": "example: add_address name City, street ...",
    "add_birthday": "example: add_birthday name dd.mm.yyyy",
    "add_email": "example: add_email name somemail@someservis.com",
    "change_email": "example: change_email name somemail@someservis.com:",
    "add_phone": "example: add_phone name 0501111111 or +30501111111",
    "birthdays": "example: birthdays N(N=number of days from today)",
    "change_phone": "example: change_phone name ____(old_phone) ____(new_phone)",
    "close, exit, good_bye": "example: close",
    "del_contact": "example: del_contact name",
    "hello": "example: hello (show Welcome)",
    "search": "example:search some_info(name,phone,email,address or bd)",
    "show_contacts_tabl": "show all contacts in table",
    "show_contacts_string": "show all contacs in strings",
    "show_list_commands": "show list commands",
    "help": "help",
}


def create_request_show_help(*args):
    request_help = RequestShowHelp()
    string_handler = Handler(request_help)
    return string_handler.output_date(helper)


def create_request_show_string(*args):
    request_string = RequestShowString()
    string_handler = Handler(request_string)
    return string_handler.output_date(address_book)


def create_request_show_table(*args):
    request_table = RequestShowTable()
    string_handler = Handler(request_table)
    return string_handler.output_date(show_contacts_tabl(""))


def load_ab() -> AddressBook:
    destination = Path.home()
    sourse = Path("address_book.dat")
    path = destination.joinpath(sourse)
    open(path, "a").close()

    return path


address_book = AddressBook(load_ab())

try:
    address_book.read_from_file()
except:
    pass

table = Table(title="Address book")
console = Console()


def reset_table():
    global table

    table = Table(title="Address book")

    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Birthday", style="magenta")
    table.add_column("Phones", justify="right", style="green")
    table.add_column("E-mail", justify="right", style="green")
    table.add_column("Address", justify="right", style="green")


def save_to_file(func):
    def inner(args):
        result = func(args)
        address_book.save_to_file()
        return result

    return inner


def read_from_file(func):
    def inner(args):
        result = func(args)
        address_book.read_from_file()
        return result

    return inner


def input_error(func):
    def inner(args):
        try:
            result = func(args)
            return result
        except IndexError:
            if func.__name__ == "add" or func.__name__ == "change":
                return "Give me name and phone please"
            elif func.__name__ == "phone":
                return "Give me phone please"
            elif func.__name__ == "birthdays":
                return "Give me a number of days please!"
            else:
                return "Wrong parameters!"
        except KeyError:
            if func.__name__ == "phone" or func.__name__ == "change":
                return "Contact doesn't exist"
        except ValueError:
            if func.__name__ == "change":
                return "Contact doesn't exist"
            elif func.__name__ == "birthdays":
                return "Give me a number of days please!"
            else:
                return "Wrong parameters"
        except PhoneError:
            return "Phone must contain 10 digits and starts with 0 or 12 digits and starts with 380"
        except BirthdayError:
            return "Birthday format is dd.mm.yyyy"
        except EmailError:
            return "Please enter your email correctly"

    return inner


def hello(args):
    return "How can I help you?"


@input_error
@save_to_file
def add(args):
    name = Name(args[0])
    rec = Record(name)
    return address_book.add_record(rec)


@input_error
@save_to_file
def add_phone(args):
    name = Name(args[0])
    phone = Phone(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_phone(phone)
    rec = Record(name, phone)
    return address_book.add_record(rec)


@input_error
@save_to_file
def del_contact(args: str) -> str:
    name = Name(args[0])
    rec: Record = address_book.get(str(name))
    if rec:
        return address_book.del_record(rec)
    return f"No contact {name} in address book"


@input_error
@save_to_file
def add_email(args):
    name = Name(args[0])
    email = Email(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_email(email)
    rec = Record(name, email)
    return address_book.add_record(rec)


@input_error
@save_to_file
def add_birthday(args):
    name = Name(args[0])
    birthday = Birthday(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_birthday(birthday)
    rec = Record(name, birthday)
    return address_book.add_record(rec)


@input_error
@save_to_file
def add_address(args):
    name = Name(args[0])
    address_str = " ".join(x for x in args[1:])
    address = Address(address_str)
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_address(address)
    rec = Record(name, address)
    return address_book.add_record(rec)


@input_error
@save_to_file
def del_contact(args: str) -> str:
    name = Name(args[0])
    rec: Record = address_book.get(str(name))
    if rec:
        return address_book.del_record(rec)
    return f"No contact {name} in address book"


@input_error
@save_to_file
def change(args):
    """Get 2 phones to change
    or 1 phone to remove"""
    record = address_book.search_record_by_name(args[0])
    try:
        new_phone = Phone(args[2])
        return record.change_phone(args[1], new_phone)
    except:
        return record.remove_phone(args[1])


@input_error
@read_from_file
def search(args):
    reset_table()
    records = address_book.search_record(args[0])
    if not records:
        return f"Contacts not found"
    for rec in records:
        table.add_row(
            str(rec.name),
            str(rec.birthday),
            ", ".join(str(p) for p in rec.phones),
            str(rec.email),
            str(rec.address),
        )

    console = Console()
    console.print()

    return ""


@input_error
@read_from_file
def show_contacts_tabl(args):
    page = 0
    count = 0
    count_of_records = int(args[0]) if len(args) else 5
    records = address_book.values()
    if not records:
        return f"No contacts"
    for rec in records:
        if not count:
            page += 1
            print(f"page {page}")
            reset_table()
        if count == count_of_records:
            console = Console()
            console.print(table)
            page += 1
            print(f"page {page}")
            reset_table()
            count = 0
        count += 1
        table.add_row(
            str(rec.name),
            str(rec.birthday),
            ", ".join(str(p) for p in rec.phones),
            str(rec.email),
            str(rec.address),
        )
    console = Console()
    console.print(table)

    return ""


@read_from_file
@input_error
def birthdays(args):
    reset_table()
    days = int(args[0])
    birthdays_list = address_book.birthdays(days)
    if not birthdays_list:
        return f"No birthdays in the next {days} days"
    for rec in birthdays_list:
        table.add_row(
            str(rec.name),
            str(rec.birthday),
            ", ".join(str(p) for p in rec.phones),
            str(rec.email),
            str(rec.address),
        )

    console = Console()
    console.print(table)

    return ""


def no_command(args):
    return "Unknown command"


COMMANDS = {
    ("add_name",): add,
    ("add_address", "change_address"): add_address,
    ("add_birthday",): add_birthday,
    ("add_email", "change_email"): add_email,
    ("add_phone",): add_phone,
    ("birthdays",): birthdays,
    ("change_phone",): change,
    ("close",): exit,
    ("del_contact",): del_contact,
    ("exit",): exit,
    ("good_bye",): exit,
    ("hello",): hello,
    ("search",): search,
    ("switcher",): switcher,
    ("show_contacts_tabl",): create_request_show_table,
    ("show_contacts_string",): create_request_show_string,
    ("help",): create_request_show_help,
}


def get_list_for_prediction():
    name_for_pred = [name for name in address_book.keys()]
    email_for_pred = [
        str(mails.email)
        for mails in address_book.values()
        if str(mails.email) != "None"
    ]
    address_for_pred = [
        str(rec.address) for rec in address_book.values() if rec.address
    ]
    phone_for_pred = [str(rec.phones) for rec in address_book.values() if rec.phones]
    phones = [phone[1:-1] for phone in phone_for_pred]
    list_for_predict = [command for commands in COMMANDS.keys() for command in commands]
    list_for_predict.extend(name_for_pred)
    list_for_predict.extend(email_for_pred)
    list_for_predict.extend(address_for_pred)
    list_for_predict.extend(phones)
    list_for_predict = WordCompleter(list_for_predict)
    return list_for_predict


def style_for_input():
    style = Style.from_dict({"": "ansicyan underline"})
    return style


def parser(text: str) -> tuple[callable, list[str]]:
    text = text.strip().split()
    for comm, func in COMMANDS.items():
        if text[0].lower() in comm:
            text = text[1:]
            return func, text
    return no_command, ""


def main():
    while True:
        user_input = prompt(
            ">>> ", completer=get_list_for_prediction(), style=style_for_input()
        )
        command, data = parser(user_input)
        if command == exit:
            print("Buy! Have a nice day!")
            break
        result = command(data)
        print(result)


if __name__ == "__main__":
    main()
