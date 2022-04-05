from urllib.parse import quote_plus as urlenc
import argparse
import sys
import re


class Arguments:
    p = argparse.ArgumentParser
    wait_sec = 0.0
    left = ''
    right = ''
    command = ''
    databases = []
    tables = {}
    columns = {}

    def add_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'request', help='http request file (e.g. intersepted request by burp) payload place should be holded by %%5EPAYLOAD%%5E (html encoded ^PAYLOAD^)')
        parser.add_argument(
            '-p', '--proxy', help='http or socks5 proxy')
        parser.add_argument(
            '-w', '--wait', help='interval between http requests (default: 0.0)')
        parser.add_argument(
            '-d', '--database', help='database from which you want to dump tables (comma separate (arg[/num][,arg[/num][, ...]]))')
        parser.add_argument(
            '-t', '--table', help='table from which you want to dump columns (comma separate (arg[/num][,arg[/num][, ...]]))')
        parser.add_argument(
            '-c', '--column', help='column from which you want to dump data (comma separate (arg[/num][,arg[/num][, ...]]))')
        parser.add_argument(
            '-v', '--verbose', help='verbose mode', action='store_true')
        parser.add_argument(
            '-l', '--left', help='padding string for left', required=True)
        parser.add_argument(
            '-r', '--right', help='padding string for right', required=True)

        return parser

    def retr_option(self, expl, val, verbose, error):
        try:
            result = expl(val)
            if self.p.verbose:
                print(verbose, file=sys.stderr)
            return result
        except:
            print(error, file=sys.stderr)
            exit(1)

    def option_handler(self):
        if self.p.proxy:
            def expl(a): re.match(r'^socks5h?$|^https?$', a) or Exception
            val = self.p.proxy.split(':')[0]
            verbose = f"debug: proxy set: {self.p.proxy}"
            error = f"error: invalid proxy: {self.p.proxy}"
        if self.p.wait:
            def expl(a): return float(a)
            verbose = f"debug: set wait sec for retrieving http requests: {self.p.wait}"
            error = f"error: cannot convert wait to float: -w {self.p.wait}"
            self.wait_sec = self.retr_option(expl, self.p.wait, verbose, error)

    @staticmethod
    def retr_args(raw_args):
        result = []
        for arg in raw_args.split(','):
            elem, *num = arg.split('/')
            num = num or [1]
            result += [elem] * int(num[0])

        return result

    @staticmethod
    def retr_database_list(raw_databases):
        result = []
        for db in raw_databases:
            if db not in result:
                result.append(db)

        return result

    @staticmethod
    def retr_table_dic(raw_databases, raw_tables):
        result = {}
        for db, tb in zip(raw_databases, raw_tables):
            if db not in result:
                result[db] = []
            if tb not in result[db]:
                result[db].append(tb)

        return result

    @staticmethod
    def retr_column_dic(raw_databases, raw_tables, raw_columns):
        result = {}
        for db, tb, cl in zip(raw_databases, raw_tables, raw_columns):
            if db not in result:
                result[db] = {}
            if tb not in result[db]:
                result[db][tb] = []
            if cl not in result[db][tb]:
                result[db][tb].append(cl)

        return result

    def parse_arguments(self):
        if self.p.database is None and self.p.table is None and self.p.column is None:
            self.command = 'database'

        elif self.p.database and self.p.table is None and self.p.column is None:
            raw_databases = self.retr_args(self.p.database)
            self.databases = self.retr_database_list(raw_databases)
            self.command = 'table'

        elif self.p.database and self.p.table and self.p.column is None:
            raw_databases = self.retr_args(self.p.database)
            raw_tables = self.retr_args(self.p.table)
            if len(raw_databases) != len(raw_tables):
                if len(raw_databases) == 1:
                    raw_databases = [raw_databases[0]] * len(raw_tables)

                elif len(raw_tables) == 1:
                    raw_tables = [raw_tables[0]] * len(raw_databases)

                else:
                    print('error: argument length is different', file=sys.stderr)
                    exit(1)

            self.tables = self.retr_table_dic(raw_databases, raw_tables)
            self.databases = self.retr_database_list(raw_databases)
            self.command = 'column'

        elif self.p.database and self.p.table and self.p.column:
            raw_databases = self.retr_args(self.p.database)
            raw_tables = self.retr_args(self.p.table)
            raw_columns = self.retr_args(self.p.column)
            if len(raw_databases) != len(raw_tables) or len(raw_databases) != len(raw_columns):
                if len(raw_databases) == 1:
                    raw_databases = [raw_databases[0]] * \
                        max(len(raw_tables), len(raw_columns))

                if len(raw_tables) == 1:
                    raw_tables = [raw_tables[0]] * \
                        max(len(raw_databases), len(raw_columns))

                if len(raw_columns) == 1:
                    raw_columns = [raw_columns[0]] * \
                        max(len(raw_databases), len(raw_tables))

                if len(raw_databases) != len(raw_tables) or len(raw_databases) != len(raw_columns):
                    print('error: argument length is different', file=sys.stderr)
                    exit(1)

            self.columns = self.retr_column_dic(
                raw_databases, raw_tables, raw_columns)
            self.tables = self.retr_table_dic(raw_databases, raw_tables)
            self.databases = self.retr_database_list(raw_databases)
            self.command = 'data'
        else:
            print('error: invalid arguments', file=sys.stderr)
            exit(1)

    def __init__(self):
        parser = self.add_arguments()
        self.p = parser.parse_args()
        self.option_handler()

        self.left = urlenc(self.p.left)
        self.right = urlenc(self.p.right)

        self.parse_arguments()


class MssqlTimeArguments(Arguments):
    sleep_sec = 1

    def add_arguments(self):
        parser = super().add_arguments()
        parser.add_argument(
            '-s', '--sleep', help='seconds for sleep to be considered valid when the response takes longer than this (default: 1)')

        return parser

    def option_handler(self):
        super().option_handler()
        if self.p.sleep:
            def expl(a): return int(a)
            verbose = f"debug: set sleep sec for judging valid queries: {self.p.sleep}"
            error = f"error: cannot convert sleep to int: -s {self.p.sleep}"
            self.sleep_sec = self.retr_option(
                expl, self.p.sleep, verbose, error)

    def __init__(self):
        super().__init__()
